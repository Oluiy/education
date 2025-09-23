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

### Required Config Vars
- `DATABASE_URL`: Set by Heroku Postgres, or use SQLite for dev (not recommended in Heroku dynos)
- `REDIS_URL` or (`REDIS_HOST`, `REDIS_PORT`): If using Heroku Redis, parse `REDIS_URL`
- `SECRET_KEY`, `JWT_SECRET`, etc. per your security needs

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

## Rollbacks and Logs
- In Dashboard → Activity → Rollback
- Logs: More → View logs

