const port = Number(process.env.SOL_PUPPETEER_PORT || 8776);
const response = await fetch('http://127.0.0.1:' + port + '/health', {signal: AbortSignal.timeout(5000)});
const data = await response.json();
if (!response.ok || data.status !== 'ready' || !data.browser_connected) {
  throw new Error('Puppeteer runtime not healthy: ' + JSON.stringify(data));
}
console.log(JSON.stringify(data));
