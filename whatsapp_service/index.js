try { require('dotenv').config(); } catch (e) {}
const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcodeTerminal = require('qrcode-terminal');
const express = require('express');

let QRCode = null;
try { QRCode = require('qrcode'); } catch (e) {}

const PORT = process.env.PORT || 3000;
const API_KEY = process.env.WA_API_KEY || '';
const CHROME_PATH = process.env.CHROME_PATH ||
    (process.platform === 'win32'
        ? 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
        : '/usr/bin/google-chrome-stable');
const DATA_PATH = process.env.WA_DATA_PATH || './.wwebjs_auth';

const app = express();
app.use(express.json({ limit: '50mb' }));

// API key check (sirf tab jab WA_API_KEY set ho)
app.use((req, res, next) => {
    if (!API_KEY) return next();
    const key = req.headers['x-api-key'] || (req.path === '/qr' ? req.query.key : null);
    if (key !== API_KEY) {
        return res.status(401).json({ status: 'error', message: 'Unauthorized' });
    }
    next();
});

// ---------------- WhatsApp client ----------------
const client = new Client({
    authStrategy: new LocalAuth({ dataPath: DATA_PATH }),
    webVersionCache: {
        type: 'remote',
        remotePath: 'https://raw.githubusercontent.com/wppconnect-team/wa-version-https/main/html/2.3000.1014111620-alpha.html',
    },
    puppeteer: {
        headless: true,
        protocolTimeout: 300000,
        executablePath: CHROME_PATH,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu',
            '--disable-extensions',
            '--disable-component-update'
        ]
    }
});

let isReady = false;
let lastQr = null;
let recovering = null;

client.on('qr', (qr) => {
    isReady = false;
    lastQr = qr;
    console.log('\n--- SCAN THIS QR CODE WITH YOUR WHATSAPP ---\n');
    qrcodeTerminal.generate(qr, { small: true });
});

client.on('ready', () => {
    isReady = true;
    lastQr = null;
    console.log('✅ WhatsApp Microservice Ready & Connected!');
});

client.on('auth_failure', (msg) => {
    isReady = false;
    console.error('❌ Auth failure:', msg);
});

client.on('disconnected', (reason) => {
    console.log('⚠️ Disconnected:', reason);
    recoverClient('disconnected');
});

// Safe init function
function initializeClient() {
    client.initialize().catch((e) => {
        console.error('❌ Init failed:', e.message || e);
        setTimeout(() => {
            console.log('🔄 Retrying initialize...');
            initializeClient();
        }, 5000);
    });
}

initializeClient();

// ---------------- Auto-recovery helpers ----------------
function isFrameError(err) {
    const msg = String((err && err.message) || err);
    return /detached Frame|Execution context was destroyed|Target closed|Session closed|Protocol error|Navigating frame was detached/i.test(msg);
}

async function waitUntilReady(ms = 60000) {
    const start = Date.now();
    while (!isReady) {
        if (Date.now() - start > ms) throw new Error('Client ready nahi hua (timeout)');
        await new Promise((r) => setTimeout(r, 1000));
    }
}

function recoverClient(reason) {
    if (recovering) return recovering;
    console.log(`🔄 Recovering WhatsApp client (${reason})...`);
    isReady = false;
    recovering = (async () => {
        try { await client.destroy(); } catch (e) {}
        await new Promise((r) => setTimeout(r, 4000));
        initializeClient();
        await waitUntilReady(60000);
        console.log('✅ Client recovered');
    })()
        .catch((e) => console.error('❌ Recovery failed:', e.message))
        .finally(() => { recovering = null; });
    return recovering;
}

async function doSend({ cleanNumber, message, file_base64, filename, mimetype }) {
    const numberDetails = await client.getNumberId(cleanNumber);
    if (!numberDetails) return { notRegistered: true };

    const chatId = numberDetails._serialized;

    if (file_base64) {
        const pureBase64 = file_base64.replace(/^data:.*?;base64,/, '');
        const media = new MessageMedia(
            mimetype || 'application/octet-stream',
            pureBase64,
            filename || 'document'
        );
        await client.sendMessage(chatId, media, {
            caption: message || '',
            sendMediaAsDocument: true,
            sendSeen: false
        });
    } else {
        await client.sendMessage(chatId, message || '', { sendSeen: false });
    }
    return { chatId };
}

