# Security

## What's real right now

- **Password hashing:** bcrypt via passlib (`backend/app/security/hashing.py`) -- passwords are never stored or logged in plain text.
- **Auth tokens:** JWT via python-jose (`backend/app/security/jwt.py`), signed with `JWT_SECRET`. The default in `.env.example` is a placeholder (`changeme_...`) -- **a real random secret must be generated before any real deployment**, e.g. `python -c "import secrets; print(secrets.token_urlsafe(64))"`.
- **API keys stay server-side.** `GEMINI_API_KEY` and `TAVILY_API_KEY` are read by the backend only; the frontend never sees them (it only talks to the backend's own API, configured via `NEXT_PUBLIC_API_URL`). Never move a secret key into a `NEXT_PUBLIC_*` env var -- anything prefixed that way ships in the browser bundle.
- **CORS** is restricted to `CORS_ORIGINS` (defaults to localhost) rather than left wide open.

## What's a stub, not yet real protection

- **Rate limiting** (`backend/app/security/rate_limit.py`) is an in-memory per-process stub -- fine for local dev, not sufficient for production (won't work correctly across multiple backend instances, resets on restart). Replace with a real backing store (Redis) before public launch.
- **Role-based access** (admin vs. regular user vs. lawyer tier) doesn't exist yet -- `/admin/*` endpoints have no auth check wired in yet. **Do not deploy the admin API publicly until this is fixed.**
- **File upload security** (virus/malware scanning, file-type validation, size limits) for the future document-upload feature is not implemented -- `POST /documents` currently accepts a file with minimal validation. This is a hard blocker before real document upload ships.
- **No security audit has been performed.** Required before this handles real people's real legal situations, which can include sensitive personal information (accusations, disputes, health/family details).

## Prompt injection

Uploaded documents and any text pulled from the web (once live search exists) must be treated as *data*, never as instructions to the AI. `backend/app/rag/engine.py`'s system prompt is set once, server-side, per request -- retrieved article text and user input are passed as content, not concatenated into the system prompt itself, which is the basic mitigation. This has not been adversarially tested yet; add prompt-injection test cases to `tests/security/` before trusting it fully (that directory currently has scaffolding but no real injection test cases -- see the Evaluation doc's testing-order note: retrieval and generation correctness come first, injection/adversarial testing is part of the same "before production" gate as the security audit).

## No-hallucination policy (the project's core security property, arguably)

See `docs/architecture.md#no-hallucination-enforcement-two-layers-not-one`. A legal tool that confidently states a fake law is arguably a worse security failure than a leaked password -- it's covered here for that reason even though it's implemented in `rag/`, not `security/`.

## Pre-launch checklist (not done, listed honestly)

HTTPS/TLS (handled by hosting platform, e.g. Render/Vercel, not app code) · real RBAC · Redis-backed rate limiting · file upload scanning · secrets management (a real secret store, not `.env` files, for production) · security audit · privacy policy + terms reviewed under Egyptian law · account/document deletion that actually deletes.
