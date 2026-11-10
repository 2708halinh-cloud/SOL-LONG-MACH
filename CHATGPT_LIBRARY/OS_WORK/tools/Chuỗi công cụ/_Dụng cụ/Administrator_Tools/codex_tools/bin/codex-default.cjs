'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { execFileSync, spawn } = require('node:child_process');

function readUserEnvironment(name) {
  try {
    const output = execFileSync(
      'reg.exe',
      ['query', 'HKCU\\Environment', '/v', name],
      { encoding: 'utf8', windowsHide: true, stdio: ['ignore', 'pipe', 'ignore'] }
    );
    const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const match = output.match(new RegExp(
      '^\\s*' + escaped + '\\s+REG_\\w+\\s+(.+?)\\s*$',
      'mi'
    ));
    return match ? match[1].trim() : '';
  } catch {
    return '';
  }
}

if (!process.env.COMETAPI_KEY) {
  const userKey = readUserEnvironment('COMETAPI_KEY');
  if (userKey) process.env.COMETAPI_KEY = userKey;
}

const args = process.argv.slice(2);
const hasProfile = args.some((arg) =>
  arg === '--profile' || arg === '-p' || arg.startsWith('--profile=')
);
const ignoresUserConfig = args.includes('--ignore-user-config');
// Preserve the user's actual default Codex configuration. A provider profile
// is selected only when the caller passes --profile/-p explicitly.
const routedArgs = args;

const appData = process.env.APPDATA || path.join(process.env.USERPROFILE || '', 'AppData', 'Roaming');
const cliPath = path.join(appData, 'npm', 'node_modules', '@openai', 'codex', 'bin', 'codex.js');

if (!fs.existsSync(cliPath)) {
  console.error('Codex CLI entrypoint was not found at the installed npm location.');
  process.exit(1);
}

const child = spawn(process.execPath, [cliPath, ...routedArgs], {
  stdio: 'inherit',
  env: process.env,
  windowsHide: false,
});

child.once('error', (error) => {
  console.error(`Unable to start Codex CLI: ${error.message}`);
  process.exit(1);
});

child.once('exit', (code) => {
  process.exit(code == null ? 1 : code);
});