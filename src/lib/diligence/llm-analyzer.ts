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

const ANALYSIS_PROMPT = `You are a Senior M&A Partner at a top-tier law firm (e.g., Wachtell or Skadden). 
Review this contract for CRITICAL deal-breakers and hidden risks.

Be aggressive. If a provision is missing or weak, flag it.

Analyze for:
1. MISSING PROTECTIONS (High Priority):
   - Confidentiality/NDA: Is any protection included? (Lack of this is CRITICAL)
   - Escrow/Holdback: Are funds set aside for breaches?
   - Survival Periods: Do reps last < 18 months?
   - MAC Clause: Is there a "Material Adverse Change" exit?
   
2. REGULATORY & SECTOR RISKS:
   - Energy Regulatory (FERC/DOE): Are regulatory approvals closing conditions? Are there backup plans?
   - Antitrust: Is there a "Hell or High Water" or termination fee?

3. OPERATIONAL DISRUPTIONS:
   - Transition Services: Is 60 days too short? (Energy usually needs 90-180)
   - Indemnification Gaps: Are notice periods (e.g. 60 days) too short to discover losses?

4. FINANCIAL VOLATILITY:
   - Stock Consideration: Is the buyer's stock price protected?

For EACH issue found, return a JSON object with:
- category: [jurisdiction, financial, legal, operational, compliance, vague_language, missing_info, liability, intellectual_property, tax, employee, customer, other]
- severity: [CRITICAL, HIGH, MEDIUM, LOW]
- title: Senior-level risk title
- description: Concise legal/business explanation (2 sentences)
- quote: Exact text from contract (or "N/A" if missing)
- score: 1-10
- recommendation: Specific negotiation strategy

Return ONLY a JSON array. If no flags, return [].

Contract text:
{text}

JSON response:`;

function generateId(): string {
  return `llm_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function chunkText(text: string, maxChars: number = 15000): string[] {
  if (text.length <= maxChars) {
    return [text];
  }

  const chunks: string[] = [];
  let currentChunk = '';

  // Split by paragraphs to avoid breaking mid-sentence
  const paragraphs = text.split('\n\n');

  for (const para of paragraphs) {
    if (currentChunk.length + para.length > maxChars) {
      if (currentChunk) {
        chunks.push(currentChunk);
      }
      currentChunk = para;
    } else {
      currentChunk += currentChunk ? '\n\n' + para : para;
    }
  }

  if (currentChunk) {
    chunks.push(currentChunk);
  }

  return chunks;
}

async function callLLM(prompt: string): Promise<any> {
  try {
    // Using z-ai-web-dev-sdk for LLM analysis
    const ZAI = await import('z-ai-web-dev-sdk').then(m => m.default || m);

    if (typeof ZAI.create !== 'function') {
      console.error('  ZAI.create is not a function. SDK content:', Object.keys(ZAI));
      return [];
    }

    const zai = await ZAI.create();

    console.log('  Calling LLM API via zai.chat.completions.create...');

    // Call the LLM with the prompt and a timeout
    const chatPromise = zai.chat.completions.create({
      messages: [
        {
          role: 'system',
          content: 'You are an expert M&A attorney. You always respond with valid JSON arrays.'
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      stream: false,
      thinking: { type: "disabled" }
    });

    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('LLM call timed out after 60s')), 60000)
    );

    const response = await Promise.race([chatPromise, timeoutPromise]) as any;

    // Parse the response based on the observed structure in skills/LLM/scripts/chat.ts
    const responseText = response.choices?.[0]?.message?.content ||
      response.content ||
      response.message?.content ||
      JSON.stringify(response);

    if (!responseText) {
      console.warn('  LLM returned empty response');
      return [];
    }

    // Clean response
    let cleanedText = responseText.trim();
    const jsonMatch = cleanedText.match(/```json\s*([\s\S]*?)\s*```/) ||
      cleanedText.match(/```\s*([\s\S]*?)\s*```/);

    if (jsonMatch) {
      cleanedText = jsonMatch[1];
    } else if (cleanedText.includes('[') && cleanedText.includes(']')) {
      // Fallback: try to find the array if no code block
      const start = cleanedText.indexOf('[');
      const end = cleanedText.lastIndexOf(']');
      if (start !== -1 && end !== -1 && end > start) {
        cleanedText = cleanedText.substring(start, end + 1);
      }
    }

    cleanedText = cleanedText.trim();

    try {
      return JSON.parse(cleanedText);
    } catch (parseError) {
      console.error('  Failed to parse LLM JSON:', cleanedText.substring(0, 100) + '...');
      return [];
    }
  } catch (error) {
    console.error('  LLM call error:', error instanceof Error ? error.message : error);
    return [];
  }
}


async function analyzeChunk(chunk: string, chunkIndex: number): Promise<RedFlag[]> {
  try {
    console.log(`  Analyzing chunk ${chunkIndex + 1} (${chunk.length} characters)`);

    const prompt = ANALYSIS_PROMPT.replace('{text}', chunk);

    const response = await callLLM(prompt);

    // Handle different response formats
    let flagsArray: any[] = [];

    if (Array.isArray(response)) {
      flagsArray = response;
    } else if (response && response.flags && Array.isArray(response.flags)) {
      flagsArray = response.flags;
    } else if (response && typeof response === 'object') {
      flagsArray = [response];
    }

    // Convert to our RedFlag format
    const flags: RedFlag[] = [];

    for (const item of flagsArray) {
      try {
        flags.push({
          id: generateId(),
          category: item.category || 'other',
          severity: item.severity || 'MEDIUM',
          title: item.title || 'Unspecified Issue',
          description: item.description || '',
          location: (item.quote || item.location || '').substring(0, 500),
          score: Math.min(10, Math.max(1, parseInt(item.score) || 5)),
          source: 'llm_analyzer',
          recommendation: item.recommendation
        });
      } catch (err) {
        console.error('Failed to parse individual flag:', err);
      }
    }

    console.log(`  Chunk ${chunkIndex + 1} found ${flags.length} flags`);

    return flags;
  } catch (error) {
    console.error(`Error analyzing chunk ${chunkIndex}:`, error);
    return [];
  }
}

export async function analyzeWithLLM(text: string): Promise<RedFlag[]> {
  console.log('Running LLM-based analysis...');

  try {
    // Split text into manageable chunks
    const chunks = chunkText(text, 15000);
    console.log(`Text split into ${chunks.length} chunks for LLM analysis`);

    // Analyze chunks sequentially (to avoid overwhelming the API)
    const allFlags: RedFlag[] = [];

    for (let i = 0; i < chunks.length; i++) {
      const flags = await analyzeChunk(chunks[i], i);
      allFlags.push(...flags);

      // Small delay between chunks to avoid rate limiting
      if (i < chunks.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }

    console.log(`LLM analyzer found ${allFlags.length} red flags`);

    return allFlags;
  } catch (error) {
    console.error('LLM analysis error:', error);
    // Return empty array on error to allow the analysis to continue with rule-based flags only
    return [];
  }
}
