"""Contract Compliance Guard - Streamlit UI with Adversarial Debate View.

A consulting-grade contract review tool using adversarial AI agents.
Corporate Legal design palette with executive-first presentation.
"""

import streamlit as st
import json
import html
import time
from pathlib import Path
from dotenv import load_dotenv
import os

from src.agent import run_analysis, has_api_key, load_demo_results
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
# CONSULTING-GRADE CSS (McKinsey Style) - Loaded from external file
# ============================================================================
def load_css() -> str:
    """Load CSS from external file."""
    css_path = Path(__file__).parent / "static" / "styles.css"
    if css_path.exists():
        with open(css_path, "r") as f:
            return f.read()
    return ""

# Apply CSS
css_content = load_css()
st.markdown(f"""
<style>
{css_content}
</style>

<!-- Confidentiality Banner -->
<div class="confidential-banner">CONFIDENTIAL — CLIENT PROPRIETARY DATA</div>
""", unsafe_allow_html=True)


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
        
        # Escape LLM/demo content for security
        point_escaped = html.escape(arg.get('point', ''))
        argument_escaped = html.escape(arg.get('argument', ''))
        strength_escaped = html.escape(strength)
        
        st.markdown(f"""
        <div class="argument-card">
            <strong>{point_escaped}</strong>
            <span class="strength-badge {strength_class}">{strength_escaped}</span>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #2D2A26;">
                {argument_escaped}
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
        
        # Escape LLM/demo content for security
        clause_escaped = html.escape(finding.get('clause', ''))
        finding_escaped = html.escape(finding.get('finding', ''))
        
        st.markdown(f"""
        <div class="finding-card {risk}">
            <strong>{clause_escaped}</strong>
            {get_risk_pill(risk)}
            <p style="margin: 0.5rem 0; font-size: 0.9rem; color: #2D2A26;">
                {finding_escaped}
            </p>
        """, unsafe_allow_html=True)
        
        if finding.get('asc_606_reference'):
            asc_ref_escaped = html.escape(finding['asc_606_reference'])
            st.markdown(f'<span class="asc-reference">{asc_ref_escaped}</span>', unsafe_allow_html=True)
        
        if finding.get('exact_quote'):
            quote_escaped = html.escape(finding['exact_quote'][:150])
            st.markdown(f'<div class="contract-quote">"{quote_escaped}..."</div>', unsafe_allow_html=True)
        
        if finding.get('suggested_revision'):
            revision_escaped = html.escape(finding['suggested_revision'])
            st.markdown(f'<p style="font-size: 0.8rem; color: #1B4332; margin: 0.5rem 0 0 0;"><strong>💡 Suggested:</strong> {revision_escaped}</p>', unsafe_allow_html=True)
        
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
                <p style="margin: 0.5rem 0 0 0; color: #5C5752;">{action}</p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 2.5rem; font-weight: 700; font-family: 'Merriweather', Georgia, serif; color: {'#E74C3C' if risk_score > 60 else '#D4A84B' if risk_score > 30 else '#1B4332'};">
                    {risk_score}
                </div>
                <div style="font-size: 0.8rem; color: #5C5752; text-transform: uppercase; letter-spacing: 0.05em;">Risk Score</div>
                <div style="font-size: 0.75rem; color: #8B7355;">{confidence}% confidence</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Reasoning - escape LLM/demo content
    st.markdown("### 🎯 Resolver Reasoning")
    reasoning_escaped = html.escape(verdict.get('reasoning', ''))
    st.markdown(f"> {reasoning_escaped}")
    
    # Key factors - escape LLM/demo content
    st.markdown("### 🔑 Key Factors")
    for factor in verdict.get('key_factors', []):
        factor_escaped = html.escape(factor)
        st.markdown(f"• {factor_escaped}")


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
            
            # Escape demo/LLM content
            tool_escaped = html.escape(step.get('tool', ''))
            summary_escaped = html.escape(summary)
            
            st.markdown(f"""
            <div class="investigation-step">
                • <strong>Step {step['step']}:</strong> {tool_escaped}
                <span class="{status_class}">[{summary_escaped}]</span>
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
