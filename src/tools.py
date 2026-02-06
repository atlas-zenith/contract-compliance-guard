"""Tools for Contract Compliance Guard analysis."""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from .config import (
    PAYMENT_TERMS_MAX_DAYS,
    RETURN_PERIOD_MAX_DAYS,
    AUTO_ESCALATION_MAX_PERCENT,
    RISK_WEIGHTS,
    ASC_606_RISK_FACTORS,
)


def load_contract(contract_id: str) -> str:
    """Load contract text from file."""
    from .config import CONTRACT_FILES
    
    if contract_id not in CONTRACT_FILES:
        raise ValueError(f"Unknown contract: {contract_id}")
    
    contract_path = Path(__file__).parent.parent / "data" / "contracts" / CONTRACT_FILES[contract_id]
    
    if not contract_path.exists():
        raise FileNotFoundError(f"Contract file not found: {contract_path}")
    
    with open(contract_path, "r") as f:
        return f.read()


def extract_contract_terms(contract_text: str) -> Dict[str, Any]:
    """Extract key terms from contract text using pattern matching."""
    terms = {}
    
    # Extract parties
    parties_match = re.search(r'PARTIES:.*?(?=\n\d\.|\nEFFECTIVE)', contract_text, re.DOTALL | re.IGNORECASE)
    if parties_match:
        parties_text = parties_match.group(0)
        provider_match = re.search(r'(?:Provider|Licensor|Supplier|Consignor|Manufacturer|Developer):\s*([^"\n]+?)(?:\s*\("|\n)', parties_text)
        customer_match = re.search(r'(?:Customer|Licensee|Distributor|Consignee|Buyer|Client):\s*([^"\n]+?)(?:\s*\("|\n)', parties_text)
        terms['parties'] = {
            'provider': provider_match.group(1).strip() if provider_match else 'Unknown',
            'customer': customer_match.group(1).strip() if customer_match else 'Unknown'
        }
    
    # Extract effective date
    date_match = re.search(r'EFFECTIVE DATE:\s*(\w+ \d+, \d{4}|\d{4}-\d{2}-\d{2})', contract_text, re.IGNORECASE)
    if date_match:
        terms['effective_date'] = date_match.group(1)
    
    # Extract term/duration
    term_match = re.search(r'(?:TERM|Initial term|INITIAL TERM):\s*(\d+)\s*months', contract_text, re.IGNORECASE)
    if term_match:
        terms['term_months'] = int(term_match.group(1))
    elif 'Perpetual' in contract_text:
        terms['term_months'] = 0
        terms['perpetual_license'] = True
    
    # Extract payment terms
    payment_match = re.search(r'Net[\s-]?(\d+)\s*days?', contract_text, re.IGNORECASE)
    if payment_match:
        terms['payment_terms_days'] = int(payment_match.group(1))
    
    # Extract total value
    value_patterns = [
        r'Total[^:]*:\s*\$?([\d,]+(?:\.\d{2})?)',
        r'Annual[^:]*:\s*\$?([\d,]+(?:\.\d{2})?)',
        r'license fee:\s*\$?([\d,]+(?:\.\d{2})?)',
        r'subscription fee:\s*\$?([\d,]+(?:\.\d{2})?)',
    ]
    for pattern in value_patterns:
        match = re.search(pattern, contract_text, re.IGNORECASE)
        if match:
            terms['total_value'] = float(match.group(1).replace(',', ''))
            break
    
    # Check for return rights
    if re.search(r'right\s+(?:of|to)\s+return|unconditional\s+return', contract_text, re.IGNORECASE):
        terms['has_return_rights'] = True
        return_days_match = re.search(r'(\d+)\s*(?:days?|DAYS)\s*(?:of|from)\s*delivery', contract_text, re.IGNORECASE)
        if return_days_match:
            terms['return_period_days'] = int(return_days_match.group(1))
    
    # Check for auto-renewal
    if re.search(r'auto(?:matic(?:ally)?)?[\s-]?renew', contract_text, re.IGNORECASE):
        terms['auto_renewal'] = True
        # Check for escalation
        escalation_match = re.search(r'(?:increase|escalat\w*)\s*(?:by\s*)?(\d+(?:\.\d+)?)\s*(?:percent|%)', contract_text, re.IGNORECASE)
        if escalation_match:
            terms['annual_escalation_percent'] = float(escalation_match.group(1))
    
    # Check for consignment
    if re.search(r'consignment|title\s+retention|retains?\s+(?:full\s+)?(?:legal\s+)?title', contract_text, re.IGNORECASE):
        terms['consignment'] = True
    
    # Check for MFC/price protection
    if re.search(r'most\s+favored\s+customer|MFC|price\s+protection|price\s+match', contract_text, re.IGNORECASE):
        terms['mfc_clause'] = True
        terms['price_protection'] = True
    
    # Check for milestone payments
    if re.search(r'milestone[\s-]?(?:based|payment)|contingent\s+(?:on|upon)', contract_text, re.IGNORECASE):
        terms['milestone_based'] = True
    
    # Check for liability cap
    liability_match = re.search(r'liability[^.]*(?:shall\s+)?not\s+exceed[^.]*(\d+\s+months?\s+(?:of\s+)?fees|fees\s+paid|license\s+fee)', contract_text, re.IGNORECASE)
    if liability_match:
        terms['liability_cap'] = liability_match.group(1)
    elif re.search(r'unlimited\s+liability', contract_text, re.IGNORECASE):
        terms['unlimited_liability'] = True
    
    return terms