// ---------------- Routes ----------------
app.get('/status', (req, res) => {
    res.json({ status: 'ok', ready: isReady, needs_qr: !!lastQr });
});

app.get('/qr', async (req, res) => {
    if (isReady) return res.send('✅ Already connected');
    if (!lastQr) return res.send('QR abhi ban raha hai, 10 sec baad refresh karo');
    if (!QRCode) return res.send('`npm i qrcode` chalao, ya terminal wala QR scan karo');
    const img = await QRCode.toDataURL(lastQr, { width: 320 });
    res.send(`<meta http-equiv="refresh" content="20">
              <h3>WhatsApp → Linked Devices → Link a device</h3>
              <img src="${img}">`);
});

app.post('/send', async (req, res) => {
    if (recovering) { try { await recovering; } catch (e) {} }

    // Request aane par agar client instant ready na ho toh wait karega
    if (!isReady) {
        try {
            await waitUntilReady(15000);
        } catch (e) {
            return res.status(503).json({ status: 'error', message: 'WhatsApp client ready nahi hai, thodi der baad try karo' });
        }
    }

    const { phone_number, message, file_base64, filename, mimetype } = req.body;
    if (!phone_number) {
        return res.status(400).json({ status: 'error', message: 'phone_number is required' });
    }

    if (file_base64 && file_base64.length * 0.75 > 20 * 1024 * 1024) {
        return res.status(413).json({ status: 'error', message: 'File 20 MB se badi hai' });
    }

    let cleanNumber = String(phone_number).replace(/\D/g, '');
    if (cleanNumber.length === 10) cleanNumber = '91' + cleanNumber;

    const args = { cleanNumber, message, file_base64, filename, mimetype };

    console.log('📩 Incoming request received...');

    try {
        let result;
        try {
            result = await doSend(args);
        } catch (err) {
            if (!isFrameError(err)) throw err;
            console.warn('⚠️ Frame/page error, client restart karke ek baar retry kar raha hu...');
            await recoverClient('frame error');
            if (!isReady) throw new Error('WhatsApp reconnect nahi ho paya, thodi der baad try karo');
            result = await doSend(args);
        }

        if (result.notRegistered) {
            return res.status(400).json({ status: 'error', message: 'Number WhatsApp par registered nahi hai!' });
        }

        console.log(`✅ Message successfully sent to ${result.chatId}`);
        res.json({ status: 'success', message: 'WhatsApp message sent successfully!' });
    } catch (error) {
        console.error('❌ Error sending message:', error);
        res.status(500).json({ status: 'error', error: error.toString() });
    }
});

app.listen(PORT, '127.0.0.1', () => console.log(`🚀 Microservice running on http://127.0.0.1:${PORT}`));

// Clean shutdown
async function shutdown() {
    try { await client.destroy(); } catch (e) {}
    process.exit(0);
}
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
process.on('unhandledRejection', (e) => console.error('Unhandled rejection:', e));



























































// try { require('dotenv').config(); } catch (e) {}
// const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
// const qrcodeTerminal = require('qrcode-terminal');
// const express = require('express');

// let QRCode = null;
// try { QRCode = require('qrcode'); } catch (e) {}

// const PORT = process.env.PORT || 3000;
// const API_KEY = process.env.WA_API_KEY || '';
// const CHROME_PATH = process.env.CHROME_PATH ||
//     (process.platform === 'win32'
//         ? 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
//         : '/usr/bin/google-chrome-stable');
// const DATA_PATH = process.env.WA_DATA_PATH || './.wwebjs_auth';

// const app = express();
// app.use(express.json({ limit: '50mb' }));

// // API key check (sirf tab jab WA_API_KEY set ho)
// app.use((req, res, next) => {
//     if (!API_KEY) return next();
//     const key = req.headers['x-api-key'] || (req.path === '/qr' ? req.query.key : null);
//     if (key !== API_KEY) {
//         return res.status(401).json({ status: 'error', message: 'Unauthorized' });
//     }
//     next();
// });

