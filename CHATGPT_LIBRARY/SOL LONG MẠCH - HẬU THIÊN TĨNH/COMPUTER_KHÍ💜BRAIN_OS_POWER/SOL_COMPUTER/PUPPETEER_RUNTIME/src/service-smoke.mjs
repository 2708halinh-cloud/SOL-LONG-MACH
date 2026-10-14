import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import net from 'node:net';

const port = await new Promise((resolve, reject) => {
  const probe = net.createServer();
  probe.once('error', reject);
  probe.listen(0, '127.0.0.1', () => {
    const candidate = probe.address().port;
    probe.close(() => resolve(candidate));
  });
});
const child = spawn(process.execPath, ['src/server.mjs'], {
  env: {...process.env, SOL_PUPPETEER_PORT: String(port)},
  stdio: ['ignore', 'ignore', 'pipe'],
});
let stderr = '';
child.stderr.setEncoding('utf8');
child.stderr.on('data', data => {stderr = (stderr + data).slice(-4000);});
const origin = 'http://127.0.0.1:' + port;

try {
  let healthy = false;
  for (let i = 0; i < 90; i += 1) {
    if (child.exitCode !== null) break;
    try {
      const response = await fetch(origin + '/health', {signal: AbortSignal.timeout(1000)});
      const data = await response.json();
      if (response.ok && data.browser_connected) {
        healthy = true;
        break;
      }
    } catch {
      // Wait for the browser to start.
    }
    await new Promise(resolve => setTimeout(resolve, 250));
  }
  assert.ok(healthy, 'Runtime did not become healthy: ' + stderr);
  const reply = await fetch(origin + '/render', {
    method: 'POST',
    headers: {'content-type': 'application/json'},
    body: JSON.stringify({html: '<!doctype html><title>Runtime test</title><main>SOL RENDER OK</main>'}),
  });
  assert.equal(reply.status, 200);
  const result = await reply.json();
  assert.equal(result.title, 'Runtime test');
  assert.match(result.text, /SOL RENDER OK/);
  assert.equal(Buffer.from(result.png_base64, 'base64').subarray(0, 8).toString('hex'), '89504e470d0a1a0a');
  console.log(JSON.stringify({status: 'PASS', service: '127.0.0.1:' + port, health: 'ready', render: 'PNG verified'}));
} finally {
  child.kill('SIGTERM');
}
