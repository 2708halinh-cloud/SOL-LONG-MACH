import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../../COMPUTER_KHÍ💜BRAIN_OS_POWER/MEMORY_ARCHIVE_THỊT🟠THỔ_SOUL/BRAINWAVE_REGISTRY');
const bands = ['ALPHA', 'BETA', 'GAMMA', 'DELTA', 'THETA'];
const expected = ['.gitignore', ...bands.map(x => x + '_GATEWAY.json'), 'REGISTRY_POLICY.json'].sort();
assert.deepEqual(fs.readdirSync(root).sort(), expected, 'Public registry must contain metadata-only allowlist');
const edges = ['REALITY', 'SPACE', 'TIME', 'MIND', 'POWER'];
for (const band of bands) {
 const data = JSON.parse(fs.readFileSync(path.join(root, band + '_GATEWAY.json'), 'utf8'));
 assert.equal(data.brainwave_type, band);
 assert.equal(data.document_kind, 'PUBLIC_TEMPLATE_ONLY');
 assert.equal(data.raw_signal_present, false);
 assert.equal(data.live_eeg_measured, false);
 assert.equal(data.source_ref, null);
 assert.equal(data.source_hash, null);
 assert.equal(data.storage_vault.location, null);
 assert.deepEqual(Object.keys(data.relations).sort(), edges.slice().sort());
 for (const value of Object.values(data.relations)) assert.equal(value.verification_status, 'unverified_edge');
}
const policy=JSON.parse(fs.readFileSync(path.join(root, 'REGISTRY_POLICY.json'), 'utf8'));
assert.equal(policy.ingest_rules.raw_upload_to_public_repo, false);
assert.equal(policy.ingest_rules.hash_is_not_encryption, true);
assert.equal(policy.physical_actuation.default, 'DISABLED');
const edge=policy.transitions.find(x=>x.from==='BETA'&&x.to==='DELTA');
assert.equal(edge.motor_policy, 'SAFE_STOP');
console.log('Five shadow gates and private-source safety policy validated.');
