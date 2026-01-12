const PDFParser = require('pdf2json');

export async function parsePDF(filePath: string): Promise<string> {
  return new Promise((resolve) => {
    try {
      const pdfParser = new PDFParser(null, 1);

      pdfParser.on("pdfParser_dataError", (errData: any) => {
        console.error('PDF parsing error:', errData.parserError);
        resolve(''); // Return empty string to allow analysis to fail gracefully
      });

      pdfParser.on("pdfParser_dataReady", () => {
        let text = pdfParser.getRawTextContent();

        // Normalize text: pdf2json raw text often has extra spaces between characters
        // and uses specific page break markers.
        text = text.replace(/----------------Page \(\d+\) Break----------------/g, '\n');

        // Fix spaced-out characters (e.g., "P a y m e n t" -> "Payment")
        // This regex looks for 3 or more occurrences of "char space" to identify spaced text
        if (/(?:[A-Za-z]\s){3,}/.test(text)) {
          // First, handle the most obvious spaced-out words
          text = text.replace(/([A-Z])\s(?=[A-Z]\s)/g, '$1');
          // Then handle lowercase if they are also spaced
          text = text.replace(/([a-z])\s(?=[a-z]\s)/g, '$1');
          // Final pass: reduce double spaces to single spaces
          text = text.replace(/\s+/g, ' ');
        } else {
          // Regular cleanup of multiple spaces
          text = text.replace(/\s+/g, ' ');
        }

        console.log(`Successfully extracted ${text.length} characters from PDF using pdf2json: ${filePath}`);
        resolve(text || '');
      });

      pdfParser.loadPDF(filePath);
    } catch (error) {
      console.error('PDF parsing catch error:', error);
      resolve('');
    }
  });
}

export async function extractTextFromPDFBuffer(buffer: Buffer): Promise<string> {
  // pdf2json loadPDF works better with file paths, but we can use parseBuffer if available
  // To keep it simple and consistent, we'll suggest using parsePDF with the temp file
  return '';
}


