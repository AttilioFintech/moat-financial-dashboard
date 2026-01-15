import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from groq import Groq
import json
import numpy as np
import hashlib

# Configurazione pagina
st.set_page_config(
    page_title="Moat Financial Dashboard",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Custom per migliorare l'estetica
st.markdown("""
<style>
    .big-metric {
        font-size: 3rem !important;
        font-weight: bold;
        color: #1f4788;
    }
    .achievement-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .alert-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATABASE & CONNESSIONI ====================
@st.cache_resource
def get_db_connection():
    return sqlite3.connect('gestione_conti_casa_demo.db', check_same_thread=False)

@st.cache_resource
def get_groq_client():
    try:
        api_key = st.secrets["groq"]["api_key"]
        return Groq(api_key=api_key)
    except Exception as e:
        return None

# ==================== INIZIALIZZAZIONE TABELLE ====================
def init_all_tables():
    """Inizializza tutte le tabelle necessarie per il sistema"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabella notifiche/alert
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Notifications (
            id INTEGER PRIMARY KEY,
            tipo VARCHAR(50) CHECK(tipo IN ('alert', 'opportunity', 'achievement', 'warning')),
            titolo VARCHAR(200) NOT NULL,
            messaggio TEXT NOT NULL,
            priorita VARCHAR(20) CHECK(priorita IN ('low', 'medium', 'high', 'critical')),
            data_creazione DATETIME DEFAULT CURRENT_TIMESTAMP,
            letta INTEGER DEFAULT 0,
            data_lettura DATETIME,
            azione_suggerita TEXT,
            dati_json TEXT
        )
    """)
    
    # Tabella achievements/badge
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Achievements (
            id INTEGER PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            descrizione TEXT,
            categoria VARCHAR(50) CHECK(categoria IN ('moat_defense', 'moat_investing', 'consistency', 'growth', 'special')),
            icona TEXT,
            requisiti_json TEXT,
            punti INTEGER DEFAULT 100,
            sbloccato INTEGER DEFAULT 0,
            data_sblocco DATETIME,
            livello INTEGER DEFAULT 1
        )
    """)
    
    # Tabella obiettivi personalizzati
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Goals (
            id INTEGER PRIMARY KEY,
            nome VARCHAR(200) NOT NULL,
            descrizione TEXT,
            tipo VARCHAR(50) CHECK(tipo IN ('moat_score', 'investment_score', 'wide_moat_perc', 'asset_count', 'patrimonio', 'risparmio', 'custom')),
            valore_target DECIMAL(12, 2) NOT NULL,
            valore_attuale DECIMAL(12, 2),
            data_inizio DATE NOT NULL,
            data_target DATE,
            completato INTEGER DEFAULT 0,
            data_completamento DATETIME,
            priorita VARCHAR(20) CHECK(priorita IN ('low', 'medium', 'high')),
            reward_achievement_id INTEGER,
            FOREIGN KEY (reward_achievement_id) REFERENCES Achievements(id)
        )
    """)
    
    # Tabella predizioni ML (semplificata)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Predictions (
            id INTEGER PRIMARY KEY,
            data_predizione DATETIME DEFAULT CURRENT_TIMESTAMP,
            tipo_predizione VARCHAR(50) CHECK(tipo_predizione IN ('moat_score', 'patrimonio', 'wide_moat_spending', 'monthly_savings')),
            periodo_mesi INTEGER NOT NULL,
            valore_predetto DECIMAL(12, 2) NOT NULL,
            confidenza DECIMAL(5, 2),
            dati_json TEXT
        )
    """)
    
    # Tabella storico giornaliero (per tracking continuo)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DailySnapshot (
            id INTEGER PRIMARY KEY,
            data DATE UNIQUE NOT NULL,
            moat_score DECIMAL(5, 2),
            investment_score DECIMAL(5, 2),
            patrimonio_totale DECIMAL(12, 2),
            entrate_mensili DECIMAL(10, 2),
            uscite_mensili DECIMAL(10, 2),
            tasso_risparmio DECIMAL(5, 2),
            wide_moat_perc DECIMAL(5, 2),
            dati_completi_json TEXT
        )
    """)
    
    conn.commit()
    
    # Inizializza achievements di default
    #init_default_achievements()

def init_default_achievements():
    # Disabilitato per deploy Cloud
    return

    
    achievements = [
        # Moat Defense
        ('Fortress Builder', 'Raggiungi un Moat Score di 70+', 'moat_defense', '🏰', 
         json.dumps({'moat_score': 70}), 150, 1),
        ('Impenetrable', 'Raggiungi un Moat Score di 85+', 'moat_defense', '⚡', 
         json.dumps({'moat_score': 85}), 300, 2),
        ('Steady Income', 'Raggiungi 80% di entrate ricorrenti', 'moat_defense', '💰', 
         json.dumps({'entrate_ricorrenti_perc': 80}), 200, 1),
        
        # Moat Investing
        ('Smart Investor', 'Investi 20% in Wide Moat', 'moat_investing', '💎', 
         json.dumps({'wide_moat_perc': 20}), 150, 1),
        ('Portfolio Master', 'Possiedi 10+ asset diversificati', 'moat_investing', '📊', 
         json.dumps({'asset_count': 10}), 200, 1),
        ('Wealth Builder', 'Patrimonio cresciuto del 25%', 'moat_investing', '🚀', 
         json.dumps({'asset_growth': 25}), 250, 1),
        
        # Consistency
        ('Consistent Saver', '6 mesi consecutivi con risparmio positivo', 'consistency', '📈', 
         json.dumps({'mesi_risparmio_positivo': 6}), 200, 1),
        ('Year Champion', '12 mesi di tracking completati', 'consistency', '🏆', 
         json.dumps({'mesi_tracking': 12}), 300, 1),
        
        # Growth
        ('Net Worth 50K', 'Patrimonio netto superiore a €50,000', 'growth', '💵', 
         json.dumps({'patrimonio': 50000}), 250, 1),
        ('Net Worth 100K', 'Patrimonio netto superiore a €100,000', 'growth', '💰', 
         json.dumps({'patrimonio': 100000}), 500, 2),
        
        # Special
        ('AI Pioneer', 'Utilizza le raccomandazioni AI 5 volte', 'special', '🤖', 
         json.dumps({'ai_usage': 5}), 100, 1),
        ('Perfect Month', 'Mese con Investment Score 90+', 'special', '⭐', 
         json.dumps({'investment_score': 90}), 400, 2),
    ]
    
    for ach in achievements:
        cursor.execute("""
            INSERT OR IGNORE INTO Achievements 
            (nome, descrizione, categoria, icona, requisiti_json, punti, livello)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ach)
    
    conn.commit()