// // ---------------- WhatsApp client ----------------
// const client = new Client({
//     authStrategy: new LocalAuth({ dataPath: DATA_PATH }),
//     puppeteer: {
//         headless: true,
//         protocolTimeout: 120000,
//         executablePath: CHROME_PATH,
//         args: [
//             '--no-sandbox',
//             '--disable-setuid-sandbox',
//             '--disable-dev-shm-usage',
//             '--disable-accelerated-2d-canvas',
//             '--no-first-run',
//             '--disable-gpu',
//             '--single-process' //
//         ]
//     }
// });

// let isReady = false;
// let lastQr = null;
// let recovering = null;

// client.on('qr', (qr) => {
//     isReady = false;
//     lastQr = qr;
//     console.log('\n--- SCAN THIS QR CODE WITH YOUR WHATSAPP ---\n');
//     qrcodeTerminal.generate(qr, { small: true });
// });

// client.on('ready', () => {
//     isReady = true;
//     lastQr = null;
//     console.log('✅ WhatsApp Microservice Ready & Connected!');
// });

// client.on('auth_failure', (msg) => {
//     isReady = false;
//     console.error('❌ Auth failure:', msg);
// });

// client.on('disconnected', (reason) => {
//     console.log('⚠️ Disconnected:', reason);
//     recoverClient('disconnected');
// });

// client.initialize().catch((e) => console.error('❌ Init failed:', e));

// // ---------------- Auto-recovery helpers ----------------
// function isFrameError(err) {
//     const msg = String((err && err.message) || err);
//     return /detached Frame|Execution context was destroyed|Target closed|Session closed|Protocol error|Navigating frame was detached/i.test(msg);
// }

// async function waitUntilReady(ms) {
//     const start = Date.now();
//     while (!isReady) {
//         if (Date.now() - start > ms) throw new Error('Client ready nahi hua (timeout)');
//         await new Promise((r) => setTimeout(r, 1000));
//     }
// }

// function recoverClient(reason) {
//     if (recovering) return recovering;
//     console.log(`🔄 Recovering WhatsApp client (${reason})...`);
//     isReady = false;
//     recovering = (async () => {
//         try { await client.destroy(); } catch (e) {}
//         await new Promise((r) => setTimeout(r, 3000));
//         await client.initialize();
//         await waitUntilReady(90000);
//         console.log('✅ Client recovered');
//     })()
//         .catch((e) => console.error('❌ Recovery failed:', e.message))
//         .finally(() => { recovering = null; });
//     return recovering;
// }

// async function doSend({ cleanNumber, message, file_base64, filename, mimetype }) {
//     const numberDetails = await client.getNumberId(cleanNumber);
//     if (!numberDetails) return { notRegistered: true };

//     const chatId = numberDetails._serialized;

//     if (file_base64) {
//         const pureBase64 = file_base64.replace(/^data:.*?;base64,/, '');
//         const media = new MessageMedia(
//             mimetype || 'application/octet-stream',
//             pureBase64,
//             filename || 'document'
//         );
//         await client.sendMessage(chatId, media, {
//             caption: message || '',
//             sendMediaAsDocument: true,
//             sendSeen: false
//         });
//     } else {
//         await client.sendMessage(chatId, message || '', { sendSeen: false });
//     }
//     return { chatId };
// }

// // ---------------- Routes ----------------
// app.get('/status', (req, res) => {
//     res.json({ status: 'ok', ready: isReady, needs_qr: !!lastQr });
// });

// app.get('/qr', async (req, res) => {
//     if (isReady) return res.send('✅ Already connected');
//     if (!lastQr) return res.send('QR abhi ban raha hai, 10 sec baad refresh karo');
//     if (!QRCode) return res.send('`npm i qrcode` chalao, ya terminal wala QR scan karo');
//     const img = await QRCode.toDataURL(lastQr, { width: 320 });
//     res.send(`<meta http-equiv="refresh" content="20">
//               <h3>WhatsApp → Linked Devices → Link a device</h3>
//               <img src="${img}">`);
// });

