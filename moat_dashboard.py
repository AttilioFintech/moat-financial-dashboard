import streamlit as st

from pages.dashboard import render as dashboard_page
from pages.trajectory import render as trajectory_page
from pages.whatif import render as whatif_page
from pages.vulnerabilities import render as vulnerabilities_page
from pages.archetypes import render as archetypes_page
from pages.about import render as about_page


page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Trajectory",
        "What-If",
        "Vulnerabilities",
        "Archetypes",
        "About"
    ]
)

if page == "Dashboard":
    dashboard_page()
elif page == "Trajectory":
    trajectory_page()
elif page == "What-If":
    whatif_page()
elif page == "Vulnerabilities":
    vulnerabilities_page()
elif page == "Archetypes":
    archetypes_page()
elif page == "About":
    about_page()

