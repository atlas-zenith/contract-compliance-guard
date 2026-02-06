"""Configuration for Contract Compliance Guard."""

import json
from pathlib import Path
from typing import Dict, Any


def load_company_policy() -> Dict[str, Any]:
    """Load company policy configuration.
    
    Raises:
        FileNotFoundError: If policy file doesn't exist
        ValueError: If policy file contains invalid JSON
    """
    policy_path = Path(__file__).parent.parent / "data" / "company_policy.json"
    if not policy_path.exists():
        raise FileNotFoundError(f"Policy file not found: {policy_path}")
    try:
        with open(policy_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid policy JSON: {e}")


# Load policy at module level for easy access
COMPANY_POLICY = load_company_policy()

# Contract analysis thresholds
PAYMENT_TERMS_MAX_DAYS = COMPANY_POLICY.get("payment_terms_max_days", 60)
RETURN_PERIOD_MAX_DAYS = COMPANY_POLICY.get("return_period_max_days", 30)
AUTO_ESCALATION_MAX_PERCENT = COMPANY_POLICY.get("auto_escalation_max_percent", 3)
VARIABLE_CONSIDERATION_THRESHOLD = COMPANY_POLICY.get("variable_consideration_threshold_percent", 10)

# Clauses requiring legal review
REQUIRES_LEGAL_REVIEW = COMPANY_POLICY.get("requires_legal_review", [])

# ASC 606 risk factors
ASC_606_RISK_FACTORS = COMPANY_POLICY.get("asc_606_risk_factors", {})

# Risk score weights
RISK_WEIGHTS = {
    "extended_payment_terms": 15,
    "right_of_return": 25,
    "price_protection": 30,
    "mfc_clause": 30,
    "milestone_payments": 10,
    "consignment": 35,
    "auto_renewal_high_escalation": 12,
    "unlimited_liability": 20,
    "variable_consideration": 15,
}

# Confidence adjustments
CONFIDENCE_FACTORS = {
    "clear_terms": 5,
    "ambiguous_language": -10,
    "multiple_risk_factors": -5,
    "industry_standard": 3,
}

# Demo mode contract mappings
CONTRACT_FILES = {
    "standard_saas": "standard_saas.txt",
    "extended_payment": "extended_payment.txt",
    "right_of_return": "right_of_return.txt",
    "milestone_payment": "milestone_payment.txt",
    "price_protection": "price_protection.txt",
    "auto_renewal": "auto_renewal.txt",
    "consignment": "consignment.txt",
    "clean_license": "clean_license.txt",
}

# Contract display names
CONTRACT_DISPLAY_NAMES = {
    "standard_saas": "Standard SaaS Agreement",
    "extended_payment": "Enterprise Software License (Net 120)",
    "right_of_return": "Distribution Agreement (90-day Returns)",
    "milestone_payment": "Custom Development (Milestone-based)",
    "price_protection": "Strategic Supply (MFC Clause)",
    "auto_renewal": "Managed IT Services (5% Escalation)",
    "consignment": "Consignment Agreement",
    "clean_license": "Software License (Clean)",
}
