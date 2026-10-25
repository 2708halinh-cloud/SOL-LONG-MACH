# HOSPOSIK · Public HTTPS deployment

Domain: `gambbrazil.gambbrazil.fun`.

The original Termux `127.0.0.1` instance remains unchanged. This is an independently deployable instance with its own durable SQLite database. **It is not a tunnel into Termux and does not automatically synchronize existing Termux memory.**

## Provisioning

The adjacent `render.yaml` describes a Node.js 24 web service in Singapore with a **paid Starter plan** and a persistent 1 GiB disk mounted at `/var/data`. Do not create a billed service without confirming price and user approval. Set custom domain `gambbrazil.gambbrazil.fun` on the chosen hosting service before changing Hostinger A/CNAME records.

Required values: `HOSPOSIK_PUBLIC_MODE=true`, `HOSPOSIK_DATA_DIR=/var/data`, generated `HOSPOSIK_TOKEN` and provider-managed `PORT`. Health endpoint: `GET /health`. All agent APIs require Bearer authentication. TLS must terminate at the hosting provider's HTTPS reverse proxy. DNS UDP is disabled in public mode (Hostinger remains the authoritative public DNS zone).

Run a staging smoke test first: `npm ci && node test/public.mjs`. Final activation requires a real provider endpoint and external HTTPS readback; a GitHub commit is not a deployment.
