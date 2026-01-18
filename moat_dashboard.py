import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from groq import Groq
import json
import numpy as np

# Configurazione pagina
st.set_page_config(
    page_title="Moat Financial Dashboard",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Custom - Colore dominante: Deep Blue (#1e3a8a)
st.markdown("""
<style>
    :root {
        --moat-blue: #1e3a8a;
        --moat-light: #3b82f6;
        --moat-accent: #60a5fa;
    }
    
    .big-kpi {
        font-size: 4rem !important;
        font-weight: bold;
        color: var(--moat-blue);
        text-align: center;
        margin: 20px 0;
    }
    
    .kpi-label {
        font-size: 1.2rem;
        color: #6b7280;
        text-align: center;
        font-weight: 500;
    }
    
    .pro-banner {
        background: linear-gradient(135deg, var(--moat-blue) 0%, var(--moat-light) 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        margin: 20px 0;
        text-align: center;
    }
    
    .pro-cta {
        background: white;
        color: var(--moat-blue);
        padding: 15px 40px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 1.1rem;
        border: none;
        cursor: pointer;
        display: inline-block;
        margin: 10px;
        text-decoration: none;
    }
    
    .claim {
        font-size: 1.5rem;
        color: var(--moat-blue);
        font-weight: 600;
        margin: 20px 0;
    }
    
    .secondary-section {
        margin-top: 40px;
        padding-top: 30px;
        border-top: 2px solid #e5e7eb;
    }
    
    .achievement-badge {
        background: linear-gradient(135deg, var(--moat-blue) 0%, var(--moat-light) 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATABASE & CONNESSIONI ====================
DB_PATH = "gestione_conti_casa_demo.db"

@st.cache_resource
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

@st.cache_resource
def get_groq_client():
    try:
        api_key = st.secrets["groq"]["api_key"]
        return Groq(api_key=api_key)
    except Exception as e:
        return None

# ==================== INIZIALIZZAZIONE TABELLE ====================
def init_all_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Notifications (
            id INTEGER PRIMARY KEY,
            tipo VARCHAR(50),
            titolo VARCHAR(200),
            messaggio TEXT,
            priorita VARCHAR(20),
            data_creazione DATETIME DEFAULT CURRENT_TIMESTAMP,
            letta INTEGER DEFAULT 0,
            data_lettura DATETIME,
            azione_suggerita TEXT,
            dati_json TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Achievements (
            id INTEGER PRIMARY KEY,
            nome VARCHAR(100),
            descrizione TEXT,
            categoria VARCHAR(50),
            icona TEXT,
            requisiti_json TEXT,
            punti INTEGER DEFAULT 100,
            sbloccato INTEGER DEFAULT 0,
            data_sblocco DATETIME,
            livello INTEGER DEFAULT 1
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS AccessRequests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            profile TEXT,
            note TEXT,
            request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    """)
    
    conn.commit()

# ==================== CARICAMENTO DATI ====================
@st.cache_data(ttl=300)
def load_all_data():
    conn = get_db_connection()
    
    try:
        trans_query = "SELECT * FROM Transazioni ORDER BY data DESC"
        df_trans = pd.read_sql_query(trans_query, conn)
    except Exception:
        df_trans = pd.DataFrame()
    
    if 'data' in df_trans.columns:
        df_trans['data'] = pd.to_datetime(df_trans['data'], errors='coerce')
    
    if 'moat_classification' not in df_trans.columns:
        df_trans['moat_classification'] = None
    
    try:
        assets_query = "SELECT * FROM Assets WHERE attivo = 1"
        df_assets = pd.read_sql_query(assets_query, conn)
    except Exception:
        df_assets = pd.DataFrame()
    
    return df_trans, df_assets

# ==================== CALCOLO METRICHE ====================
def calculate_moat_metrics(df):
    metrics = {}
    
    if df is None or len(df) == 0:
        return {
            'entrate_totali': 0,
            'entrate_ricorrenti': 0,
            'percentuale_ricorrenti': 0,
            'uscite_fisse': 0,
            'uscite_variabili': 0,
            'tasso_risparmio': 0,
            'investimenti_personali': 0,
            'spesa_protezione': 0,
            'fonti_entrate': 0
        }
    
    entrate = df[df['direzione'] == 'Entrata'] if 'direzione' in df.columns else pd.DataFrame()
    
    if 'is_ricorrente' in df.columns:
        entrate_ricorrenti = entrate[entrate['is_ricorrente'] == 'Sì']
    else:
        entrate_ricorrenti = pd.DataFrame()
    
    uscite = df[df['direzione'] == 'Uscita'] if 'direzione' in df.columns else pd.DataFrame()
    
    metrics['entrate_totali'] = entrate['importo'].sum() if 'importo' in entrate.columns else 0
    metrics['entrate_ricorrenti'] = entrate_ricorrenti['importo'].sum() if 'importo' in entrate_ricorrenti.columns else 0
    metrics['percentuale_ricorrenti'] = (
        metrics['entrate_ricorrenti'] / metrics['entrate_totali'] * 100 
        if metrics['entrate_totali'] > 0 else 0
    )
    
    if 'classe_finanziaria' in uscite.columns:
        metrics['uscite_fisse'] = uscite[uscite['classe_finanziaria'] == 'Uscite fisse']['importo'].sum()
        metrics['uscite_variabili'] = uscite[uscite['classe_finanziaria'] == 'Uscite variabili']['importo'].sum()
    else:
        metrics['uscite_fisse'] = 0
        metrics['uscite_variabili'] = uscite['importo'].sum() if 'importo' in uscite.columns else 0
    
    total_uscite = uscite['importo'].sum() if 'importo' in uscite.columns else 0
    metrics['tasso_risparmio'] = (
        (metrics['entrate_totali'] - total_uscite) / metrics['entrate_totali'] * 100 
        if metrics['entrate_totali'] > 0 else 0
    )
    
    metrics['investimenti_personali'] = 0
    metrics['spesa_protezione'] = 0
    
    metrics['fonti_entrate'] = (
        entrate['tipo'].nunique()
        if 'tipo' in entrate.columns and not entrate.empty
        else 0
    )
    
    return metrics

def calculate_moat_score(metrics):
    score = 0
    score += min((metrics['percentuale_ricorrenti'] / 100) * 30, 30)
    tasso = max(0, min(metrics['tasso_risparmio'], 50))
    score += (tasso / 50) * 25
    score += min(metrics['fonti_entrate'] / 5 * 15, 15)
    return round(score, 1)

def calculate_investment_metrics(df_trans, assets_df):
    metrics = {
        'total_assets': 0,
        'num_assets': 0,
        'asset_types': 0,
        'asset_growth': 0,
        'asset_count': 0
    }
    
    if assets_df is not None and not assets_df.empty and 'valore' in assets_df.columns:
        metrics['total_assets'] = assets_df['valore'].sum()
        metrics['num_assets'] = len(assets_df)
        metrics['asset_count'] = len(assets_df)
        metrics['asset_types'] = assets_df['tipologia'].nunique() if 'tipologia' in assets_df.columns else 0
    
    return metrics

def calculate_investment_score(metrics):
    score = 0
    if metrics.get('total_assets', 0) > 0:
        score += 30
    if metrics.get('num_assets', 0) >= 2:
        score += 20
    if metrics.get('asset_types', 0) >= 2:
        score += 20
    return min(score, 100)

def get_allocation_quality(moat_metrics, invest_metrics):
    """Calcola un punteggio di qualità dell'allocazione 0-100"""
    score = 0
    
    # Ricorrenza entrate (30 punti)
    score += min(moat_metrics.get('percentuale_ricorrenti', 0) * 0.3, 30)
    
    # Diversificazione asset (30 punti)
    asset_types = invest_metrics.get('asset_types', 0)
    score += min(asset_types * 10, 30)
    
    # Tasso risparmio (40 punti)
    tasso = max(0, moat_metrics.get('tasso_risparmio', 0))
    score += min(tasso * 0.8, 40)
    
    return round(score, 1)

# STEP 3: Strategic Insight Generator (rule-based, semplice ma potente)
def get_strategic_insight(moat_metrics, invest_metrics, moat_score):
    """
    Genera UN insight strategico chiave basato sulla situazione finanziaria.
    Questo è il tipo di insight che giustifica PRO.
    """
    insights = []
    
    # Regola 1: Income concentration
    if moat_score < 70 and moat_metrics.get('percentuale_ricorrenti', 0) < 50:
        impact = round((70 - moat_score) * 0.4)
        insights.append({
            'title': 'Income Concentration Risk',
            'message': f'Your defensibility is limited by income concentration. Increasing recurring income by +15% would raise your Moat Score by ~{impact} points.',
            'priority': 'high',
            'category': 'stability'
        })
    
    # Regola 2: Low savings rate
    if moat_metrics.get('tasso_risparmio', 0) < 15:
        insights.append({
            'title': 'Savings Capacity Gap',
            'message': f'Current savings rate of {moat_metrics["tasso_risparmio"]:.1f}% limits defensive capacity. Target: 20%+ for sustainable wealth building.',
            'priority': 'high',
            'category': 'allocation'
        })
    
    # Regola 3: Single income source
    if moat_metrics.get('fonti_entrate', 0) <= 1:
        insights.append({
            'title': 'Single Point of Failure',
            'message': 'Reliance on one income source creates systemic vulnerability. Adding 1-2 parallel revenue streams would significantly strengthen your position.',
            'priority': 'critical',
            'category': 'diversification'
        })
    
    # Regola 4: No investment diversification
    if invest_metrics.get('asset_types', 0) == 0:
        insights.append({
            'title': 'Zero Investment Allocation',
            'message': 'No tracked investment assets. Even modest allocation (5-10% of income) compounds defensibility over time.',
            'priority': 'medium',
            'category': 'growth'
        })
    
    # Regola 5: Strong position
    if moat_score >= 75 and moat_metrics.get('percentuale_ricorrenti', 0) >= 60:
        insights.append({
            'title': 'Strong Defensive Position',
            'message': f'Your {moat_score:.0f} Moat Score indicates solid financial defensibility. Focus: optimize allocation quality and explore growth opportunities.',
            'priority': 'low',
            'category': 'optimization'
        })
    
    # Ritorna l'insight con priorità più alta
    if not insights:
        return {
            'title': 'Build Your Moat',
            'message': 'Track 90 days of data to unlock personalized strategic insights.',
            'priority': 'info',
            'category': 'onboarding'
        }
    
    # Ordina per priorità
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
    insights.sort(key=lambda x: priority_order.get(x['priority'], 5))
    
    return insights[0]

# ==================== INIZIALIZZA ====================
init_all_tables()

# ==================== UI PRINCIPALE ====================

# Sidebar
with st.sidebar:
    st.image("assets/logo_moat.png", use_container_width=True)
    
    st.markdown("---")
    
    # NUOVO CLAIM - STEP 1: Riposizionamento mentale
    st.markdown("""
    <div style="padding: 20px; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); 
                border-radius: 10px; margin-bottom: 20px;">
        <p style="font-size: 1.1rem; color: white; font-weight: 700; margin: 0; line-height: 1.4;">
        Moat is a decision system that measures and strengthens the defensibility of your financial life.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Why Defensibility Matters")
    st.markdown("""
    Moat doesn't measure what you spend.
    
    **It measures how hard you are to destabilize.**
    
    • Financial shock resistance  
    • Income predictability & diversity  
    • Capital allocation quality
    """)
    
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "📈 Analytics", "🎯 Goals", "ℹ️ About"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # STEP 2: CTA PRO come ACCESSO SELETTIVO (non abbonamento)
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); 
                padding: 25px; border-radius: 12px; text-align: center; color: white;">
        <p style="font-size: 1.3rem; font-weight: 700; margin: 0 0 8px 0;">
        Moat Strategic Access
        </p>
        <p style="font-size: 0.9rem; margin-bottom: 15px; opacity: 0.95; line-height: 1.5;">
        Complete defensibility analysis<br>
        Advanced allocation intelligence<br>
        Strategic insights & scenarios
        </p>
        <p style="font-size: 0.75rem; opacity: 0.8; margin-top: 10px; font-style: italic;">
        Access is limited. Not all requests are accepted.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # STEP 4: Waitlist seria con database
    if st.button("🔒 Request Strategic Access", use_container_width=True, type="primary"):
        st.session_state['show_access_form'] = True
    
    # Form di richiesta accesso
    if st.session_state.get('show_access_form', False):
        with st.form("access_request_form"):
            st.markdown("#### Strategic Access Request")
            email = st.text_input("Email", placeholder="your@email.com")
            profile = st.selectbox("Profile", [
                "Freelancer / Consultant",
                "Entrepreneur",
                "Senior Professional",
                "Investor",
                "Other"
            ])
            note = st.text_area("Why Moat? (optional)", placeholder="What are you looking to strengthen?", max_chars=300)
            
            submitted = st.form_submit_button("Submit Request")
            
            if submitted:
                if email and '@' in email:
                    # Salva nel database
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    try:
                        cursor.execute("""
                            INSERT INTO AccessRequests (email, profile, note)
                            VALUES (?, ?, ?)
                        """, (email, profile, note))
                        
                        conn.commit()
                        
                        st.success("✓ Request submitted successfully")
                        st.info("**Requests are reviewed manually.**\n\nStrategic access is granted selectively based on profile fit and capacity.")
                        st.session_state['show_access_form'] = False
                        
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Please provide a valid email address")

# Carica dati
df_trans, df_assets = load_all_data()

if df_trans is None or len(df_trans) == 0:
    df_trans = pd.DataFrame(columns=['data'])
else:
    if 'data' not in df_trans.columns:
        df_trans['data'] = pd.NaT

df_trans['data'] = pd.to_datetime(df_trans['data'], errors='coerce')

# Assicura colonne necessarie
columns_defaults = {
    'is_ricorrente': 'No',
    'direzione': 'Uscita',
    'importo': 0,
    'tipo': 'Generico',
    'categoria': 'Altro',
    'classe_finanziaria': 'Uscite variabili'
}

for col, default in columns_defaults.items():
    if col not in df_trans.columns:
        df_trans[col] = default

# Filtro periodo
col1, col2 = st.columns(2)
with col1:
    date_from = st.date_input("From", value=datetime.now() - timedelta(days=90))
with col2:
    date_to = st.date_input("To", value=datetime.now())

df_filtered = df_trans[
    (df_trans['data'] >= pd.Timestamp(date_from)) & 
    (df_trans['data'] <= pd.Timestamp(date_to))
]

if len(df_filtered) == 0:
    st.warning("No transactions in this period. Using demo data for visualization.")
    df_filtered = df_trans.tail(50) if len(df_trans) > 0 else df_trans

# Calcola metriche
moat_metrics = calculate_moat_metrics(df_filtered)
moat_score = calculate_moat_score(moat_metrics)
invest_metrics = calculate_investment_metrics(df_filtered, df_assets)
invest_score = calculate_investment_score(invest_metrics)
allocation_quality = get_allocation_quality(moat_metrics, invest_metrics)

# STEP 3: Genera Strategic Insight
strategic_insight = get_strategic_insight(moat_metrics, invest_metrics, moat_score)

# ==================== DASHBOARD PRINCIPALE ====================
if page == "📊 Dashboard":
    
    # KPI Principali
    st.markdown("## Your Financial Position")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<p class="kpi-label">Defensibility Score</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="big-kpi">{moat_score:.0f}</p>', unsafe_allow_html=True)
        delta_def = moat_score - 70
        st.markdown(f'<p style="text-align: center; color: {"green" if delta_def >= 0 else "red"};">'
                   f'{"+" if delta_def >= 0 else ""}{delta_def:.0f} vs target</p>', 
                   unsafe_allow_html=True)
    
    with col2:
        st.markdown('<p class="kpi-label">Stability Score</p>', unsafe_allow_html=True)
        stability = moat_metrics['percentuale_ricorrenti']
        st.markdown(f'<p class="big-kpi">{stability:.0f}%</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="text-align: center; color: #6b7280;">recurring income</p>', 
                   unsafe_allow_html=True)
    
    with col3:
        st.markdown('<p class="kpi-label">Allocation Quality</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="big-kpi">{allocation_quality:.0f}</p>', unsafe_allow_html=True)
        delta_alloc = allocation_quality - 70
        st.markdown(f'<p style="text-align: center; color: {"green" if delta_alloc >= 0 else "red"};">'
                   f'{"+" if delta_alloc >= 0 else ""}{delta_alloc:.0f} vs benchmark</p>', 
                   unsafe_allow_html=True)
    
    st.markdown("---")
    
    # STEP 3: Strategic Insight Card (Feature Killer)
    insight_color_map = {
        'critical': '#dc2626',
        'high': '#ea580c',
        'medium': '#f59e0b',
        'low': '#10b981',
        'info': '#3b82f6'
    }
    
    insight_bg = insight_color_map.get(strategic_insight['priority'], '#6b7280')
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {insight_bg} 0%, {insight_bg}dd 100%); 
                padding: 25px; border-radius: 12px; color: white; margin: 20px 0;">
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <span style="font-size: 1.5rem; margin-right: 10px;">💡</span>
            <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;">
                Strategic Insight
            </span>
        </div>
        <h3 style="margin: 10px 0; font-size: 1.3rem; font-weight: 700;">
            {strategic_insight['title']}
        </h3>
        <p style="margin: 15px 0 0 0; font-size: 1rem; line-height: 1.6; opacity: 0.95;">
            {strategic_insight['message']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gauge principale
    health_score = (moat_score + allocation_quality) / 2
    
    fig_main = go.Figure(go.Indicator(
        mode="gauge+number",
        value=health_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall Financial Health", 'font': {'size': 24, 'color': '#1e3a8a'}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#1e3a8a"},
            'steps': [
                {'range': [0, 40], 'color': "#fee2e2"},
                {'range': [40, 70], 'color': "#fef3c7"},
                {'range': [70, 100], 'color': "#d1fae5"}
            ],
            'threshold': {
                'line': {'color': "#059669", 'width': 4},
                'thickness': 0.75,
                'value': 85
            }
        }
    ))
    
    fig_main.update_layout(height=350, margin=dict(l=40, r=40, t=80, b=40))
    st.plotly_chart(fig_main, use_container_width=True)
    
    # Quick insights
    col1, col2 = st.columns(2)
    
    with col1:
        if health_score >= 80:
            st.success("✓ Strong defensive position. Your financial moat is solid.")
        elif health_score >= 60:
            st.info("→ Good foundation. Focus on strengthening weak points.")
        else:
            st.warning("⚠ Defensive gaps detected. Priority action needed.")
    
    with col2:
        net_worth = float(invest_metrics.get("total_assets", 0) or 0)
        st.metric("Net Worth (€)", round(net_worth))
        st.metric("Savings Rate", f"{moat_metrics['tasso_risparmio']:.1f}%")
    
    # Sezione secondaria
    with st.expander("📊 Detailed Analytics", expanded=False):
        
        st.markdown("### Income & Expense Breakdown")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Income", f"€{moat_metrics['entrate_totali']:,.0f}")
            st.metric("Recurring Income", f"{moat_metrics['percentuale_ricorrenti']:.1f}%")
            st.metric("Income Sources", moat_metrics['fonti_entrate'])
        
        with col2:
            st.metric("Fixed Expenses", f"€{moat_metrics['uscite_fisse']:,.0f}")
            st.metric("Variable Expenses", f"€{moat_metrics['uscite_variabili']:,.0f}")
            total_expenses = moat_metrics['uscite_fisse'] + moat_metrics['uscite_variabili']
            st.metric("Total Expenses", f"€{total_expenses:,.0f}")
        
        # Trend chart
        if len(df_filtered) > 0 and 'data' in df_filtered.columns:
            df_filtered['mese'] = df_filtered['data'].dt.to_period('M').astype(str)
            
            entrate_mensili = df_filtered[df_filtered['direzione'] == 'Entrata'].groupby('mese')['importo'].sum()
            uscite_mensili = df_filtered[df_filtered['direzione'] == 'Uscita'].groupby('mese')['importo'].sum()
            
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=entrate_mensili.index,
                y=entrate_mensili.values,
                name='Income',
                line=dict(color='#10b981', width=2),
                fill='tozeroy'
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=uscite_mensili.index,
                y=uscite_mensili.values,
                name='Expenses',
                line=dict(color='#ef4444', width=2)
            ))
            
            fig_trend.update_layout(
                title="Monthly Trends",
                height=350,
                hovermode='x unified',
                plot_bgcolor='white'
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
    
    # PRO CTA - STEP 2: Riposizionamento come Sistema Élite
    st.markdown("---")
    st.markdown("""
    <div class="pro-banner">
        <h2 style="margin: 0 0 10px 0; font-size: 1.8rem;">Moat Strategic Access</h2>
        <p style="font-size: 1rem; margin-bottom: 5px; opacity: 0.9;">
        Not a subscription. A relationship.
        </p>
        <p style="font-size: 1.15rem; margin: 20px 0; line-height: 1.6; font-weight: 500;">
        Complete defensibility analysis • Long-term scenario modeling<br>
        Allocation intelligence • Strategic advisory insights
        </p>
        <p style="font-size: 0.85rem; opacity: 0.8; font-style: italic; margin-bottom: 25px;">
        Access is limited and granted selectively based on profile fit.
        </p>
        <div>
            <a href="#access" class="pro-cta">🔒 Request Access</a>
            <p style="font-size: 0.75rem; margin-top: 15px; opacity: 0.7;">
            Requests are reviewed manually. Not all requests are accepted.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Pricing table - STEP 2: Riposizionamento Pricing
    with st.expander("💎 Access Tiers"):
        st.markdown("""
        ### Moat Access Structure
        
        **🌐 Moat Core** (Public / Demo)
        - Basic defensibility dashboard
        - 90-day data window
        - Moat Score calculation
        - Limited insights
        
        **Purpose:** Understand the framework
        
        ---
        
        **👑 Moat Strategic Access** (Selective)
        - Complete defensibility analysis
        - Unlimited historical data
        - Advanced scenario modeling
        - Strategic insights & allocation intelligence
        - Long-term trend projections
        - Data export capabilities
        
        **Investment:** €290/year or €49/month (by invitation only)
        
        **Important:** Access is granted selectively. Not all requests are accepted.  
        We prioritize individuals with:
        - Multiple income streams or complex financial situations
        - Significant capital allocation decisions
        - High autonomy in financial planning
        - Long-term strategic orientation
        
        ---
        
        📧 **How to Request Access**
        
        Click "Request Strategic Access" in the sidebar.  
        Requests are reviewed manually within 48-72 hours.
        """)
        
        st.info("**Philosophy:** Moat Strategic Access is not about features.  \nIt's about giving the right tools to people who will use them to build something defensible.")

elif page == "📈 Analytics":
    st.markdown("## Financial Analytics")
    
    st.markdown("### Defensibility Components")
    
    categories = [
        'Recurring\nIncome',
        'Savings\nRate',
        'Income\nDiversity',
        'Asset\nAllocation'
    ]
    
    values = [
        min(moat_metrics.get('percentuale_ricorrenti', 0), 100) / 100 * 30,
        max(0, min(moat_metrics.get('tasso_risparmio', 0), 50)) / 50 * 25,
        min(moat_metrics.get('fonti_entrate', 0) / 5 * 15, 15),
        min(invest_metrics.get('asset_types', 0) / 3 * 30, 30)
    ]
    
    max_values = [30, 25, 15, 30]
    
    fig_radar = go.Figure()
    
    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Current',
        line_color='#1e3a8a'
    ))
    
    fig_radar.add_trace(go.Scatterpolar(
        r=max_values,
        theta=categories,
        fill='toself',
        name='Target',
        line_color='#93c5fd',
        opacity=0.3
    ))
    
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 30])),
        showlegend=True,
        height=450
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # Breakdown dettagliato
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Recurring Income", f"{moat_metrics['percentuale_ricorrenti']:.0f}%")
    
    with col2:
        st.metric("Savings Rate", f"{moat_metrics['tasso_risparmio']:.0f}%")
    
    with col3:
        st.metric("Income Sources", moat_metrics['fonti_entrate'])
    
    with col4:
        st.metric("Asset Types", invest_metrics['asset_types'])

