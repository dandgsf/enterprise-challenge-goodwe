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
POWER_CHART_COLORS = ["#F6C453", "#4CC9F0", "#C4A7FF"]
BALANCE_CHART_COLORS = ["#F6C453", "#4CC9F0", "#C4A7FF", "#42D3B7"]

THEME_CSS = """
<style>
    :root {
        --ops-ink: #f4f7f9;
        --ops-muted: #b8c5ce;
        --ops-surface: #17222b;
        --ops-canvas: #0e151b;
        --ops-border: #3b4b57;
        --ops-red: #e60013;
        --ops-red-strong: #ff6b76;
        --ops-teal: #42d3b7;
    }

    .stApp {
        background: var(--ops-canvas);
        color: var(--ops-ink);
    }

    [data-testid="stSidebar"] > div:first-child {
        background: #080d12;
        border-right: 1px solid #2b3a45;
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #f8fafc !important;
    }

    [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
    [data-testid="stSidebar"] small {
        color: #dce6ed !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(203, 213, 223, 0.28);
        border-radius: 14px;
        padding: 0.65rem;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button * {
        color: #f4f7f9 !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] [data-baseweb="input"] {
        border-radius: 10px;
    }

    [data-testid="stMainBlockContainer"] [data-testid="stCaptionContainer"],
    [data-testid="stMainBlockContainer"] [data-testid="stCaptionContainer"] p {
        color: var(--ops-muted) !important;
        opacity: 1 !important;
    }

    h1, h2, h3 {
        color: var(--ops-ink);
        font-family: Aptos, "Segoe UI", sans-serif;
        letter-spacing: -0.02em;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--ops-surface);
        border: 1px solid var(--ops-border);
        border-radius: 16px;
        box-shadow: 0 18px 38px -28px rgba(0, 0, 0, 0.88);
    }

    [data-testid="stMetric"] {
        background: var(--ops-surface);
        border-top: 3px solid var(--ops-red);
        border-radius: 14px;
        box-shadow: 0 14px 28px -22px rgba(0, 0, 0, 0.92);
        min-height: 7.4rem;
        padding: 0.9rem 1rem 0.75rem;
        transition: transform 180ms ease, box-shadow 180ms ease;
    }

    [data-testid="stMetric"]:hover {
        box-shadow: 0 18px 32px -22px rgba(0, 0, 0, 1);
        transform: translateY(-2px);
    }

    [data-testid="stMetricLabel"] p {
        color: var(--ops-muted) !important;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.01em;
        white-space: normal;
    }

    [data-testid="stMetricValue"] {
        color: var(--ops-ink);
        font-variant-numeric: tabular-nums;
    }

    .stButton > button[kind="primary"] {
        background: var(--ops-red);
        border: 1px solid var(--ops-red);
        border-radius: 10px;
        box-shadow: 0 10px 20px -16px rgba(230, 0, 19, 0.8);
        font-weight: 700;
        transition: transform 160ms ease, background 160ms ease, box-shadow 160ms ease;
    }

    .stButton > button[kind="primary"],
    .stButton > button[kind="primary"] p {
        color: #ffffff !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: #bf0010;
        border-color: #bf0010;
        box-shadow: 0 14px 24px -16px rgba(191, 0, 16, 0.84);
        transform: translateY(-1px);
    }

    .stButton > button[kind="primary"]:active {
        transform: translateY(1px) scale(0.99);
    }

    [data-baseweb="tab-list"] {
        gap: 0.7rem;
        border-bottom: 1px solid var(--ops-border);
    }

    button[data-baseweb="tab"] {
        color: #c4d0d8 !important;
        font-weight: 650;
        padding: 0.45rem 0.25rem 0.65rem;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--ops-red-strong) !important;
    }

    button[data-baseweb="tab"] p {
        color: inherit !important;
    }

    [data-testid="stSelectbox"] label p,
    [data-testid="stRadio"] label p {
        color: #e6edf2 !important;
        font-weight: 600;
    }

    [data-testid="stTable"] thead tr,
    [data-testid="stTable"] thead th {
        background: #263640 !important;
    }

    [data-testid="stTable"] thead th p {
        color: #f4f7f9 !important;
        font-weight: 700;
    }

    [data-testid="stTable"] tbody td p {
        color: #e6edf2 !important;
    }

    [data-testid="stTable"] tbody tr:nth-child(even) {
        background: #111b23;
    }

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    .ops-signal {
        align-items: center;
        color: var(--ops-muted);
        display: inline-flex;
        font-size: 0.78rem;
        font-weight: 650;
        gap: 0.45rem;
        letter-spacing: 0.01em;
        margin-top: 0.1rem;
    }

    .ops-signal__dot {
        animation: ops-pulse 2.2s ease-in-out infinite;
        background: var(--ops-teal);
        border-radius: 50%;
        display: inline-block;
        height: 0.5rem;
        width: 0.5rem;
    }

    @keyframes ops-pulse {
        0%, 100% { opacity: 0.6; transform: scale(0.9); }
        50% { opacity: 1; transform: scale(1.15); }
    }

    @media (prefers-reduced-motion: reduce) {
        .ops-signal__dot { animation: none; }
        [data-testid="stMetric"],
        .stButton > button[kind="primary"] { transition: none; }
    }

    @media (max-width: 760px) {
        [data-testid="stMetric"] { min-height: auto; }
        [data-baseweb="tab-list"] { gap: 0.25rem; }
        button[data-baseweb="tab"] { font-size: 0.8rem; }

        [data-testid="stVerticalBlockBorderWrapper"] h2 {
            font-size: 1.35rem;
        }

        [data-testid="stVerticalBlockBorderWrapper"] .ops-signal {
            font-size: 0.68rem;
        }
    }
</style>
"""


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

    for start in range(0, len(metrics), 3):
        row_metrics = metrics[start : start + 3]
        columns = st.columns(len(row_metrics))
        for column, metric in zip(columns, row_metrics, strict=True):
            column.metric(metric.label, metric.value, help=metric.context)


