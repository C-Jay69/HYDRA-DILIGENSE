// Types
export interface RedFlag {
  id: string;
  category: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  description: string;
  location: string;
  score: number;
  source: string;
  recommendation?: string;
}

// Configuration
const OFFSHORE_JURISDICTIONS = [
  'Cayman Islands', 'BVI', 'British Virgin Islands',
  'Bermuda', 'Panama', 'Isle of Man', 'Jersey',
  'Guernsey', 'Liechtenstein', 'Luxembourg',
  'Cyprus', 'Malta', 'Seychelles', 'Bahamas'
];

const WEASEL_WORDS = [
  'reasonable', 'material', 'substantial', 'significant',
  'timely', 'commercially reasonable', 'best efforts'
];

const HIGH_RISK_PHRASES = [
  'to be provided', 'being finalized', 'being compiled',
  'will be attached', 'to be determined', 'subject to',
  'contingent upon'
];

// Helper functions
function getContext(text: string, start: number, end: number, chars: number = 150): string {
  const contextStart = Math.max(0, start - chars);
  const contextEnd = Math.min(text.length, end + chars);
  let context = text.slice(contextStart, contextEnd).trim();

  if (contextStart > 0) context = '...' + context;
  if (contextEnd < text.length) context = context + '...';

  return context;
}

