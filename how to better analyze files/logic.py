import re

class MA_Contract_Analyzer:
    def __init__(self, document_text):
        self.text = document_text.lower()
        self.doc_type = None
        self.flags = []

    def run_analysis(self):
        # STEP 1: CLASSIFY THE DOCUMENT
        self.doc_type = self.classify_document()
        print(f"Document Identified as: {self.doc_type}")

        # STEP 2: ROUTE TO CORRECT LOGIC
        if self.doc_type == "LOI":
            self.analyze_loi()
        elif self.doc_type == "DEFINITIVE_AGREEMENT":
            self.analyze_spa()
        else:
            self.flags.append({"severity": "CRITICAL", "msg": "Unknown document type."})

        return self.flags

    def classify_document(self):
        # Simple keyword weighting for classification
        loi_keywords = ["letter of intent", "term sheet", "memorandum of understanding", "non-binding"]
        spa_keywords = ["stock purchase agreement", "asset purchase agreement", "merger agreement", "indemnification"]
        
        if any(x in self.text for x in loi_keywords):
            return "LOI"
        elif any(x in self.text for x in spa_keywords):
            return "DEFINITIVE_AGREEMENT"
        return "UNKNOWN"

    # ==========================================
    # LOGIC SPECIFIC TO LOI (What you missed)
    # ==========================================
    def analyze_loi(self):
        print("Running LOI specific checks...")
        
        # CHECK 1: BINDING VS NON-BINDING (The "Fatal Error" check)
        # We look for a disclaimer stating parts are non-binding.
        if "non-binding" not in self.text and "not binding" not in self.text:
            self.flags.append({
                "severity": "CRITICAL",
                "issue": "Risk of Inadvertent Binding Contract",
                "recommendation": "Add explicit language stating the LOI is non-binding except for Exclusivity/Confidentiality."
            })

        # CHECK 2: PRICE CERTAINTY
        # Detecting vague price mechanisms
        if "subject to further discussion" in self.text or "to be determined" in self.text:
             self.flags.append({
                "severity": "HIGH",
                "issue": "Undefined Purchase Price",
                "recommendation": "Set a base valuation (e.g., '$10M' or '5x EBITDA') to avoid wasting time."
            })

        # CHECK 3: EXCLUSIVITY DURATION
        # Regex to find the number of days near the word "exclusivity"
        match = re.search(r'(\d+)\s+days', self.text)
        if match:
            days = int(match.group(1))
            if days < 45:
                self.flags.append({
                    "severity": "MEDIUM",
                    "issue": f"Short Exclusivity Period ({days} days)",
                    "recommendation": "Extend to 60-90 days to allow for full due diligence."
                })

        # CHECK 4: DUE DILIGENCE SCOPE
        # Check if the scope is limited to just financials
        if "financial statements" in self.text and "legal" not in self.text:
            self.flags.append({
                "severity": "MEDIUM",
                "issue": "Restrictive Due Diligence Scope",
                "recommendation": "Expand scope to include legal, IP, HR, and tax documents."
            })

    # ==========================================
    # LOGIC SPECIFIC TO SPA (What you ran before)
    # ==========================================
    def analyze_spa(self):
        print("Running SPA specific checks...")
        
        # This is where your PREVIOUS analysis logic belongs
        required_clauses = ["material adverse change", "liability cap", "indemnification", "employee benefits"]
        
        for clause in required_clauses:
            if clause not in self.text:
                self.flags.append({
                    "severity": "HIGH", 
                    "issue": f"Missing {clause.title()} Clause",
                    "recommendation": f"Draft a standard {clause} provision."
                })

# ==========================================
# TEST WITH YOUR DOCUMENT TEXT
# ==========================================
doc_text = """
Letter of Intent – Acme Corp. (Buyer) & BrightFuture Ltd. (Seller)
1. Intent: Buyer intends to acquire 100 % of Seller’s equity.
2. Purchase Price: The purchase price will be determined based on industry standard adjustments and is subject to further discussion.
3. Due Diligence: Seller will provide financial statements for the past three years.
4. Confidentiality: Both parties agree to keep discussions confidential.
5. Exclusivity: Seller will not negotiate with other parties for 30 days.
6. Governing Law: This LOI shall be governed by the laws of the State of Delaware.
"""

analyzer = MA_Contract_Analyzer(doc_text)
results = analyzer.run_analysis()

import json
print(json.dumps(results, indent=2))