// app.post('/send', async (req, res) => {
//     if (recovering) { try { await recovering; } catch (e) {} }

//     if (!isReady) {
//         return res.status(503).json({ status: 'error', message: 'WhatsApp client ready nahi hai, thodi der baad try karo' });
//     }

//     const { phone_number, message, file_base64, filename, mimetype } = req.body;
//     if (!phone_number) {
//         return res.status(400).json({ status: 'error', message: 'phone_number is required' });
//     }

//     // Bahut badi file tab ko crash kar sakti hai
//     if (file_base64 && file_base64.length * 0.75 > 20 * 1024 * 1024) {
//         return res.status(413).json({ status: 'error', message: 'File 20 MB se badi hai' });
//     }

//     let cleanNumber = String(phone_number).replace(/\D/g, '');
//     if (cleanNumber.length === 10) cleanNumber = '91' + cleanNumber;

//     const args = { cleanNumber, message, file_base64, filename, mimetype };

//     console.log('📩 Incoming request received...');

//     try {
//         let result;
//         try {
//             result = await doSend(args);
//         } catch (err) {
//             if (!isFrameError(err)) throw err;
//             console.warn('⚠️ Frame/page error, client restart karke ek baar retry kar raha hu...');
//             await recoverClient('frame error');
//             if (!isReady) throw new Error('WhatsApp reconnect nahi ho paya, thodi der baad try karo');
//             result = await doSend(args);
//         }

//         if (result.notRegistered) {
//             return res.status(400).json({ status: 'error', message: 'Number WhatsApp par registered nahi hai!' });
//         }

//         console.log(`✅ Message successfully sent to ${result.chatId}`);
//         res.json({ status: 'success', message: 'WhatsApp message sent successfully!' });
//     } catch (error) {
//         console.error('❌ Error sending message:', error);
//         res.status(500).json({ status: 'error', error: error.toString() });
//     }
// });

// app.listen(PORT, '127.0.0.1', () => console.log(`🚀 Microservice running on http://127.0.0.1:${PORT}`));

// // Clean shutdown
// async function shutdown() {
//     try { await client.destroy(); } catch (e) {}
//     process.exit(0);
// }
// process.on('SIGINT', shutdown);
// process.on('SIGTERM', shutdown);
// process.on('unhandledRejection', (e) => console.error('Unhandled rejection:', e));























































































// const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
// const qrcode = require('qrcode-terminal');
// const express = require('express');

// const app = express();
// app.use(express.json({ limit: '50mb' }));

// const client = new Client({
//     authStrategy: new LocalAuth(),
//     puppeteer: {
//         headless: true,
//         protocolTimeout: 120000,
//         executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
//         args: [
//             '--no-sandbox',
//             '--disable-setuid-sandbox',
//             '--disable-dev-shm-usage',
//             '--disable-accelerated-2d-canvas',
//             '--no-first-run',
//             '--disable-gpu'
//         ]
//     }
// });

// let isReady = false;

// client.on('qr', (qr) => {
//     isReady = false;
//     console.log('\n--- SCAN THIS QR CODE WITH YOUR WHATSAPP ---\n');
//     qrcode.generate(qr, { small: true });
// });

// client.on('ready', () => {
//     isReady = true;
//     console.log('✅ WhatsApp Microservice Ready & Connected!');
// });

// client.on('auth_failure', (msg) => {
//     isReady = false;
//     console.error('❌ Auth failure:', msg);
// });

// client.on('disconnected', (reason) => {
//     isReady = false;
//     console.log('⚠️ Disconnected:', reason);
// });

// client.initialize();

// app.post('/send', async (req, res) => {
//     if (!isReady) {
//         return res.status(503).json({ status: 'error', message: 'WhatsApp client is still initializing...' });
//     }

//     console.log('📩 Incoming request received...');
//     const { phone_number, message, file_base64, filename, mimetype } = req.body;

//     if (!phone_number) {
//         return res.status(400).json({ status: 'error', message: 'phone_number is required' });
//     }

//     try {
//         let cleanNumber = String(phone_number).replace(/\D/g, '');
//         if (cleanNumber.length === 10) cleanNumber = '91' + cleanNumber;

