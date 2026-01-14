"""
M&A Contract Analysis Engine
Comprehensive Detection Framework for Letters of Intent, Term Sheets,
Stock Purchase Agreements, Asset Purchase Agreements, and Merger Agreements

Author: Contract Analysis Platform
Version: 1.0.0
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import re


# =============================================================================
# ENUMS AND BASE CLASSES
# =============================================================================

class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Category(Enum):
    MISSING_PROVISION = "missing_provision"
    VAGUE_LANGUAGE = "vague_language"
    UNFAVORABLE_TERMS = "unfavorable_terms"
    STRUCTURAL_ISSUE = "structural_issue"
    COMPLIANCE_RISK = "compliance_risk"
    FINANCIAL_RISK = "financial_risk"
    TIMELINE_ISSUE = "timeline_issue"
    AMBIGUITY = "ambiguity"
    NON_STANDARD = "non_standard"
    INCOMPLETE_DEFINITION = "incomplete_definition"


class DocumentType(Enum):
    LOI = "letter_of_intent"
    TERM_SHEET = "term_sheet"
    STOCK_PURCHASE = "stock_purchase_agreement"
    ASSET_PURCHASE = "asset_purchase_agreement"
    MERGER_AGREEMENT = "merger_agreement"
    UNKNOWN = "unknown"


class PartyRole(Enum):
    BUYER = "buyer"
    SELLER = "seller"
    NEUTRAL = "neutral"


@dataclass
class DetectionPattern:
    """Defines a single detection pattern for a provision"""
    name: str
    description: str
    severity: Severity
    category: Category
    
    # Detection patterns
    presence_patterns: list = field(default_factory=list)  # Patterns that indicate presence
    absence_is_flag: bool = False  # If True, flag when NOT found
    vague_patterns: list = field(default_factory=list)  # Patterns indicating vagueness
    problematic_patterns: list = field(default_factory=list)  # Red flag patterns
    
    # Context
    required_in: list = field(default_factory=list)  # Document types where required
    recommended_in: list = field(default_factory=list)  # Document types where recommended
    
    # Scoring
    base_risk_score: int = 5
    
    # Recommendations
    recommendation: str = ""
    buyer_perspective: str = ""
    seller_perspective: str = ""
    
    # Related provisions
    related_provisions: list = field(default_factory=list)
    
    # Sub-checks (nested requirements)
    sub_checks: list = field(default_factory=list)


@dataclass
class Flag:
    """Represents a detected issue"""
    provision_name: str
    severity: Severity
    category: Category
    risk_score: int
    description: str
    recommendation: str
    contract_context: str
    location: Optional[tuple] = None  # (start, end) positions
    sub_flags: list = field(default_factory=list)


# =============================================================================
# COMPREHENSIVE M&A PROVISION DEFINITIONS
# =============================================================================

class MAAProvisionLibrary:
    """
    Complete library of M&A provisions to check.
    Organized by category with full detection patterns.
    """
    
    @staticmethod
    def get_all_provisions() -> dict:
        """Returns all provision checks organized by category"""
        
        return {
            # =================================================================
            # SECTION 1: STRUCTURAL & DEFINITIONAL
            # =================================================================
            "structural": {
                
                "binding_nonbinding_designation": DetectionPattern(
                    name="Binding/Non-Binding Designation",
                    description="LOIs and term sheets must clearly specify which provisions are legally binding and which are non-binding expressions of intent.",
                    severity=Severity.CRITICAL,
                    category=Category.STRUCTURAL_ISSUE,
                    presence_patterns=[
                        r"(?i)(non-?binding|not\s+binding|no\s+binding|legally\s+binding)",
                        r"(?i)(binding\s+provisions?|binding\s+obligations?)",
                        r"(?i)(except\s+for.*(?:confidentiality|exclusivity).*binding)",
                        r"(?i)(shall\s+be\s+binding|are\s+binding|is\s+binding)",
                        r"(?i)(binding\s+effect|legal\s+effect)",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.LOI, DocumentType.TERM_SHEET],
                    base_risk_score=9,
                    recommendation="Add explicit section designating which provisions are binding (typically confidentiality, exclusivity, expenses, governing law) and which are non-binding.",
                    buyer_perspective="Without clear designation, buyer may be inadvertently bound to terms intended as negotiable.",
                    seller_perspective="Without clear designation, seller may have limited legal recourse for breaches of intended binding terms.",
                    related_provisions=["confidentiality", "exclusivity", "governing_law"]
                ),
                
                "document_type_identification": DetectionPattern(
                    name="Document Type Identification",
                    description="Document should clearly identify itself as LOI, Term Sheet, Purchase Agreement, etc.",
                    severity=Severity.MEDIUM,
                    category=Category.STRUCTURAL_ISSUE,
                    presence_patterns=[
                        r"(?i)(letter\s+of\s+intent|loi)",
                        r"(?i)(term\s+sheet)",
                        r"(?i)(stock\s+purchase\s+agreement|spa)",
                        r"(?i)(asset\s+purchase\s+agreement|apa)",
                        r"(?i)(merger\s+agreement)",
                        r"(?i)(agreement\s+and\s+plan\s+of\s+merger)",
                        r"(?i)(memorandum\s+of\s+understanding|mou)",
                    ],
                    absence_is_flag=True,
                    base_risk_score=5,
                    recommendation="Ensure document title and introductory paragraph clearly identify the document type.",
                ),
                
                "party_identification": DetectionPattern(
                    name="Party Identification",
                    description="All parties must be clearly identified with full legal names, jurisdiction of organization, and roles.",
                    severity=Severity.CRITICAL,
                    category=Category.STRUCTURAL_ISSUE,
                    presence_patterns=[
                        r"(?i)(buyer|purchaser|acquir[oe]r)",
                        r"(?i)(seller|target|company)",
                        r"(?i)(a\s+\w+\s+(corporation|llc|limited|inc\.|company)\s+(organized|incorporated|formed))",
                        r"(?i)(hereinafter\s+(referred\s+to\s+as\s+)?[\"\']\w+[\"\'])",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.LOI, DocumentType.TERM_SHEET, DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=9,
                    recommendation="Include full legal names, entity types, jurisdictions of organization, and principal places of business for all parties.",
                    sub_checks=[
                        "buyer_legal_name",
                        "seller_legal_name",
                        "entity_type",
                        "jurisdiction_of_organization",
                        "principal_place_of_business"
                    ]
                ),
                
                "transaction_structure": DetectionPattern(
                    name="Transaction Structure",
                    description="The transaction structure (stock purchase, asset purchase, merger, etc.) must be clearly defined.",
                    severity=Severity.CRITICAL,
                    category=Category.STRUCTURAL_ISSUE,
                    presence_patterns=[
                        r"(?i)(purchase.*(?:all|100\s*%|one\s+hundred\s+percent).*(?:stock|shares|equity|membership\s+interests))",
                        r"(?i)(acquire.*assets)",
                        r"(?i)(merger|merg(?:e|ing)\s+with)",
                        r"(?i)(stock\s+purchase|share\s+purchase|equity\s+purchase)",
                        r"(?i)(asset\s+purchase|asset\s+acquisition)",
                        r"(?i)(reverse\s+triangular\s+merger|forward\s+merger)",
                    ],
                    absence_is_flag=True,
                    base_risk_score=9,
                    recommendation="Clearly specify whether this is a stock/equity purchase, asset purchase, forward merger, reverse triangular merger, or other structure.",
                    related_provisions=["tax_treatment", "liability_assumption"]
                ),
                
                "recitals_background": DetectionPattern(
                    name="Recitals/Background Section",
                    description="Agreement should include recitals explaining the context and purpose of the transaction.",
                    severity=Severity.LOW,
                    category=Category.STRUCTURAL_ISSUE,
                    presence_patterns=[
                        r"(?i)(recitals|whereas|background)",
                        r"(?i)(the\s+parties\s+desire|the\s+parties\s+wish)",
                    ],
                    absence_is_flag=True,
                    recommended_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=3,
                    recommendation="Include recitals section to provide context, which aids in contract interpretation.",
                ),
                
                "effective_date": DetectionPattern(
                    name="Effective Date",
                    description="Document must specify when it becomes effective.",
                    severity=Severity.HIGH,
                    category=Category.STRUCTURAL_ISSUE,
                    presence_patterns=[
                        r"(?i)(effective\s+(as\s+of|date))",
                        r"(?i)(dated\s+(as\s+of)?)",
                        r"(?i)(this\s+agreement.*made.*as\s+of)",
                        r"(?i)(entered\s+into\s+(as\s+of|on))",
                    ],
                    absence_is_flag=True,
                    base_risk_score=7,
                    recommendation="Specify the effective date clearly, either as a specific date or tied to execution.",
                ),
                
                "definitions_section": DetectionPattern(
                    name="Definitions Section",
                    description="Complex agreements should have a comprehensive definitions section.",
                    severity=Severity.MEDIUM,
                    category=Category.STRUCTURAL_ISSUE,
                    presence_patterns=[
                        r"(?i)(definitions|defined\s+terms)",
                        r"(?i)(\"[A-Z][^\"]+\"\s+(means|shall\s+mean|has\s+the\s+meaning))",
                        r"(?i)(as\s+defined\s+(herein|below|in\s+section))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    recommended_in=[DocumentType.LOI, DocumentType.TERM_SHEET],
                    base_risk_score=6,
                    recommendation="Include comprehensive definitions section for all capitalized terms.",
                ),
            },
            
            # =================================================================
            # SECTION 2: PURCHASE PRICE & CONSIDERATION
            # =================================================================
            "purchase_price": {
                
                "purchase_price_amount": DetectionPattern(
                    name="Purchase Price Specification",
                    description="The purchase price must be clearly specified or the formula for determining it must be defined.",
                    severity=Severity.CRITICAL,
                    category=Category.FINANCIAL_RISK,
                    presence_patterns=[
                        r"(?i)(purchase\s+price.*\$[\d,]+)",
                        r"(?i)(consideration.*\$[\d,]+)",
                        r"(?i)(aggregate.*(?:purchase\s+price|consideration))",
                        r"(?i)(\$[\d,]+.*(?:million|billion|thousand))",
                        r"(?i)([\d.]+x\s+(?:ebitda|revenue|earnings))",  # Multiple-based pricing
                    ],
                    vague_patterns=[
                        r"(?i)(to\s+be\s+determined|tbd)",
                        r"(?i)(subject\s+to\s+(?:further\s+)?(?:discussion|negotiation|agreement))",
                        r"(?i)(industry\s+standard)",
                        r"(?i)(fair\s+market\s+value)",
                        r"(?i)(mutually\s+agree[d]?)",
                    ],
                    absence_is_flag=True,
                    base_risk_score=9,
                    recommendation="Specify exact purchase price or detailed formula. If using multiples, specify the exact multiple and define the metric (e.g., '5.0x TTM Adjusted EBITDA').",
                    sub_checks=[
                        "price_formula_clarity",
                        "reference_metric_definition",
                        "calculation_methodology"
                    ]
                ),
                
                "form_of_consideration": DetectionPattern(
                    name="Form of Consideration",
                    description="Must specify whether consideration is cash, stock, notes, or combination.",
                    severity=Severity.HIGH,
                    category=Category.FINANCIAL_RISK,
                    presence_patterns=[
                        r"(?i)(cash\s+consideration|paid\s+in\s+cash|cash\s+payment)",
                        r"(?i)(stock\s+consideration|shares\s+of\s+(?:common|preferred))",
                        r"(?i)(promissory\s+note|seller\s+note|deferred\s+payment)",
                        r"(?i)(combination\s+of\s+cash\s+and)",
                        r"(?i)(rollover\s+equity)",
                    ],
                    absence_is_flag=True,
                    base_risk_score=8,
                    recommendation="Clearly specify the form of consideration and breakdown if mixed.",
                    related_provisions=["stock_valuation", "note_terms"]
                ),
                
                "working_capital_adjustment": DetectionPattern(
                    name="Working Capital Adjustment",
                    description="Most M&A deals include working capital adjustments to the purchase price.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(working\s+capital\s+(?:adjustment|target|peg|true-?up))",
                        r"(?i)(net\s+working\s+capital)",
                        r"(?i)(current\s+assets.*current\s+liabilities)",
                        r"(?i)(nwc\s+target)",
                        r"(?i)(closing\s+(?:date\s+)?working\s+capital)",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    recommended_in=[DocumentType.LOI, DocumentType.TERM_SHEET],
                    base_risk_score=7,
                    recommendation="Include working capital adjustment mechanism with clearly defined target, calculation methodology, collar/threshold, and dispute resolution process.",
                    sub_checks=[
                        "nwc_target_amount",
                        "nwc_calculation_methodology",
                        "nwc_collar_threshold",
                        "nwc_dispute_resolution",
                        "nwc_true_up_timing"
                    ]
                ),
                
                "net_debt_adjustment": DetectionPattern(
                    name="Net Debt Adjustment",
                    description="Purchase price should be adjusted for debt and cash at closing.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(net\s+debt|debt-?free|cash-?free)",
                        r"(?i)(indebtedness.*(?:adjustment|deducted|reduced))",
                        r"(?i)(closing\s+(?:date\s+)?(?:debt|indebtedness|cash))",
                        r"(?i)(enterprise\s+value.*equity\s+value)",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Define net debt clearly (what obligations are included) and specify adjustment mechanism.",
                    sub_checks=[
                        "debt_definition",
                        "debt_like_items",
                        "cash_definition",
                        "trapped_cash_treatment"
                    ]
                ),
                
                "transaction_expenses_adjustment": DetectionPattern(
                    name="Transaction Expenses Adjustment",
                    description="Specify treatment of seller's transaction expenses (legal, accounting, investment banking fees).",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(transaction\s+expenses?|seller.*expenses?|company.*expenses?)",
                        r"(?i)(unpaid.*(?:fees|expenses).*closing)",
                        r"(?i)(advisor[y]?\s+fees|investment\s+bank(?:ing|er)\s+fees)",
                    ],
                    absence_is_flag=True,
                    base_risk_score=6,
                    recommendation="Specify whether seller transaction expenses are deducted from purchase price or paid separately, with clear definition of included expenses.",
                ),
                
                "earnout_provisions": DetectionPattern(
                    name="Earnout Provisions",
                    description="If purchase price includes earnouts, detailed terms must be specified.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(earn-?out|contingent\s+(?:consideration|payment)|performance\s+(?:payment|bonus))",
                        r"(?i)(additional\s+consideration.*(?:based\s+on|contingent|if))",
                        r"(?i)(milestone\s+payment)",
                    ],
                    # Not absence_is_flag because earnouts aren't always present
                    problematic_patterns=[
                        r"(?i)(sole\s+discretion)",  # Too much discretion for buyer
                        r"(?i)(reasonable\s+efforts)",  # Vague effort standard
                    ],
                    base_risk_score=8,
                    recommendation="If earnouts present, specify: metrics (revenue, EBITDA, etc.), measurement periods, targets, calculation methodology, acceleration triggers, dispute resolution, and buyer's operational covenants.",
                    sub_checks=[
                        "earnout_metric_definition",
                        "earnout_measurement_period",
                        "earnout_targets",
                        "earnout_calculation",
                        "earnout_acceleration",
                        "earnout_dispute_mechanism",
                        "earnout_operational_covenants",
                        "earnout_accounting_principles"
                    ]
                ),
                
                "escrow_holdback": DetectionPattern(
                    name="Escrow/Holdback Provisions",
                    description="Standard M&A deals include escrow or holdback for indemnification claims.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(escrow|holdback|hold-?back|retained\s+amount)",
                        r"(?i)(escrow\s+agent|escrow\s+agreement)",
                        r"(?i)(indemnification\s+escrow|indemnity\s+escrow)",
                        r"(?i)((?:\d+|ten|fifteen|twenty)\s*%.*(?:escrow|holdback))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    recommended_in=[DocumentType.LOI, DocumentType.TERM_SHEET],
                    base_risk_score=7,
                    recommendation="Include escrow/holdback provisions (typically 10-15% of purchase price) with clear terms on amount, duration, release conditions, and escrow agent.",
                    sub_checks=[
                        "escrow_amount",
                        "escrow_duration",
                        "escrow_release_conditions",
                        "escrow_agent_identity",
                        "escrow_disputes"
                    ]
                ),
                
                "purchase_price_allocation": DetectionPattern(
                    name="Purchase Price Allocation",
                    description="For asset deals and stock deals with 338(h)(10) elections, purchase price allocation is critical for tax purposes.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(purchase\s+price\s+allocation|allocation.*purchase\s+price)",
                        r"(?i)(section\s+1060|irs\s+form\s+8594)",
                        r"(?i)(338\s*\(?h?\)?\s*\(?\s*10\)?)",
                        r"(?i)(allocat(?:e|ion).*(?:assets|goodwill|intangible))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.ASSET_PURCHASE],
                    recommended_in=[DocumentType.STOCK_PURCHASE],
                    base_risk_score=6,
                    recommendation="Include purchase price allocation methodology, timeline for agreement, and dispute resolution. Reference IRS Form 8594/Section 1060 for asset deals.",
                ),
                
                "stock_consideration_terms": DetectionPattern(
                    name="Stock Consideration Terms",
                    description="If consideration includes stock, detailed terms must be specified.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(stock\s+consideration|share\s+consideration|equity\s+consideration)",
                        r"(?i)(shares\s+of\s+(?:common|preferred)\s+stock)",
                        r"(?i)(exchange\s+ratio)",
                        r"(?i)(fixed\s+(?:value|number)\s+of\s+shares)",
                    ],
                    base_risk_score=8,
                    recommendation="Specify: number of shares or exchange ratio, valuation mechanism, registration rights, lock-up periods, price protection/collars, and treatment of fractional shares.",
                    sub_checks=[
                        "share_count_or_ratio",
                        "stock_valuation_methodology",
                        "registration_rights",
                        "lock_up_provisions",
                        "price_collars",
                        "fractional_share_treatment"
                    ]
                ),
                
                "seller_note_terms": DetectionPattern(
                    name="Seller Note Terms",
                    description="If consideration includes seller financing, note terms must be specified.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(seller\s+note|promissory\s+note|seller\s+financ)",
                        r"(?i)(deferred\s+(?:purchase\s+price|payment|consideration))",
                        r"(?i)(subordinated\s+(?:note|debt))",
                    ],
                    base_risk_score=8,
                    recommendation="Specify: principal amount, interest rate, payment schedule, maturity, security/subordination, prepayment rights, default provisions, and acceleration triggers.",
                    sub_checks=[
                        "note_principal",
                        "note_interest_rate",
                        "note_payment_schedule",
                        "note_maturity",
                        "note_security",
                        "note_subordination",
                        "note_prepayment",
                        "note_default_triggers"
                    ]
                ),
            },
            
            # =================================================================
            # SECTION 3: DUE DILIGENCE
            # =================================================================
            "due_diligence": {
                
                "due_diligence_scope": DetectionPattern(
                    name="Due Diligence Scope",
                    description="The scope and categories of due diligence must be comprehensive.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(due\s+diligence|diligence\s+review|diligence\s+investigation)",
                        r"(?i)(access\s+to.*(?:books|records|documents|information))",
                        r"(?i)(diligence\s+(?:materials?|documents?|items?))",
                    ],
                    vague_patterns=[
                        r"(?i)(reasonable\s+access)",
                        r"(?i)(customary\s+due\s+diligence)",
                        r"(?i)(standard\s+diligence)",
                    ],
                    absence_is_flag=True,
                    base_risk_score=8,
                    recommendation="Specify comprehensive due diligence scope covering: financials, tax, legal, IP, environmental, HR, IT, commercial, regulatory, insurance, and real estate.",
                    sub_checks=[
                        "dd_financial",
                        "dd_tax",
                        "dd_legal",
                        "dd_ip",
                        "dd_environmental",
                        "dd_hr_employment",
                        "dd_it_systems",
                        "dd_commercial",
                        "dd_regulatory",
                        "dd_insurance",
                        "dd_real_estate"
                    ]
                ),
                
                "due_diligence_period": DetectionPattern(
                    name="Due Diligence Period",
                    description="A specific time period for due diligence should be defined.",
                    severity=Severity.HIGH,
                    category=Category.TIMELINE_ISSUE,
                    presence_patterns=[
                        r"(?i)(due\s+diligence\s+period)",
                        r"(?i)(diligence.*(?:days?|weeks?|period|until))",
                        r"(?i)((\d+)\s*(?:calendar|business|working)?\s*days?.*(?:diligence|investigation))",
                        r"(?i)(access.*through|access.*until)",
                    ],
                    absence_is_flag=True,
                    base_risk_score=7,
                    recommendation="Specify due diligence period with clear start date, end date, and any extension mechanisms.",
                ),
                
                "financial_statements_access": DetectionPattern(
                    name="Financial Statements Access",
                    description="Access to financial statements and records.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(financial\s+statements?|audited\s+financials?|unaudited\s+financials?)",
                        r"(?i)(balance\s+sheets?|income\s+statements?|cash\s+flow)",
                        r"(?i)(management\s+accounts|monthly\s+financials?)",
                        r"(?i)((?:three|3|five|5)\s+years?.*financials?)",
                    ],
                    vague_patterns=[
                        r"(?i)(relevant\s+financial|appropriate\s+financial)",
                    ],
                    absence_is_flag=True,
                    base_risk_score=7,
                    recommendation="Specify: years of audited/unaudited financials, interim statements, management accounts, and format requirements.",
                    sub_checks=[
                        "audited_financial_years",
                        "unaudited_interim_statements",
                        "management_accounts",
                        "budget_projections",
                        "audit_workpapers"
                    ]
                ),
                
                "facility_access": DetectionPattern(
                    name="Facility Access",
                    description="Access to physical facilities and operations.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(facilit(?:y|ies)\s+(?:access|visit|inspection|tour))",
                        r"(?i)(site\s+visits?|on-?site\s+(?:access|inspection))",
                        r"(?i)(physical\s+inspection)",
                        r"(?i)(access\s+to.*(?:premises|locations?|offices?|plants?))",
                    ],
                    absence_is_flag=True,
                    recommended_in=[DocumentType.LOI, DocumentType.TERM_SHEET],
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE],
                    base_risk_score=5,
                    recommendation="Include right to visit and inspect all material facilities, with reasonable notice requirements.",
                ),
                
                "personnel_access": DetectionPattern(
                    name="Management/Personnel Access",
                    description="Access to interview key personnel and management.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(access\s+to.*(?:management|personnel|employees|officers|key\s+people))",
                        r"(?i)(interview.*(?:management|employees|personnel))",
                        r"(?i)(management\s+(?:meetings?|presentations?|discussions?))",
                    ],
                    absence_is_flag=True,
                    base_risk_score=5,
                    recommendation="Include right to interview management and key employees, subject to reasonable coordination with seller.",
                ),
                
                "customer_vendor_access": DetectionPattern(
                    name="Customer/Vendor Access",
                    description="Access to contact customers, vendors, and business partners.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)((?:customer|vendor|supplier|client)\s+(?:access|contacts?|references?|calls?|meetings?))",
                        r"(?i)(contact.*(?:customers?|vendors?|suppliers?|clients?))",
                        r"(?i)(customer\s+diligence|commercial\s+diligence)",
                    ],
                    base_risk_score=5,
                    recommendation="Specify whether buyer can contact customers/vendors directly or only through seller-arranged calls, and any consent requirements.",
                ),
                
                "data_room_access": DetectionPattern(
                    name="Data Room Access",
                    description="Access to virtual or physical data room.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(data\s+room|virtual\s+data\s+room|vdr)",
                        r"(?i)(document\s+repository)",
                        r"(?i)(diligence\s+portal)",
                    ],
                    absence_is_flag=True,
                    recommended_in=[DocumentType.LOI, DocumentType.TERM_SHEET],
                    base_risk_score=4,
                    recommendation="Specify data room access terms, including timing, user permissions, and document production timeline.",
                ),
                
                "quality_of_earnings": DetectionPattern(
                    name="Quality of Earnings Report",
                    description="Right to conduct or receive quality of earnings analysis.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(quality\s+of\s+earnings|q\s*of\s*e|qoe)",
                        r"(?i)(earnings\s+(?:quality|analysis|report))",
                        r"(?i)(financial\s+diligence\s+report)",
                    ],
                    absence_is_flag=True,
                    recommended_in=[DocumentType.LOI, DocumentType.TERM_SHEET],
                    base_risk_score=4,
                    recommendation="Include right to conduct quality of earnings analysis with access to underlying data and personnel.",
                ),
                
                "environmental_diligence": DetectionPattern(
                    name="Environmental Due Diligence",
                    description="Environmental assessments and Phase I/II reports.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(environmental\s+(?:diligence|assessment|review|audit|report))",
                        r"(?i)(phase\s+(?:i|1|ii|2)\s+(?:environmental|assessment|report))",
                        r"(?i)(environmental\s+site\s+assessment|esa)",
                        r"(?i)(hazardous\s+(?:materials?|substances?|waste))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE],
                    base_risk_score=5,
                    recommendation="Include right to conduct Phase I (and if needed Phase II) environmental assessments.",
                ),
                
                "it_systems_diligence": DetectionPattern(
                    name="IT/Systems Due Diligence",
                    description="Review of IT systems, cybersecurity, and data practices.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(it\s+(?:diligence|systems?|infrastructure|review))",
                        r"(?i)(cybersecurity|cyber\s+security|information\s+security)",
                        r"(?i)(technology\s+(?:systems?|infrastructure|review|assessment))",
                        r"(?i)(data\s+(?:privacy|protection|security))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE],
                    base_risk_score=5,
                    recommendation="Include IT systems review covering infrastructure, security, data privacy compliance, and technical debt.",
                ),
            },
            
            # =================================================================
            # SECTION 4: REPRESENTATIONS & WARRANTIES
            # =================================================================
            "representations_warranties": {
                
                "reps_warranties_general": DetectionPattern(
                    name="Representations and Warranties Section",
                    description="Definitive agreements must contain comprehensive representations and warranties.",
                    severity=Severity.CRITICAL,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(representations?\s+and\s+warranties?)",
                        r"(?i)((?:seller|company|target)\s+represents?\s+and\s+warrants?)",
                        r"(?i)((?:buyer|purchaser)\s+represents?\s+and\s+warrants?)",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=10,
                    recommendation="Include comprehensive representations and warranties covering all material aspects of the target business.",
                ),
                
                "organization_authority_rep": DetectionPattern(
                    name="Organization and Authority Representation",
                    description="Representation that parties are validly organized and authorized to enter the transaction.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(duly\s+(?:organized|incorporated|formed))",
                        r"(?i)(validly\s+existing)",
                        r"(?i)(good\s+standing)",
                        r"(?i)((?:corporate|company)\s+(?:power|authority))",
                        r"(?i)(duly\s+authorized)",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=8,
                    recommendation="Include standard organization, valid existence, good standing, and authority representations.",
                ),
                
                "capitalization_rep": DetectionPattern(
                    name="Capitalization Representation",
                    description="Representation regarding equity ownership, outstanding securities, and capital structure.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(capitalization)",
                        r"(?i)(authorized.*(?:shares?|stock|capital))",
                        r"(?i)(issued\s+and\s+outstanding)",
                        r"(?i)(no\s+(?:other|additional)\s+(?:equity|shares?|securities))",
                        r"(?i)((?:options?|warrants?|convertible).*(?:outstanding|issued))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=8,
                    recommendation="Include detailed capitalization representation covering all classes of equity, options, warrants, and convertible securities.",
                ),
                
                "financial_statements_rep": DetectionPattern(
                    name="Financial Statements Representation",
                    description="Representation that financial statements are accurate and prepared in accordance with GAAP.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(financial\s+statements?\s+(?:are|have\s+been|were).*(?:prepared|accurate|true|correct))",
                        r"(?i)(gaap|generally\s+accepted\s+accounting\s+principles)",
                        r"(?i)(fairly\s+present.*(?:financial|results|condition))",
                        r"(?i)(present\s+fairly.*(?:financial\s+position|results\s+of\s+operations))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=8,
                    recommendation="Include representation that financial statements are GAAP compliant and fairly present the company's financial condition.",
                ),
                
                "no_undisclosed_liabilities_rep": DetectionPattern(
                    name="No Undisclosed Liabilities Representation",
                    description="Representation that there are no material undisclosed liabilities.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(no\s+(?:undisclosed|other|additional|material)\s+liabilit(?:y|ies))",
                        r"(?i)(liabilities.*(?:other\s+than|except).*(?:financial\s+statements|disclosed))",
                        r"(?i)(absence\s+of.*liabilities)",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=8,
                    recommendation="Include representation regarding absence of undisclosed liabilities, with appropriate carve-outs for liabilities in the ordinary course.",
                ),
                
                "litigation_rep": DetectionPattern(
                    name="Litigation Representation",
                    description="Representation regarding pending or threatened litigation.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(litigation|legal\s+proceedings?|lawsuits?|claims?)",
                        r"(?i)(pending\s+or\s+threatened)",
                        r"(?i)(no\s+(?:material\s+)?(?:litigation|proceedings?|actions?|suits?))",
                        r"(?i)((?:legal|judicial|administrative)\s+(?:actions?|proceedings?))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Include representation covering pending and threatened litigation, claims, investigations, and proceedings.",
                ),
                
                "compliance_with_laws_rep": DetectionPattern(
                    name="Compliance with Laws Representation",
                    description="Representation regarding compliance with applicable laws and regulations.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(compliance\s+with\s+(?:applicable\s+)?laws?)",
                        r"(?i)((?:in\s+)?compliance\s+(?:in\s+all\s+material\s+respects\s+)?with.*(?:laws?|regulations?|statutes?))",
                        r"(?i)(legal\s+compliance)",
                        r"(?i)((?:not\s+in\s+)?violation\s+of\s+(?:any\s+)?(?:laws?|regulations?))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Include representation regarding compliance with all applicable laws, regulations, and governmental orders.",
                ),
                
                "material_contracts_rep": DetectionPattern(
                    name="Material Contracts Representation",
                    description="Representation regarding material contracts and their status.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(material\s+contracts?)",
                        r"(?i)(contracts?.*(?:schedule|exhibit|disclosure))",
                        r"(?i)(no\s+(?:breach|default|violation).*(?:contracts?|agreements?))",
                        r"(?i)((?:in\s+)?full\s+force\s+and\s+effect)",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Include representation listing all material contracts with representation that they are valid, binding, and not in breach.",
                ),
                
                "intellectual_property_rep": DetectionPattern(
                    name="Intellectual Property Representation",
                    description="Representation regarding ownership and protection of intellectual property.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(intellectual\s+property|ip\s+(?:rights?|assets?))",
                        r"(?i)(patents?|trademarks?|copyrights?|trade\s+secrets?)",
                        r"(?i)(proprietary\s+(?:rights?|technology|information))",
                        r"(?i)((?:owns?|ownership|title).*(?:ip|intellectual\s+property))",
                        r"(?i)(no\s+(?:infringement|misappropriation))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Include comprehensive IP representation covering ownership, registrations, licenses, infringement, and employee/contractor IP assignments.",
                    sub_checks=[
                        "ip_ownership",
                        "ip_registrations",
                        "ip_licenses_in",
                        "ip_licenses_out",
                        "ip_infringement",
                        "ip_assignments"
                    ]
                ),
                
                "employee_matters_rep": DetectionPattern(
                    name="Employee Matters Representation",
                    description="Representation regarding employees, employment agreements, and labor matters.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(employee\s+(?:matters?|relations?|list|census))",
                        r"(?i)(employment\s+(?:agreements?|contracts?))",
                        r"(?i)(labor\s+(?:matters?|relations?|disputes?|unions?))",
                        r"(?i)((?:compensation|salary|benefits?|bonus).*(?:employees?|personnel))",
                        r"(?i)(collective\s+bargaining)",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Include representation covering employee census, compensation, benefits, agreements, labor relations, and compliance with employment laws.",
                ),
                
                "employee_benefits_rep": DetectionPattern(
                    name="Employee Benefits/ERISA Representation",
                    description="Representation regarding employee benefit plans and ERISA compliance.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(employee\s+benefit\s+plans?|benefit\s+plans?)",
                        r"(?i)(erisa|pension|retirement\s+plan)",
                        r"(?i)(401\s*\(?k\)?|defined\s+benefit|defined\s+contribution)",
                        r"(?i)(health\s+(?:insurance|plan|benefits?))",
                        r"(?i)(multiemployer\s+plan)",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Include comprehensive ERISA representation covering all benefit plans, qualified status, funding, prohibited transactions, and multiemployer plan liability.",
                ),
                
                "tax_rep": DetectionPattern(
                    name="Tax Representation",
                    description="Representation regarding tax matters, filings, and liabilities.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(tax\s+(?:matters?|returns?|liabilit(?:y|ies)|filings?))",
                        r"(?i)(filed\s+(?:all\s+)?(?:required\s+)?tax\s+returns?)",
                        r"(?i)((?:paid|payment\s+of)\s+(?:all\s+)?taxes)",
                        r"(?i)(no\s+(?:tax\s+)?(?:audits?|examinations?|assessments?))",
                        r"(?i)(tax\s+(?:deficienc(?:y|ies)|claims?))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Include comprehensive tax representation covering filings, payments, audits, reserves, transfer pricing, and net operating losses.",
                ),
                
                "environmental_rep": DetectionPattern(
                    name="Environmental Representation",
                    description="Representation regarding environmental compliance and liabilities.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(environmental\s+(?:matters?|compliance|laws?|liabilit(?:y|ies)|permits?))",
                        r"(?i)(hazardous\s+(?:substances?|materials?|waste))",
                        r"(?i)(environmental\s+(?:contamination|remediation|cleanup))",
                        r"(?i)(cercla|superfund|rcra)",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Include environmental representation covering compliance, permits, contamination, remediation obligations, and environmental liabilities.",
                ),
                
                "insurance_rep": DetectionPattern(
                    name="Insurance Representation",
                    description="Representation regarding insurance coverage.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(insurance\s+(?:polic(?:y|ies)|coverage|matters?))",
                        r"(?i)((?:adequate|sufficient)\s+insurance)",
                        r"(?i)(insured\s+(?:against|for))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=5,
                    recommendation="Include representation regarding adequacy of insurance coverage, claims history, and policy status.",
                ),
                
                "real_property_rep": DetectionPattern(
                    name="Real Property Representation",
                    description="Representation regarding owned and leased real property.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(real\s+property|real\s+estate)",
                        r"(?i)(owned\s+(?:real\s+)?propert(?:y|ies))",
                        r"(?i)(leased\s+(?:real\s+)?propert(?:y|ies)|lease(?:d|s)\s+premises)",
                        r"(?i)((?:title|ownership)\s+to\s+(?:real\s+)?property)",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=5,
                    recommendation="Include representation covering owned real property (title, liens, encumbrances) and leased property (lease terms, compliance, landlord consents).",
                ),
                
                "related_party_transactions_rep": DetectionPattern(
                    name="Related Party Transactions Representation",
                    description="Representation regarding transactions with related parties.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(related\s+party\s+(?:transactions?|agreements?|arrangements?))",
                        r"(?i)(affiliate\s+(?:transactions?|agreements?|contracts?))",
                        r"(?i)((?:transactions?|dealings?)\s+with\s+(?:affiliates?|related\s+parties?))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=6,
                    recommendation="Include representation disclosing all related party transactions and agreements that will continue post-closing.",
                ),
                
                "brokers_rep": DetectionPattern(
                    name="Brokers/Finders Fee Representation",
                    description="Representation regarding broker and finder fees.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(brokers?|finders?|investment\s+bank(?:ers?)?)",
                        r"(?i)((?:broker(?:age)?|finder(?:\'?s)?)\s+fees?)",
                        r"(?i)(no\s+(?:other\s+)?(?:broker|finder|agent))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=5,
                    recommendation="Include representation that no broker or finder fees are owed except as disclosed, with indemnification for any undisclosed fees.",
                ),
                
                "data_privacy_rep": DetectionPattern(
                    name="Data Privacy/Cybersecurity Representation",
                    description="Representation regarding data privacy and cybersecurity.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(data\s+(?:privacy|protection|security))",
                        r"(?i)(privacy\s+(?:laws?|policies?|compliance))",
                        r"(?i)(gdpr|ccpa|hipaa|pci)",
                        r"(?i)(personal\s+(?:data|information)|pii)",
                        r"(?i)(cybersecurity|cyber\s+security|data\s+breach)",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Include representation covering data privacy compliance (GDPR, CCPA, HIPAA as applicable), privacy policies, data security measures, and breach history.",
                ),
                
                "anti_corruption_rep": DetectionPattern(
                    name="Anti-Corruption/FCPA Representation",
                    description="Representation regarding anti-bribery and anti-corruption compliance.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(anti-?corruption|anti-?bribery)",
                        r"(?i)(fcpa|foreign\s+corrupt\s+practices\s+act)",
                        r"(?i)(uk\s+bribery\s+act)",
                        r"(?i)(corrupt\s+(?:payments?|practices?))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Include representation regarding FCPA and anti-corruption compliance, especially for targets with international operations.",
                ),
                
                "sanctions_export_rep": DetectionPattern(
                    name="Sanctions/Export Control Representation",
                    description="Representation regarding sanctions and export control compliance.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(sanctions?|ofac|sdn\s+list)",
                        r"(?i)(export\s+control|ear|itar)",
                        r"(?i)((?:trade|economic)\s+sanctions?)",
                        r"(?i)((?:restricted|denied)\s+part(?:y|ies))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Include representation regarding OFAC sanctions compliance and export control compliance (EAR, ITAR as applicable).",
                ),
                
                "no_other_reps_warranty": DetectionPattern(
                    name="No Other Representations Clause",
                    description="Clause disclaiming representations other than those expressly made.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(no\s+other\s+representations?)",
                        r"(?i)((?:except\s+(?:for|as)).*(?:expressly|specifically)\s+(?:set\s+forth|made|stated))",
                        r"(?i)(disclaim(?:s|ing)?\s+(?:all\s+)?(?:other\s+)?(?:representations?|warranties?))",
                        r"(?i)(as-?is)",
                    ],
                    base_risk_score=5,
                    recommendation="Consider adding disclaimer of extra-contractual representations to limit liability exposure.",
                ),
                
                "knowledge_qualifiers": DetectionPattern(
                    name="Knowledge Qualifiers Definition",
                    description="Definition of 'knowledge' for purposes of qualified representations.",
                    severity=Severity.MEDIUM,
                    category=Category.INCOMPLETE_DEFINITION,
                    presence_patterns=[
                        r"(?i)(\"knowledge\"|knowledge\s+of\s+(?:seller|company)|seller(?:\'s|s)?\s+knowledge)",
                        r"(?i)(to\s+the\s+knowledge\s+of)",
                        r"(?i)(actual\s+knowledge|constructive\s+knowledge)",
                        r"(?i)(knowledge.*(?:means|shall\s+mean|defined))",
                    ],
                    vague_patterns=[
                        r"(?i)(best\s+of.*knowledge)",  # Vague knowledge standard
                    ],
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=6,
                    recommendation="Define 'knowledge' precisely, including whether it's actual or constructive knowledge, and identify the individuals whose knowledge is attributed to the company.",
                ),
                
                "materiality_qualifiers": DetectionPattern(
                    name="Materiality/MAE Qualifiers",
                    description="Use and definition of materiality qualifiers and Material Adverse Effect.",
                    severity=Severity.HIGH,
                    category=Category.AMBIGUITY,
                    presence_patterns=[
                        r"(?i)(material\s+adverse\s+(?:effect|change|event)|mae|mac)",
                        r"(?i)(\"material\"|material\s+(?:means|shall\s+mean))",
                        r"(?i)(in\s+all\s+material\s+respects)",
                    ],
                    problematic_patterns=[
                        r"(?i)(double\s+material)",  # Double materiality scrape
                    ],
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Define Material Adverse Effect/Change carefully with appropriate carve-outs. Be consistent in application of materiality qualifiers.",
                ),
                
                "disclosure_schedules_reference": DetectionPattern(
                    name="Disclosure Schedules Reference",
                    description="Reference to and requirements for disclosure schedules.",
                    severity=Severity.HIGH,
                    category=Category.STRUCTURAL_ISSUE,
                    presence_patterns=[
                        r"(?i)(disclosure\s+(?:schedules?|letter))",
                        r"(?i)(schedule\s+\d+\.\d+)",
                        r"(?i)(set\s+forth\s+(?:on|in)\s+schedule)",
                        r"(?i)(seller\s+disclosure\s+(?:schedule|letter))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Include comprehensive disclosure schedules and specify updating mechanism, cross-reference rules, and standard for disclosure (specific vs. general).",
                ),
            },
            
            # =================================================================
            # SECTION 5: COVENANTS
            # =================================================================
            "covenants": {
                
                "pre_closing_covenants_general": DetectionPattern(
                    name="Pre-Closing Covenants Section",
                    description="Covenants governing conduct between signing and closing.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(pre-?closing\s+covenants?|covenants?\s+(?:prior\s+to|pending)\s+closing)",
                        r"(?i)(between\s+(?:signing|execution|the\s+date\s+hereof)\s+and\s+(?:closing|the\s+closing\s+date))",
                        r"(?i)(conduct\s+of\s+(?:the\s+)?business)",
                        r"(?i)(interim\s+(?:period|covenants?|operating\s+covenants?))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=8,
                    recommendation="Include comprehensive pre-closing covenants governing business operations between signing and closing.",
                ),
                
                "ordinary_course_covenant": DetectionPattern(
                    name="Ordinary Course of Business Covenant",
                    description="Covenant to operate business in ordinary course pending closing.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(ordinary\s+course\s+of\s+business)",
                        r"(?i)(conduct\s+(?:of\s+)?(?:the\s+)?business\s+in\s+the\s+ordinary\s+course)",
                        r"(?i)(consistent\s+with\s+past\s+practice)",
                    ],
                    vague_patterns=[
                        r"(?i)(ordinary\s+course(?!\s+of\s+business))",  # Missing "of business"
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=8,
                    recommendation="Define ordinary course precisely and include specific permitted/prohibited actions list.",
                ),
                
                "negative_covenants": DetectionPattern(
                    name="Negative/Restrictive Covenants",
                    description="Specific restrictions on seller's conduct pending closing.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(shall\s+not.*without.*(?:prior\s+)?(?:written\s+)?consent)",
                        r"(?i)((?:seller|company|target)\s+shall\s+not)",
                        r"(?i)(prohibited\s+(?:actions?|conduct))",
                        r"(?i)(negative\s+covenants?|restrictive\s+covenants?)",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Include specific negative covenants covering: equity issuances, dividends, asset sales, debt incurrence, capex, material contracts, employment changes, etc.",
                    sub_checks=[
                        "no_equity_issuance",
                        "no_dividends",
                        "no_asset_sales",
                        "no_debt_incurrence",
                        "capex_restrictions",
                        "contract_restrictions",
                        "employment_restrictions",
                        "accounting_method_restrictions"
                    ]
                ),
                
                "access_covenant": DetectionPattern(
                    name="Access Covenant",
                    description="Ongoing access to information and personnel pending closing.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(access.*(?:pending|prior\s+to)\s+closing)",
                        r"(?i)(continued\s+access)",
                        r"(?i)(access\s+to.*(?:books|records|personnel|facilities))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=5,
                    recommendation="Include covenant for continued access to information, personnel, and facilities pending closing.",
                ),
                
                "notification_covenant": DetectionPattern(
                    name="Notification/Update Covenant",
                    description="Obligation to notify of material changes or breaches.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)((?:shall|will)\s+(?:promptly\s+)?(?:notify|inform|advise))",
                        r"(?i)(notification\s+(?:covenant|obligation))",
                        r"(?i)(notice\s+of.*(?:material|breach|change))",
                        r"(?i)(update.*(?:disclosure|schedules?))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=5,
                    recommendation="Include covenant requiring prompt notification of material developments, rep breaches, and schedule updates.",
                ),
                
                "efforts_to_close_covenant": DetectionPattern(
                    name="Efforts to Close Covenant",
                    description="Covenant regarding efforts to satisfy closing conditions and consummate transaction.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)((?:commercially\s+)?reasonable\s+(?:best\s+)?efforts)",
                        r"(?i)(best\s+efforts)",
                        r"(?i)(use\s+(?:its|their)\s+(?:commercially\s+)?reasonable\s+efforts)",
                        r"(?i)(efforts\s+to\s+(?:consummate|close|satisfy))",
                    ],
                    vague_patterns=[
                        r"(?i)(reasonable\s+efforts(?!\s+(?:to|covenant)))",  # Standalone without context
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Specify effort standard (best efforts vs. commercially reasonable efforts) and what it requires.",
                ),
                
                "regulatory_approval_covenant": DetectionPattern(
                    name="Regulatory Approval Covenant",
                    description="Covenant regarding obtaining required regulatory approvals.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)((?:regulatory|governmental)\s+(?:approvals?|consents?|filings?))",
                        r"(?i)(hsr|hart-?scott-?rodino)",
                        r"(?i)(antitrust\s+(?:approval|clearance|filing))",
                        r"(?i)(cfius|(?:foreign\s+)?investment\s+review)",
                        r"(?i)(fcc|fda|(?:sec|securities)\s+(?:approval|filing))",
                    ],
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Include specific covenants for required regulatory filings (HSR, CFIUS, industry-specific) with timing requirements and cooperation obligations.",
                    sub_checks=[
                        "hsr_filing_covenant",
                        "cfius_review",
                        "industry_regulatory_approvals",
                        "state_approvals",
                        "foreign_approvals"
                    ]
                ),
                
                "hell_or_high_water_covenant": DetectionPattern(
                    name="Hell or High Water/Divestiture Covenant",
                    description="Commitment regarding divestitures or remedies for regulatory approval.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(hell\s+or\s+high\s+water)",
                        r"(?i)(divest(?:iture)?|hold\s+separate|behavioral\s+remed(?:y|ies))",
                        r"(?i)(antitrust\s+(?:remed(?:y|ies)|commitment))",
                    ],
                    required_in=[DocumentType.MERGER_AGREEMENT],  # Primarily large public deals
                    base_risk_score=6,
                    recommendation="For deals requiring antitrust approval, specify whether buyer must accept divestitures or behavioral remedies (hell or high water) or if there are limits.",
                ),
                
                "third_party_consents_covenant": DetectionPattern(
                    name="Third Party Consents Covenant",
                    description="Covenant to obtain required third party consents.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(third\s+party\s+consents?)",
                        r"(?i)(consents?\s+(?:required|necessary|needed))",
                        r"(?i)(change\s+of\s+control\s+consents?)",
                        r"(?i)(landlord\s+consents?|customer\s+consents?|vendor\s+consents?)",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=5,
                    recommendation="Include covenant to use efforts to obtain required third party consents, with list of material consents required as closing condition.",
                ),
                
                "exclusivity_noshop": DetectionPattern(
                    name="Exclusivity/No-Shop Provision",
                    description="Restriction on seller's ability to solicit or engage with other potential buyers.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(exclusivity|exclusive\s+(?:dealing|negotiation|right))",
                        r"(?i)(no-?shop|no\s+shop)",
                        r"(?i)(no-?solicitation|no\s+solicitation)",
                        r"(?i)(shall\s+not.*(?:solicit|encourage|initiate|negotiate).*(?:other|alternative|competing))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.LOI, DocumentType.TERM_SHEET],
                    recommended_in=[DocumentType.STOCK_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Include no-shop provision with clear scope, duration, and any fiduciary out carve-outs.",
                    sub_checks=[
                        "exclusivity_duration",
                        "exclusivity_scope",
                        "fiduciary_out",
                        "matching_rights",
                        "window_shop"
                    ]
                ),
                
                "fiduciary_out": DetectionPattern(
                    name="Fiduciary Out",
                    description="Carve-out allowing seller to respond to unsolicited superior proposals.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(fiduciary\s+(?:out|exception|duties?))",
                        r"(?i)(superior\s+proposal)",
                        r"(?i)(intervening\s+event)",
                        r"(?i)(board.*fiduciary\s+(?:duties?|obligations?))",
                    ],
                    recommended_in=[DocumentType.MERGER_AGREEMENT],
                    base_risk_score=5,
                    recommendation="For public company deals, consider fiduciary out provisions allowing board to respond to unsolicited superior proposals.",
                ),
                
                "employee_retention_covenant": DetectionPattern(
                    name="Employee Retention Covenant",
                    description="Covenants regarding treatment and retention of employees.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(employee\s+(?:retention|matters?|continuation|treatment))",
                        r"(?i)(retain(?:ing)?\s+(?:key\s+)?employees?)",
                        r"(?i)(employment\s+(?:offers?|continuation))",
                        r"(?i)((?:key|critical)\s+employees?)",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=5,
                    recommendation="Include provisions regarding employee treatment, retention bonuses, and employment offers.",
                ),
                
                "non_compete_covenant": DetectionPattern(
                    name="Non-Competition Covenant",
                    description="Post-closing non-compete restrictions on seller/principals.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(non-?competition?|(?:shall|will)\s+not\s+compete)",
                        r"(?i)(restrictive\s+covenant)",
                        r"(?i)(covenant\s+not\s+to\s+compete)",
                        r"(?i)(competitive\s+(?:business|activit(?:y|ies)))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Include non-compete with clear scope (geographic, business lines), duration, and covered persons.",
                    sub_checks=[
                        "noncompete_duration",
                        "noncompete_geographic_scope",
                        "noncompete_business_scope",
                        "noncompete_covered_persons"
                    ]
                ),
                
                "non_solicit_covenant": DetectionPattern(
                    name="Non-Solicitation Covenant",
                    description="Post-closing restrictions on soliciting employees or customers.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(non-?solicitation?|(?:shall|will)\s+not\s+solicit)",
                        r"(?i)((?:not|refrain\s+from)\s+solicit(?:ing)?.*(?:employees?|customers?))",
                        r"(?i)((?:employee|customer)\s+non-?solicitation?)",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=6,
                    recommendation="Include non-solicitation of employees and customers with clear scope and duration.",
                    sub_checks=[
                        "employee_nonsolicit_duration",
                        "customer_nonsolicit_duration",
                        "covered_employees",
                        "covered_customers"
                    ]
                ),
                
                "confidentiality_covenant": DetectionPattern(
                    name="Confidentiality Covenant",
                    description="Confidentiality obligations regarding transaction and business information.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(confidential(?:ity)?)",
                        r"(?i)(non-?disclosure|nda)",
                        r"(?i)((?:proprietary|confidential)\s+information)",
                        r"(?i)((?:shall|will)\s+(?:keep|maintain|hold)\s+(?:in\s+)?(?:confidence|confidential))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.LOI, DocumentType.TERM_SHEET, DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=8,
                    recommendation="Include comprehensive confidentiality provisions with clear definitions, permitted disclosures, duration, and return/destruction obligations.",
                    sub_checks=[
                        "confidential_info_definition",
                        "confidentiality_duration",
                        "permitted_disclosures",
                        "return_destruction_obligations",
                        "survival_period"
                    ]
                ),
                
                "public_announcement_covenant": DetectionPattern(
                    name="Public Announcement Covenant",
                    description="Restrictions on public announcements regarding the transaction.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(public\s+(?:announcement|disclosure|statement))",
                        r"(?i)(press\s+release)",
                        r"(?i)((?:mutual|joint)\s+(?:consent|approval).*(?:announcement|disclosure|press))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.LOI, DocumentType.TERM_SHEET, DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=5,
                    recommendation="Include covenant requiring mutual consent for public announcements and form of initial announcement.",
                ),
                
                "books_records_covenant": DetectionPattern(
                    name="Books and Records Covenant",
                    description="Post-closing access to books and records.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(books\s+and\s+records)",
                        r"(?i)((?:access|retention).*books)",
                        r"(?i)(record\s+retention)",
                        r"(?i)(post-?closing\s+access)",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=4,
                    recommendation="Include covenant for post-closing access to books and records (typically for tax, litigation, or regulatory purposes).",
                ),
                
                "tail_insurance_covenant": DetectionPattern(
                    name="D&O Tail Insurance Covenant",
                    description="Covenant to maintain or obtain tail D&O insurance for pre-closing acts.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(tail\s+(?:insurance|policy|coverage))",
                        r"(?i)(d\s*&\s*o\s+(?:insurance|coverage))",
                        r"(?i)(directors?\s+and\s+officers?\s+(?:insurance|indemnification))",
                        r"(?i)(run-?off\s+(?:insurance|coverage|policy))",
                    ],
                    required_in=[DocumentType.MERGER_AGREEMENT],
                    recommended_in=[DocumentType.STOCK_PURCHASE],
                    base_risk_score=5,
                    recommendation="Include covenant to maintain or purchase D&O tail insurance for pre-closing acts (typically 6 years).",
                ),
            },
            
            # =================================================================
            # SECTION 6: CLOSING CONDITIONS
            # =================================================================
            "closing_conditions": {
                
                "closing_conditions_general": DetectionPattern(
                    name="Closing Conditions Section",
                    description="Definitive agreements must contain conditions to closing.",
                    severity=Severity.CRITICAL,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(conditions?\s+(?:to|of|precedent\s+to)\s+(?:the\s+)?closing)",
                        r"(?i)(closing\s+conditions?)",
                        r"(?i)((?:condition|subject)\s+to\s+the\s+(?:satisfaction|waiver))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    recommended_in=[DocumentType.LOI, DocumentType.TERM_SHEET],
                    base_risk_score=9,
                    recommendation="Include comprehensive closing conditions for both buyer's and seller's obligations.",
                ),
                
                "rep_accuracy_condition": DetectionPattern(
                    name="Representation Accuracy Condition",
                    description="Condition that representations are accurate at closing.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(representations?\s+(?:and\s+warranties?\s+)?(?:shall\s+be|are)\s+(?:true|accurate|correct))",
                        r"(?i)((?:accuracy|truth)\s+of\s+representations?)",
                        r"(?i)(representations?.*(?:true\s+and\s+correct|accurate).*(?:closing|date))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=8,
                    recommendation="Include condition that reps are accurate at closing, specifying the standard (in all respects, in all material respects, or MAE-qualified).",
                ),
                
                "covenant_compliance_condition": DetectionPattern(
                    name="Covenant Compliance Condition",
                    description="Condition that covenants have been performed/complied with.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(covenants?\s+(?:shall\s+have\s+been\s+)?(?:performed|complied|satisfied))",
                        r"(?i)(compliance\s+with.*covenants?)",
                        r"(?i)((?:performed|complied\s+with).*(?:all\s+)?(?:covenants?|agreements?|obligations?))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=8,
                    recommendation="Include condition that all covenants have been performed in all material respects.",
                ),
                
                "no_mac_condition": DetectionPattern(
                    name="No MAC/MAE Condition",
                    description="Condition that no Material Adverse Change/Effect has occurred.",
                    severity=Severity.CRITICAL,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(no\s+material\s+adverse\s+(?:change|effect|event))",
                        r"(?i)(mac\s+(?:condition|closing\s+condition))",
                        r"(?i)((?:absence|no\s+occurrence)\s+of.*(?:material\s+adverse|mac|mae))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    recommended_in=[DocumentType.LOI, DocumentType.TERM_SHEET],
                    base_risk_score=9,
                    recommendation="Include no-MAC condition as buyer protection, with carefully defined MAC definition and appropriate carve-outs.",
                    related_provisions=["mac_definition"]
                ),
                
                "mac_definition": DetectionPattern(
                    name="MAC/MAE Definition",
                    description="Definition of Material Adverse Change/Effect.",
                    severity=Severity.CRITICAL,
                    category=Category.INCOMPLETE_DEFINITION,
                    presence_patterns=[
                        r"(?i)(\"material\s+adverse\s+(?:change|effect)\"|material\s+adverse\s+(?:change|effect)\s+(?:means|shall\s+mean))",
                        r"(?i)(\"mac\"|\"mae\")",
                        r"(?i)(material\s+adverse.*(?:means|shall\s+mean|is\s+defined))",
                    ],
                    vague_patterns=[
                        r"(?i)(material\s+adverse(?!.*(?:means|shall\s+mean|carve-?out|except|other\s+than|excluding)))",  # MAC mentioned but not defined
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.ASSET_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=9,
                    recommendation="Define MAC carefully. Standard carve-outs include: general economic conditions, industry conditions, market conditions, natural disasters, pandemics, changes in law, and effects of transaction announcement.",
                    sub_checks=[
                        "mac_carveout_general_economy",
                        "mac_carveout_industry_conditions",
                        "mac_carveout_market_conditions",
                        "mac_carveout_natural_disasters",
                        "mac_carveout_pandemic",
                        "mac_carveout_law_changes",
                        "mac_carveout_announcement_effects",
                        "mac_carveout_disproportionate_impact_exception"
                    ]
                ),
                
                "regulatory_approval_condition": DetectionPattern(
                    name="Regulatory Approval Condition",
                    description="Condition that required regulatory approvals have been obtained.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)((?:regulatory|governmental)\s+(?:approvals?|consents?|clearance).*(?:obtained|received|satisfied))",
                        r"(?i)(hsr.*(?:waiting\s+period|expired|terminated))",
                        r"(?i)(antitrust\s+(?:approval|clearance).*(?:condition|obtained))",
                    ],
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Include condition for expiration of HSR waiting period and receipt of any other required regulatory approvals.",
                ),
                
                "shareholder_approval_condition": DetectionPattern(
                    name="Shareholder/Board Approval Condition",
                    description="Condition that required corporate approvals have been obtained.",
                    severity=Severity.HIGH,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)((?:shareholder|stockholder|board|member)\s+approval)",
                        r"(?i)((?:requisite|required)\s+(?:company|seller)?\s*(?:vote|approval))",
                        r"(?i)(approval\s+of.*(?:shareholders?|stockholders?|board|members?))",
                    ],
                    absence_is_flag=True,
                    required_in=[DocumentType.STOCK_PURCHASE, DocumentType.MERGER_AGREEMENT],
                    base_risk_score=7,
                    recommendation="Include condition for required shareholder/board approvals, specifying vote thresholds and approval requirements.",
                ),
                
                "third_party_consent_condition": DetectionPattern(
                    name="Third Party Consent Condition",
                    description="Condition that material third party consents have been obtained.",
                    severity=Severity.MEDIUM,
                    category=Category.MISSING_PROVISION,
                    presence_patterns=[
                        r"(?i)(third\s+party\s+consents?\s+(?:shall\s+have\s+been\s+)?(?:obtained|received))",
                        r"(?i)(material\s+consents?\s+(?:condition|obtained))",
                        