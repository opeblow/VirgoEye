# VPS deployment

The Anthropic-backed application needs no GPU. The production Dockerfiles under
`deploy/` build a standalone Next.js frontend and a single FastAPI worker. Build
from the repository root, using the same release tag for both images:

```sh
docker build -f deploy/frontend.Dockerfile -t virgoeye-frontend:RELEASE .
docker build -f deploy/backend.Dockerfile -t virgoeye-backend:RELEASE .
```

Install the server-only settings described in [PUBLIC_DEMO.md](PUBLIC_DEMO.md)
at `/opt/virgoeye/backend.env`, owned by root with mode 600. Set
`VIRGO_USAGE_DB=/data/usage.sqlite3`. Never put real credentials in the build
context, repository, image, frontend environment, or command-line arguments.

Then run `sh deploy/start-vps.sh RELEASE`. It replaces only VirgoEye's two
containers, preserves `/opt/virgoeye/data`, and binds the frontend to loopback
port 3011. The backend has no published host port. Containers run as non-root
users, with read-only filesystems, limited memory and rotating logs. Back up
the persistent usage database using SQLite's backup API, not by deleting or
resetting it. For rollback, run the script with the prior image tag.

## Temporary preview

The supplied systemd unit runs an outbound SSH tunnel through localhost.run.
Create the unprivileged `virgo-preview` system user, copy the unit into
`/etc/systemd/system`, then enable it. SSH host keys are saved and checked on
subsequent connections. No account SSH key is offered to the tunnel provider.
Read the generated HTTPS address from `journalctl -u virgoeye-preview`.

**This is a preview address, not a stable submission URL.** The free tunnel
provider changes hostnames periodically and limits bandwidth. TLS terminates
at that provider; its connection to the VPS uses encrypted SSH. Use public
sample images when evaluating this preview. The tunnel process and containers
restart automatically, but the resulting public address may change.

For a permanent deployment, use a domain you control, verify its DNS with the
hosting provider, and configure its HTTPS reverse proxy. On a shared-IP VPS,
an IP-based free hostname cannot satisfy a provider's DNS TXT ownership check.
Vercel can host the frontend, but the VPS backend still needs a reachable,
secure endpoint and persistent budget storage.

Before sharing, verify both analysis routes enforce the configured access mode, run a
live sample through the public frontend, check streaming and report download,
and confirm ledger records survive backend restart. See PUBLIC_DEMO.md for
budget behavior and release checks.

## Verified preview configuration — 20 September 2026

- Claude Sonnet 5; $4 conservative reservation budget; 30 total admissions;
  two admissions per minute; anonymous access enabled on both analysis endpoints
  by explicit user request. Budget and admission limits remain active.
- Input/output prices: $2/$10 per million tokens, checked against
  [Anthropic's pricing](https://platform.claude.com/docs/en/about-claude/pricing).
- Persistent ledger retained exactly across a container replacement.
- 84 backend tests passed inside the deployed Python 3.12 image; frontend
  production build and standalone report-export test passed.
- SSE responses use `Cache-Control: no-cache, no-transform` to prevent proxy
  compression from holding back live progress until analysis completes.
- Public HTTPS smoke test with normal compression negotiation: first SSE
  event in 1.94 seconds, full live affected-leaf inspection in 32.05 seconds.
  Both analysis routes rejected an invalid access code. These are single-run
  functional measurements, not performance guarantees.
- The existing unrelated VPS service remains running. No VPS resize or paid
  hosting service was added. The existing VPS balance still funds its runtime.

The current preview has no access code. If code-gated access is enabled again,
keep its code in an ignored local file and the server's protected environment
file. Do not commit it. Treat the
[free tunnel's changing address](https://localhost.run/docs/forever-free/) as a
preview-only limitation; it is unsuitable as the final judging URL.

The free provider rotated the initial hostname during the active tunnel session.
An active SSH connection does not guarantee that an older hostname still works.
Read the most recent `tcpip-forward` address from the service journal.
