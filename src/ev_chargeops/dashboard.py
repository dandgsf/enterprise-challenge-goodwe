"""Página Streamlit do EV ChargeOps.

Toda métrica recebida aqui já foi calculada pela camada de domínio. Filtros
alteram somente linhas visíveis e nunca recalculam os denominadores globais.
"""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from ev_chargeops.viewmodels import DashboardViewModel, NoticeViewModel

ProcessHandler = Callable[
    [UploadedFile | None, UploadedFile | None, Decimal, Decimal], DashboardViewModel
]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
GOODWE_LOGO_PATH = PROJECT_ROOT / "assets" / "brand" / "goodwe.svg"
FIAP_ON_LOGO_PATH = PROJECT_ROOT / "assets" / "brand" / "fiap-on.svg"


def _render_notice(notice: NoticeViewModel) -> None:
    renderers = {
        "error": st.error,
        "success": st.success,
        "warning": st.warning,
    }
    renderers.get(notice.level, st.info)(notice.message)


def _render_metric_strip(metrics: tuple) -> None:
    if not metrics:
        st.info("Nenhuma métrica disponível para o recorte atual.")
        return

    columns = st.columns(len(metrics))
    for column, metric in zip(columns, metrics, strict=True):
        column.metric(metric.label, metric.value, help=metric.context)


def _render_brand_header(view_model: DashboardViewModel) -> None:
    """Exibe as marcas do projeto sem competir com os indicadores da aplicação."""
    with st.container(border=True):
        goodwe_column, identity_column, fiap_column = st.columns(
            (1, 4.7, 1.3), vertical_alignment="center"
        )
        with goodwe_column:
            st.image(GOODWE_LOGO_PATH, width=46)
            st.caption("GoodWe")
        with identity_column:
            st.header(view_model.title)
            st.caption(view_model.subtitle)
        with fiap_column:
            st.image(FIAP_ON_LOGO_PATH, width=112)
    st.divider()


def _render_sidebar(
    view_model: DashboardViewModel,
    process_handler: ProcessHandler | None,
) -> DashboardViewModel:
    with st.sidebar:
        st.header("Fontes e premissas")
        st.caption("Os arquivos enviados são processados somente em memória.")
        sessions_upload = st.file_uploader(
            "Sessões de recarga (CSV)", type=("csv",), key="sessions_upload"
        )
        energy_upload = st.file_uploader(
            "Energia da planta (CSV)", type=("csv",), key="energy_upload"
        )
        tariff = st.number_input(
            "Tarifa (R$/kWh)", min_value=0.0, value=0.92, step=0.01, format="%.2f"
        )
        common_cost = st.number_input(
            "Custo comum mensal (R$)",
            min_value=0.0,
            value=80.0,
            step=10.0,
            format="%.2f",
        )

        if st.button("Aplicar e processar", type="primary", width="stretch"):
            only_one_upload = (sessions_upload is None) != (energy_upload is None)
            if only_one_upload:
                st.warning("Envie os dois CSVs ou deixe ambos vazios para usar a demonstração.")
            elif process_handler is None:
                st.info("O processamento será conectado pela camada de composição do MVP.")
            else:
                try:
                    view_model = process_handler(
                        sessions_upload,
                        energy_upload,
                        Decimal(str(tariff)),
                        Decimal(str(common_cost)),
                    )
                    st.session_state["ev_chargeops_view_model"] = view_model
                    st.success("Arquivos processados. O painel foi atualizado.")
                except (TypeError, ValueError) as exc:
                    st.error(f"Não foi possível processar os arquivos: {exc}")

        st.divider()
        st.markdown(f"**Período:** {view_model.reference_period}")
        st.caption(f"Sessões: {view_model.sessions_source}")
        st.caption(f"Energia: {view_model.energy_source}")
        st.caption(f"Atualizado em: {view_model.generated_at}")
        st.warning(f"Ociosidade: {view_model.idle_measurement}")

    return view_model


def _render_overview(view_model: DashboardViewModel) -> None:
    _render_metric_strip(view_model.overview_metrics)
    st.subheader("Reconciliação")
    if view_model.reconciliation:
        st.table(
            pd.DataFrame(
                {"Indicador": row.label, "Valor": row.value} for row in view_model.reconciliation
            )
        )
    else:
        st.info("Processe as fontes para gerar a reconciliação do fechamento.")
    st.caption(
        "Os indicadores usam o conjunto global validado. Filtros das demais abas não alteram "
        "o denominador do rateio."
    )


