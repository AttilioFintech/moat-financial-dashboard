# 🧪 Moat Smoke Test

**Obiettivo:** Verificare che FREE users capiscano dove sono, ma non possano decidere senza PRO.

---

## 🔄 Test Flow

### **1. Avvio App**

```bash
streamlit run app.py

✅ Verifica:
	∙	App si avvia senza errori
	∙	Sidebar mostra solo “Strategic Setup” e “About”
	∙	Nessun crash

2. Onboarding Completo
Navigate: Strategic Setup
Compila:
	∙	Part 1: Strategic Context (3 domande)
	∙	Part 2: Financial Metrics (income, expenses, emergency fund)
	∙	Part 3: Income Sources (almeno 1 source)
Verifica somma:
	∙	Total sources = Total income (altrimenti warning appare)
Click: Lock In Position

✅ Verifica:
	∙	Vedi “Position Locked”
	∙	Archetype assegnato (Stable/Variable/Portfolio/Emerging)
	∙	Moat Score baseline mostrato
	∙	Income concentration calcolata
	∙	Sidebar sblocca tutte le pagine

3. Dashboard (FREE User)
Navigate: Dashboard
✅ Verifica:
	∙	Strategic Alert appare (se vulnerabilità presente)
	∙	Moat Score visualizzato con dati reali
	∙	Emergency Coverage mostra mesi corretti
	∙	Income Concentration mostra % reale
	∙	Positioning statement coerente con score
❓ Chiedi a te stesso:
“Capisco dove sono (score, metriche), ma posso decidere cosa fare?”
Risposta attesa: NO. Vedi stato, non azioni.

4. Vulnerabilities (FREE User)
Navigate: Vulnerabilities
✅ Verifica:
	∙	Mostra IL rischio dominante (non lista)
	∙	Title chiaro (es: “Single-Source Dependency”)
	∙	Description spiega conseguenze
	∙	“If This Persists” section presente
	∙	NO actionable recommendations (quelle sono PRO)
❓ Chiedi a te stesso:
“So cosa rischio, ma so come proteggermi?”
Risposta attesa: NO. Conosci rischio, non soluzione.

5. What-If (FREE User - PRO Gate)
Navigate: What-If
✅ Verifica:
	∙	PRO gate appare
	∙	Titolo: “What-If Engine”
	∙	Messaggio spiega cosa stai perdendo
	∙	NO sliders visibili
	∙	“Request Access” button presente (non funzionale per MVP)
❓ Chiedi a te stesso:
“Vorrei testare uno scenario, posso farlo?”
Risposta attesa: NO. Gate blocca.

6. Trajectory (FREE User - PRO Gate)
Navigate: Trajectory
✅ Verifica:
	∙	PRO gate appare
	∙	Messaggio su “vedere prima quello che altri scoprono dopo”
	∙	NO grafico visibile
	∙	Gate coerente con What-If

7. Stress Test (FREE User - PRO Gate)

Navigate: Stress Test
✅ Verifica:
	∙	PRO gate appare
	∙	Messaggio su testing resilienza
	∙	NO scenari visibili


8. Benchmarks (FREE User - Partial)
Navigate: Benchmarks
✅ Verifica:
	∙	Mostra tue metriche (emergency months, savings rate, concentration)
	∙	Benchmark numerico NASCOSTO (mostra “🔒 PRO”)
	∙	Assessment QUALITATIVO visibile (“below typical”, “functional”, etc.)
	∙	“What operators do” section visibile (generale)
❓ Chiedi a te stesso:
“Capisco se sono sopra/sotto la media?”
Risposta attesa: VAGAMENTE. Sai direzione, non gap preciso.

9. Enable PRO (Dev Mode)
Navigate: Sidebar → Dev Controls
✅ Verifica:
	∙	“Dev Controls” expander presente
	∙	“Enable PRO” checkbox funziona
	∙	Status cambia da “📊 Free Tier” a “✓ Strategic Access Active”

10. What-If (PRO User)
Con PRO attivo, navigate: What-If
✅ Verifica:
	∙	NO PRO gate
	∙	Sliders visibili (income/expense change)
	∙	Impact analysis calcola correttamente
	∙	Moat Score delta mostrato
	∙	Strategic assessment presente
	∙	“What operators like you do” section appare
Test scenario:
	∙	Income: +20%
	∙	Expense: +10%
Verifica:
	∙	Surplus aumenta
	∙	Moat Score cambia
	∙	Assessment coerente

11. Trajectory (PRO User)
✅ Verifica:
	∙	Grafico 12-month visibile
	∙	3 scenari (conservative/base/aggressive)
	∙	Emergency coverage finale calcolata
	∙	Alternative paths section presente


12. Stress Test (PRO User)
✅ Verifica:
	∙	4 stress scenarios visibili
	∙	Per ogni scenario: monthly burn, total impact, survives/fails
	∙	Overall resilience score calcolato
	∙	Operator actions per resilience level

13. Benchmarks (PRO User)
✅ Verifica:
	∙	Benchmark NUMERICO visibile (es: “11.5 mo”)
	∙	Gap analysis precisa (es: “-6.7 mo”)
	∙	Assessment SPECIFICO (non generico)
	∙	Colori appropriati (rosso/giallo/verde)

14. Persistence Test
Chiudi app: Ctrl+C
Riapri: streamlit run app.py
Navigate: Dashboard
✅ Verifica:
	∙	Dati ANCORA presenti (no need to redo onboarding)
	∙	Moat Score corretto
	∙	Metriche corrette
Se dati spariti:
	∙	❌ Persistence non funziona
	∙	Verifica che core/persistence.py sia corretto
	∙	Verifica che database si crei (moat_data.db o /tmp/moat_data.db)

✅ CRITERIO SUCCESSO
FREE User Flow:
“Vedo dove sono. Capisco i rischi. Ma non posso simulare decisioni o comparare precisamente con peers.”
PRO User Flow:
“Posso testare scenari, vedere traiettorie, stress testare struttura, e comparare numericamente con operators simili.”
Se questo è chiaro → TEST PASSED.

🚨 Red Flags
❌ FREE user vede benchmark numerici → PRO gate rotto❌ PRO gate non appare su What-If/Trajectory/Stress Test → Gate mancante❌ Dati spariscono dopo chiusura app → Persistence rotta❌ Moat Score hardcoded (non usa dati reali) → Integration mancante❌ Income concentration sempre 100% → Calcolo rotto

📝 Note Post-Test
Dopo il test, annota:
Cosa funziona bene:
	∙	[scrivi qui]
Cosa confonde:
	∙	[scrivi qui]
Cosa manca (che NON aggiungeremo ora):
	∙	[scrivi qui]
Decisione finale:
	∙	FREEZE - Moat è presentabile
	∙	FIX NEEDED - [descrivi cosa]

