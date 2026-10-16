import puppeteer from 'puppeteer';

export async function launchBrowser() {
  const executablePath = process.env.PUPPETEER_EXECUTABLE_PATH || undefined;
  const args = process.env.CI === 'true' ? ['--no-sandbox', '--disable-setuid-sandbox'] : [];
  return puppeteer.launch({
    headless: true,
    args,
    ...(executablePath ? {executablePath} : {}),
  });
}

export async function renderHtml(browser, html) {
  if (typeof html !== 'string' || Buffer.byteLength(html, 'utf8') > 1024 * 1024) {
    throw new TypeError('HTML must be a string at most 1 MiB');
  }
  const page = await browser.newPage();
  try {
    await page.setViewport({width: 800, height: 480, deviceScaleFactor: 1});
    await page.setJavaScriptEnabled(false);
    await page.setRequestInterception(true);
    page.on('request', request => {
      const url = request.url();
      const allowed = url.startsWith('about:') || url.startsWith('data:');
      void (allowed ? request.continue() : request.abort()).catch(() => {});
    });
    await page.setContent(html, {waitUntil: 'load', timeout: 12000});
    const info = await page.evaluate(() => ({
      title: document.title,
      text: document.body?.innerText ?? '',
    }));
    const png = await page.screenshot({type: 'png'});
    return {...info, png_base64: Buffer.from(png).toString('base64')};
  } finally {
    await page.close();
  }
}
