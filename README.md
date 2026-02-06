# Contract Compliance Guard ⚖️

**Adversarial AI Agents for Contract Risk Analysis**

An enterprise-grade contract review tool that uses competing AI agents to identify risky clauses and ASC 606 revenue recognition issues. The "debate" between Advocate and Auditor agents creates a more thorough analysis than a single-pass review.

![McKinsey Consulting Grade UI](https://img.shields.io/badge/Style-McKinsey%20Consulting%20Grade-051C2C)
![Demo Mode](https://img.shields.io/badge/Demo-No%20API%20Key%20Required-6366F1)
![ASC 606](https://img.shields.io/badge/ASC%20606-Revenue%20Recognition-00A9F4)

---

## 🎯 What It Does

The Contract Compliance Guard analyzes contracts through four specialized AI agents:

1. **Extractor Agent** — Pulls key terms: parties, dates, amounts, payment terms, clauses
2. **Advocate Agent 🟢** — Argues why the contract is acceptable and standard
3. **Auditor Agent 🔴** — Hunts for risky clauses and compliance issues
4. **Resolver Agent** — Weighs both sides and makes a final recommendation

This adversarial pattern ensures comprehensive analysis by forcing examination from multiple perspectives.

---

## 📊 Risk Categories Detected

### ASC 606 Revenue Recognition Risks
- **Extended Payment Terms** (>60 days) — May indicate financing component
- **Unconditional Returns** (>30 days) — Variable consideration concerns
- **Price Protection / MFC Clauses** — Open-ended variable consideration
- **Milestone Payments** — Contingent revenue timing issues
- **Consignment** — Control transfer failures
- **Bill-and-Hold** — Specific criteria requirements

### Commercial Risks
- Unlimited liability exposure
- Unfavorable auto-renewal terms
- Excessive price escalation (>3%)
- One-sided termination rights

---

## 🚀 Quick Start

### Demo Mode (No API Key Required)

```bash
# Clone and enter directory
cd contract-compliance-guard

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app works immediately with **pre-recorded analyses** for 8 sample contracts.

### Live Mode (With API Key)

```bash
# Copy environment template
cp .env.example .env

# Add your Anthropic API key to .env
# ANTHROPIC_API_KEY=your_key_here

# Run the app
streamlit run app.py
```

Click "Switch to Live Mode" in the sidebar to use real AI analysis.

---

## 📁 Sample Contracts

| Contract | Risk Level | Key Issue | Recommendation |
|----------|------------|-----------|----------------|
| Standard SaaS | 🟢 Low (18) | None significant | Approve |
| Extended Payment | 🟡 Medium (52) | Net-120 terms | Legal Review |
| Right of Return | 🔴 High (85) | 90-day unconditional | Reject |
| Milestone Payment | 🟡 Medium (48) | Contingent payments | Legal Review |
| Price Protection | 🔴 High (88) | MFC clause | Reject |
| Auto-Renewal | 🟡 Medium (55) | 5% escalation | Legal Review |
| Consignment | 🔴 High (92) | No control transfer | Reject |
| Clean License | 🟢 Low (12) | Standard terms | Approve |

---

## 🏗️ Architecture

```
Contract Input
    ↓
┌─────────────────────────────────────┐
│         Extractor Agent             │
│   Extracts: parties, terms, clauses │
└─────────────────────────────────────┘
    ↓
┌─────────────────┬─────────────────┐
│  Advocate 🟢    │   Auditor 🔴    │
│  "Contract is   │  "I found these │
│   standard"     │   risk flags"   │
│                 │                 │
│  - Strong args  │  - ASC 606 refs │
│  - Industry std │  - Exact quotes │
│  - Mitigations  │  - Fix suggest. │
└────────┬────────┴────────┬────────┘
         ↓                 ↓
┌─────────────────────────────────────┐
│          Resolver Agent             │
│   Weighs arguments, final verdict   │
│   Risk Score (0-100) + Confidence   │
└─────────────────────────────────────┘
    ↓
Risk Assessment + Recommendation
(Approve / Legal Review / Reject)
```

---

## 📂 Project Structure

```
contract-compliance-guard/
├── app.py                    # Streamlit UI (MBB consulting grade)
├── src/
│   ├── agent.py             # Multi-agent orchestration
│   ├── tools.py             # Analysis tools
│   ├── state.py             # State schema
│   ├── config.py            # Policy thresholds
│   └── prompts.py           # Agent system prompts
├── data/
│   ├── contracts/           # 8 sample contracts
│   │   ├── standard_saas.txt
│   │   ├── extended_payment.txt
│   │   ├── right_of_return.txt
│   │   ├── milestone_payment.txt
│   │   ├── price_protection.txt
│   │   ├── auto_renewal.txt
│   │   ├── consignment.txt
│   │   └── clean_license.txt
│   ├── company_policy.json  # Risk thresholds
│   └── demo_results.json    # Pre-recorded analyses
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🎨 Design Philosophy

### McKinsey Consulting Grade
- **Pyramid Principle**: Executive summary first, details on demand
- **Navy palette**: #051C2C (navy), #00A9F4 (electric blue), white
- **Serif headers**: Professional, authoritative typography
- **Status pills**: Visual risk indicators, not raw text
- **Adversarial debate view**: Two-column Advocate vs Auditor

### User Experience
- Works immediately without API key (demo mode)
- Live mode available with Anthropic API key
- One-click analysis with detailed trace
- Expandable sections for deep-dive

---

## 📋 Policy Configuration

Edit `data/company_policy.json` to customize risk thresholds:

```json
{
  "payment_terms_max_days": 60,
  "return_period_max_days": 30,
  "auto_escalation_max_percent": 3,
  "requires_legal_review": [
    "unlimited_liability",
    "indemnification",
    "most_favored_customer"
  ]
}
```

---

## 🔬 Technology Stack

- **Frontend**: Streamlit with custom CSS
- **AI Agents**: LangChain + LangGraph (live mode)
- **LLM**: Claude claude-sonnet-4-20250514 (Anthropic)
- **Design**: McKinsey consulting palette

---

## 📄 License

MIT License - Copyright (c) 2026 Atlas

---

## 🙏 Acknowledgments

- ASC 606 guidance from FASB
- MBB consulting design patterns
- Adversarial AI research

---

*Built with ❤️ for Finance & Legal teams who review contracts at scale.*
