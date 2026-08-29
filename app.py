"""Entrypoint local do dashboard Streamlit."""

from ev_chargeops.dashboard import render_dashboard
from ev_chargeops.viewmodels import empty_dashboard_view_model

render_dashboard(empty_dashboard_view_model())
