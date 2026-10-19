# Sepsis Management System

PostgreSQL does the clinical work: triggers run `assess_sepsis()`, create alerts and `pg_notify`.
Flask streams the notifications over SSE, Vue renders them, and a simulator drives everything
through the REST API.

## Setup (EndeavourOS / zsh)

```bash
sudo pacman -S postgresql nodejs npm dbeaver uv tree
sudo systemctl enable --now postgresql
sudo -u postgres initdb -D /var/lib/postgres/data   # only if not initialised

sudo -u postgres psql -c "CREATE USER sepsis_user WITH PASSWORD 'sepsis_pass';"
sudo -u postgres psql -c "CREATE DATABASE sepsis_db OWNER sepsis_user;"

cd backend
cp -n .env.example .env
uv sync                                  # pyproject.toml is already provided
export PGPASSWORD=sepsis_pass
for f in 001_schema 002_functions 003_views 004_seed; do
  psql -h localhost -U sepsis_user -d sepsis_db -v ON_ERROR_STOP=1 -f sql/$f.sql
done
uv run python seed_admin.py              # admin@sepsis.local / admin12345

uv run python app.py                     # terminal 1 - API on :5000
cd ../frontend && cp -n .env.example .env; npm install && npm run dev   # terminal 2 - UI on :5173
cd ../backend && uv run python simulate.py --speed 1   # terminal 3 - simulator
```

Log in at http://localhost:5173 with `admin@sepsis.local` / `admin12345`.

### Reset the database

```bash
sudo -u postgres psql -c "DROP DATABASE IF EXISTS sepsis_db WITH (FORCE);"
sudo -u postgres psql -c "CREATE DATABASE sepsis_db OWNER sepsis_user;"
# then re-run the four sql files and seed_admin.py
```

### Simulator flags

`--seed N` (default 42), `--speed X` (2 = twice as fast, 0.5 = half), `--duration S` (stop after S
simulated seconds; default runs until Ctrl+C).

## Verify before the demo

```bash
psql -h localhost -U sepsis_user -d sepsis_db -c "\d vital_signs"        # CHECKs + idx_vitals_patient_time
uv run ruff check . && uv run black --check .                             # run `black .` and `ruff check --fix .` first
```

Then check each acceptance item:
- Manual `INSERT` of a bad vital in DBeaver creates an alert (see `docs/DEMO_SCRIPT.md`).
- In DevTools -> Network, `stream/alerts` is a single long-lived `text/event-stream` request.
- After 5+ minutes of simulation:
  `SELECT patient_id, count(*) FROM sepsis_episodes WHERE outcome='ongoing' GROUP BY 1 HAVING count(*)>1;`
  returns no rows.

## Troubleshooting

| Problem | Fix |
|---|---|
| `zsh: no matches found: psycopg[binary]` | Quote it: `"psycopg[binary]"` |
| `uv run` tries to build the project | Remove `[build-system]` and `[project.scripts]` from `pyproject.toml` |
| Browser CORS error | Check `frontend/.env` -> `VITE_API_URL=http://localhost:5000/api`, restart Vite |
| SSE returns 401 | The token must be a query param: `/api/stream/alerts?token=<access_token>` |
| `psql: FATAL: Peer authentication failed` | Use `-h localhost` and `PGPASSWORD` |
| `flask run` picks the wrong module | Use `uv run python app.py` (the `app/` package and `app.py` share a name) |
| No new alert on a repeated manual insert | The patient still has an ongoing episode. Use another patient, or `UPDATE sepsis_episodes SET outcome='recovered' WHERE patient_id=3;` first |
| `notifies(timeout=...)` TypeError | Needs psycopg >= 3.2 (`uv sync` installs it) |