# ==================== SISTEMA NOTIFICHE ====================
def check_and_create_notifications(moat_metrics, invest_metrics, moat_score, invest_score):
    """Sistema intelligente che genera notifiche basate sui dati"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    notifications = []
    
    # Alert: Moat Score basso
    if moat_score < 50:
        notifications.append({
            'tipo': 'alert',
            'titolo': '⚠️ Moat Score Critico',
            'messaggio': f'Il tuo Moat Score è {moat_score:.1f}, sotto la soglia di sicurezza. Azioni immediate necessarie!',
            'priorita': 'critical',
            'azione_suggerita': 'Aumenta le entrate ricorrenti e riduci le uscite variabili'
        })
    
    # Alert: Tasso risparmio negativo
    if moat_metrics.get('tasso_risparmio', 0) < 0:
        notifications.append({
            'tipo': 'alert',
            'titolo': '🚨 Risparmio Negativo',
            'messaggio': 'Stai spendendo più di quanto guadagni questo periodo!',
            'priorita': 'critical',
            'azione_suggerita': 'Rivedi immediatamente le spese e identifica tagli necessari'
        })
    
    # Warning: Wide Moat basso
    if invest_metrics.get('wide_moat_percentage', 0) < 10:
        notifications.append({
            'tipo': 'warning',
            'titolo': '⚠️ Investimenti Wide Moat Insufficienti',
            'messaggio': f'Solo {invest_metrics.get("wide_moat_percentage", 0):.1f}% delle spese va in investimenti duraturi',
            'priorita': 'high',
            'azione_suggerita': 'Sposta risorse dal consumo agli investimenti in formazione, salute o asset'
        })
    
    # Opportunity: Liquidità accumulata
    entrate_recenti = moat_metrics.get('entrate_totali', 0)
    uscite_recenti = moat_metrics.get('uscite_fisse', 0) + moat_metrics.get('uscite_variabili', 0)
    liquidita_potenziale = entrate_recenti - uscite_recenti
    
    if liquidita_potenziale > 1000:
        notifications.append({
            'tipo': 'opportunity',
            'titolo': '💰 Opportunità di Investimento',
            'messaggio': f'Hai accumulato circa €{liquidita_potenziale:.2f} di surplus. Considera di investirlo!',
            'priorita': 'medium',
            'azione_suggerita': 'Valuta investimenti in ETF, formazione o fondi di emergenza'
        })
    
    # Opportunity: Troppe spese di consumo
    consumo = invest_metrics.get('consumo_spending', 0)
    total_spending = invest_metrics.get('total_spending', 1)
    consumo_perc = (consumo / total_spending * 100) if total_spending > 0 else 0
    
    if consumo_perc > 40:
        notifications.append({
            'tipo': 'opportunity',
            'titolo': '🔄 Opportunità di Ottimizzazione',
            'messaggio': f'{consumo_perc:.1f}% delle spese è consumo. Potresti convertire parte in investimenti',
            'priorita': 'medium',
            'azione_suggerita': f'Riducendo consumo del 20% libereresti €{consumo * 0.20:.2f}'
        })
    
    # Achievement unlock notifications
    check_achievements(moat_metrics, invest_metrics, moat_score, invest_score, notifications)
    
    # Salva notifiche non lette
    for notif in notifications:
        # Verifica se già esiste una simile recente (ultime 24h)
        cursor.execute("""
            SELECT COUNT(*) FROM Notifications 
            WHERE titolo = ? AND data_creazione > datetime('now', '-1 day')
        """, (notif['titolo'],))
        
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO Notifications 
                (tipo, titolo, messaggio, priorita, azione_suggerita)
                VALUES (?, ?, ?, ?, ?)
            """, (notif['tipo'], notif['titolo'], notif['messaggio'], 
                  notif['priorita'], notif.get('azione_suggerita')))
    
    conn.commit()
    return notifications

def get_unread_notifications():
    """Recupera notifiche non lette"""
    conn = get_db_connection()
    query = """
        SELECT * FROM Notifications 
        WHERE letta = 0 
        ORDER BY priorita DESC, data_creazione DESC
        LIMIT 10
    """
    return pd.read_sql_query(query, conn)

