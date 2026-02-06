"""Multi-agent system for Contract Compliance Guard.

This module implements the adversarial agent architecture:
1. Extractor Agent - Extracts key terms from contracts
2. Advocate Agent - Argues the contract is acceptable
3. Auditor Agent - Identifies risky clauses
4. Resolver Agent - Weighs arguments and makes final decision
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required for demo mode


def has_api_key() -> bool:
    """Check if Anthropic API key is available."""
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def load_demo_results() -> Dict[str, Any]:
    """Load pre-recorded demo results."""
    demo_path = Path(__file__).parent.parent / "data" / "demo_results.json"
    with open(demo_path, "r") as f:
        return json.load(f)


def run_demo_analysis(contract_id: str) -> Dict[str, Any]:
    """Run analysis using pre-recorded demo results."""
    demo_results = load_demo_results()
    
    if contract_id not in demo_results:
        raise ValueError(f"Contract {contract_id} not found in demo results")
    
    return demo_results[contract_id]


def run_live_analysis(contract_id: str) -> Dict[str, Any]:
    """Run live analysis using AI agents.
    
    This would use LangGraph and Claude to actually analyze the contract.
    For now, falls back to demo mode if not implemented.
    """
    # Check for API key
    if not has_api_key():
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    
    try:
        # Attempt to import and use LangGraph
        from langchain_anthropic import ChatAnthropic
        from langgraph.graph import StateGraph, END
        
        from .tools import (
            load_contract,
            extract_contract_terms,
            check_payment_terms,
            check_return_rights,
            check_variable_consideration,
            calculate_risk_score,
        )
        from .prompts import (
            EXTRACTOR_SYSTEM_PROMPT,
            ADVOCATE_SYSTEM_PROMPT,
            AUDITOR_SYSTEM_PROMPT,
            RESOLVER_SYSTEM_PROMPT,
        )
        from .state import ContractAnalysisState
        
        # Initialize Claude
        llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)
        
        # Load contract
        contract_text = load_contract(contract_id)
        
        # Define the graph
        def extraction_node(state: ContractAnalysisState) -> ContractAnalysisState:
            """Extract terms from contract."""
            terms = extract_contract_terms(state["contract_text"])
            state["extracted_terms"] = terms
            state["trace"].append({
                "step": 1,
                "tool": "extract_contract_terms",
                "summary": f"Extracted key terms from contract"
            })
            return state
        
        def policy_check_node(state: ContractAnalysisState) -> ContractAnalysisState:
            """Run policy checks."""
            terms = state["extracted_terms"]
            
            payment_check = check_payment_terms(terms)
            state["trace"].append({
                "step": 2,
                "tool": "check_payment_terms",
                "summary": "✓ Compliant" if payment_check["compliant"] else "⚠ Issues found"
            })
            
            return_check = check_return_rights(terms)
            state["trace"].append({
                "step": 3,
                "tool": "check_return_rights", 
                "summary": "✓ Compliant" if return_check["compliant"] else "⚠ Issues found"
            })
            
            variable_check = check_variable_consideration(terms)
            state["trace"].append({
                "step": 4,
                "tool": "check_variable_consideration",
                "summary": "✓ Compliant" if variable_check["compliant"] else "⚠ Issues found"
            })
            
            state["_payment_check"] = payment_check
            state["_return_check"] = return_check
            state["_variable_check"] = variable_check
            
            return state
        
        def advocate_node(state: ContractAnalysisState) -> ContractAnalysisState:
            """Generate Advocate arguments."""
            # Use LLM to generate advocate arguments
            messages = [
                {"role": "system", "content": ADVOCATE_SYSTEM_PROMPT},
                {"role": "user", "content": f"""
Analyze this contract and provide your best arguments for why it should be approved:

Contract Terms:
{json.dumps(state["extracted_terms"], indent=2)}

Contract Text (relevant sections):
{state["contract_text"][:3000]}

Provide 3-5 strong arguments in favor of accepting this contract.
Format as JSON array with: point, argument, strength (strong/moderate/weak)
"""}
            ]
            
            response = llm.invoke(messages)
            
            # Parse response (simplified - real implementation would be more robust)
            try:
                arguments = json.loads(response.content)
            except json.JSONDecodeError:
                arguments = [{"point": "Analysis", "argument": response.content, "strength": "moderate"}]
            
            state["advocate_arguments"] = arguments
            state["trace"].append({
                "step": 5,
                "tool": "generate_advocate_argument",
                "summary": f"Generated {len(arguments)} arguments"
            })
            
            return state
        
        def auditor_node(state: ContractAnalysisState) -> ContractAnalysisState:
            """Generate Auditor findings."""
            messages = [
                {"role": "system", "content": AUDITOR_SYSTEM_PROMPT},
                {"role": "user", "content": f"""
