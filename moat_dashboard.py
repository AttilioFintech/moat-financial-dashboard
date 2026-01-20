import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from groq import Groq
import json
import numpy as np

# ==================== CONFIGURAZIONE PAGINA ====================
st.set_page_config(
    page_title="Moat Financial Dashboard",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS CUSTOM ====================
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
    
    .vulnerability-card {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        padding: 25px;
        border-radius: 12px;
        color: white;
        margin: 15px 0;
    }
    
    .vulnerability-card.medium {
        background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
    }
    
    .vulnerability-card.low {
        background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
    }
    
    .archetype-card {
        border: 2px solid var(--moat-blue);
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        background: white;
    }
    
    .archetype-card:hover {
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2);
        transform: translateY(-2px);
        transition: all 0.3s ease;
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
    
    .trajectory-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 5px solid #f59e0b;
        padding: 25px;
        border-radius: 10px;
        margin: 20px 0;
    }
    
    .onboarding-box {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border: 2px solid var(--moat-blue);
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        margin: 25px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATABASE ====================
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
    except Exception:
        return None

# ==================== INIZIALIZZAZIONE TABELLE ====================
def init_all_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabella Access Requests
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS AccessRequests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            profile TEXT,
            note TEXT,
            request_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            review_date DATETIME,
            reviewed_by TEXT,
            decision_note TEXT
        )
    """)
    
    # Tabella Email Log
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS EmailLog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient TEXT,
            subject TEXT,
            body TEXT,
            sent_date DATETIME,
            status TEXT
        )
    """)
    
    # Tabella Notifications
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
    
    # Tabella Achievements
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
    
    conn.commit()

# ==================== STEP 1: CALCOLI REALI VULNERABILITY ====================

def calculate_emergency_months(moat_metrics):
    """Calcola quanti mesi di copertura ha l'emergency fund"""
    monthly_expenses = (moat_metrics['uscite_fisse'] + moat_metrics['uscite_variabili'])
    monthly_income = moat_metrics['entrate_totali']
    monthly_savings = monthly_income - monthly_expenses
    
    # Stima conservativa: assumiamo liquidità = 3x risparmio mensile
    estimated_liquidity = max(monthly_savings * 3, 0)
    
    if monthly_expenses > 0:
        return round(estimated_liquidity / monthly_expenses, 1)
    return 0

def calculate_debt_ratio(moat_metrics):
    """Calcola il rapporto debito/reddito (stimato)"""
    # Stima: uscite fisse includono rate di debito
    # Assumiamo che ~40% delle uscite fisse siano debiti
    estimated_debt_payments = moat_metrics['uscite_fisse'] * 0.4
    
    if moat_metrics['entrate_totali'] > 0:
        return round((estimated_debt_payments / moat_metrics['entrate_totali']) * 100, 1)
    return 0

def calculate_expense_growth(moat_metrics):
    """Calcola la crescita delle spese (placeholder - richiede dati storici)"""
    # In una versione completa, confronteresti periodo corrente vs. periodo precedente
    # Per ora, placeholder con logica semplificata
    fixed_ratio = moat_metrics['uscite_fisse'] / (moat_metrics['uscite_fisse'] + moat_metrics['uscite_variabili']) if (moat_metrics['uscite_fisse'] + moat_metrics['uscite_variabili']) > 0 else 0
    
    # Se le uscite fisse sono >60% del totale, segnala crescita
    if fixed_ratio > 0.6:
        return round((fixed_ratio - 0.6) * 100, 1)
    return 0

def calculate_income_concentration(moat_metrics):
    """Calcola concentrazione del reddito"""
    num_sources = moat_metrics.get('fonti_entrate', 1)
    # Score inverso: più fonti = minore concentrazione
    if num_sources >= 3:
        return 20  # Bassa concentrazione
    elif num_sources == 2:
        return 50  # Media concentrazione
    else:
        return 85  # Alta concentrazione

# ==================== STEP 1: WHAT-IF ENGINE CON 3 SLIDER ====================

