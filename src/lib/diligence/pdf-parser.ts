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
        const text = pdfParser.getRawTextContent();
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