Analyze this contract for risky clauses and compliance issues:

Contract Terms:
{json.dumps(state["extracted_terms"], indent=2)}

Policy Check Results:
- Payment: {json.dumps(state.get("_payment_check", {}))}
- Returns: {json.dumps(state.get("_return_check", {}))}
- Variable Consideration: {json.dumps(state.get("_variable_check", {}))}

Contract Text:
{state["contract_text"][:4000]}

Identify all risky clauses. For each finding include:
- clause: The problematic clause
- risk_level: high/medium/low
- finding: Your analysis
- asc_606_reference: ASC 606 citation if applicable
- exact_quote: Exact text from contract
- suggested_revision: How to fix it

Format as JSON array.
"""}
            ]
            
            response = llm.invoke(messages)
            
            try:
                findings = json.loads(response.content)
            except json.JSONDecodeError:
                findings = [{"clause": "Analysis", "risk_level": "medium", "finding": response.content}]
            
            state["auditor_findings"] = findings
            state["trace"].append({
                "step": 6,
                "tool": "generate_auditor_findings",
                "summary": f"Found {len(findings)} issues"
            })
            
            return state
        
        def resolver_node(state: ContractAnalysisState) -> ContractAnalysisState:
            """Resolve the debate and make final recommendation."""
            messages = [
                {"role": "system", "content": RESOLVER_SYSTEM_PROMPT},
                {"role": "user", "content": f"""
Make a final decision on this contract:

ADVOCATE ARGUMENTS:
{json.dumps(state["advocate_arguments"], indent=2)}

AUDITOR FINDINGS:
{json.dumps(state["auditor_findings"], indent=2)}

CONTRACT TERMS:
{json.dumps(state["extracted_terms"], indent=2)}

Weigh both sides and provide:
1. risk_score (0-100)
2. confidence (0-100)
3. recommendation (approve/legal_review/reject)
4. reasoning (explain your decision)
5. key_factors (list of 3-5 key factors)

Format as JSON object.
"""}
            ]
            
            response = llm.invoke(messages)
            
            try:
                verdict = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback - calculate from checks
                risk_score = calculate_risk_score(
                    state.get("_payment_check", {}),
                    state.get("_return_check", {}),
                    state.get("_variable_check", {})
                )
                verdict = {
                    "risk_score": risk_score,
                    "confidence": 70,
                    "recommendation": "legal_review" if risk_score > 30 else "approve",
                    "reasoning": response.content,
                    "key_factors": ["See detailed analysis"]
                }
            
            state["resolver_verdict"] = verdict
            state["trace"].append({
                "step": 7,
                "tool": "resolve_debate",
                "summary": f"Verdict: {verdict['recommendation'].upper()} (score {verdict['risk_score']}/100)"
            })
            
            return state
        
        # Build graph
        workflow = StateGraph(ContractAnalysisState)
        
        workflow.add_node("extract", extraction_node)
        workflow.add_node("policy_check", policy_check_node)
        workflow.add_node("advocate", advocate_node)
        workflow.add_node("auditor", auditor_node)
        workflow.add_node("resolver", resolver_node)
        
        workflow.set_entry_point("extract")
        workflow.add_edge("extract", "policy_check")
        workflow.add_edge("policy_check", "advocate")
        workflow.add_edge("policy_check", "auditor")
        workflow.add_edge("advocate", "resolver")
        workflow.add_edge("auditor", "resolver")
        workflow.add_edge("resolver", END)
        
        graph = workflow.compile()
        
        # Run analysis
        initial_state = {
            "contract_id": contract_id,
            "contract_text": contract_text,
            "trace": []
        }
        
        final_state = graph.invoke(initial_state)
        
        return final_state
        
    except ImportError:
        # LangGraph not available, fall back to demo
        return run_demo_analysis(contract_id)


def run_analysis(contract_id: str, use_demo: bool = False) -> Dict[str, Any]:
    """Run contract analysis, with demo mode fallback.
    
    Args:
        contract_id: The contract identifier
        use_demo: Force demo mode even if API key available
        
    Returns:
        Analysis results including advocate/auditor arguments and verdict
    """
    if use_demo or not has_api_key():
        return run_demo_analysis(contract_id)
    
    try:
        return run_live_analysis(contract_id)
    except Exception as e:
        # Fall back to demo on any error
        print(f"Live analysis failed: {e}, falling back to demo mode")
        return run_demo_analysis(contract_id)