def whatif_engine(moat_metrics, income_change=0, expense_change=0, recurring_change=0):
    """
    What-If Scenario Engine
    Returns: new metrics and score based on changes
    """
    new_metrics = moat_metrics.copy()
    
    # Applica variazioni
    new_metrics['entrate_totali'] *= (1 + income_change/100)
    new_metrics['entrate_ricorrenti'] *= (1 + recurring_change/100)
    
    total_expenses = new_metrics['uscite_fisse'] + new_metrics['uscite_variabili']
    new_total_expenses = total_expenses * (1 + expense_change/100)
    
    # Ridistribuisci proporzionalmente
    if total_expenses > 0:
        ratio = new_metrics['uscite_fisse'] / total_expenses
        new_metrics['uscite_fisse'] = new_total_expenses * ratio
        new_metrics['uscite_variabili'] = new_total_expenses * (1 - ratio)
    
    # Ricalcola percentuali
    if new_metrics['entrate_totali'] > 0:
        new_metrics['percentuale_ricorrenti'] = (new_metrics['entrate_ricorrenti'] / new_metrics['entrate_totali']) * 100
        new_metrics['tasso_risparmio'] = ((new_metrics['entrate_totali'] - new_total_expenses) / new_metrics['entrate_totali']) * 100
    
    # Ricalcola score
    new_score = calculate_moat_score(new_metrics)
    
    return new_metrics, new_score

# ==================== STEP 2: TRAJECTORY PROJECTION ====================

def calculate_trajectory_projection(moat_metrics, months=12):
    """
    Proietta la traiettoria finanziaria per i prossimi N mesi
    Returns: DataFrame con proiezione mese per mese
    """
    monthly_income = moat_metrics['entrate_totali']
    monthly_expenses = moat_metrics['uscite_fisse'] + moat_metrics['uscite_variabili']
    monthly_savings = monthly_income - monthly_expenses
    
    # Stima crescita spese (2% annuo = ~0.17% mensile)
    expense_growth_rate = 0.0017
    
    # Assumiamo income stabile (scenario conservativo)
    income_growth_rate = 0.0
    
    projection = []
    cumulative_savings = max(monthly_savings * 3, 0)  # Starting emergency fund
    
    for month in range(months):
        current_income = monthly_income * (1 + income_growth_rate * month)
        current_expenses = monthly_expenses * (1 + expense_growth_rate * month)
        current_savings = current_income - current_expenses
        
        cumulative_savings += current_savings
        
        # Calcola mesi di copertura
        months_coverage = cumulative_savings / current_expenses if current_expenses > 0 else 0
        
        # Calcola savings rate
        savings_rate = (current_savings / current_income * 100) if current_income > 0 else 0
        
        projection.append({
            'month': month + 1,
            'income': current_income,
            'expenses': current_expenses,
            'savings': current_savings,
            'cumulative_savings': cumulative_savings,
            'months_coverage': months_coverage,
            'savings_rate': savings_rate
        })
    
    return pd.DataFrame(projection)

# ==================== STRATEGIC INSIGHTS ====================

