// PDF text extraction using pdf-parse
// We use require instead of import to avoid bundling issues with Next.js/Webpack
const pdfParse = require('pdf-parse');
import { readFile } from 'fs/promises';

export async function parsePDF(filePath: string): Promise<string> {
  try {
    const dataBuffer = await readFile(filePath);
    const data = await pdfParse(dataBuffer);

    console.log(`Successfully extracted ${data.text.length} characters from PDF: ${filePath}`);
    return data.text || '';
  } catch (error) {
    console.error('PDF parsing error:', error);
    // Return empty string rather than throwing to allow analysis to continue
    return '';
  }
}

export async function extractTextFromPDFBuffer(buffer: Buffer): Promise<string> {
  try {
    const data = await pdfParse(buffer);
    return data.text || '';
  } catch (error) {
    console.error('PDF buffer parsing error:', error);
    return '';
  }
}