def check_payment_terms(terms: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze payment terms against company policy."""
    result = {
        'compliant': True,
        'issues': [],
        'risk_score_contribution': 0
    }
    
    payment_days = terms.get('payment_terms_days', 30)
    
    if payment_days > PAYMENT_TERMS_MAX_DAYS:
        result['compliant'] = False
        excess_days = payment_days - PAYMENT_TERMS_MAX_DAYS
        result['issues'].append({
            'type': 'extended_payment_terms',
            'severity': 'medium' if excess_days <= 30 else 'high',
            'description': f'Net {payment_days} exceeds policy limit of {PAYMENT_TERMS_MAX_DAYS} days',
            'asc_606_reference': ASC_606_RISK_FACTORS.get('extended_payment_terms', {}).get('reference')
        })
        # Calculate risk contribution
        result['risk_score_contribution'] = min(RISK_WEIGHTS['extended_payment_terms'] * (1 + excess_days / 60), 25)
    
    return result


def check_return_rights(terms: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze return/refund clauses against company policy."""
    result = {
        'compliant': True,
        'issues': [],
        'risk_score_contribution': 0
    }
    
    if not terms.get('has_return_rights'):
        return result
    
    return_days = terms.get('return_period_days', 0)
    
    if return_days > RETURN_PERIOD_MAX_DAYS:
        result['compliant'] = False
        result['issues'].append({
            'type': 'extended_return_period',
            'severity': 'high' if return_days > 60 else 'medium',
            'description': f'{return_days}-day return period exceeds policy limit of {RETURN_PERIOD_MAX_DAYS} days',
            'asc_606_reference': ASC_606_RISK_FACTORS.get('right_of_return', {}).get('reference')
        })
        # Higher risk for unconditional returns
        multiplier = 1.5 if return_days > 60 else 1.0
        result['risk_score_contribution'] = RISK_WEIGHTS['right_of_return'] * multiplier
    
    return result


def check_variable_consideration(terms: Dict[str, Any]) -> Dict[str, Any]:
    """Check for variable consideration elements (rebates, MFC, contingencies)."""
    result = {
        'compliant': True,
        'issues': [],
        'risk_score_contribution': 0
    }
    
    # Check for MFC clause
    if terms.get('mfc_clause'):
        result['compliant'] = False
        result['issues'].append({
            'type': 'mfc_clause',
            'severity': 'high',
            'description': 'Most Favored Customer clause creates open-ended variable consideration',
            'asc_606_reference': ASC_606_RISK_FACTORS.get('price_protection', {}).get('reference')
        })
        result['risk_score_contribution'] += RISK_WEIGHTS['mfc_clause']
    
    # Check for milestone payments
    if terms.get('milestone_based'):
        result['issues'].append({
            'type': 'milestone_payments',
            'severity': 'medium',
            'description': 'Milestone-based payments may require constraint on variable consideration',
            'asc_606_reference': ASC_606_RISK_FACTORS.get('milestone_payments', {}).get('reference')
        })
        result['risk_score_contribution'] += RISK_WEIGHTS['milestone_payments']
    
    # Check for consignment
    if terms.get('consignment'):
        result['compliant'] = False
        result['issues'].append({
            'type': 'consignment',
            'severity': 'high',
            'description': 'Consignment arrangement fails transfer of control criteria',
            'asc_606_reference': ASC_606_RISK_FACTORS.get('consignment', {}).get('reference')
        })
        result['risk_score_contribution'] += RISK_WEIGHTS['consignment']
    
    # Check for high escalation
    escalation = terms.get('annual_escalation_percent', 0)
    if escalation > AUTO_ESCALATION_MAX_PERCENT:
        result['issues'].append({
            'type': 'high_escalation',
            'severity': 'medium',
            'description': f'{escalation}% annual escalation exceeds {AUTO_ESCALATION_MAX_PERCENT}% policy threshold',
            'asc_606_reference': None
        })
        result['risk_score_contribution'] += RISK_WEIGHTS['auto_renewal_high_escalation']
    
    return result


def calculate_risk_score(
    payment_check: Dict,
    return_check: Dict,
    variable_check: Dict
) -> int:
    """Calculate overall risk score from individual checks."""
    total_score = (
        payment_check.get('risk_score_contribution', 0) +
        return_check.get('risk_score_contribution', 0) +
        variable_check.get('risk_score_contribution', 0)
    )
    
    # Cap at 100
    return min(int(total_score), 100)


def get_contract_summary(contract_id: str) -> Dict[str, Any]:
    """Get summary info for a contract without full analysis."""
    from .config import CONTRACT_DISPLAY_NAMES
    
    demo_path = Path(__file__).parent.parent / "data" / "demo_results.json"
    with open(demo_path, "r") as f:
        demo_results = json.load(f)
    
    if contract_id in demo_results:
        result = demo_results[contract_id]
        return {
            'id': contract_id,
            'name': CONTRACT_DISPLAY_NAMES.get(contract_id, contract_id),
            'risk_score': result['resolver_verdict']['risk_score'],
            'recommendation': result['resolver_verdict']['recommendation'],
            'total_value': result.get('total_value', 0),
            'parties': result.get('parties', {})
        }
    
    return None
