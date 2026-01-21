# 1. Importiamo le funzioni render una sola volta all'inizio
from pages.dashboard import render as dashboard_page
from pages.trajectory import render as trajectory_page
from pages.whatif import render as whatif_page
from pages.vulnerabilities import render as vulnerabilities_page
from pages.archetypes import render as archetypes_page
from pages.about import render as about_page

# =============================
# CONFIGURAZIONE PAGINA
# =============================
st.set_page_config(
    page_title="Moat – Strategic Financial Resilience",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================
# SIDEBAR (Navigazione)
# =============================
st.sidebar.title("🏰 MOAT")

st.sidebar.markdown(
    """
    **Strategic Financial Resilience Tool**
    
    Moat helps you decide **where to allocate**
    your time, energy, and capital —  
    not how much coffee to cut.
    """
)

# Mappatura etichette -> Funzioni (per rendere il codice pulito)
PAGE_MAP = {
    "📊 Strategic Dashboard": dashboard_page,
    "🔮 What-If Scenarios": whatif_page,
    "📈 Trajectory": trajectory_page,
    "🛡 Vulnerabilities": vulnerabilities_page,
    "🧠 Archetypes": archetypes_page,
    "ℹ️ About": about_page
}

# Selezione della pagina tramite Radio
selected_label = st.sidebar.radio("Navigate", list(PAGE_MAP.keys()))

st.sidebar.divider()

st.sidebar.markdown(
    """
    🔒 **PRO ACCESS**
    
    Advanced simulations, projections  
    and strategic recommendations  
    are available via selective access.
    """
)

# =============================
# LOGICA DI ROUTING (Esecuzione)
# =============================
# Eseguiamo direttamente la funzione corrispondente alla scelta
if selected_label in PAGE_MAP:
    PAGE_MAP[selected_label]()
else:
    st.error("Page not found.")
