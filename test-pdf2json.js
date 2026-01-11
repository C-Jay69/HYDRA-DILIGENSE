const PDFParser = require("pdf2json");
const fs = require('fs');
const path = require('path');

function test() {
    try {
        const pdfParser = new PDFParser(null, 1);
        const filePath = path.join(process.cwd(), 'upload', 'M&A DUE DILLIGENCE ANALYZER-SETUP GUIDE.pdf');

        console.log('Testing file:', filePath);

        pdfParser.on("pdfParser_dataError", errData => {
            console.error('Parser Error:', errData.parserError);
            process.exit(1);
        });

        pdfParser.on("pdfParser_dataReady", pdfData => {
            const text = pdfParser.getRawTextContent();
            console.log('Text extracted length:', text.length);
            console.log('Preview:', text.substring(0, 200));
            process.exit(0);
        });

        pdfParser.loadPDF(filePath);
    } catch (e) {
        console.error('Catch Error:', e);
        process.exit(1);
    }
}
test();
