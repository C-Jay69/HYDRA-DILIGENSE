const pdfjs = require('pdfjs-dist/legacy/build/pdf.js');
const fs = require('fs');
const path = require('path');

async function test() {
    try {
        const filePath = path.join(process.cwd(), 'upload', 'M&A DUE DILLIGENCE ANALYZER-SETUP GUIDE.pdf');
        console.log('Testing file:', filePath);
        const data = new Uint8Array(fs.readFileSync(filePath));

        const loadingTask = pdfjs.getDocument({
            data: data,
            useSystemFonts: true,
            disableFontFace: true,
            isEvalSupported: false
        });

        const pdf = await loadingTask.promise;
        console.log('Pages:', pdf.numPages);

        let fullText = '';
        for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const textContent = await page.getTextContent();
            const pageText = textContent.items.map(item => item.str).join(' ');
            fullText += pageText + ' ';
        }

        console.log('Text length:', fullText.length);
        console.log('Preview:', fullText.substring(0, 100));
        process.exit(0);
    } catch (error) {
        console.error('Error:', error);
        process.exit(1);
    }
}

test();
