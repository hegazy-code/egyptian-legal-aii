# Deployment

## Why not PythonAnywhere

An earlier, separate project on this account (a smaller Flask tool) was deployed to PythonAnywhere's free tier and hit two real, verified problems worth remembering here: (1) the free tier restricts outbound network calls to a small domain allowlist -- `generativelanguage.googleapis.com` (Gemini) wasn't confirmed safely covered, and a separate search provider's domain (Tavily) was confirmed **not** on that allowlist -- and (2) it made local iteration awkward (console-based file editing, manual `pip install` per change). Neither problem is a good fit for a multi-service app (Postgres + FastAPI + Next.js) anyway. This project targets a different, free-tier-friendly stack instead:

| Piece | Free option | Notes |
|---|---|---|
| Postgres + pgvector | [Supabase](https://supabase.com) or [Neon](https://neon.tech) | Both have genuine free tiers with pgvector support, no credit card required at signup as of this writing -- verify current limits before committing, free tiers change. |
| Backend (FastAPI) | [Render](https://render.com) free web service | Sleeps on inactivity on the free tier -- fine for early usage, revisit once there's real traffic. |
| Frontend (Next.js) | [Vercel](https://vercel.com) free tier | Built for Next.js specifically, no config needed beyond connecting the repo. |
| LLM | Gemini free tier | `GEMINI_API_KEY`, no card, rate-limited (see backend `.env.example` comments). |
| Live search (once wired in) | Tavily free tier | 1,000 searches/month, no card. Confirm Render's outbound network isn't restricted the way PythonAnywhere's was (it generally isn't, but verify once this is actually implemented, rather than assuming). |

## Environments

- **Development:** `localhost` -- either native (`uvicorn --reload` + `npm run dev`) or `docker compose up`.
- **Staging:** not set up yet. Recommended: a separate Render service + separate Supabase/Neon project + `staging.` Vercel deployment, once there's something worth staging.
- **Production:** not set up yet -- this skeleton has not been deployed anywhere. Don't deploy the admin API or document upload publicly until the gaps in `docs/security.md` are closed.

## Before any real deployment

Generate a real `JWT_SECRET` (not the placeholder in `.env.example`), set real `CORS_ORIGINS`, confirm `DEBUG=false`, and read `docs/security.md`'s pre-launch checklist in full -- most of it isn't done yet.