//         const numberDetails = await client.getNumberId(cleanNumber);
//         if (!numberDetails) {
//             return res.status(400).json({ status: 'error', message: 'Number WhatsApp par registered nahi hai!' });
//         }

//         const chatId = numberDetails._serialized;

//         if (file_base64) {
//             // "data:application/pdf;base64," prefix ho to hata do
//             const pureBase64 = file_base64.replace(/^data:.*?;base64,/, '');

//             const media = new MessageMedia(
//                 mimetype || 'application/pdf',
//                 pureBase64,
//                 filename || 'Salary_Slip.pdf'
//             );

//             await client.sendMessage(chatId, media, {
//                 caption: message || '',
//                 sendMediaAsDocument: true,
//                 sendSeen: false            // 👈 main fix
//             });
//         } else {
//             await client.sendMessage(chatId, message || '', {
//                 sendSeen: false            // 👈 main fix
//             });
//         }

//         console.log(`✅ Message successfully sent to ${chatId}`);
//         res.json({ status: 'success', message: 'WhatsApp message sent successfully!' });

//     } catch (error) {
//         console.error('❌ Error sending message:', error);
//         res.status(500).json({ status: 'error', error: error.toString() });
//     }
// });

// app.listen(3000, () => console.log('🚀 Microservice running on http://localhost:3000'));






























































// const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
// const qrcode = require('qrcode-terminal');
// const express = require('express');

// const app = express();
// app.use(express.json({ limit: '50mb' }));

// const client = new Client({
//     authStrategy: new LocalAuth(),
//     puppeteer: {
//         headless: true,
//         protocolTimeout: 120000,
//         executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
//         args: [
//             '--no-sandbox',
//             '--disable-setuid-sandbox',
//             '--disable-dev-shm-usage',
//             '--disable-accelerated-2d-canvas',
//             '--no-first-run',
//             '--no-zygote',
//             '--disable-gpu'
//         ]
//     }
// });

// let isReady = false;

// client.on('qr', (qr) => {
//     isReady = false;
//     console.log('\n--- SCAN THIS QR CODE WITH YOUR WHATSAPP ---\n');
//     qrcode.generate(qr, { small: true });
// });

// client.on('ready', () => {
//     isReady = true;
//     console.log('✅ WhatsApp Microservice Ready & Connected!');
// });

// client.on('disconnected', () => {
//     isReady = false;
// });

// client.initialize();

// app.post('/send', async (req, res) => {
//     if (!isReady) {
//         return res.status(503).json({ status: 'error', message: 'WhatsApp client is still initializing...' });
//     }

//     console.log('📩 Incoming request received...');
//     const { phone_number, message, file_base64, filename, mimetype } = req.body;

//     try {
//         let cleanNumber = String(phone_number).replace(/\D/g, '');
//         if (cleanNumber.length === 10) cleanNumber = '91' + cleanNumber;

//         // 1. Get exact WhatsApp ID object (Injects internal store ID)
//         const numberDetails = await client.getNumberId(cleanNumber);
        
//         if (!numberDetails) {
//             return res.status(400).json({ status: 'error', message: 'Number WhatsApp par registered nahi hai!' });
//         }

//         const chatId = numberDetails._serialized;

//         // 2. Media prepare karein
//         let media = null;
//         if (file_base64) {
//             media = new MessageMedia(
//                 mimetype || 'application/pdf',
//                 file_base64,
//                 filename || 'Salary_Slip.pdf'
//             );
//         }

//         // 3. Send message using serialized target ID
//         if (media) {
//             await client.sendMessage(chatId, media, {
//                 caption: message || '',
//                 sendMediaAsDocument: true
//             });
//         } else {
//             await client.sendMessage(chatId, message || '');
//         }

//         console.log(`✅ Message successfully sent to ${chatId}`);
//         res.json({ status: 'success', message: 'WhatsApp message sent successfully!' });

//     } catch (error) {
//         console.error('❌ Error sending message:', error);
//         res.status(500).json({ status: 'error', error: error.toString() });
//     }
// });

// app.listen(3000, () => console.log('🚀 Microservice running on http://localhost:3000'));