function generateId(): string {
  return `rule_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// Helper to create a regex that handles spaced-out characters
// e.g. "Cayman" -> "C\s*a\s*y\s*m\s*a\s*n"
function fuzzyPattern(term: string): string {
  return term
    .split('')
    .map(c => /[A-Za-z0-9]/.test(c) ? `${c}\\s*` : '\\s*')
    .join('')
    .replace(/(\\s\*)+$/, ''); // Remove trailing space marker
}

// Analysis functions
function checkOffshoreJurisdictions(text: string, flags: RedFlag[]): void {
  for (const jurisdiction of OFFSHORE_JURISDICTIONS) {
    const pattern = new RegExp(fuzzyPattern(jurisdiction), 'gi');
    let match;

    while ((match = pattern.exec(text)) !== null) {
      const context = getContext(text, match.index, match.index + match[0].length);

      // Check if in governing law or arbitration section
      const contextLower = context.toLowerCase();
      const isGoverningLaw = contextLower.includes('governing law') ||
        contextLower.includes('arbitration') ||
        contextLower.includes('dispute resolution');

      const severity: 'CRITICAL' | 'HIGH' = isGoverningLaw ? 'CRITICAL' : 'HIGH';

      flags.push({
        id: generateId(),
        category: 'jurisdiction',
        severity,
        title: `Offshore Jurisdiction: ${jurisdiction}`,
        description: `Document references ${jurisdiction}, which may indicate jurisdiction shopping or regulatory arbitrage.`,
        location: context,
        score: severity === 'CRITICAL' ? 9 : 7,
        source: 'rule_engine',
        recommendation: 'Require arbitration in neutral jurisdiction (Delaware, New York, or London). Investigate why offshore jurisdiction was chosen.'
      });
    }
  }
}

function checkWeaselWords(text: string, flags: RedFlag[]): void {
  const weaselCount: Record<string, number> = {};

  for (const word of WEASEL_WORDS) {
    const escapedWord = word.replace(/\s+/g, '\\s+');
    const pattern = new RegExp(`\\b${escapedWord}\\b`, 'gi');
    const matches = text.match(pattern);

    if (matches && matches.length > 3) {
      weaselCount[word] = matches.length;

      const firstMatchIndex = text.search(pattern);
      const context = getContext(text, firstMatchIndex, firstMatchIndex + word.length);

      flags.push({
        id: generateId(),
        category: 'vague_language',
        severity: 'MEDIUM',
        title: `Excessive Vague Language: '${word}' (${matches.length}x)`,
        description: `Term '${word}' appears ${matches.length} times. Vague language creates ambiguity and potential for disputes.`,
        location: context,
        score: 5,
        source: 'rule_engine',
        recommendation: `Request specific definitions and thresholds. Replace '${word}' with measurable criteria.`
      });
    }
  }
}

function checkHighRiskPhrases(text: string, flags: RedFlag[]): void {
  for (const phrase of HIGH_RISK_PHRASES) {
    const pattern = new RegExp(fuzzyPattern(phrase), 'gi');
    let match;

    while ((match = pattern.exec(text)) !== null) {
      const context = getContext(text, match.index, match.index + match[0].length);

      flags.push({
        id: generateId(),
        category: 'missing_info',
        severity: 'HIGH',
        title: `Deferred Disclosure: '${phrase}'`,
        description: 'Critical information is deferred or incomplete. This is a major red flag - you are signing before having full information.',
        location: context,
        score: 8,
        source: 'rule_engine',
        recommendation: 'STOP. Do not sign until all referenced information is provided and reviewed. No post-closing surprises.'
      });
    }
  }
}

function checkMissingSchedules(text: string, flags: RedFlag[]): void {
  // Find all schedule references
  const schedulePattern = /Schedule\s+([A-Z0-9]+(?:\([a-z0-9]+\))?)/gi;
  const referencedSchedules = new Set();
  let match;

  while ((match = schedulePattern.exec(text)) !== null) {
    referencedSchedules.add(match[1]);
  }

  // Look for phrases indicating schedules are missing
  const missingIndicators = [
    'being finalized', 'to be provided', 'being compiled',
    'will be attached', 'to be determined'
  ];

  for (const indicator of missingIndicators) {
    if (text.toLowerCase().includes(indicator)) {
      const pattern = new RegExp(`.{0,100}${indicator}.{0,100}`, 'gi');
      const contextMatch = text.match(pattern);

      if (contextMatch) {
        flags.push({
          id: generateId(),
          category: 'missing_info',
          severity: 'CRITICAL',
          title: 'Missing or Incomplete Schedules',
          description: `Schedules are incomplete: '${indicator}'. Never sign with missing schedules.`,
          location: contextMatch[0],
          score: 10,
          source: 'rule_engine',
          recommendation: 'Require all schedules to be completed and attached before signing. Missing schedules = unknown liabilities.'
        });
        break; // Only flag once
      }
    }
  }
}

function checkDateAnomalies(text: string, flags: RedFlag[]): void {
  // Look for audit dates
  const auditPattern = /audit(?:ed)?.{0,50}(?:19|20)(\d{2})/gi;
  let match;

  while ((match = auditPattern.exec(text)) !== null) {
    const year = parseInt(match[1]);
    const fullYear = year > 50 ? 1900 + year : 2000 + year;

    // Flag audits older than 2 years
    const currentYear = new Date().getFullYear();
    if (fullYear < currentYear - 2) {
      const context = getContext(text, match.index, match.index + match[0].length);

      flags.push({
        id: generateId(),
        category: 'financial',
        severity: 'HIGH',
        title: `Outdated Financial Audit (${fullYear})`,
        description: `Most recent audit mentioned is from ${fullYear}, which is too old to be reliable.`,
        location: context,
        score: 7,
        source: 'rule_engine',
        recommendation: 'Require current audited financials (within 12 months). Outdated audits hide recent problems.'
      });
    }
  }
}

function checkPaymentRedFlags(text: string, flags: RedFlag[]): void {
  const redFlags = [
    {
      pattern: /earnout.*(?:undefined|to be determined|mutually agreed)/gi,
      title: 'Undefined Earnout Targets',
      severity: 'CRITICAL' as const,
      score: 10,
      recommendation: 'Never accept undefined earnout metrics. Specify exact EBITDA/revenue targets and calculation methods.'
    },
    {
      pattern: /deferred.*(?:performance metrics|to be determined)/gi,
      title: 'Undefined Deferred Payment Terms',
      severity: 'HIGH' as const,
      score: 8,
      recommendation: 'All deferred payment triggers must be clearly defined at signing.'
    }
  ];

  for (const { pattern, title, severity, score, recommendation } of redFlags) {
    let match;
    pattern.lastIndex = 0; // Reset regex

    while ((match = pattern.exec(text)) !== null) {
      const context = getContext(text, match.index, match.index + match[0].length);

      flags.push({
        id: generateId(),
        category: 'financial',
        severity,
        title,
        description: 'Payment terms are incomplete or subject to future agreement. This creates massive dispute risk.',
        location: context,
        score,
        source: 'rule_engine',
        recommendation
      });
    }
  }
}

function checkLiabilityLimitations(text: string, flags: RedFlag[]): void {
  // Look for indemnification survival periods
  const survivalPattern = /(?:surviv|representations).*?(\d+)\s*(?:months?|days?)/gi;
  let match;

  while ((match = survivalPattern.exec(text)) !== null) {
    const period = parseInt(match[1]);

    if (period < 12) { // Less than 12 months is suspicious
      const context = getContext(text, match.index, match.index + match[0].length);

      flags.push({
        id: generateId(),
        category: 'liability',
        severity: 'HIGH',
        title: `Short Survival Period (${period} months)`,
        description: `Representations survive only ${period} months. Industry standard is 18-24 months minimum.`,
        location: context,
        score: 7,
        source: 'rule_engine',
        recommendation: `Negotiate longer survival period (minimum 18 months). ${period} months is insufficient for most issues to surface.`
      });
    }
  }
}

function checkCustomerConcentration(text: string, flags: RedFlag[]): void {
  // Look for patterns like "top 10 customers represent X%"
  const concentrationPattern = /top\s+\d+\s+customers?.*?(\d+)%/gi;
  let match;

  while ((match = concentrationPattern.exec(text)) !== null) {
    const percentage = parseInt(match[1]);

    if (percentage > 50) {
      const context = getContext(text, match.index, match.index + match[0].length);
      const severity: 'CRITICAL' | 'HIGH' = percentage > 70 ? 'CRITICAL' : 'HIGH';

      flags.push({
        id: generateId(),
        category: 'customer',
        severity,
        title: `High Customer Concentration (${percentage}%)`,
        description: `Top customers represent ${percentage}% of revenue. Loss of any major customer could be catastrophic.`,
        location: context,
        score: percentage > 70 ? 9 : 7,
        source: 'rule_engine',
        recommendation: 'Require customer retention agreements, escrow protection, or earnout tied to customer retention.'
      });
    }
  }
}

function checkRequiredProvisions(text: string, flags: RedFlag[]): void {
  const requiredProvisions = [
    {
      id: "escrow",
      keywords: ["escrow", "holdback", "retention"],
      title: "Missing Escrow/Holdback Provision"
    },
    {
      id: "survival_period",
      keywords: ["survival", "survive closing", "survival period"],
      title: "Missing Survival Period Provision"
    },
    {
      id: "mac_clause",
      keywords: ["material adverse", "material adverse change", "material adverse effect"],
      title: "Missing MAC Clause"
    },
    {
      id: "liability_cap",
      keywords: ["cap", "limitation of liability", "maximum liability"],
      title: "Missing Liability Cap"
    },
    {
      id: "environmental",
      keywords: ["environmental", "hazardous", "pollution", "cleanup"],
      title: "Missing Environmental Provision"
    },
    {
      id: "employee_benefits",
      keywords: ["employee benefit", "pension", "401k", "ERISA"],
      title: "Missing Employee Benefits Provision"
    },
    {
      id: "confidentiality",
      keywords: ["confidential", "non-disclosure", "ndia", "proprietary information"],
      title: "Missing Confidentiality Provision"
    }
  ];

  const textLower = text.toLowerCase();

  for (const provision of requiredProvisions) {
    // Check if any keyword matches (using fuzzy match logic silently or simple lower case)
    const hasProvision = provision.keywords.some(keyword => {
      const pattern = new RegExp(fuzzyPattern(keyword), 'i');
      return pattern.test(text);
    });

    if (!hasProvision) {
      const severity = provision.id === 'confidentiality' ? 'CRITICAL' : 'HIGH';
      const score = provision.id === 'confidentiality' ? 10 : 7;

      flags.push({
        id: generateId(),
        category: provision.id === 'confidentiality' ? 'legal' : 'missing_info',
        severity,
        title: provision.title,
        description: provision.id === 'confidentiality'
          ? "The agreement lacks a confidentiality clause, exposing deal terms and strategic data to misuse. This is a non-negotiable term in M&A."
          : `This M&A agreement lacks a ${provision.id.replace('_', ' ')} provision, which is standard and critical for protecting the parties.`,
        location: "N/A - Provision not found in document",
        score,
        source: "rule_engine",
        recommendation: provision.id === 'confidentiality'
          ? "STOP. Demand a robust confidentiality and non-disclosure clause immediately."
          : `Add a comprehensive ${provision.id.replace('_', ' ')} provision to protect both parties.`
      });
    }
  }
}

function checkRegulatoryRisks(text: string, flags: RedFlag[]): void {
  const regulatoryKeywords = [
    { term: "FERC", title: "Federal Energy Regulatory Commission (FERC) Approval Required" },
    { term: "Regulatory Approval", title: "Material Regulatory Closing Condition" },
    { term: "Antitrust", title: "Antitrust/Competition Filing Required" }
  ];

  for (const { term, title } of regulatoryKeywords) {
    const pattern = new RegExp(fuzzyPattern(term), 'gi');
    let match;

    while ((match = pattern.exec(text)) !== null) {
      const context = getContext(text, match.index, match.index + match[0].length);

      flags.push({
        id: generateId(),
        category: 'compliance',
        severity: 'HIGH',
        title,
        description: `The deal hinges on ${term} approval. Energy and utility deals face high regulatory scrutiny; denial could kill the transaction.`,
        location: context,
        score: 8,
        source: 'rule_engine',
        recommendation: `Develop a regulatory strategy and backup plan (e.g., 'hell or high water' provisions or extended timelines).`
      });
    }
  }
}

function checkShortNoticePeriods(text: string, flags: RedFlag[]): void {
  // Check transition services period
  const transitionPattern = /(?:transition|integration).*?(\d+)\s*(?:days?|weeks?)/gi;
  let match;

  while ((match = transitionPattern.exec(text)) !== null) {
    const value = parseInt(match[1]);
    const isWeeks = match[0].toLowerCase().includes('week');
    const days = isWeeks ? value * 7 : value;

    if (days < 90) {
      const context = getContext(text, match.index, match.index + match[0].length);
      flags.push({
        id: generateId(),
        category: 'operational',
        severity: 'MEDIUM',
        title: `Short Transition Period (${days} days)`,
        description: `A ${days}-day transition period is often insufficient for complex integrations (IT, HR, Compliance). Risks operational disruption.`,
        location: context,
        score: 6,
        source: 'rule_engine',
        recommendation: "Negotiate a 90-180 day transition period to ensure a stable handover."
      });
    }
  }

  // Check indemnification claim notice period
  const noticePattern = /(?:claim|indemnification)\s+notice.*?(\d+)\s*(?:days?|weeks?)/gi;
  while ((match = noticePattern.exec(text)) !== null) {
    const value = parseInt(match[1]);
    const isWeeks = match[0].toLowerCase().includes('week');
    const days = isWeeks ? value * 7 : value;

    if (days < 90) {
      const context = getContext(text, match.index, match.index + match[0].length);
      flags.push({
        id: generateId(),
        category: 'liability',
        severity: 'MEDIUM',
        title: `Aggressive Claim Notice Period (${days} days)`,
        description: `Discovery of liabilities often takes longer than ${days} days. This compressed window may bar valid claims.`,
        location: context,
        score: 5,
        source: 'rule_engine',
        recommendation: "Request a 90-180 day claim notice period to allow for post-closing audits and discovery."
      });
    }
  }
}

function checkStockConsideration(text: string, flags: RedFlag[]): void {
  const stockPattern = /(\d+(?:\.\d+)?)\s*shares?\s+of\s+(?:buyer|purchaser|parent)/gi;
  let match;

  while ((match = stockPattern.exec(text)) !== null) {
    const ratio = match[1];
    const context = getContext(text, match.index, match.index + match[0].length);

    flags.push({
      id: generateId(),
      category: 'financial',
      severity: 'LOW',
      title: `Stock Consideration Volatility (Ratio: ${ratio})`,
      description: `Payment includes buyer stock. Market volatility could devalue the deal significantly between signing and closing.`,
      location: context,
      score: 3,
      source: 'rule_engine',
      recommendation: "Implement a stock collar (price floor/ceiling) or an escrow to hedge against buyer stock price drops."
    });
  }
}

// Main analysis function
export async function analyzeWithRules(text: string): Promise<RedFlag[]> {
  const flags: RedFlag[] = [];

  console.log('Running rule-based analysis...');
  console.log('Rule engine text preview:', text.substring(0, 500).replace(/\n/g, ' '));

  // Run all checks
  checkOffshoreJurisdictions(text, flags);
  checkWeaselWords(text, flags);
  checkHighRiskPhrases(text, flags);
  checkMissingSchedules(text, flags);
  checkDateAnomalies(text, flags);
  checkPaymentRedFlags(text, flags);
  checkLiabilityLimitations(text, flags);
  checkCustomerConcentration(text, flags);
  checkRequiredProvisions(text, flags);
  checkRegulatoryRisks(text, flags);
  checkShortNoticePeriods(text, flags);
  checkStockConsideration(text, flags);

  console.log(`Rule engine found ${flags.length} red flags`);

  return flags;
}
