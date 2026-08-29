"""Entrypoint local do dashboard Streamlit."""

from decimal import Decimal

from ev_chargeops.composition import build_dashboard_view
from ev_chargeops.dashboard import render_dashboard
from ev_chargeops.uploads import read_upload_pair
from ev_chargeops.viewmodels import DashboardViewModel


def process_sources(
    sessions_upload,
    energy_upload,
    tariff: Decimal,
    common_cost: Decimal,
) -> DashboardViewModel:
    """Processa uploads pareados ou recarrega os dados simulados incluídos."""

    if sessions_upload is None and energy_upload is None:
        return build_dashboard_view(
            tariff_per_kwh=tariff,
            monthly_common_cost=common_cost,
        )
    if sessions_upload is None or energy_upload is None:
        raise ValueError("Os dois arquivos CSV precisam ser enviados em conjunto.")
    sessions_payload, energy_payload = read_upload_pair(sessions_upload, energy_upload)
    return build_dashboard_view(
        sessions_payload,
        energy_payload,
        sessions_filename=sessions_upload.name,
        energy_filename=energy_upload.name,
        tariff_per_kwh=tariff,
        monthly_common_cost=common_cost,
    )


def main() -> None:
    """Renderiza o aplicativo quando executado pelo Streamlit."""

    render_dashboard(build_dashboard_view(), process_handler=process_sources)


if __name__ == "__main__":
    main()
