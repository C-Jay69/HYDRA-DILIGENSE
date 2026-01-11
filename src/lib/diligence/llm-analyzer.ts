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

const ANALYSIS_PROMPT = `You are an expert M&A attorney reviewing a contract section for red flags.

Analyze the following contract section and identify any red flags related to:
- Vague or undefined terms that create ambiguity
- Missing critical information or deferred disclosures
- Unusual liability limitations or indemnification gaps
- Suspicious payment structures or undefined earnout terms
- Jurisdiction or dispute resolution concerns
- Customer concentration or key person dependencies
- Tax, IP, compliance, or regulatory risks
- Any other material concerns

For EACH red flag you identify, return a JSON object with:
- category: one of [jurisdiction, financial, legal, operational, compliance, vague_language, missing_info, liability, intellectual_property, tax, employee, customer, other]
- severity: one of [CRITICAL, HIGH, MEDIUM, LOW]
- title: brief title (max 80 chars)
- description: explanation of why this is concerning (2-3 sentences)
- quote: exact text from the section that triggered this flag
- score: risk score from 1-10
- recommendation: specific action to take

Return ONLY a JSON array of red flags. If no red flags, return empty array [].

Contract section:
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
    const sdk = await import('z-ai-web-dev-sdk');

    // Handle different export patterns (named or default)
    const LLMClass = sdk.LLM || (sdk as any).default?.LLM || sdk.default;

    if (typeof LLMClass !== 'function') {
      console.error('  LLM is not a constructor. SDK content:', Object.keys(sdk));
      return [];
    }

    // Create an LLM client instance
    const llm = new (LLMClass as any)({
      apiKey: process.env.AI_SDK_API_KEY || ''
    });

    console.log('  Calling LLM API...');

    // ... (rest of the function with timeout logic)
    const chatPromise = llm.chat({
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
      temperature: 0.3,
      maxTokens: 2000,
      model: 'open-source'
    });

    const timeoutPromise = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('LLM call timed out after 60s')), 60000)
    );

    const response = await Promise.race([chatPromise, timeoutPromise]) as any;

    // Parse the response
    const responseText = response.content || response.message?.content || response.text || '';

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
