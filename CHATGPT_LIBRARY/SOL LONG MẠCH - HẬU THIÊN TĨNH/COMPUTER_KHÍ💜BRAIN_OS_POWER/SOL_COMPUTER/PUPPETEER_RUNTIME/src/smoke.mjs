import assert from 'node:assert/strict';
import {launchBrowser, renderHtml} from './browser.mjs';

const browser = await launchBrowser();
try {
  const result = await renderHtml(
    browser,
    '<!doctype html><html><head><title>SOL Browser</title></head><body><main>SOL PUPPETEER READY</main></body></html>'
  );
  assert.equal(result.title, 'SOL Browser');
  assert.match(result.text, /SOL PUPPETEER READY/);
  assert.equal(Buffer.from(result.png_base64, 'base64').subarray(0, 8).toString('hex'), '89504e470d0a1a0a');
  console.log(JSON.stringify({status: 'PASS', component: 'PUPPETEER_RUNTIME', browser: await browser.version(), screenshot: 'PNG verified'}));
} finally {
  await browser.close();
}
