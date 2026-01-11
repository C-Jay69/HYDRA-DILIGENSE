const pdfParse = require('pdf-parse');
const fs = require('fs');
const path = require('path');

async function test() {
    try {
        const filePath = path.join(process.cwd(), 'upload', 'M&A DUE DILLIGENCE ANALYZER-SETUP GUIDE.pdf');
        console.log('Testing file:', filePath);
        if (!fs.existsSync(filePath)) {
            console.error('File does not exist!');
            process.exit(1);
        }
        const dataBuffer = fs.readFileSync(filePath);
        console.log('Buffer size:', dataBuffer.length);
        const data = await pdfParse(dataBuffer);
        console.log('--- DATA START ---');
        console.log('Pages:', data.numpages);
        console.log('Text extracted length:', data.text ? data.text.length : 0);
        console.log('First 100 chars:', data.text ? data.text.substring(0, 100) : 'N/A');
        console.log('--- DATA END ---');
        process.exit(0);
    } catch (e) {
        console.error('Error during PDF parsing:', e);
        process.exit(1);
    }
}
test();
