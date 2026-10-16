# SOL / @Remote Desktop Connection — Windows 11 Pro

This is a REAL Windows Remote Desktop Connection (.rdp) profile and a Python DNS/TCP-3389 probe, not a VPN or an invented running RDP server.

- **User preferred Computer:** `gambbrazil-sol100726.is` — on Redmi DNS lookup 2026-10-17 returned UNRESOLVED. This is a user-chosen routing alias, NOT VERIFIED HOST.
- **LAN fallback Computer:** `192.168.1.12` — prior Windows shortcut candidate, RDP TCP 3389 unreachable when tested from Redmi. PC's actual current IPv4 not confirmed.
- **Not a Windows RDP host:** `cosmos.dns-parking.com`, `nova.dns-parking.com` (authoritative DNS service); `gambbrazil.fun` (website); `ai.sol.gambbrazil.fun` resolves to private `10.15.224.83` (previous gateway snapshot, NOT a verified PC).
- Other user aliases `gambbrazil-mei250726.is` and `gambbrazil-minh200925.is` did not resolve on Redmi in the same probe.
- Windows `DESKTOP-86ITNQ4` via Desktop Commander offline during last observation. VS Code tunnel `https://insiders.vscode.dev/tunnel/desktop-86itnq4/c:/Users/halin` is a different connection transport, not RDP.
- RDP host requires Remote Desktop enabled, Windows Pro, Windows firewall permitting 3389, reachability from the client network or an authorized VPN. **No automatic public port forwarding.**

## Operation

From a Windows computer (mstsc.exe): run `SOL_REMOTE_DESKTOP_DOMAIN.rdp`, or put `gambbrazil-sol100726.is` in the **Computer** field. A functional connection requires the host's DNS A/AAAA resolution and port 3389 being reachable. If DNS is not ready, use the correct Windows LAN/VPN IP (not a DNS nameserver and not a gateway).

On a Python-equipped client:
`python rdp_router.py --computer gambbrazil-sol100726.is`
`python rdp_router.py --computer 192.168.1.12 --profile SOL_REMOTE_DESKTOP_LAN.rdp`

No passwords, tokens, username or private keys in the profile. Credentials supplied through RDP client prompt.

## DNS binding

The Hostinger registrar delegates `gambbrazil.fun` to `cosmos.dns-parking.com` and `gambbrazil-mei250726.is` as observed from Hostinger `domains_portfolio_get` on 2026-10-17. The other three names in the user's five-name list are user-provided references, not five proven live delegated servers. Hostinger `dns_records_list` confirms 24 record groups, including mail, HOSPOSIK and an A record for `ai.sol`. Detailed sanitized DNS index: `../Network_Policy/HOSTINGER_DNS_RDP_BINDINGS_CURRENT.json`. This integration does not modify authoritative DNS or the Windows blocking policy.

Next evidence needed for RDP: actual Windows interface address, its DNS mapping, port listening, route on the client network. Do not use an unavailable ChatGPT/OpenAI relay as a prerequisite.