def _render_brand_header(view_model: DashboardViewModel) -> None:
    """Exibe as marcas do projeto sem competir com os indicadores da aplicação."""
    with st.container(border=True):
        goodwe_column, identity_column = st.columns((1, 6.2), vertical_alignment="center")
        with goodwe_column:
            st.image(GOODWE_LOGO_PATH, width=46)
            st.caption("GoodWe")
        with identity_column:
            title_column, fiap_column = st.columns((4.8, 1.2), vertical_alignment="center")
            with title_column:
                st.header(view_model.title)
                st.caption(view_model.subtitle)
            with fiap_column:
                st.image(FIAP_ON_LOGO_PATH, width=112)
            st.markdown(
                "<div class='ops-signal' role='status'>"
                "<span class='ops-signal__dot' aria-hidden='true'></span>"
                "Modo demonstrativo · processamento local</div>",
                unsafe_allow_html=True,
            )
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
    st.subheader(f"Memória de cálculo — {selected_unit}")
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
        chart_mode = st.radio(
            "Visualização energética",
            ("Potência instantânea", "Balanço energético"),
            horizontal=True,
            key="energy_chart_mode",
        )
        if chart_mode == "Potência instantânea":
            chart_data = pd.DataFrame(point.as_chart_row() for point in view_model.energy_points)
            chart_data = chart_data.set_index("Horário")
            st.line_chart(chart_data, color=POWER_CHART_COLORS, width="stretch")
        else:
            balance_data = pd.DataFrame(
                point.as_balance_chart_row() for point in view_model.energy_points
            )
            balance_data = balance_data.set_index("Horário")
            st.line_chart(balance_data, color=BALANCE_CHART_COLORS, width="stretch")
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
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(THEME_CSS, unsafe_allow_html=True)
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