def mark_notification_read(notif_id):
    """Marca una notifica come letta"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Notifications 
        SET letta = 1, data_lettura = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (notif_id,))
    conn.commit()

# ==================== SISTEMA ACHIEVEMENTS ====================
def check_achievements(moat_metrics, invest_metrics, moat_score, invest_score, notifications):
    """Controlla e sblocca achievements"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Recupera achievements non sbloccati
    cursor.execute("SELECT * FROM Achievements WHERE sbloccato = 0")
    achievements = cursor.fetchall()
    
    for ach in achievements:
        ach_id, nome, desc, cat, icon, req_json, punti, sbloccato, data_sblocco, livello = ach
        requisiti = json.loads(req_json)
        
        unlocked = False
        
        # Controlla requisiti
        if 'moat_score' in requisiti and moat_score >= requisiti['moat_score']:
            unlocked = True
        elif 'investment_score' in requisiti and invest_score >= requisiti['investment_score']:
            unlocked = True
        elif 'entrate_ricorrenti_perc' in requisiti:
            if moat_metrics.get('percentuale_ricorrenti', 0) >= requisiti['entrate_ricorrenti_perc']:
                unlocked = True
        elif 'wide_moat_perc' in requisiti:
            if invest_metrics.get('wide_moat_percentage', 0) >= requisiti['wide_moat_perc']:
                unlocked = True
        elif 'asset_count' in requisiti:
            if invest_metrics.get('asset_count', 0) >= requisiti['asset_count']:
                unlocked = True
        elif 'asset_growth' in requisiti:
            if invest_metrics.get('asset_growth', 0) >= requisiti['asset_growth']:
                unlocked = True
        elif 'patrimonio' in requisiti:
            if invest_metrics.get('total_assets', 0) >= requisiti['patrimonio']:
                unlocked = True
        
        if unlocked:
            # Sblocca achievement
            cursor.execute("""
                UPDATE Achievements 
                SET sbloccato = 1, data_sblocco = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (ach_id,))
            
            # Crea notifica
            notifications.append({
                'tipo': 'achievement',
                'titolo': f'🏆 Achievement Sbloccato: {nome}',
                'messaggio': f'{icon} {desc} | +{punti} punti',
                'priorita': 'high',
                'azione_suggerita': 'Congratulazioni! Continua così!'
            })
    
    conn.commit()

def get_achievements_summary():
    """Recupera riepilogo achievements"""
    conn = get_db_connection()
    
    total = pd.read_sql_query("SELECT COUNT(*) as total FROM Achievements", conn).iloc[0]['total']
    unlocked = pd.read_sql_query("SELECT COUNT(*) as unlocked FROM Achievements WHERE sbloccato = 1", conn).iloc[0]['unlocked']
    points = pd.read_sql_query("SELECT SUM(punti) as points FROM Achievements WHERE sbloccato = 1", conn).iloc[0]['points']
    
    return {
        'total': total,
        'unlocked': unlocked,
        'points': points if points else 0,
        'completion_rate': (unlocked / total * 100) if total > 0 else 0
    }

# ==================== PREDIZIONI SEMPLICI ====================
def predict_future_metrics(df, months_ahead=3):
    """Predizioni semplici basate su trend"""
    
    # Aggrega dati mensili
    df['mese'] = df['data'].dt.to_period('M')
    
    # Calcola medie mobili
    entrate_mensili = df[df['direzione'] == 'Entrata'].groupby('mese')['importo'].sum()
    uscite_mensili = df[df['direzione'] == 'Uscita'].groupby('mese')['importo'].sum()
    
    predictions = {}
    
    if len(entrate_mensili) >= 3:
        # Trend lineare semplice
        recent_entrate = entrate_mensili.tail(3).mean()
        growth_rate = entrate_mensili.pct_change().mean()
        
        pred_entrate = recent_entrate * (1 + growth_rate) ** months_ahead
        predictions['entrate_future'] = pred_entrate
        
    if len(uscite_mensili) >= 3:
        recent_uscite = uscite_mensili.tail(3).mean()
        growth_rate_uscite = uscite_mensili.pct_change().mean()
        
        pred_uscite = recent_uscite * (1 + growth_rate_uscite) ** months_ahead
        predictions['uscite_future'] = pred_uscite
    
    if 'entrate_future' in predictions and 'uscite_future' in predictions:
        predictions['risparmio_future'] = predictions['entrate_future'] - predictions['uscite_future']
        predictions['tasso_risparmio_future'] = (predictions['risparmio_future'] / predictions['entrate_future'] * 100)
    
    predictions['confidenza'] = min(len(entrate_mensili) * 10, 80)  # Max 80%
    
    return predictions

# ==================== CARICAMENTO DATI ====================
@st.cache_data(ttl=300)
def load_all_data():
    """Carica tutti i dati necessari in modo tollerante (compatibile con demo)"""
    conn = get_db_connection()

    # --- Transazioni ---
    try:
        # prima proviamo con eliminata
        trans_query = "SELECT * FROM Transazioni WHERE eliminata = 0 ORDER BY data DESC"
        df_trans = pd.read_sql_query(trans_query, conn)
    except Exception:
        try:
            # se eliminata non esiste, togliamo il filtro
            trans_query = "SELECT * FROM Transazioni ORDER BY data DESC"
            df_trans = pd.read_sql_query(trans_query, conn)
        except Exception:
            # se la tabella non esiste proprio, usiamo un dataframe vuoto
            df_trans = pd.DataFrame()

    # conversione data se presente
    if 'data' in df_trans.columns:
        df_trans['data'] = pd.to_datetime(df_trans['data'], errors='coerce')

    # moat classification se manca
    if 'moat_classification' not in df_trans.columns:
        df_trans['moat_classification'] = None

    # --- Assets ---
    try:
        assets_query = "SELECT * FROM Assets WHERE attivo = 1"
        df_assets = pd.read_sql_query(assets_query, conn)
        asset_columns_defaults = {
            'valore_attuale': 0,
            'valore_acquisto': 0,
            'prezzo_medio': 0,
            'quantità': 0,
            'categoria': 'Generico',
            'data_acquisto': pd.NaT
        }

        for col, default in asset_columns_defaults.items():
            if col not in df_assets.columns:
                df_assets[col] = default


        if 'data_acquisto' in df_assets.columns:
            df_assets['data_acquisto'] = pd.to_datetime(df_assets['data_acquisto'], errors='coerce')
    except Exception:
        df_assets = pd.DataFrame()

    return df_trans, df_assets
# ==================== CALCOLO METRICHE (import dalle altre pagine) ====================
def calculate_moat_metrics(df):
    """Calcola metriche Economic Moat"""
    metrics = {}
    entrate = df[df['direzione'] == 'Entrata']
    entrate_ricorrenti = entrate[entrate['is_ricorrente'] == 'Sì']
    uscite = df[df['direzione'] == 'Uscita']
    
    metrics['entrate_totali'] = entrate['importo'].sum()
    metrics['entrate_ricorrenti'] = entrate_ricorrenti['importo'].sum()
    metrics['percentuale_ricorrenti'] = (
        metrics['entrate_ricorrenti'] / metrics['entrate_totali'] * 100 
        if metrics['entrate_totali'] > 0 else 0
    )
    
    metrics['uscite_fisse'] = uscite[uscite['classe_finanziaria'] == 'Uscite fisse']['importo'].sum()
    metrics['uscite_variabili'] = uscite[uscite['classe_finanziaria'] == 'Uscite variabili']['importo'].sum()
    metrics['tasso_risparmio'] = (
        (metrics['entrate_totali'] - uscite['importo'].sum()) / 
        metrics['entrate_totali'] * 100 
        if metrics['entrate_totali'] > 0 else 0
    )
    
    # Investimenti personali
    cat_inv = ['Formazione', 'Salute', 'Libri', 'Corsi', 'Educazione']
    investimenti = uscite[uscite['categoria'].isin(cat_inv)]
    metrics['investimenti_personali'] = investimenti['importo'].sum()
    
    # Protezione
    cat_prot = ['Assicurazione', 'Risparmio', 'Emergenza', 'Fondo']
    protezioni = df[df['categoria'].str.contains('|'.join(cat_prot), case=False, na=False)]
    metrics['spesa_protezione'] = protezioni['importo'].sum()
    
    # Diversificazione
    metrics['fonti_entrate'] = entrate['tipo'].nunique()
    
    return metrics

def calculate_moat_score(metrics):
    """Calcola Moat Score"""
    score = 0
    
    # Entrate Ricorrenti (30)
    score += min((metrics['percentuale_ricorrenti'] / 100) * 30, 30)
    
    # Tasso Risparmio (25)
    tasso = max(0, min(metrics['tasso_risparmio'], 50))
    score += (tasso / 50) * 25
    
    # Investimenti Personali (20)
    if metrics['entrate_totali'] > 0:
        perc_inv = (metrics['investimenti_personali'] / metrics['entrate_totali']) * 100
        score += min(perc_inv / 10 * 20, 20)
    
    # Diversificazione (15)
    score += min(metrics['fonti_entrate'] / 5 * 15, 15)
    
    # Protezione (10)
    if metrics['entrate_totali'] > 0:
        perc_prot = (metrics['spesa_protezione'] / metrics['entrate_totali']) * 100
        score += min(perc_prot / 5 * 10, 10)
    
    return round(score, 1)

def classify_transaction_moat(row):
    """Classifica transazione"""
    categoria = str(row.get('categoria', '')).lower()
    tipo = str(row.get('tipo', '')).lower()
    
    wide_keywords = ['formazione', 'corso', 'investimento', 'casa', 'salute']
    narrow_keywords = ['risparmio', 'auto', 'computer']
    consumo_keywords = ['spesa', 'ristorante', 'abbigliamento', 'intrattenimento']
    
    text = f"{categoria} {tipo}"
    
    for kw in wide_keywords:
        if kw in text:
            return 'wide_moat'
    for kw in narrow_keywords:
        if kw in text:
            return 'narrow_moat'
    for kw in consumo_keywords:
        if kw in text:
            return 'consumo'
    
    return 'no_moat'

def calculate_investment_metrics(df_trans, assets_df):
    metrics = {}

    if assets_df is None or assets_df.empty:
        metrics['total_assets'] = 0
        metrics['num_assets'] = 0
        metrics['asset_types'] = 0
        return metrics

    # sicurezza colonne
    if 'valore' not in assets_df.columns:
        metrics['total_assets'] = 0
        metrics['num_assets'] = 0
        metrics['asset_types'] = 0
        return metrics

    metrics['total_assets'] = assets_df['valore'].sum()
    metrics['num_assets'] = len(assets_df)
    metrics['asset_types'] = assets_df['tipologia'].nunique() if 'tipologia' in assets_df.columns else 0

    return metrics


def calculate_investment_score(metrics):
    score = 0

    # totale asset
    total_assets = metrics.get('total_assets', 0)
    num_assets = metrics.get('num_assets', 0)
    asset_types = metrics.get('asset_types', 0)

    # scoring semplice e coerente per demo
    if total_assets > 0:
        score += 30
    if num_assets >= 2:
        score += 20
    if asset_types >= 2:
        score += 20

    # opzionali (se in futuro esistono)
    wide_perc = metrics.get('wide_moat_percentage', 0)
    if wide_perc >= 50:
        score += 10

    return min(score, 100)


# ==================== INIZIALIZZA ====================
init_all_tables()

# ==================== UI PRINCIPALE ====================
st.title("🏆 Moat Financial Dashboard - Sistema Completo")

# Sidebar per navigazione
with st.sidebar:
    st.header("🎯 Navigazione")
    page = st.radio(
        "Sezione",
        ["📊 Dashboard", "🏰 Economic Moat", "💎 Moat Investing", "🎮 Gamification", "🔔 Notifiche", "📈 Predizioni"]
    )
    
    st.divider()
    
    # Achievement summary
    ach_summary = get_achievements_summary()
    st.subheader("🏆 I Tuoi Achievement")
    st.metric("Sbloccati", f"{ach_summary['unlocked']}/{ach_summary['total']}")
    st.progress(ach_summary['completion_rate'] / 100)
    st.metric("Punti Totali", f"{ach_summary['points']:.0f}")
    
    st.divider()
    
    # Notifiche non lette
    notif_unread = get_unread_notifications()
    if len(notif_unread) > 0:
        st.warning(f"🔔 {len(notif_unread)} notifiche non lette")

# Carica dati
df_trans, df_assets = load_all_data()
# --- sicurezza: garantiamo che la colonna 'data' esista ---
if df_trans is None or len(df_trans) == 0:
    # dataframe vuoto
    df_trans = pd.DataFrame(columns=['data'])
else:
    # se manca la colonna data, la creiamo
    if 'data' not in df_trans.columns:
        df_trans['data'] = pd.NaT

# assicuriamo formato datetime
df_trans['data'] = pd.to_datetime(df_trans['data'], errors='coerce')

# Filtro periodo (comune a tutte le pagine)
col1, col2 = st.columns(2)
with col1:
    date_from = st.date_input("Da", value=datetime.now() - timedelta(days=90))
with col2:
    date_to = st.date_input("A", value=datetime.now())

# Filtra
df_filtered = df_trans[
    (df_trans['data'] >= pd.Timestamp(date_from)) & 
    (df_trans['data'] <= pd.Timestamp(date_to))
]

if len(df_filtered) == 0:
    st.warning("Nessuna transazione nel periodo")
    st.stop()
# --- colonne di sicurezza per la demo online ---
# se mancano alcune colonne nel DB, le creiamo con valori di default

columns_defaults = {
    'is_ricorrente': 'No',
    'is_energia': 'No',
    'emoji': '',
    'archiviato': '',
    'attiva': 1
}

for col, default in columns_defaults.items():
    if col not in df_filtered.columns:
        df_filtered[col] = default
# Calcola tutte le metriche
moat_metrics = calculate_moat_metrics(df_filtered)
moat_score = calculate_moat_score(moat_metrics)
invest_metrics = calculate_investment_metrics(df_filtered, df_assets)
invest_score = calculate_investment_score(invest_metrics)

# Genera notifiche
check_and_create_notifications(moat_metrics, invest_metrics, moat_score, invest_score)

# ==================== PAGINA: DASHBOARD ====================
if page == "📊 Dashboard":
    st.header("📊 Dashboard Unificata")
    
    # KPI principali in evidenza
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<p class="big-metric">🏰</p>', unsafe_allow_html=True)
        st.metric("Moat Score", f"{moat_score:.1f}/100", 
                 delta=f"{moat_score - 70:+.1f} vs target")
    
    with col2:
        st.markdown('<p class="big-metric">💎</p>', unsafe_allow_html=True)
        st.metric("Investment Score", f"{invest_score:.1f}/100",
                 delta=f"{invest_score - 70:+.1f} vs target")
    
    with col3:
        st.markdown('<p class="big-metric">💰</p>', unsafe_allow_html=True)
        st.metric("Patrimonio"), f"€{invest_metrics['total_assets']:,.0f}",
        asset_growth = invest_metrics.get('asset_growth', 0)
        delta = f"{asset_growth:+.1f}%"
        # --- sicurezza metriche investimento (demo) ---
        defaults = {
            'asset_growth': 0,
            'total_assets': 0,
            'num_assets': 0,
            'asset_types': 0
        }

for k, v in defaults.items():
    invest_metrics.setdefault(k, v)
    
    with col4:
        st.markdown('<p class="big-metric">📈</p>', unsafe_allow_html=True)
        st.metric("Tasso Risparmio", f"{moat_metrics['tasso_risparmio']:.1f}%",
                 delta=f"{moat_metrics['tasso_risparmio'] - 20:+.1f}% vs 20%")
    
    st.divider()
    
    # Grafici combinati
    col1, col2 = st.columns(2)
    
    with col1:
        # Dual gauge: Moat + Investment Score
        fig_dual = go.Figure()
        
        fig_dual.add_trace(go.Indicator(
            mode="gauge+number",
            value=moat_score,
            domain={'x': [0, 0.48], 'y': [0, 1]},
            title={'text': "Moat Score", 'font': {'size': 16}},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 40], 'color': "lightgray"},
                    {'range': [40, 70], 'color': "lightyellow"},
                    {'range': [70, 100], 'color': "lightgreen"}
                ]
            }
        ))
        
        fig_dual.add_trace(go.Indicator(
            mode="gauge+number",
            value=invest_score,
            domain={'x': [0.52, 1], 'y': [0, 1]},
            title={'text': "Investment Score", 'font': {'size': 16}},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "purple"},
                'steps': [
                    {'range': [0, 40], 'color': "lightgray"},
                    {'range': [40, 70], 'color': "lightyellow"},
                    {'range': [70, 100], 'color': "lightgreen"}
                ]
            }
        ))
        
        fig_dual.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_dual, use_container_width=True)
    
    with col2:
        # Health Score combinato
        health_score = (moat_score + invest_score) / 2
        
        fig_health = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=health_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Financial Health Score", 'font': {'size': 20}},
            delta={'reference': 70, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 40], 'color': '#ffcccc'},
                    {'range': [40, 70], 'color': '#ffffcc'},
                    {'range': [70, 100], 'color': '#ccffcc'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 85
                }
            }
        ))
        fig_health.update_layout(height=300)
        st.plotly_chart(fig_health, use_container_width=True)
        
        if health_score >= 80:
            st.success("🏆 Situazione finanziaria eccellente!")
        elif health_score >= 60:
            st.info("✅ Situazione finanziaria buona")
        elif health_score >= 40:
            st.warning("⚠️ Situazione da migliorare")
        else:
            st.error("🚨 Situazione critica - azione immediata necessaria")
    
    # Trend temporale combinato
    st.subheader("📈 Evoluzione Temporale")
    
    df_filtered['mese'] = df_filtered['data'].dt.to_period('M').astype(str)
    
    # Entrate vs Uscite mensili
    entrate_mensili = df_filtered[df_filtered['direzione'] == 'Entrata'].groupby('mese')['importo'].sum()
    uscite_mensili = df_filtered[df_filtered['direzione'] == 'Uscita'].groupby('mese')['importo'].sum()
    
    fig_trend = go.Figure()
    
    fig_trend.add_trace(go.Bar(
        x=entrate_mensili.index,
        y=entrate_mensili.values,
        name='Entrate',
        marker_color='green'
    ))
    
    fig_trend.add_trace(go.Bar(
        x=uscite_mensili.index,
        y=-uscite_mensili.values,
        name='Uscite',
        marker_color='red'
    ))
    
    # Saldo
    saldo = entrate_mensili.subtract(uscite_mensili, fill_value=0)
    fig_trend.add_trace(go.Scatter(
        x=saldo.index,
        y=saldo.values,
        name='Saldo Netto',
        mode='lines+markers',
        line=dict(color='blue', width=3)
    ))
    
    fig_trend.update_layout(
        title="Trend Mensile Entrate/Uscite",
        barmode='relative',
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Notifiche importanti in evidenza
    st.subheader("🔔 Notifiche Recenti")
    notif_recent = get_unread_notifications()
    
    if len(notif_recent) > 0:
        for _, notif in notif_recent.head(3).iterrows():
            priority_color = {
                'critical': '🚨',
                'high': '⚠️',
                'medium': '💡',
                'low': 'ℹ️'
            }
            
            with st.expander(f"{priority_color.get(notif['priorita'], 'ℹ️')} {notif['titolo']}"):
                st.write(notif['messaggio'])
                if notif['azione_suggerita']:
                    st.info(f"**Azione suggerita:** {notif['azione_suggerita']}")
                
                if st.button("Segna come letto", key=f"read_{notif['id']}"):
                    mark_notification_read(notif['id'])
                    st.rerun()
    else:
        st.success("✅ Nessuna notifica! Tutto sotto controllo.")
    
    # Quick stats
    st.subheader("📊 Statistiche Rapide")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Transazioni Analizzate", len(df_filtered))
        st.metric("Asset Registrati", invest_metrics['asset_count'])
    
    with col2:
        st.metric("Entrate Ricorrenti", f"{moat_metrics['percentuale_ricorrenti']:.1f}%")
        st.metric("Investimenti Wide Moat", f"{invest_metrics['wide_moat_percentage']:.1f}%")
    
    with col3:
        st.metric("Fonti di Entrata", moat_metrics['fonti_entrate'])
        st.metric("Investimenti Personali", f"€{moat_metrics['investimenti_personali']:.0f}")

# ==================== PAGINA: ECONOMIC MOAT ====================
elif page == "🏰 Economic Moat":
    st.header("🏰 Economic Moat Analysis")

    st.info("Questa sezione analizza quanto è **difendibile** la tua posizione finanziaria")

    # Score components
    col1, col2 = st.columns([2, 1])

    with col1:
        # Radar chart
        categories = [
            'Entrate Ricorrenti',
            'Tasso Risparmio',
            'Investimenti Self',
            'Diversificazione',
            'Protezione'
        ]

        values = [
            min(moat_metrics.get('percentuale_ricorrenti', 0), 100) / 100 * 30,
            max(0, min(moat_metrics.get('tasso_risparmio', 0), 50)) / 50 * 25,
            (
                min(
                    (moat_metrics.get('investimenti_personali', 0) /
                     moat_metrics.get('entrate_totali', 1) * 100),
                    10
                ) / 10 * 20
                if moat_metrics.get('entrate_totali', 0) > 0 else 0
            ),
            min(moat_metrics.get('fonti_entrate', 0) / 5 * 15, 15),
            (
                min(
                    (moat_metrics.get('spesa_protezione', 0) /
                     moat_metrics.get('entrate_totali', 1) * 100),
                    5
                ) / 5 * 10
                if moat_metrics.get('entrate_totali', 0) > 0 else 0
            )
        ]

        max_values = [30, 25, 20, 15, 10]

        fig_radar = go.Figure()

        fig_radar.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Attuale'
            )
        )

        fig_radar.add_trace(
            go.Scatterpolar(
                r=max_values,
                theta=categories,
                fill='toself',
                name='Massimo'
            )
        )

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True)),
            showlegend=True
        )

        st.plotly_chart(fig_radar, use_container_width=True)



    
    with col2:
        st.subheader("Componenti")
        
        for cat, val, max_val in zip(categories, values, max_values):
            perc = (val / max_val * 100) if max_val > 0 else 0
            st.progress(perc / 100, text=f"**{cat}**")
            st.caption(f"{val:.1f}/{max_val}")
            st.divider()
    
    # Dettagli metriche
    st.subheader("📊 Dettaglio Metriche")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Entrate Totali", f"€{moat_metrics['entrate_totali']:,.2f}")
        st.metric("Entrate Ricorrenti", f"{moat_metrics['percentuale_ricorrenti']:.1f}%")
    
    with col2:
        st.metric("Uscite Fisse", f"€{moat_metrics['uscite_fisse']:,.2f}")
        st.metric("Uscite Variabili", f"€{moat_metrics['uscite_variabili']:,.2f}")
    
    with col3:
        st.metric("Tasso Risparmio", f"{moat_metrics['tasso_risparmio']:.1f}%")
        st.metric("Fonti Entrate", moat_metrics['fonti_entrate'])

# ==================== PAGINA: MOAT INVESTING ====================
elif page == "💎 Moat Investing":
    st.header("💎 Moat Investing Analysis")
    
    st.info("Questa sezione analizza come stai **investendo** per costruire ricchezza duratura")
    
    # Allocazione spese
    col1, col2 = st.columns(2)
    
    with col1:
        # Sunburst
        moat_data = pd.DataFrame({
            'labels': ['Totale', 'Wide Moat', 'Narrow Moat', 'No Moat', 'Consumo'],
            'parents': ['', 'Totale', 'Totale', 'Totale', 'Totale'],
            'values': [
                invest_metrics['total_spending'],
                invest_metrics['wide_moat_spending'],
                invest_metrics['narrow_moat_spending'],
                invest_metrics['no_moat_spending'],
                invest_metrics['consumo_spending']
            ]
        })
        
        fig_sun = px.sunburst(
            moat_data,
            names='labels',
            parents='parents',
            values='values',
            title="Allocazione Spese per Tipo Moat"
        )
        st.plotly_chart(fig_sun, use_container_width=True)
    
    with col2:
        # Tabella allocazione
        st.subheader("Dettaglio Allocazione")
        
        alloc_df = pd.DataFrame({
            'Tipo': ['🏰 Wide Moat', '🛡️ Narrow Moat', '⚠️ No Moat', '🛒 Consumo'],
            'Importo (€)': [
                invest_metrics['wide_moat_spending'],
                invest_metrics['narrow_moat_spending'],
                invest_metrics['no_moat_spending'],
                invest_metrics['consumo_spending']
            ],
            '%': [
                f"{invest_metrics['wide_moat_spending']/invest_metrics['total_spending']*100:.1f}%",
                f"{invest_metrics['narrow_moat_spending']/invest_metrics['total_spending']*100:.1f}%",
                f"{invest_metrics['no_moat_spending']/invest_metrics['total_spending']*100:.1f}%",
                f"{invest_metrics['consumo_spending']/invest_metrics['total_spending']*100:.1f}%"
            ] if invest_metrics['total_spending'] > 0 else ['0%']*4
        })
        
        st.dataframe(alloc_df, use_container_width=True, hide_index=True)
        
        st.divider()
        
        st.metric("Tasso Investimento", f"{invest_metrics['investment_rate']:.1f}%")
        st.metric("Target Wide Moat", "20%", 
                 delta=f"{invest_metrics['wide_moat_percentage'] - 20:+.1f}%")
    
    # Patrimonio
    if invest_metrics['total_assets'] > 0:
        st.subheader("💎 Patrimonio Familiare")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Patrimonio Totale", f"€{invest_metrics['total_assets']:,.2f}")
        
        with col2:
            st.metric("Numero Asset", invest_metrics['asset_count'])
        
        with col3:
            st.metric("Crescita", f"{invest_metrics['asset_growth']:.1f}%")

# ==================== PAGINA: GAMIFICATION ====================
elif page == "🎮 Gamification":
    st.header("🎮 Sistema Gamification")
    
    st.markdown("""
    Sblocca achievements, accumula punti e raggiungi i tuoi obiettivi finanziari!
    Ogni traguardo ti avvicina alla libertà finanziaria.
    """)
    
    # Summary achievements
    ach_sum = get_achievements_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Achievement Sbloccati", f"{ach_sum['unlocked']}/{ach_sum['total']}")
    
    with col2:
        st.metric("Tasso Completamento", f"{ach_sum['completion_rate']:.0f}%")
    
    with col3:
        st.metric("Punti Totali", f"{ach_sum['points']:.0f}")
    
    with col4:
        # Calcola livello basato su punti
        level = int(ach_sum['points'] / 500) + 1
        st.metric("Livello", level)
    
    # Progress bar generale
    st.progress(ach_sum['completion_rate'] / 100, text=f"Completamento Generale: {ach_sum['completion_rate']:.0f}%")
    
    st.divider()
    
    # Lista achievements per categoria
    conn = get_db_connection()
    achievements_df = pd.read_sql_query("SELECT * FROM Achievements ORDER BY categoria, livello", conn)
    
    for categoria in achievements_df['categoria'].unique():
        with st.expander(f"📁 {categoria.replace('_', ' ').title()}"):
            cat_achs = achievements_df[achievements_df['categoria'] == categoria]
            
            for _, ach in cat_achs.iterrows():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    if ach['sbloccato']:
                        st.markdown(f"✅ **{ach['icona']} {ach['nome']}** (Livello {ach['livello']})")
                    else:
                        st.markdown(f"🔒 **{ach['icona']} {ach['nome']}** (Livello {ach['livello']})")
                    st.caption(ach['descrizione'])
                
                with col2:
                    st.write(f"**{ach['punti']} punti**")
                
                with col3:
                    if ach['sbloccato']:
                        st.success("Sbloccato!")
                    else:
                        st.info("In corso...")
                
                st.divider()
    
    # Sistema obiettivi
    st.subheader("🎯 I Tuoi Obiettivi")
    
    goals_df = pd.read_sql_query("SELECT * FROM Goals WHERE completato = 0 ORDER BY priorita DESC", conn)
    
    if len(goals_df) > 0:
        for _, goal in goals_df.iterrows():
            progress = (goal['valore_attuale'] / goal['valore_target'] * 100) if goal['valore_target'] > 0 else 0
            
            st.progress(min(progress / 100, 1.0), text=f"**{goal['nome']}**")
            st.caption(f"Progresso: {goal['valore_attuale']:.2f} / {goal['valore_target']:.2f}")
    else:
        st.info("Nessun obiettivo attivo. Creane uno nuovo!")
    
    # Crea nuovo obiettivo
    with st.expander("➕ Crea Nuovo Obiettivo"):
        with st.form("new_goal"):
            goal_nome = st.text_input("Nome Obiettivo")
            goal_tipo = st.selectbox("Tipo", 
                ['moat_score', 'investment_score', 'wide_moat_perc', 'patrimonio', 'risparmio']
            )
            goal_target = st.number_input("Valore Target", min_value=0.0, step=100.0)
            goal_data = st.date_input("Data Target")
            goal_priorita = st.selectbox("Priorità", ['low', 'medium', 'high'])
            
            if st.form_submit_button("Crea Obiettivo"):
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Goals (nome, tipo, valore_target, data_inizio, data_target, priorita)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (goal_nome, goal_tipo, goal_target, datetime.now().date(), goal_data, goal_priorita))
                conn.commit()
                st.success("Obiettivo creato!")
                st.rerun()

# ==================== PAGINA: NOTIFICHE ====================
elif page == "🔔 Notifiche":
    st.header("🔔 Centro Notifiche")
    
    # Filtri
    col1, col2 = st.columns(2)
    
    with col1:
        filter_tipo = st.multiselect(
            "Tipo",
            ['alert', 'opportunity', 'achievement', 'warning'],
            default=['alert', 'opportunity', 'achievement', 'warning']
        )
    
    with col2:
        show_read = st.checkbox("Mostra anche lette", value=False)
    
    # Query notifiche
    query = f"""
        SELECT * FROM Notifications 
        WHERE tipo IN ({','.join(['?']*len(filter_tipo))})
    """
    
    if not show_read:
        query += " AND letta = 0"
    
    query += " ORDER BY priorita DESC, data_creazione DESC LIMIT 50"
    
    notif_df = pd.read_sql_query(query, get_db_connection(), params=filter_tipo)
    
    if len(notif_df) > 0:
        for _, notif in notif_df.iterrows():
            # Icone per tipo
            tipo_icons = {
                'alert': '🚨',
                'opportunity': '💡',
                'achievement': '🏆',
                'warning': '⚠️'
            }
            
            # Colori per priorità
            priority_style = {
                'critical': 'background-color: #ffcccc; padding: 15px; border-radius: 10px; margin: 10px 0;',
                'high': 'background-color: #fff3cd; padding: 15px; border-radius: 10px; margin: 10px 0;',
                'medium': 'background-color: #d1ecf1; padding: 15px; border-radius: 10px; margin: 10px 0;',
                'low': 'background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin: 10px 0;'
            }
            
            with st.container():
                st.markdown(f'<div style="{priority_style.get(notif["priorita"], "")}">', unsafe_allow_html=True)
                
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.markdown(f"### {tipo_icons.get(notif['tipo'], 'ℹ️')} {notif['titolo']}")
                    st.write(notif['messaggio'])
                    
                    if notif['azione_suggerita']:
                        st.info(f"**💡 Azione suggerita:** {notif['azione_suggerita']}")
                    
                    st.caption(f"📅 {notif['data_creazione']}")
                
                with col2:
                    if notif['letta'] == 0:
                        if st.button("✓ Letta", key=f"mark_{notif['id']}"):
                            mark_notification_read(notif['id'])
                            st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.divider()
    else:
        st.success("✅ Nessuna notifica! Tutto sotto controllo.")

# ==================== PAGINA: PREDIZIONI ====================
elif page == "📈 Predizioni":
    st.header("📈 Predizioni e Proiezioni")
    
    st.info("Analisi predittiva basata sui tuoi trend storici")
    
    # Calcola predizioni
    predictions = predict_future_metrics(df_trans, months_ahead=6)
    
    if len(predictions) > 0:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'entrate_future' in predictions:
                st.metric(
                    "Entrate Previste (6 mesi)",
                    f"€{predictions['entrate_future']:,.2f}",
                    help=f"Confidenza: {predictions['confidenza']:.0f}%"
                )
        
        with col2:
            if 'uscite_future' in predictions:
                st.metric(
                    "Uscite Previste (6 mesi)",
                    f"€{predictions['uscite_future']:,.2f}",
                    help=f"Confidenza: {predictions['confidenza']:.0f}%"
                )
        
        with col3:
            if 'risparmio_future' in predictions:
                st.metric(
                    "Risparmio Previsto (6 mesi)",
                    f"€{predictions['risparmio_future']:,.2f}",
                    delta=f"{predictions['tasso_risparmio_future']:.1f}%",
                    help=f"Confidenza: {predictions['confidenza']:.0f}%"
                )
        
        # Grafico proiezione
        st.subheader("📊 Proiezione Patrimonio")
        
        months = list(range(1, 13))
        current_patrimonio = invest_metrics['total_assets']
        monthly_saving = predictions.get('risparmio_future', 0) / 6
        
        patrimonio_projection = []
        for month in months:
            projected = current_patrimonio + (monthly_saving * month)
            patrimonio_projection.append(projected)
        
        fig_proj = go.Figure()
        
        fig_proj.add_trace(go.Scatter(
            x=months,
            y=patrimonio_projection,
            mode='lines+markers',
            name='Proiezione Patrimonio',
            line=dict(color='green', width=3),
            fill='tozeroy'
        ))
        
        fig_proj.update_layout(
            title="Proiezione Crescita Patrimonio (12 mesi)",
            xaxis_title="Mesi",
            yaxis_title="Patrimonio (€)",
            height=400
        )
        
        st.plotly_chart(fig_proj, use_container_width=True)
        
        # Scenario analysis
        st.subheader("🔮 Analisi Scenari")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📉 Scenario Pessimista**")
            st.markdown("Risparmio -20%")
            pessimistic = current_patrimonio + (monthly_saving * 0.8 * 12)
            st.metric("Patrimonio a 12 mesi", f"€{pessimistic:,.2f}")
        
        with col2:
            st.markdown("**📊 Scenario Base**")
            st.markdown("Trend attuale")
            base = current_patrimonio + (monthly_saving * 12)
            st.metric("Patrimonio a 12 mesi", f"€{base:,.2f}")
        
        with col3:
            st.markdown("**📈 Scenario Ottimista**")
            st.markdown("Risparmio +20%")
            optimistic = current_patrimonio + (monthly_saving * 1.2 * 12)
            st.metric("Patrimonio a 12 mesi", f"€{optimistic:,.2f}")
    
    else:
        st.warning("Non ci sono abbastanza dati storici per generare predizioni affidabili. Continua a tracciare le transazioni!")

# Footer
st.divider()
st.caption(f"⏰ Ultimo aggiornamento: {datetime.now().strftime('%d/%m/%Y %H:%M')} | 🏆 Moat Financial Dashboard v2.0")