def get_structural_vulnerabilities(moat_metrics, invest_metrics, moat_score):
    """
    STEP 1: Vulnerabilità strutturali (non metriche)
    Framing élite: rischi sistemici, non errori personali
    """
    vulnerabilities = []
    
    # 1. Emergency Fund Analysis
    months_coverage = calculate_emergency_months(moat_metrics)
    if months_coverage < 6:
        vulnerabilities.append({
            'title': 'Structural Risk Detected',
            'message': f'Your financial system can absorb only ~{months_coverage} months of income disruption. Target: 6+ months for institutional-grade resilience.',
            'impact_points': round((6 - months_coverage) * 3),
            'priority': 'critical',
            'category': 'stability'
        })
    
    # 2. Debt Ratio Analysis
    debt_ratio = calculate_debt_ratio(moat_metrics)
    if debt_ratio > 30:
        vulnerabilities.append({
            'title': 'Leverage Exposure',
            'message': f'Debt obligations ({debt_ratio:.0f}% of income) reduce your strategic flexibility during income shocks. Optimal range: <30%.',
            'impact_points': round((debt_ratio - 30) * 0.5),
            'priority': 'high',
            'category': 'flexibility'
        })
    
    # 3. Expense Growth Analysis
    expense_growth = calculate_expense_growth(moat_metrics)
    if expense_growth > 5:
        vulnerabilities.append({
            'title': 'Cost Creep Risk',
            'message': f'Fixed expenses are growing faster than income, weakening defensibility. This trend compounds vulnerability over time.',
            'impact_points': round(expense_growth * 2),
            'priority': 'high',
            'category': 'sustainability'
        })
    
    # 4. Income Concentration
    if moat_metrics.get('fonti_entrate', 0) <= 1:
        vulnerabilities.append({
            'title': 'Single Point of Failure',
            'message': 'Reliance on one income source creates systemic vulnerability. Adding 1-2 parallel revenue streams would significantly strengthen your position.',
            'impact_points': 15,
            'priority': 'critical',
            'category': 'diversification'
        })
    
    # Ordina per priorità
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    vulnerabilities.sort(key=lambda x: priority_order.get(x['priority'], 5))
    
    return vulnerabilities

def get_strategic_archetypes():
    """
    STEP 2: Strategic Archetypes (non demo utenti)
    Modelli di rischio, non profili demografici
    """
    return {
        'independent_operator': {
            'label': 'Independent Operator',
            'description': 'Freelancer, consultant, or solo professional',
            'key_risks': [
                'Income concentration (single client dependency)',
                'Revenue volatility during market downturns',
                'Limited operational leverage'
            ],
            'moat_priorities': [
                ('Recurring Income', 40, 'Critical for stability'),
                ('Emergency Fund', 35, '6-12 months recommended'),
                ('Income Diversification', 25, 'Minimum 3 sources')
            ],
            'benchmark_score': 65,
            'typical_vulnerabilities': [
                'Low recurring income ratio (<40%)',
                'Insufficient emergency fund (<3 months)',
                'High time-for-money dependency'
            ]
        },
        
        'capital_allocator': {
            'label': 'Capital Allocator',
            'description': 'Entrepreneur or business owner',
            'key_risks': [
                'Business concentration risk',
                'Liquidity constraints during growth phases',
                'Personal/business finance entanglement'
            ],
            'moat_priorities': [
                ('Asset Diversification', 40, 'Separate personal capital'),
                ('Savings Rate', 35, 'Reinvestment capacity'),
                ('Income Stability', 25, 'Predictable cash flow')
            ],
            'benchmark_score': 70,
            'typical_vulnerabilities': [
                'Over-allocation to single business',
                'Undiversified asset base',
                'Irregular personal income extraction'
            ]
        },
        
        'hybrid_strategist': {
            'label': 'Hybrid Income Strategist',
            'description': 'W-2 employee + side income streams',
            'key_risks': [
                'Time allocation inefficiency',
                'Parallel income stream fragility',
                'Opportunity cost miscalculation'
            ],
            'moat_priorities': [
                ('Income Quality', 40, 'Leverage vs. time trade-off'),
                ('Allocation Quality', 35, 'Strategic capital deployment'),
                ('Diversification', 25, 'Sustainable parallel streams')
            ],
            'benchmark_score': 72,
            'typical_vulnerabilities': [
                'Side income not truly defensible',
                'Suboptimal time-to-revenue ratio',
                'Unclear strategic direction'
            ]
        }
    }

# ==================== EMAIL AUTOMATION ====================