elif page == "🎯 Goals":
    st.markdown("## Financial Goals")
    
    st.info("Set and track your financial objectives. PRO members get advanced goal tracking and notifications.")
    
    goals = [
        {"name": "Reach 80% recurring income", "current": moat_metrics['percentuale_ricorrenti'], "target": 80},
        {"name": "Achieve 30% savings rate", "current": max(0, moat_metrics['tasso_risparmio']), "target": 30},
        {"name": "Diversify to 5 income sources", "current": moat_metrics['fonti_entrate'], "target": 5}
    ]
    
    for idx, goal in enumerate(goals):
        progress = min(goal['current'] / goal['target'], 1.0)
        st.markdown(f"**{goal['name']}**")
        st.progress(progress, text=f"{goal['current']:.1f} / {goal['target']}")
        st.markdown("---")

elif page == "ℹ️ About":
    st.markdown("## What is Moat?")
    
    st.markdown("""
    ### A decision system that measures and strengthens the defensibility of your financial life.
    
    ---
    
    #### The Core Principle
    
    **Moat doesn't measure what you spend.**  
    **It measures how hard you are to destabilize.**
    
    Traditional personal finance tools focus on:
    - Budgeting
    - Expense tracking
    - Savings goals
    
    Moat focuses on:
    - **Income stability** — How predictable is your cash flow?
    - **Diversification** — How many failure points exist?
    - **Allocation quality** — How strategically deployed is your capital?
    - **Shock resistance** — How long can you sustain disruption?
    
    ---
    
    #### Who is Moat For?
    
    Moat is designed for individuals with:
    
    ✓ **High financial autonomy** — You make your own decisions  
    ✓ **Multiple income streams** — Freelance, business, investments  
    ✓ **Strategic mindset** — You think in systems, not tactics  
    ✓ **Long-term orientation** — You're building, not just managing
    
    Moat is **not** for:
    - Beginners learning to budget
    - Household expense tracking
    - Simple salary-based finances
    
    ---
    
    #### The Moat Score
    
    Your **Moat Score** (0-100) measures financial defensibility across:
    
    1. **Income Stability** (30 pts) — Recurring vs. volatile income
    2. **Savings Capacity** (25 pts) — Margin between income and expenses
    3. **Diversification** (15 pts) — Number of independent income sources
    4. **Asset Allocation** (30 pts) — Quality and diversity of investments
    
    **Target:** 70+ for sustainable defensibility  
    **Elite:** 85+ indicates institutional-grade resilience
    
    ---
    
    #### Strategic Access vs. Core
    
    **Moat Core** (Free)
    - Understand the framework
    - See your current score
    - Track basic metrics
    
    **Moat Strategic Access** (Selective)
    - Complete analysis & scenario modeling
    - Advanced allocation intelligence
    - Long-term trend projections
    - Strategic insights that feel like consulting
    
    **Access is not automatic.** Requests are reviewed manually.
    
    ---
    
    #### Philosophy
    
    > "The best personal finance tool is not the one that tracks every euro.  
    > It's the one that makes you harder to break."
    
    Moat is built for people who:
    - Don't need to be told to save
    - Want to optimize, not just monitor
    - Think about financial decisions strategically
    - Build systems, not spreadsheets
    
    ---
    
    **Ready to measure your defensibility?**
    
    Start with Moat Core, then request Strategic Access when you're ready for deeper analysis.
    """)
    
    st.markdown("---")
    
    if st.button("🔒 Request Strategic Access", type="primary", use_container_width=True):
        st.session_state['show_access_form'] = True
        st.rerun()

# Footer - STEP 1: Messaging coerente
st.markdown("---")
col1, col2 = st.columns([3, 1])
with col1:
    st.caption("🏆 **Moat** — Measure and strengthen the defensibility of your financial life")
with col2:
    st.caption(f"Updated: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
