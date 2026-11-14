import http from 'node:http';
import {launchBrowser, renderHtml} from './browser.mjs';

const hostname = '127.0.0.1';
const port = Number(process.env.SOL_PUPPETEER_PORT || 8776);
if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error('Invalid SOL_PUPPETEER_PORT');
}
const browser = await launchBrowser();
const send = (res, status, body) => {
  res.writeHead(status, {'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', 'x-content-type-options': 'nosniff'});
  res.end(JSON.stringify(body));
};
const server = http.createServer(async (req, res) => {
  try {
    if (req.method === 'GET' && req.url === '/health') {
      return send(res, browser.connected ? 200 : 503, {
        status: browser.connected ? 'ready' : 'disconnected',
        service: 'SOL_PUPPETEER_RUNTIME',
        browser_connected: browser.connected,
      });
    }
    if (req.method !== 'POST' || req.url !== '/render') {
      return send(res, 404, {error: 'not_found'});
    }
    if ((req.headers['content-type'] || '').split(';')[0].trim() !== 'application/json') {
      return send(res, 415, {error: 'json_required'});
    }
    const origin = req.headers.origin;
    if (origin && origin !== 'http://' + hostname + ':' + port) {
      return send(res, 403, {error: 'origin_denied'});
    }
    let body = '';
    for await (const chunk of req) {
      body += chunk.toString('utf8');
      if (Buffer.byteLength(body, 'utf8') > 1024 * 1024) {
        return send(res, 413, {error: 'body_too_large'});
      }
    }
    const payload = JSON.parse(body);
    if (typeof payload.html !== 'string') {
      return send(res, 400, {error: 'html_required'});
    }
    const result = await renderHtml(browser, payload.html);
    return send(res, 200, result);
  } catch (error) {
    return send(res, 400, {error: error?.message || 'bad_request'});
  }
});
server.listen(port, hostname, () => {
  console.log(JSON.stringify({service: 'SOL_PUPPETEER_RUNTIME', status: 'listening', host: hostname, port}));
});
async function shutdown() {
  server.close();
  await browser.close();
}
process.once('SIGINT', () => {void shutdown();});
process.once('SIGTERM', () => {void shutdown();});
