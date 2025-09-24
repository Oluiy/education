# Deploying EduNerve Microservices to Heroku via Dashboard

This repository is a monorepo with multiple Python microservices under `services/*` and an API gateway under `api-gateway/`. Heroku deploys one app per service. Use GitHub integration and the Heroku Subdirectory Buildpack to deploy each service folder.

## Prerequisites
- Repo hosted on GitHub (recommended for Dashboard deploys)
- Each service has:
  - `Procfile` with a `web:` entry (uses `$PORT`)
  - `requirements.txt`
  - `runtime.txt` (e.g., `python-3.11.9`)
- For Postgres/Redis, plan to add add-ons and set config vars accordingly.

## Option A: Deploy a Service from a Subdirectory (Recommended)
Use the Heroku Subdirectory Buildpack to target a folder within the monorepo.

Steps (example for `services/auth-service`):
1. Create a new app in the Heroku Dashboard
2. In Settings → Add buildpack (order matters):
   - https://github.com/timanovsky/subdir-heroku-buildpack
   - heroku/python
3. In Settings → Reveal Config Vars, add:
   - `PROJECT_PATH` = `services/auth-service`
   - `DATABASE_URL` = set automatically if using Heroku Postgres add-on
   - Any other env vars required by the service (see below)
4. In Resources → Add-ons: add Heroku Postgres, Heroku Redis (if needed)
5. In Deploy → Deployment method: connect to your GitHub repo and choose branch
6. Enable Automatic Deploys (optional) → Deploy Branch

Repeat for other services with their own `PROJECT_PATH` values.

## Option B: Separate Git repos per service
Push each service folder as its own repo and connect each Heroku app to that repo. This avoids the subdirectory buildpack but increases repo maintenance.

## Auth Service Configuration
- Folder: `services/auth-service`
- Procfile: `web: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --log-level info --access-logfile -`
- requirements.txt: includes FastAPI, uvicorn, gunicorn, SQLAlchemy, etc.
- runtime.txt: `python-3.11.9`

### New Environment Variable Support (added)
- `ALLOWED_ORIGINS`: Comma-separated list override for CORS (e.g. `https://education-pearl-tau.vercel.app,https://api.example.com`)
- `REDIS_URL`: If provided (Heroku Redis), auto-parsed; overrides individual REDIS_HOST/PORT/PASSWORD/DB.

### Required Config Vars
- `DATABASE_URL`: Set by Heroku Postgres, or use SQLite for dev (not recommended in Heroku dynos)
- `REDIS_URL` or (`REDIS_HOST`, `REDIS_PORT`): If using Heroku Redis, parse `REDIS_URL`
- `SECRET_KEY`, `JWT_SECRET`, etc. per your security needs
- `ALLOWED_ORIGINS` (strongly recommended in production) e.g. `https://education-pearl-tau.vercel.app`

### Postgres
- Resources → Add-ons → Heroku Postgres → Provision
- Heroku sets `DATABASE_URL`

### Redis (optional but recommended)
- Resources → Add-ons → Heroku Data for Redis → Provision
- Heroku sets `REDIS_URL`. Update your code or config to use it.

## API Gateway Configuration
- Folder: `api-gateway`
- Use the same buildpack order and set `PROJECT_PATH=api-gateway`

## Health Checks
Each service exposes `/health` and `/docs`. Use these to verify deployments.

## Common Pitfalls
- Missing gunicorn in requirements while using a gunicorn Procfile
- No `runtime.txt` leading to unexpected Python versions
- Not binding to `$PORT` (your Procfile already does)
- Deploying the repo root without subdir buildpack
 - Missing `ALLOWED_ORIGINS` causes requests from Vercel domain to be blocked if not in defaults

## Troubleshooting: "No default language could be detected"
If your build fails on Heroku with this message, it means Heroku didn’t find a buildpack for your app. In a monorepo, this usually happens because the root doesn’t have language markers and the subdirectory wasn’t configured.

Fix checklist:
1) Buildpacks configured (Settings → Buildpacks)
   - First: `https://github.com/timanovsky/subdir-heroku-buildpack`
   - Second: `heroku/python`
   - Remove any unrelated/auto-added buildpacks. Click Save Changes.

2) PROJECT_PATH config var set (Settings → Reveal Config Vars)
   - Key: `PROJECT_PATH`
   - Value exactly: `services/auth-service` (or the service you’re deploying)
   - No leading slash, correct capitalization.

3) Target folder contains language markers
   - `services/<service>/requirements.txt`
   - `services/<service>/Procfile`
   - `services/<service>/runtime.txt`

4) Re-deploy
   - Deploy tab → Deploy Branch again. If still failing, toggle buildpacks order (re-save) to invalidate cache and retry.

Alternative buildpack: If you prefer ddollar’s monorepo buildpack:
- Use `https://github.com/ddollar/heroku-buildpack-monorepo`
- Set config var `APP_BASE` = `services/auth-service`
- Keep `heroku/python` as the second buildpack.

If the error persists, ensure your latest commits (including `runtime.txt` and `requirements.txt`) are pushed to GitHub and that the Heroku app is connected to that branch.

## Post-Deployment Validation Checklist (Auth Service)
1. Open https://<your-auth-app>.herokuapp.com/health → should return `{ "status": "healthy" ... }`
2. CORS test from frontend domain: Open browser console on Vercel app and attempt fetch to `/health`; no CORS error.
3. Register + Login flow via curl:
    ```bash
    # Register (adjust email)
    curl -X POST https://<your-auth-app>.herokuapp.com/auth/register \
       -H 'Content-Type: application/json' \
       -d '{"username":"demo_user","email":"demo_user@example.com","password":"DemoPass123!","full_name":"Demo User","role":"student"}'

    # Login
    curl -X POST https://<your-auth-app>.herokuapp.com/auth/login \
       -H 'Content-Type: application/json' \
       -d '{"username_or_email":"demo_user","password":"DemoPass123!","remember_me":false}'

    # Use returned access_token to fetch profile
    curl https://<your-auth-app>.herokuapp.com/auth/me \
       -H 'Authorization: Bearer <ACCESS_TOKEN>'
    ```
4. Redis session check (optional): Inspect Heroku Redis keys (requires CLI) to confirm `session:*` keys exist after login.
5. Logs: Settings → More → View logs; confirm no stack traces on requests.

## Frontend (Vercel) Integration Steps
1. Set Vercel Project Environment Variable:
    - `NEXT_PUBLIC_API_URL=https://<your-auth-app>.herokuapp.com`
2. Redeploy frontend on Vercel.
3. Ensure `ALLOWED_ORIGINS` on Heroku includes `https://<your-vercel-domain>`.
4. Test signup on production site; verify auth token saved (localStorage `auth_token`).
5. Open browser dev tools → Network: confirm 201 (register) then 200 (login) then 200 (`/auth/me`).

## Microservices Strategy (Incremental)
Deploy auth-service first (prerequisite for user identities). Subsequent services (e.g., notification, content) can be added with their own Heroku apps using the same subdirectory buildpack approach. For cross-service calls, set config vars referencing internal service URLs or route through an API gateway if deployed.

## Rollbacks and Logs
- In Dashboard → Activity → Rollback
- Logs: More → View logs