def send_access_decision_email(email, status, profile):
    """
    STEP 3: Email automation per decisioni accesso
    Tono: status-elevating, non supplicante
    """
    
    if status == 'approved':
        subject = "Strategic Access — Granted"
        body = f"""Your request has been reviewed.
You've been granted Strategic Access to Moat.

Profile: {profile}
Access Level: Full Strategic Analysis

Next Steps:
→ Log in at app.moat.financial
→ Your account has been upgraded
→ All features are now available

This access includes:
• Complete defensibility analysis
• Advanced scenario modeling
• Long-term trajectory projections
• Strategic allocation intelligence

—
Moat Strategic Team
"""
    
    elif status == 'waitlist':
        subject = "Strategic Access — Priority Queue"
        body = f"""Your request has been reviewed.

Access is currently limited.
Your profile has been added to the priority queue.

Profile: {profile}
Queue Position: You'll be notified when capacity opens

Why the wait:
Strategic Access is granted selectively to maintain analysis quality and ensure meaningful engagement with each member.

Expected Timeline: 2-4 weeks

—
Moat Strategic Team
"""
    
    else:  # rejected
        subject = "Strategic Access — Not Available"
        body = f"""Your request has been reviewed.

Based on current capacity and profile fit, we're unable to grant access at this time.

This doesn't reflect on your profile — it's a capacity constraint.

Alternative:
Moat Core remains available for basic defensibility tracking.

—
Moat Strategic Team
"""
    
    # Log email (in produzione, qui invieresti via SendGrid/AWS SES)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO EmailLog (recipient, subject, body, sent_date, status)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP, 'sent')
    """, (email, subject, body))
    conn.commit()
    
    return True

# ==================== CARICAMENTO DATI ====================

@st.cache_data(ttl=300)
def load_all_data():
    conn = get_db_connection()
    
    try:
        trans_query = "SELECT * FROM Transazioni ORDER BY data DESC"
        df_trans = pd.read_sql_query(trans_query, conn)
    except Exception:
        df_trans = pd.DataFrame()
    
    if not df_trans.empty and 'data' in df_trans.columns:
        df_trans['data'] = pd.to_datetime(df_trans['data'], errors='coerce')
    
    if 'moat_classification' not in df_trans.columns:
        df_trans['moat_classification'] = None
    
    try:
        assets_query = "SELECT * FROM Assets WHERE attivo = 1"
        df_assets = pd.read_sql_query(assets_query, conn)
    except Exception:
        df_assets = pd.DataFrame()
    
    return df_trans, df_assets

def calculate_moat_metrics(df):
    """Calcola metriche finanziarie base"""
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
    """Calcola Moat Score 0-100"""
    score = 0
    score += min((metrics['percentuale_ricorrenti'] / 100) * 30, 30)
    tasso = max(0, min(metrics['tasso_risparmio'], 50))
    score += (tasso / 50) * 25
    score += min(metrics['fonti_entrate'] / 5 * 15, 15)
    return round(score, 1)

def calculate_investment_metrics(df_trans, assets_df):
    """Calcola metriche investimenti"""
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
    """Calcola punteggio investimenti"""
    score = 0
    if metrics.get('total_assets', 0) > 0:
        score += 30
    if metrics.get('num_assets', 0) >= 2:
        score += 20
    if metrics.get('asset_types', 0) >= 2:
        score += 20
    return min(score, 100)

def get_allocation_quality(moat_metrics, invest_metrics):
    """Calcola qualità allocazione 0-100"""
    score = 0
    score += min(moat_metrics.get('percentuale_ricorrenti', 0) * 0.3, 30)
    asset_types = invest_metrics.get('asset_types', 0)
    score += min(asset_types * 10, 30)
    tasso = max(0, moat_metrics.get('tasso_risparmio', 0))
    score += min(tasso * 0.8, 40)
    return round(score, 1)

# ==================== INIZIALIZZA ====================
init_all_tables()

# ==================== SIDEBAR ====================
with st.sidebar:
    st.image("assets/logo_moat.png", use_container_width=True)
    
    st.markdown("---")
    
    # STEP 3: Onboarding forte
    st.markdown("""
    <div class="onboarding-box">
        <p style="font-size: 1.4rem; font-weight: 700; color: var(--moat-blue); margin: 0 0 15px 0;">
        You don't need all your data to start.
        </p>
        <p style="font-size: 1.1rem; color: #374151; margin: 0;">
        You need the right signals.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Navigation")
    page = st.radio(
        "",
        ["📊 Dashboard", "🔮 What-If Scenarios", "📈 Trajectory", "🎯 Strategic Archetypes", "🔍 Vulnerabilities", "ℹ️ About"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # CTA Strategic Access
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
    
    if st.button("🔒 Request Strategic Access", use_container_width=True, type="primary"):
        st.session_state['show_access_form'] = True
    
    # Form richiesta accesso
    if st.session_state.get('show_access_form', False):
        with st.form("access_request_form"):
            st.markdown("#### Strategic Access Request")
            email = st.text_input("Email", placeholder="your@email.com")
            profile = st.selectbox("Profile", [
                "Independent Operator (Freelancer/Consultant)",
                "Capital Allocator (Entrepreneur)",
                "Hybrid Strategist (Employee + Side Income)",
                "Other"
            ])
            note = st.text_area("Why Moat?", placeholder="What are you looking to strengthen?", max_chars=300)
            
            submitted = st.form_submit_button("Submit Request")
            
            if submitted:
                if email and '@' in email:
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
                    st.warning("Please provide a valid email")

# ==================== CARICA DATI ====================
df_trans, df_assets = load_all_data()

if df_trans is None or len(df_trans) == 0:
    df_trans = pd.DataFrame(columns=['data'])

df_trans['data'] = pd.to_datetime(df_trans['data'], errors='coerce')

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
    st.warning("No transactions in this period. Using demo data.")
    df_filtered = df_trans.tail(50) if len(df_trans) > 0 else df_trans

# Calcola metriche
moat_metrics = calculate_moat_metrics(df_filtered)
moat_score = calculate_moat_score(moat_metrics)
invest_metrics = calculate_investment_metrics(df_filtered, df_assets)
invest_score = calculate_investment_score(invest_metrics)
allocation_quality = get_allocation_quality(moat_metrics, invest_metrics)

# Vulnerabilità strutturali
vulnerabilities = get_structural_vulnerabilities(moat_metrics, invest_metrics, moat_score)

# ==================== PAGINE ====================

if page == "📊 Dashboard":
    st.markdown("## Your Financial Position")
    
    # KPI Principali
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<p class="kpi-label">Defensibility Score</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="big-kpi">{moat_score:.0f}</p>', unsafe_allow_html=True)
        delta = moat_score - 70
        st.markdown(f'<p style="text-align: center; color: {"green" if delta >= 0 else "red"};">'
                   f'{"+" if delta >= 0 else ""}{delta:.0f} vs target</p>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<p class="kpi-label">Stability Score</p>', unsafe_allow_html=True)
        stability = moat_metrics['percentuale_ricorrenti']
        st.markdown(f'<p class="big-kpi">{stability:.0f}%</p>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #6b7280;">recurring income</p>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<p class="kpi-label">Allocation Quality</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="big-kpi">{allocation_quality:.0f}</p>', unsafe_allow_html=True)
        delta_alloc = allocation_quality - 70
        st.markdown(f'<p style="text-align: center; color: {"green" if delta_alloc >= 0 else "red"};">'
                   f'{"+" if delta_alloc >= 0 else ""}{delta_alloc:.0f} vs benchmark</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Top Vulnerability (STEP 1 implementation)
    if vulnerabilities:
        top_vuln = vulnerabilities[0]
        vuln_class = 'vulnerability-card'
        if top_vuln['priority'] == 'high':
            vuln_class += ' medium'
        elif top_vuln['priority'] in ['low', 'info']:
            vuln_class += ' low'
        
        st.markdown(f"""
        <div class="{vuln_class}">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 1.5rem; margin-right: 10px;">⚠️</span>
                <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;">
                    Structural Vulnerability
                </span>
            </div>
            <h3 style="margin: 10px 0; font-size: 1.3rem; font-weight: 700;">
                {top_vuln['title']}
            </h3>
            <p style="margin: 15px 0 0 0; font-size: 1rem; line-height: 1.6;">
                {top_vuln['message']}
            </p>
            <p style="margin-top: 15px; font-size: 0.85rem; opacity: 0.9;">
                Potential Impact: +{top_vuln['impact_points']} Moat Points if addressed
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gauge principale
    health_score = (moat_score + allocation_quality) / 2
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=health_score,
        title={'text': "Overall Financial Health", 'font': {'size': 24, 'color': '#1e3a8a'}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#1e3a8a"},
            'steps': [
                {'range': [0, 40], 'color': "#fee2e2"},
                {'range': [40, 70], 'color': "#fef3c7"},
                {'range': [70, 100], 'color': "#d1fae5"}
            ],
            'threshold': {'line': {'color': "#059669", 'width': 4}, 'thickness': 0.75, 'value': 85}
        }
    ))
    fig.update_layout(height=350, margin=dict(l=40, r=40, t=80, b=40))
    st.plotly_chart(fig, use_container_width=True)
    
    # Quick insights
    col1, col2 = st.columns(2)
    with col1:
        if health_score >= 80:
            st.success("✓ Strong defensive position")
        elif health_score >= 60:
            st.info("→ Good foundation. Optimize weak points")
        else:
            st.warning("⚠ Defensive gaps detected")
    
    with col2:
        net_worth = float(invest_metrics.get("total_assets", 0) or 0)
        st.metric("Net Worth (€)", f"{net_worth:,.0f}")
        st.metric("Savings Rate", f"{moat_metrics['tasso_risparmio']:.1f}%")

# ==================== STEP 1: WHAT-IF SCENARIOS PAGE ====================
elif page == "🔮 What-If Scenarios":
    st.markdown("## What-If Scenario Engine")
    st.markdown("### Model how changes affect your defensibility")
    
    st.info("**Strategic insight:** Small structural changes compound over time. Use this to test allocation decisions before committing.")
    
    st.markdown("---")
    
    # Current State
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Current Position")
        st.metric("Moat Score", f"{moat_score:.0f}")
        st.metric("Monthly Income", f"€{moat_metrics['entrate_totali']:,.0f}")
        st.metric("Savings Rate", f"{moat_metrics['tasso_risparmio']:.1f}%")
    
    with col2:
        st.markdown("### Scenario Result")
        # Placeholder - will update with sliders
        st.empty()
    
    st.markdown("---")
    st.markdown("### Adjust Variables")
    
    # 3 SLIDER (STEP 1)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        income_change = st.slider(
            "Income Change (%)",
            min_value=-50,
            max_value=100,
            value=0,
            step=5,
            help="What if your income increased or decreased?"
        )
    
    with col2:
        expense_change = st.slider(
            "Expense Change (%)",
            min_value=-50,
            max_value=100,
            value=0,
            step=5,
            help="What if your expenses changed?"
        )
    
    with col3:
        recurring_change = st.slider(
            "Recurring Income Change (%)",
            min_value=-50,
            max_value=100,
            value=0,
            step=5,
            help="What if your recurring income changed?"
        )
    
    # Calcola scenario
    new_metrics, new_score = whatif_engine(moat_metrics, income_change, expense_change, recurring_change)
    
    # Mostra risultati
    st.markdown("---")
    st.markdown("### Scenario Impact")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_score = new_score - moat_score
        st.metric("New Moat Score", f"{new_score:.0f}", f"{delta_score:+.0f}")
    
    with col2:
        new_savings_rate = new_metrics['tasso_risparmio']
        delta_savings = new_savings_rate - moat_metrics['tasso_risparmio']
        st.metric("New Savings Rate", f"{new_savings_rate:.1f}%", f"{delta_savings:+.1f}%")
    
    with col3:
        new_recurring = new_metrics['percentuale_ricorrenti']
        delta_recurring = new_recurring - moat_metrics['percentuale_ricorrenti']
        st.metric("Recurring Income", f"{new_recurring:.0f}%", f"{delta_recurring:+.0f}%")
    
    with col4:
        monthly_savings_current = moat_metrics['entrate_totali'] - (moat_metrics['uscite_fisse'] + moat_metrics['uscite_variabili'])
        monthly_savings_new = new_metrics['entrate_totali'] - (new_metrics['uscite_fisse'] + new_metrics['uscite_variabili'])
        delta_monthly = monthly_savings_new - monthly_savings_current
        st.metric("Monthly Savings", f"€{monthly_savings_new:,.0f}", f"€{delta_monthly:+,.0f}")
    
    # Interpretazione
    st.markdown("---")
    
    if delta_score > 5:
        st.success(f"✓ **Strong improvement:** This scenario would increase your defensibility by {delta_score:.0f} points.")
    elif delta_score > 0:
        st.info(f"→ **Marginal improvement:** +{delta_score:.0f} points. Consider if effort justifies gain.")
    elif delta_score < -5:
        st.error(f"⚠ **Significant risk:** This would weaken your position by {abs(delta_score):.0f} points.")
    else:
        st.warning(f"→ **Neutral impact:** Minimal change ({delta_score:+.0f} points).")

# ==================== STEP 2: TRAJECTORY PAGE ====================
elif page == "📈 Trajectory":
    st.markdown("## 12-Month Financial Trajectory")
    st.markdown("### If nothing changes, here's where you're heading")
    
    # STEP 2: Copy forte
    st.markdown("""
    <div class="trajectory-box">
        <h3 style="margin: 0 0 10px 0; color: #92400e;">
            ⚠️ If nothing changes…
        </h3>
        <p style="margin: 0; font-size: 1.05rem; color: #451a03; line-height: 1.6;">
            This projection assumes your current income and spending patterns continue unchanged. 
            Small structural shifts today create exponentially different outcomes over time.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Calcola proiezione
    projection_df = calculate_trajectory_projection(moat_metrics, months=12)
    
    # Current vs Final State
    col1, col2, col3 = st.columns(3)
    
    final_month = projection_df.iloc[-1]
    
    with col1:
        current_coverage = calculate_emergency_months(moat_metrics)
        final_coverage = final_month['months_coverage']
        delta_coverage = final_coverage - current_coverage
        st.metric(
            "Emergency Fund Coverage",
            f"{final_coverage:.1f} months",
            f"{delta_coverage:+.1f} (12 months)",
            help="Projected months of expenses covered"
        )
    
    with col2:
        current_savings = moat_metrics['tasso_risparmio']
        final_savings = final_month['savings_rate']
        delta_savings_rate = final_savings - current_savings
        st.metric(
            "Savings Rate",
            f"{final_savings:.1f}%",
            f"{delta_savings_rate:+.1f}%",
            help="Projected monthly savings rate"
        )
    
    with col3:
        cumulative = final_month['cumulative_savings']
        st.metric(
            "Cumulative Savings",
            f"€{cumulative:,.0f}",
            help="Total accumulated over 12 months"
        )
    
    st.markdown("---")
    
    # Grafico traiettoria
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=projection_df['month'],
        y=projection_df['cumulative_savings'],
        mode='lines+markers',
        name='Cumulative Savings',
        line=dict(color='#1e3a8a', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Projected Cumulative Savings (12 Months)",
        xaxis_title="Month",
        yaxis_title="Cumulative Savings (€)",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Grafico Coverage
    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(
        x=projection_df['month'],
        y=projection_df['months_coverage'],
        mode='lines+markers',
        name='Months Coverage',
        line=dict(color='#059669', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(5, 150, 105, 0.1)'
    ))
    
    # Target line at 6 months
    fig2.add_hline(
        y=6,
        line_dash="dash",
        line_color="red",
        annotation_text="Target: 6 months"
    )
    
    fig2.update_layout(
        title="Emergency Fund Coverage Trajectory",
        xaxis_title="Month",
        yaxis_title="Months of Expenses Covered",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Interpretazione
    st.markdown("---")
    st.markdown("### Strategic Interpretation")
    
    if final_coverage >= 6:
        st.success(f"✓ **On track:** You'll reach institutional-grade resilience ({final_coverage:.1f} months) within 12 months at current pace.")
    elif final_coverage >= 3:
        st.info(f"→ **Moderate progress:** You'll reach {final_coverage:.1f} months coverage. Consider accelerating to reach 6-month target.")
    else:
        st.warning(f"⚠ **Insufficient trajectory:** At current pace, you'll only reach {final_coverage:.1f} months. Structural changes needed.")
    
    st.markdown("---")
    st.info("**PRO Feature:** Strategic Access members can model custom scenarios with variable growth rates, income shocks, and expense optimization strategies.")

elif page == "🎯 Strategic Archetypes":
    st.markdown("## Strategic Archetypes")
    st.markdown("### Risk Models for Different Financial Profiles")
    
    st.info("**Not user demographics. Risk archetypes.**\n\nThese are structural models of how different income strategies create different vulnerability patterns.")
    
    archetypes = get_strategic_archetypes()
    
    for key, archetype in archetypes.items():
        st.markdown(f"""
        <div class="archetype-card">
            <h3 style="color: var(--moat-blue); margin: 0 0 10px 0;">
                {archetype['label']}
            </h3>
            <p style="color: #6b7280; margin-bottom: 15px; font-style: italic;">
                {archetype['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander(f"View {archetype['label']} Analysis"):
            st.markdown("#### Key Structural Risks")
            for risk in archetype['key_risks']:
                st.markdown(f"• {risk}")
            
            st.markdown("#### Moat Priorities")
            for priority, weight, note in archetype['moat_priorities']:
                st.markdown(f"**{priority}** ({weight}% weight) — *{note}*")
            
            st.markdown("#### Typical Vulnerabilities")
            for vuln in archetype['typical_vulnerabilities']:
                st.markdown(f"⚠️ {vuln}")
            
            st.metric("Benchmark Moat Score", archetype['benchmark_score'])
            
            st.markdown("---")
            st.info(f"**Strategic insight:** This archetype typically requires {archetype['benchmark_score']}+ Moat Score to achieve institutional-grade defensibility.")

elif page == "🔍 Vulnerabilities":
    st.markdown("## Structural Vulnerabilities Analysis")
    
    if not vulnerabilities:
        st.success("### No Critical Vulnerabilities Detected")
        st.markdown("Your financial system shows solid structural defensibility. Focus on optimization and growth opportunities.")
    else:
        st.markdown(f"### {len(vulnerabilities)} Vulnerability{'ies' if len(vulnerabilities) > 1 else 'y'} Identified")
        
        for idx, vuln in enumerate(vulnerabilities, 1):
            priority_colors = {
                'critical': '#dc2626',
                'high': '#f59e0b',
                'medium': '#10b981',
                'low': '#3b82f6'
            }
            color = priority_colors.get(vuln['priority'], '#6b7280')
            
            st.markdown(f"""
            <div style="border-left: 4px solid {color}; padding: 20px; margin: 15px 0; background: #f9fafb; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: {color};">
                        #{idx} — {vuln['title']}
                    </h4>
                    <span style="background: {color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; text-transform: uppercase;">
                        {vuln['priority']}
                    </span>
                </div>
                <p style="margin: 15px 0; color: #374151; line-height: 1.6;">
                    {vuln['message']}
                </p>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px; padding-top: 15px; border-top: 1px solid #e5e7eb;">
                    <span style="font-size: 0.85rem; color: #6b7280;">
                        Category: {vuln['category'].title()}
                    </span>
                    <span style="font-size: 0.9rem; font-weight: 600; color: {color};">
                        Potential Impact: +{vuln['impact_points']} Moat Points
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("**PRO Feature:** Strategic Access members get personalized action plans for each vulnerability with timeline and resource requirements.")

elif page == "ℹ️ About":
    st.markdown("## What is Moat?")
    st.markdown("""
    ### A decision system that measures and strengthens the defensibility of your financial life.
    
    ---
    
    #### The Core Principle
    
    **Moat doesn't measure what you spend.**  
    **It measures how hard you are to destabilize.**
    
    ---
    
    #### Strategic Access
    
    Access is granted selectively based on:
    - Profile fit (complexity, autonomy, strategic orientation)
    - Current capacity
    - Meaningful engagement potential
    
    **Not a subscription. A relationship.**
    
    ---
    
    [Full documentation in About section]
    """)

# Footer
st.markdown("---")
col1, col2 = st.columns([3, 1])
with col1:
    st.caption("🏆 **Moat** — Measure and strengthen the defensibility of your financial life")
with col2:
    st.caption(f"Updated: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
