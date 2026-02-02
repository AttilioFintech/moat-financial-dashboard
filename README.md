# 🏰 Moat — Strategic Financial Resilience

**Moat is not a budgeting tool.**  
**It is a strategic positioning system for financial decision-making.**

---

## 🎯 What Moat Does

Most financial tools track what happened.  
Moat shows you **what happens if you do nothing**.

### Core Capabilities

1. **Strategic Alert System**  
   Identifies your top structural vulnerability before it cascades.

2. **Archetype-Based Calibration**  
   Adjusts thresholds based on your income type, volatility, and time horizon.

3. **PRO Decision Simulations**  
   - What-If scenarios (test income/expense changes)
   - 12-month trajectory projection
   - Stress testing (4 extreme scenarios)
   - Operator benchmarks (compare to similar profiles)

---

## 🧠 Philosophy

Financial resilience isn't about having more money.  
It's about maintaining **optionality when variables shift**.

Moat helps you:
- Identify where you're exposed **before** shocks happen
- Simulate decisions **before** committing resources
- Build defensive positions that compound over time

---

## 🏗️ Architecture

moat/
├── app.py                       # Entry point with routing
├── core/                        # Pure logic (no UI)
│   ├── metrics.py              # Financial calculations
│   ├── scoring.py              # Moat Score algorithm
│   ├── scenarios.py            # What-if + stress test logic
│   ├── trajectory.py           # Projection calculations
│   ├── vulnerabilities.py      # Risk detection
│   └── persistence.py          # SQLite storage
└── src/                         # UI + business logic
├── onboarding.py           # 3-question setup + data input
├── dashboard.py            # Strategic alert + metrics
├── vulnerabilities.py      # Top risk display
├── whatif.py               # PRO: Decision simulator
├── trajectory.py           # PRO: 12-month projection
├── stress_test.py          # PRO: Resilience testing
├── comparison.py           # PRO: Operator benchmarks
├── archetypes.py           # Archetype library
├── about.py                # Positioning page
└── utils/
├── pro_gate.py         # PRO feature gating
└── pro_comparison.py   # Peer insights engine


---

## 🚀 Setup

### Prerequisites

- Python 3.8+
- Streamlit
- SQLite (included)

### Installation

```bash
# Clone repository
git clone https://github.com/your-username/moat-financial-dashboard.git
cd moat-financial-dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py


App opens at http://localhost:8501

📊 Data Storage
Moat uses SQLite for persistence:
	∙	moat_data.db (or gestione_conti_casa_demo.db if exists)
Stores:
	∙	User financial metrics (income, expenses, emergency fund, income sources)
	∙	Onboarding data (archetype, volatility, time horizon)
	∙	Moat Score history (for future trend tracking)
No authentication yet — single user per deployment.

🎮 User Flow
	1.	Onboarding (Strategic Setup)
	∙	3 strategic questions → determine archetype
	∙	Input financial metrics (income, expenses, emergency fund, income sources)
	∙	Calculate income concentration
	2.	Dashboard
	∙	Strategic Alert (top vulnerability)
	∙	Moat Score + key metrics
	∙	Positioning assessment
	3.	Vulnerabilities
	∙	Identify THE dominant risk (not a list)
	4.	PRO Features (behind gate for FREE users)
	∙	What-If: Simulate income/expense changes
	∙	Trajectory: See 12-month projection
	∙	Stress Test: Test against 4 extreme scenarios
	∙	Benchmarks: Compare to operator peers (FREE = qualitative, PRO = numeric)

🔑 Key Metrics
Moat Score (0-100)
Composite defensibility score based on:
	∙	Emergency coverage (months)
	∙	Expense growth rate
	∙	Income concentration
Emergency Months
emergency_fund / monthly_expenses
Income Concentration
(largest_income_source / total_income) * 100
Savings Rate
((income - expenses) / income) * 100

🧩 Archetypes
Moat calibrates to 4 operator archetypes:
	1.	Stable OperatorW2 income, low volatility → standard thresholds
	2.	Variable OperatorFreelance/business, high volatility → tighter thresholds
	3.	Portfolio OperatorMixed income sources → medium sensitivity
	4.	Emerging OperatorBuilding position → default baseline
Each archetype has:
	∙	Different baseline Moat Score
	∙	Different alert thresholds
	∙	Customized copy and recommendations

🛠️ Development
Run locally with hot reload

streamlit run app.py

Database management

from core.persistence import init_db, load_user_financials

# Initialize tables
init_db()

# Load data
financials = load_user_financials()

Enable PRO (dev mode)
In sidebar → Dev Controls → Enable PRO checkbox

📝 Testing
See SMOKE_TEST.md for complete testing checklist.
Quick test:

streamlit run app.py
# Complete onboarding
# Verify PRO gate on What-If/Trajectory/Stress Test
# Enable PRO in Dev Controls
# Verify simulations work


🎯 Target Audience
Moat is built for operators:
	∙	Founders managing variable income
	∙	Professionals allocating between growth and defense
	∙	Freelancers managing volatility
	∙	Anyone who thinks in systems, not just budgets

📬 Contact
Questions or feedback?moat@yourdomain.com

📜 License
[Your license here]

Built by strategists, for strategists.

