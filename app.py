"""Contract Compliance Guard - Streamlit UI with Adversarial Debate View.

A consulting-grade contract review tool using adversarial AI agents.
McKinsey design palette with executive-first presentation.
"""

import streamlit as st
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import os

from src.agent import run_analysis, has_api_key
from src.config import CONTRACT_DISPLAY_NAMES, CONTRACT_FILES

# Load environment variables
load_dotenv()

# Page config - MUST BE FIRST
st.set_page_config(
    page_title="Contract Compliance Guard",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CONSULTING-GRADE CSS (McKinsey Style)
# ============================================================================
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Inter:wght@400;500;600&display=swap');
    
    /* Serif Headers - McKinsey Style */
    h1, h2, h3 { 
        font-family: 'Libre Baskerville', Georgia, serif !important; 
        color: #051C2C !important;
        letter-spacing: -0.02em;
    }
    
    /* Body text */
    .stMarkdown, p, span {
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Clean Metric Cards with Navy accent */
    div[data-testid="metric-container"] {
        background-color: #F8F9FA;
        border-left: 4px solid #051C2C;
        padding: 15px 20px;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    /* Confidentiality Banner */
    .confidential-banner {
        position: fixed;
        top: 0;
        right: 0;
        background: #051C2C;
        color: white;
        padding: 4px 16px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        z-index: 9999;
        border-bottom-left-radius: 4px;
    }
    
    /* Executive Summary Container */
    .executive-summary {
        background: linear-gradient(135deg, #051C2C 0%, #0A2F4E 100%);
        color: white;
        padding: 2rem 2.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
    }
    
    .executive-summary h2 {
        color: white !important;
        margin-bottom: 1.5rem;
        font-size: 1.4rem;
    }
    
    .exec-metric {
        text-align: center;
        padding: 1rem;
    }
    
    .exec-metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #00A9F4;
        font-family: 'Inter', sans-serif;
    }
    
    .exec-metric-value.high-risk { color: #EF4444; }
    .exec-metric-value.medium-risk { color: #F59E0B; }
    .exec-metric-value.low-risk { color: #10B981; }
    
    .exec-metric-label {
        font-size: 0.85rem;
        color: rgba(255,255,255,0.8);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.25rem;
    }
    
    .time-comparison {
        background: rgba(0, 169, 244, 0.15);
        border: 1px solid rgba(0, 169, 244, 0.3);
        border-radius: 6px;
        padding: 1rem 1.5rem;
        text-align: center;
        margin-top: 1rem;
    }
    
    .time-comparison .before {
        color: rgba(255,255,255,0.6);
        text-decoration: line-through;
    }
    
    .time-comparison .arrow {
        color: #00A9F4;
        font-size: 1.2rem;
        margin: 0 0.5rem;
    }
    
    .time-comparison .after {
        color: #00A9F4;
        font-weight: 600;
    }
    
    /* Status Pill Badges */
    .status-pill {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    
    .status-approve {
        background-color: #ECFDF5;
        color: #047857;
        border: 1px solid #6EE7B7;
    }
    
    .status-legal-review {
        background-color: #FEFCE8;
        color: #A16207;
        border: 1px solid #FDE047;
    }
    
    .status-reject {
        background-color: #FFE5E5;
        color: #C53030;
        border: 1px solid #FEB2B2;
    }
    
    /* Risk level badges */
    .risk-high {
        background-color: #FFE5E5;
        color: #C53030;
        border: 1px solid #FEB2B2;
    }
    
    .risk-medium {
        background-color: #FEFCE8;
        color: #A16207;
        border: 1px solid #FDE047;
    }
    
    .risk-low {
        background-color: #ECFDF5;
        color: #047857;
        border: 1px solid #6EE7B7;
    }
    
    /* Adversarial Debate Panels */
    .debate-panel {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(5, 28, 44, 0.06);
        border: 1px solid #E2E8F0;
        height: 100%;
    }
    
    .advocate-panel {
        border-top: 4px solid #10B981;
    }
    
    .auditor-panel {
        border-top: 4px solid #EF4444;
    }
    
    .debate-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #E2E8F0;
    }
    
    .debate-header .emoji {
        font-size: 1.5rem;
    }
    
    .debate-header h3 {
        margin: 0 !important;
        font-size: 1.1rem !important;
    }
    
    /* Argument/Finding Cards */
    .argument-card {
        background: #F0FDF4;
        border-left: 3px solid #10B981;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 6px 6px 0;
    }
    
    .finding-card {
        background: #FEF2F2;
        border-left: 3px solid #EF4444;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 6px 6px 0;
    }
    
    .finding-card.medium {
        background: #FFFBEB;
        border-left-color: #F59E0B;
    }
    
    .finding-card.low {
        background: #F0F9FF;
        border-left-color: #0EA5E9;
    }
    
    .strength-badge {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 10px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .strength-strong { background: #D1FAE5; color: #065F46; }
    .strength-moderate { background: #FEF3C7; color: #92400E; }
    .strength-weak { background: #FEE2E2; color: #991B1B; }
    
    /* Verdict Box */
    .verdict-box {
        background: white;
        border: 2px solid #051C2C;
        border-radius: 8px;
        padding: 1.5rem 2rem;
        margin-top: 1.5rem;
    }
    
    .verdict-approve { border-color: #10B981; background: #F0FDF4; }
    .verdict-legal-review { border-color: #F59E0B; background: #FFFBEB; }
    .verdict-reject { border-color: #EF4444; background: #FEF2F2; }
    
    /* Risk Score Dial */
    .risk-dial {
        width: 120px;
        height: 60px;
        background: conic-gradient(from 180deg, #10B981 0deg 60deg, #F59E0B 60deg 120deg, #EF4444 120deg 180deg);
        border-radius: 60px 60px 0 0;
        position: relative;
        margin: 0 auto;
    }
    
    /* Investigation Log */
    .investigation-step {
        background: #FAFBFC;
        border-left: 3px solid #00A9F4;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.9rem;
    }
    
    .investigation-step .step-ok { color: #059669; font-weight: 600; }
    .investigation-step .step-alert { color: #DC2626; font-weight: 600; }
    .investigation-step .step-info { color: #0284C7; font-weight: 600; }
    
    /* Contract Quote */
    .contract-quote {
        background: #F8FAFC;
        border-left: 3px solid #94A3B8;
        padding: 0.5rem 0.75rem;
        font-family: 'SF Mono', 'Menlo', monospace;
        font-size: 0.8rem;
        color: #475569;
        margin: 0.5rem 0;
        border-radius: 0 4px 4px 0;
    }
    
    /* ASC 606 Reference */
    .asc-reference {
        display: inline-block;
        background: #E0E7FF;
        color: #3730A3;
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #051C2C 0%, #0A2F4E 100%);
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    /* Methodology Badge */
    .methodology-badge {
        background: rgba(0, 169, 244, 0.15);
        border: 1px solid rgba(0, 169, 244, 0.3);
        border-radius: 6px;
        padding: 0.75rem 1rem;
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.9);
    }
    
    /* Demo banner */
    .demo-banner {
        background: linear-gradient(90deg, #6366F1 0%, #8B5CF6 100%);
        color: white;
        padding: 0.6rem 1rem;
        border-radius: 6px;
        margin-bottom: 1.5rem;
        text-align: center;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    /* Main page background */
    .stApp {
        background: linear-gradient(180deg, #F0F4F8 0%, #E8ECF1 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #051C2C 0%, #0A3D62 100%);
        color: white;
        border: none;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        border-radius: 6px;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #0A3D62 0%, #051C2C 100%);
        box-shadow: 0 4px 12px rgba(5, 28, 44, 0.25);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>

<!-- Confidentiality Banner -->
<div class="confidential-banner">CONFIDENTIAL — CLIENT PROPRIETARY DATA</div>
""", unsafe_allow_html=True)


def load_demo_results():
    """Load pre-recorded demo results."""
    demo_path = Path(__file__).parent / "data" / "demo_results.json"
    with open(demo_path, "r") as f:
        return json.load(f)


def get_status_pill(recommendation: str) -> str:
    """Return styled status pill HTML based on recommendation."""
    pills = {
        'approve': '<span class="status-pill status-approve">✅ APPROVE</span>',
        'legal_review': '<span class="status-pill status-legal-review">⚠️ LEGAL REVIEW</span>',
        'reject': '<span class="status-pill status-reject">❌ REJECT</span>'
    }
    return pills.get(recommendation, pills['legal_review'])


def get_risk_pill(risk_level: str) -> str:
    """Return styled risk level pill."""
    pills = {
        'high': '<span class="status-pill risk-high">🔴 HIGH</span>',
        'medium': '<span class="status-pill risk-medium">🟡 MEDIUM</span>',
        'low': '<span class="status-pill risk-low">🟢 LOW</span>'
    }
    return pills.get(risk_level.lower(), pills['medium'])


def render_executive_summary(demo_results: dict):
    """Render the Executive Summary Dashboard."""
    # Calculate aggregate metrics
    total_contracts = len(demo_results)
    high_risk = sum(1 for r in demo_results.values() if r['resolver_verdict']['recommendation'] == 'reject')
    medium_risk = sum(1 for r in demo_results.values() if r['resolver_verdict']['recommendation'] == 'legal_review')
    low_risk = sum(1 for r in demo_results.values() if r['resolver_verdict']['recommendation'] == 'approve')
    total_value = sum(r.get('total_value', 0) for r in demo_results.values())
    
    st.markdown(f"""
    <div class="executive-summary">
        <h2>⚖️ Contract Compliance Guard — Executive Summary</h2>
        <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 1.5rem;">
            <div class="exec-metric">
                <div class="exec-metric-value">{total_contracts}</div>
                <div class="exec-metric-label">Contracts Reviewed</div>
            </div>
            <div class="exec-metric">
                <div class="exec-metric-value high-risk">{high_risk}</div>
                <div class="exec-metric-label">High Risk</div>
            </div>
            <div class="exec-metric">
                <div class="exec-metric-value medium-risk">{medium_risk}</div>
                <div class="exec-metric-label">Medium Risk</div>
            </div>
            <div class="exec-metric">
                <div class="exec-metric-value low-risk">{low_risk}</div>
                <div class="exec-metric-label">Low Risk</div>
            </div>
            <div class="exec-metric">
                <div class="exec-metric-value">${total_value/1000000:.1f}M</div>
                <div class="exec-metric-label">Total Value</div>
            </div>
        </div>
        <div class="time-comparison">
            <span class="before">Manual Review: 45 min</span>
            <span class="arrow">→</span>
            <span class="after">Agent Analysis: 60 sec</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_advocate_panel(arguments: list):
    """Render the Advocate's arguments panel."""
    st.markdown("""
    <div class="debate-panel advocate-panel">
        <div class="debate-header">
            <span class="emoji">🟢</span>
            <h3>Advocate Agent</h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("*\"This contract is acceptable because...\"*")
    
    for arg in arguments:
        strength = arg.get('strength', 'moderate')
        strength_class = f"strength-{strength}"
        
        st.markdown(f"""
        <div class="argument-card">
            <strong>{arg['point']}</strong>
            <span class="strength-badge {strength_class}">{strength}</span>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #374151;">
                {arg['argument']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_auditor_panel(findings: list):
    """Render the Auditor's findings panel."""
    st.markdown("""
    <div class="debate-panel auditor-panel">
        <div class="debate-header">
            <span class="emoji">🔴</span>
            <h3>Auditor Agent</h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("*\"I found these risk factors...\"*")
    
    for finding in findings:
        risk = finding.get('risk_level', 'medium').lower()
        
        st.markdown(f"""
        <div class="finding-card {risk}">
            <strong>{finding['clause']}</strong>
            {get_risk_pill(risk)}
            <p style="margin: 0.5rem 0; font-size: 0.9rem; color: #374151;">
                {finding['finding']}
            </p>
        """, unsafe_allow_html=True)
        
        if finding.get('asc_606_reference'):
            st.markdown(f'<span class="asc-reference">{finding["asc_606_reference"]}</span>', unsafe_allow_html=True)
        
        if finding.get('exact_quote'):
            st.markdown(f'<div class="contract-quote">"{finding["exact_quote"][:150]}..."</div>', unsafe_allow_html=True)
        
        if finding.get('suggested_revision'):
            st.markdown(f'<p style="font-size: 0.8rem; color: #059669; margin: 0.5rem 0 0 0;"><strong>💡 Suggested:</strong> {finding["suggested_revision"]}</p>', unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_verdict(verdict: dict, contract_name: str):
    """Render the Resolver's verdict."""
    recommendation = verdict['recommendation']
    risk_score = verdict['risk_score']
    confidence = verdict['confidence']
    
    verdict_class = f"verdict-{recommendation.replace('_', '-')}"
    
    rec_display = {
        'approve': ('✅', 'APPROVED', 'This contract can proceed.'),
        'legal_review': ('⚠️', 'LEGAL REVIEW REQUIRED', 'Escalate to Legal/Finance for approval.'),
        'reject': ('❌', 'REJECT', 'This contract must be renegotiated.')
    }
    emoji, label, action = rec_display.get(recommendation, rec_display['legal_review'])
    
    st.markdown(f"""
    <div class="verdict-box {verdict_class}">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="margin: 0;">{emoji} {label}</h2>
                <p style="margin: 0.5rem 0 0 0; color: #6B7280;">{action}</p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 2.5rem; font-weight: 700; color: {'#EF4444' if risk_score > 60 else '#F59E0B' if risk_score > 30 else '#10B981'};">
                    {risk_score}
                </div>
                <div style="font-size: 0.8rem; color: #6B7280;">Risk Score</div>
                <div style="font-size: 0.75rem; color: #9CA3AF;">{confidence}% confidence</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Reasoning
    st.markdown("### 🎯 Resolver Reasoning")
    st.markdown(f"> {verdict['reasoning']}")
    
    # Key factors
    st.markdown("### 🔑 Key Factors")
    for factor in verdict.get('key_factors', []):
        st.markdown(f"• {factor}")


def render_investigation_trace(trace: list):
    """Render the agent investigation trace."""
    st.markdown("### 🔍 Analysis Trace")
    
    with st.chat_message("assistant", avatar="⚖️"):
        for step in trace:
            summary = step.get('summary', '')
            
            if '✓' in summary or 'APPROVE' in summary:
                status_class = "step-ok"
            elif '⚠' in summary or '🔴' in summary or 'REJECT' in summary:
                status_class = "step-alert"
            else:
                status_class = "step-info"
            
            st.markdown(f"""
            <div class="investigation-step">
                • <strong>Step {step['step']}:</strong> {step['tool']}
                <span class="{status_class}">[{summary}]</span>
            </div>
            """, unsafe_allow_html=True)


def render_sidebar(demo_results: dict, api_available: bool):
    """Render the polished sidebar."""
    with st.sidebar:
        # Logo/Title
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0 1.5rem 0;">
            <div style="font-size: 2.5rem;">⚖️</div>
            <h2 style="margin: 0.5rem 0 0 0; font-size: 1.3rem;">Contract Compliance Guard</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Methodology badge
        st.markdown("""
        <div class="methodology-badge">
            <strong>Methodology:</strong><br>
            Adversarial AI Agents + ASC 606 Compliance v1.0
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Mode indicator
        if st.session_state.get('demo_mode', True):
            st.markdown("### 🎭 Demo Mode Active")
            if api_available:
                if st.button("🔄 Switch to Live Mode", use_container_width=True):
                    st.session_state['demo_mode'] = False
                    if 'analysis_result' in st.session_state:
                        del st.session_state['analysis_result']
                    st.rerun()
        
        st.divider()
        
        # Contract selector
        st.markdown("### 📄 Select Contract")
        
        contract_options = list(CONTRACT_DISPLAY_NAMES.keys())
        selected_contract = st.selectbox(
            "Choose a contract:",
            options=contract_options,
            format_func=lambda x: CONTRACT_DISPLAY_NAMES.get(x, x)
        )
        
        # Quick risk preview
        if selected_contract in demo_results:
            result = demo_results[selected_contract]
            score = result['resolver_verdict']['risk_score']
            rec = result['resolver_verdict']['recommendation']
            st.markdown(get_status_pill(rec), unsafe_allow_html=True)
        
        st.divider()
        
        # Legend
        st.markdown("### 📊 Risk Legend")
        st.markdown("""
        - 🟢 **Low (0-30)**: Approve
        - 🟡 **Medium (31-60)**: Legal Review
        - 🔴 **High (61-100)**: Reject
        """)
        
        st.divider()
        
        # Test scenarios
        st.markdown("### 🧪 Test Scenarios")
        st.markdown("""
        - **Standard SaaS**: 🟢 Low risk
        - **Extended Payment**: 🟡 Net 120 terms
        - **Right of Return**: 🔴 90-day returns
        - **Price Protection**: 🔴 MFC clause
        - **Consignment**: 🔴 No control transfer
        """)
        
        st.divider()
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            analyze = st.button("🚀 Analyze", type="primary", use_container_width=True)
        with col2:
            clear = st.button("🗑️ Clear", use_container_width=True)
        
        return selected_contract, analyze, clear


def main():
    """Main Streamlit app."""
    
    # Initialize session state
    if 'demo_mode' not in st.session_state:
        st.session_state['demo_mode'] = True
    if 'last_contract' not in st.session_state:
        st.session_state['last_contract'] = None
    
    # Check API availability
    api_available = has_api_key()
    
    # Load demo results
    try:
        demo_results = load_demo_results()
    except Exception as e:
        st.error(f"Unable to load demo data: {e}")
        st.stop()
    
    # API key check - offer demo mode
    if not api_available and not st.session_state['demo_mode']:
        st.session_state['demo_mode'] = True
    
    # Render sidebar
    selected_contract, analyze_btn, clear_btn = render_sidebar(demo_results, api_available)
    
    # Demo mode banner
    if st.session_state.get('demo_mode', True):
        st.markdown("""
        <div class="demo-banner">
            🎭 <strong>Demo Mode</strong> — Using pre-recorded adversarial agent analyses
        </div>
        """, unsafe_allow_html=True)
    
    # Executive Summary
    render_executive_summary(demo_results)
    
    # Handle clear
    if clear_btn:
        if 'analysis_result' in st.session_state:
            del st.session_state['analysis_result']
        st.rerun()
    
    # Track contract changes
    if selected_contract != st.session_state.get('last_contract'):
        if 'analysis_result' in st.session_state:
            del st.session_state['analysis_result']
        st.session_state['last_contract'] = selected_contract
    
    # Main content
    st.markdown("---")
    
    if selected_contract:
        # Contract header
        contract_name = CONTRACT_DISPLAY_NAMES.get(selected_contract, selected_contract)
        st.markdown(f"## 📄 {contract_name}")
        
        # Handle analysis
        if analyze_btn:
            if 'analysis_result' in st.session_state:
                del st.session_state['analysis_result']
            
            spinner_text = "🎭 Loading demo analysis..." if st.session_state.get('demo_mode', True) else "⚖️ Running adversarial analysis..."
            
            with st.spinner(spinner_text):
                try:
                    time.sleep(0.8)  # Simulate processing
                    result = run_analysis(selected_contract, use_demo=st.session_state.get('demo_mode', True))
                    st.session_state['analysis_result'] = result
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
            
            st.rerun()
        
        # Display results
        if 'analysis_result' in st.session_state:
            result = st.session_state['analysis_result']
            
            # Contract info
            col1, col2, col3, col4 = st.columns(4)
            parties = result.get('parties', {})
            with col1:
                st.metric("Provider", parties.get('provider', 'N/A')[:20])
            with col2:
                st.metric("Customer", parties.get('customer', 'N/A')[:20])
            with col3:
                st.metric("Value", f"${result.get('total_value', 0):,.0f}")
            with col4:
                st.metric("Term", f"{result.get('term_months', 0)} months" if result.get('term_months') else "Perpetual")
            
            st.markdown("---")
            
            # Adversarial Debate View
            st.markdown("## ⚔️ Adversarial Debate")
            
            col_advocate, col_auditor = st.columns(2)
            
            with col_advocate:
                render_advocate_panel(result.get('advocate_arguments', []))
            
            with col_auditor:
                render_auditor_panel(result.get('auditor_findings', []))
            
            st.markdown("---")
            
            # Resolver Verdict
            st.markdown("## 🎯 Resolver Verdict")
            render_verdict(result['resolver_verdict'], contract_name)
            
            # Investigation trace in expander
            with st.expander("📋 View Analysis Trace", expanded=False):
                render_investigation_trace(result.get('trace', []))
        
        else:
            # Placeholder
            st.info("👆 Click **Analyze** to run adversarial contract review")
            
            # Show contract preview
            with st.expander("📄 Contract Preview", expanded=True):
                try:
                    contract_path = Path(__file__).parent / "data" / "contracts" / CONTRACT_FILES[selected_contract]
                    with open(contract_path, "r") as f:
                        contract_text = f.read()
                    st.code(contract_text[:2000] + "\n\n... [truncated]", language="text")
                except Exception:
                    st.warning("Contract preview not available")


if __name__ == "__main__":
    main()
