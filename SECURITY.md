# Reporting Security Vulnerabilities

Virgo-Eye processes images and runs a vision-language model inside your
environment. We take security seriously. Thanks for helping us keep the
project safe.

## Scope

Things that are in scope:

- Remote Code Execution via a crafted image payload
- Prompt-injection that escapes the pipeline's stage isolation
- SSE / API endpoints leaking data across sessions
- Path traversal or arbitrary file read/write through the backend
- Secrets or credentials committed to the repository

Out of scope:

- Phishing or social-engineering of humans
- Issues in upstream dependencies that have their own reporting channels
  (report those to the dependency maintainers)
- Local dev-only conveniences with no production impact

## Reporting

**Please do not open a public GitHub issue for security bugs.**

Instead, report privately so we can fix and disclose responsibly:

1. Open a [private vulnerability report](https://github.com/advisories/new)
   on the repository (GitHub Security tab).

   If the repo is not hosted on GitHub, or you cannot file one, email the
   maintainers with `[SECURITY]` in the subject line.

2. Include:
   - The affected version / commit
   - Reproduction steps (or a minimal payload, ideally a tiny image file)
   - The impact and your suggested severity
   - Whether it is public already

## What happens next

- We will acknowledge receipt within **5 business days**.
- We will triage, reproduce, and confirm scope.
- We will issue a fix, backport to the current release, and publish an
  advisory with a grace period before full disclosure.
- You will be credited (unless you prefer to stay anonymous).

## Safe harbor

We consider research that follows this policy to be authorized, and will not
seek to pursue legal action against researchers who act in good faith and
without causing harm.