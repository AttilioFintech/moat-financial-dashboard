"""
Persistence layer using SQLite.
Stores user_financials and session state for Moat.
"""

import sqlite3
import json
from pathlib import Path
import os


def get_db_path():
    """
    Returns path to SQLite database.
    Streamlit Cloud compatible.
    """
    # Su Streamlit Cloud, usa /tmp
    if os.getenv("STREAMLIT_RUNTIME_ENV") or os.getenv("STREAMLIT_SHARING_MODE"):
        return "/tmp/moat_data.db"
    
    # Locale: usa directory corrente
    demo_db = Path("gestione_conti_casa_demo.db")
    if demo_db.exists():
        return str(demo_db)
    return "moat_data.db"


def init_db():
    """
    Initialize database tables if they don't exist.
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # User financials table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_financials (
            id INTEGER PRIMARY KEY,
            monthly_income REAL NOT NULL,
            monthly_expenses REAL NOT NULL,
            emergency_fund REAL NOT NULL,
            income_sources TEXT NOT NULL,
            income_concentration REAL NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Onboarding data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_onboarding (
            id INTEGER PRIMARY KEY,
            income_type TEXT NOT NULL,
            volatility TEXT NOT NULL,
            time_horizon TEXT NOT NULL,
            archetype_name TEXT NOT NULL,
            archetype_data TEXT NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Moat score history (for future tracking)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS moat_score_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score REAL NOT NULL,
            emergency_months REAL,
            income_concentration REAL,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def save_user_financials(financials):
    """
    Save or update user financial data.
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # Serialize income_sources to JSON
    sources_json = json.dumps(financials["income_sources"])
    
    # Delete existing (single user for now)
    cursor.execute("DELETE FROM user_financials")
    
    # Insert new
    cursor.execute("""
        INSERT INTO user_financials 
        (id, monthly_income, monthly_expenses, emergency_fund, income_sources, income_concentration)
        VALUES (1, ?, ?, ?, ?, ?)
    """, (
        financials["monthly_income"],
        financials["monthly_expenses"],
        financials["emergency_fund"],
        sources_json,
        financials["income_concentration"]
    ))
    
    conn.commit()
    conn.close()


def load_user_financials():
    """
    Load user financial data.
    """
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT monthly_income, monthly_expenses, emergency_fund, 
                   income_sources, income_concentration
            FROM user_financials 
            WHERE id = 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "monthly_income": row[0],
            "monthly_expenses": row[1],
            "emergency_fund": row[2],
            "income_sources": json.loads(row[3]),
            "income_concentration": row[4]
        }
    except Exception:
        return None


def save_onboarding(income_type, volatility, time_horizon, archetype):
    """
    Save onboarding data.
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # Serialize archetype
    archetype_json = json.dumps(archetype)
    
    # Delete existing
    cursor.execute("DELETE FROM user_onboarding")
    
    # Insert new
    cursor.execute("""
        INSERT INTO user_onboarding
        (id, income_type, volatility, time_horizon, archetype_name, archetype_data)
        VALUES (1, ?, ?, ?, ?, ?)
    """, (
        income_type,
        volatility,
        time_horizon,
        archetype["name"],
        archetype_json
    ))
    
    conn.commit()
    conn.close()


def load_onboarding():
    """
    Load onboarding data.
    """
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT income_type, volatility, time_horizon, archetype_data
            FROM user_onboarding
            WHERE id = 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "income_type": row[0],
            "volatility": row[1],
            "time_horizon": row[2],
            "archetype": json.loads(row[3])
        }
    except Exception:
        return None


def save_moat_score(score, emergency_months, income_concentration):
    """
    Save Moat Score to history (for future trend tracking).
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO moat_score_history (score, emergency_months, income_concentration)
        VALUES (?, ?, ?)
    """, (score, emergency_months, income_concentration))
    
    conn.commit()
    conn.close()


def get_moat_score_history(limit=30):
    """
    Get recent Moat Score history.
    """
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT score, emergency_months, income_concentration, calculated_at
            FROM moat_score_history
            ORDER BY calculated_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "score": row[0],
                "emergency_months": row[1],
                "income_concentration": row[2],
                "date": row[3]
            }
            for row in rows
        ]
    except Exception:
        return []
