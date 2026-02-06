"""State schema for Contract Compliance Guard multi-agent system."""

from typing import TypedDict, List, Dict, Optional, Literal
from dataclasses import dataclass, field


class ExtractedTerms(TypedDict, total=False):
    """Extracted contract terms."""
    parties: Dict[str, str]
    effective_date: str
    term_months: int
    total_value: float
    payment_terms_days: int
    return_period_days: int
    auto_renewal: bool
    annual_escalation_percent: float
    liability_cap: str
    termination_notice_days: int
    milestone_based: bool
    consignment: bool
    mfc_clause: bool
    price_protection: bool


class AdvocateArgument(TypedDict):
    """An argument from the Advocate agent."""
    point: str
    argument: str
    strength: Literal["strong", "moderate", "weak"]


class AuditorFinding(TypedDict):
    """A finding from the Auditor agent."""
    clause: str
    risk_level: Literal["high", "medium", "low"]
    finding: str
    asc_606_reference: Optional[str]
    exact_quote: str
    suggested_revision: Optional[str]


class ResolverVerdict(TypedDict):
    """The Resolver's final verdict."""
    risk_score: int  # 0-100
    confidence: int  # 0-100
    recommendation: Literal["approve", "legal_review", "reject"]
    reasoning: str
    key_factors: List[str]


class TraceStep(TypedDict):
    """A step in the analysis trace."""
    step: int
    tool: str
    summary: str


class ContractAnalysisState(TypedDict, total=False):
    """Complete state for contract analysis."""
    # Input
    contract_id: str
    contract_text: str
    contract_name: str
    
    # Extraction results
    extracted_terms: ExtractedTerms
    
    # Adversarial debate
    advocate_arguments: List[AdvocateArgument]
    auditor_findings: List[AuditorFinding]
    
    # Resolution
    resolver_verdict: ResolverVerdict
    
    # Metadata
    trace: List[TraceStep]
    error: Optional[str]


@dataclass
class AgentMessage:
    """Message between agents."""
    sender: str
    recipient: str
    content: str
    metadata: Dict = field(default_factory=dict)


# Risk level thresholds
RISK_THRESHOLDS = {
    "low": (0, 30),
    "medium": (31, 60),
    "high": (61, 100)
}


def get_risk_level(score: int) -> str:
    """Get risk level label from score."""
    for level, (low, high) in RISK_THRESHOLDS.items():
        if low <= score <= high:
            return level
    return "high"


def get_recommendation_from_score(score: int) -> str:
    """Get recommendation based on risk score."""
    if score <= 30:
        return "approve"
    elif score <= 60:
        return "legal_review"
    else:
        return "reject"