def _render_sessions(view_model: DashboardViewModel) -> None:
    if not view_model.sessions:
        st.info("Nenhuma sessão disponível.")
        return

    statuses = ("Todas", *sorted({row.status for row in view_model.sessions}))
    selected_status = st.selectbox("Filtrar status", statuses, key="session_status_filter")
    visible_rows = tuple(
        row
        for row in view_model.sessions
        if selected_status == "Todas" or row.status == selected_status
    )
    st.caption(
        f"Exibindo {len(visible_rows)} de {len(view_model.sessions)} sessões. "
        "Este filtro é apenas visual e não recalcula faturas ou indicadores globais."
    )
    st.dataframe(
        pd.DataFrame(row.as_table_row() for row in visible_rows),
        hide_index=True,
        width="stretch",
    )
    st.warning(
        "Alertas de IA são consultivos e priorizam revisão humana; nunca autorizam ou "
        "bloqueiam cobrança automaticamente."
    )


def _render_invoices(view_model: DashboardViewModel) -> None:
    if not view_model.invoices:
        st.info("Nenhuma unidade com consumo faturável no período.")
        return

    st.dataframe(
        pd.DataFrame(row.as_table_row() for row in view_model.invoices),
        hide_index=True,
        width="stretch",
    )

    unit_ids = tuple(row.unit_id for row in view_model.invoices)
    selected_unit = st.selectbox("Detalhar unidade", unit_ids, key="invoice_unit_filter")
    visible_items = tuple(
        item for item in view_model.invoice_items if item.unit_id == selected_unit
    )
    st.subheader(f"Memoria de calculo — {selected_unit}")
    if visible_items:
        st.table(pd.DataFrame(item.as_table_row() for item in visible_items))
    else:
        st.info("Não há itens detalhados para esta unidade.")
    st.caption(
        "A seleção detalha uma fatura existente; o custo comum e os totais permanecem "
        "calculados sobre todas as unidades ativas."
    )


def _render_energy(view_model: DashboardViewModel) -> None:
    _render_metric_strip(view_model.energy_metrics)
    if view_model.energy_points:
        chart_data = pd.DataFrame(point.as_chart_row() for point in view_model.energy_points)
        chart_data = chart_data.set_index("Horário")
        st.line_chart(chart_data, width="stretch")
    else:
        st.info("Nenhum snapshot energético disponível.")

    st.subheader("Recomendações explicáveis")
    if not view_model.recommendations:
        st.info("Não há evidência suficiente para gerar recomendações.")
    for recommendation in view_model.recommendations:
        with st.expander(f"{recommendation.priority} — {recommendation.title}", expanded=True):
            st.write(recommendation.message)
            st.markdown(f"**Evidência:** {recommendation.evidence}")
            st.caption(f"Premissas e limites: {recommendation.assumptions}")
    st.info(
        "Pré-viabilidade fotovoltaica e recomendações operacionais exigem validação técnica "
        "antes de qualquer decisão real."
    )


def render_dashboard(
    view_model: DashboardViewModel,
    *,
    process_handler: ProcessHandler | None = None,
) -> None:
    """Renderiza um snapshot do dashboard sem executar regras de domínio."""
    st.set_page_config(
        page_title="EV ChargeOps",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    stored_view = st.session_state.get("ev_chargeops_view_model")
    if isinstance(stored_view, DashboardViewModel):
        view_model = stored_view
    view_model = _render_sidebar(view_model, process_handler)

    _render_brand_header(view_model)
    for notice in view_model.notices:
        _render_notice(notice)

    overview_tab, sessions_tab, invoices_tab, energy_tab = st.tabs(
        ("Visão geral", "Sessões e alertas", "Rateio e faturas", "Energia e recomendações")
    )
    with overview_tab:
        _render_overview(view_model)
    with sessions_tab:
        _render_sessions(view_model)
    with invoices_tab:
        _render_invoices(view_model)
    with energy_tab:
        _render_energy(view_model)
