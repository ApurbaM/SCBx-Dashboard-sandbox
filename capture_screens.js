const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const URL = 'http://localhost:8888/SCB_Morning_Briefing_Demo.html';
const OUT = path.join(__dirname, 'figma_screens');

async function run() {
  if (!fs.existsSync(OUT)) fs.mkdirSync(OUT);

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
    defaultViewport: { width: 1400, height: 900, deviceScaleFactor: 2 }
  });
  const page = await browser.newPage();
  await page.goto(URL, { waitUntil: 'networkidle0' });
  await sleep(1500);

  const phoneSelector = '.phone';

  async function shot(name) {
    await sleep(800);
    const el = await page.$(phoneSelector);
    await el.screenshot({ path: path.join(OUT, `${name}.png`) });
    console.log(`  ✓ ${name}.png`);
  }

  // --- 1. Lock Screen ---
  console.log('\n📱 Capturing screens...\n');
  await shot('01_Lock_Screen');

  // --- 2. Home Screen ---
  await page.click('.notification');
  await sleep(600);
  await shot('02_Home');

  // --- 3. Home scrolled (goals visible) ---
  await page.evaluate(() => {
    const body = document.querySelector('#homeBody');
    if (body) body.scrollTop = body.scrollHeight;
  });
  await sleep(500);
  await shot('03_Home_Scrolled');
  await page.evaluate(() => {
    const body = document.querySelector('#homeBody');
    if (body) body.scrollTop = 0;
  });

  // --- 4. Morning Briefing ---
  await page.evaluate(() => navigate('briefing'));
  await sleep(1200);
  await shot('04_Briefing_Top');

  // --- 5. Briefing scrolled ---
  await page.evaluate(() => {
    const body = document.querySelector('#briefingBody');
    if (body) body.scrollTop = body.scrollHeight;
  });
  await sleep(500);
  await shot('05_Briefing_Scrolled');
  await page.evaluate(() => {
    const body = document.querySelector('#briefingBody');
    if (body) body.scrollTop = 0;
  });

  // --- 6. Financial Wellness Modal ---
  await page.evaluate(() => showWellness());
  await sleep(1000);
  await shot('06_Wellness');
  await page.evaluate(() => hideWellness());
  await sleep(400);

  // --- 7. Portfolio ---
  await page.evaluate(() => navigate('portfolio'));
  await sleep(800);
  await shot('07_Portfolio');

  // --- 8. Profile ---
  await page.evaluate(() => navigate('profile'));
  await sleep(800);
  await shot('08_Profile');

  // --- 9. Chat — initial state ---
  await page.evaluate(() => navigate('chat'));
  await sleep(1500);
  await shot('09_Chat_Initial');

  // --- 10. Chat — bill payment flow ---
  await page.evaluate(() => startChatFlow('bill'));
  await sleep(2500);
  await shot('10_Chat_Bill_Options');

  // --- 11. Chat — payment confirmation screen ---
  await page.evaluate(() => chatAction('payFull'));
  await sleep(2000);
  await shot('11_Chat_Pay_Confirm');

  // --- 12. Chat — payment success ---
  await page.evaluate(() => chatAction('confirmPay'));
  await sleep(3000);
  await shot('12_Chat_Pay_Success');

  // --- 13. Chat — spend insights ---
  // Reset chat for a clean insights view
  await page.evaluate(() => {
    document.getElementById('chatMessages').innerHTML = '';
    chatInited = false;
  });
  await page.evaluate(() => navigate('chat'));
  await sleep(1500);
  await page.evaluate(() => startChatFlow('insights'));
  await sleep(2500);
  await shot('13_Chat_Insights');

  // --- 14. Chat — card upgrade (service-to-sales) ---
  await page.evaluate(() => {
    document.getElementById('chatMessages').innerHTML = '';
  });
  await page.evaluate(() => startChatFlow('s2s_card'));
  await sleep(3000);
  await shot('14_Chat_Card_Upgrade');

  // --- 15. Chat — card approved ---
  await page.evaluate(() => chatAction('applyCard'));
  await sleep(3000);
  await shot('15_Chat_Card_Approved');

  // --- 16. Chat — PointX ---
  await page.evaluate(() => {
    document.getElementById('chatMessages').innerHTML = '';
  });
  await page.evaluate(() => startChatFlow('pointx'));
  await sleep(2500);
  await shot('16_Chat_PointX');

  // --- 17. Chat — portfolio check ---
  await page.evaluate(() => {
    document.getElementById('chatMessages').innerHTML = '';
  });
  await page.evaluate(() => startChatFlow('portfolio'));
  await sleep(2500);
  await shot('17_Chat_Portfolio');

  await browser.close();

  const files = fs.readdirSync(OUT).filter(f => f.endsWith('.png'));
  console.log(`\n✅ Done! ${files.length} screens saved to: ${OUT}\n`);
  console.log('Next steps:');
  console.log('  1. Open Figma → New file');
  console.log('  2. Drag all PNGs from the figma_screens folder into the canvas');
  console.log('  3. Frame each image (Ctrl+Alt+G), set to iPhone 14 Pro (393×852)');
  console.log('  4. Switch to Prototype tab and wire the flows\n');
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

run().catch(err => { console.error('Error:', err); process.exit(1); });
