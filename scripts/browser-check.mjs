// Optional browser smoke test. Install Playwright and @sparticuz/chromium locally
// with npm install --no-save --package-lock=false playwright @sparticuz/chromium.
// Needs a static server at TEST_URL (default http://127.0.0.1:8000).
import chromium from '@sparticuz/chromium';
import {chromium as playwright} from 'playwright';
import fs from 'node:fs';
const base=process.env.TEST_URL || 'http://127.0.0.1:8000';
const browser=await playwright.launch({headless:true,executablePath:await chromium.executablePath(),args:chromium.args});
const page=await browser.newPage({viewport:{width:1440,height:1100}});
const pages=['','pages/accounts.html','pages/returns.html','pages/bonuses.html','pages/protection.html','pages/flagged.html','pages/sources.html'];
let errors=[];
page.on('pageerror',e=>errors.push(e.message));
fs.mkdirSync('test-results',{recursive:true});
try {
  for(const url of pages){
    const response=await page.goto(`${base}/${url}`);
    if(response.status()!==200)throw Error('HTTP '+response.status());
    if(await page.locator('h1').count()!==1)throw Error('Heading count');
    console.log('PASS desktop',url||'index.html');
  }
  await page.goto(`${base}/`);
  await page.screenshot({path:'test-results/desktop.png',fullPage:true});
  await page.goto(`${base}/pages/accounts.html`);
  await page.locator('#search').fill('Marcus');
  if(await page.locator('tbody tr:visible').count()!==1)throw Error('Search filter');
  await page.locator('#search').fill('no-such-bank');
  if(!await page.locator('.no-results').isVisible())throw Error('No result message');
  await page.locator('#search').fill('');
  await page.locator('#status').selectOption('unverified');
  if(await page.locator('tbody tr:visible').count()!==8)throw Error('Unverified filter');
  await page.locator('#status').selectOption('');
  await page.locator('#category').selectOption('National digital');
  if(await page.locator('tbody tr:visible').count()!==5)throw Error('Category filter');
  await page.setViewportSize({width:390,height:844});
  for(const url of pages){
    await page.goto(`${base}/${url}`);
    if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Mobile body overflow: '+url);
    console.log('PASS mobile',url||'index.html');
  }
  await page.goto(`${base}/`);
  await page.screenshot({path:'test-results/mobile.png',fullPage:true});
  if(errors.length)throw Error(errors.join('\n'));
  console.log('PASS filters, no-results, mobile overflow, zero browser exceptions');
} finally { await browser.close(); }
