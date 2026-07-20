# CittaAI — Living Intelligence

> Enterprise‑grade AI intelligence & transformation partner — the redesigned CittaAI web experience.
> `Same content. Completely elevated experience.`

---

## Table of contents
1. [Tech stack](#tech-stack)
2. [Prerequisites](#prerequisites)
3. [Project structure](#project-structure)
4. [Quick start (TL;DR)](#quick-start-tldr)
5. [Detailed setup](#detailed-setup)
6. [Environment variables](#environment-variables)
7. [Available scripts](#available-scripts)
8. [Adding / updating content](#adding--updating-content)
9. [Adding / updating images](#adding--updating-images)
10. [Deployment](#deployment)
11. [Troubleshooting — get rid of all errors](#troubleshooting--get-rid-of-all-errors)

---

## Tech stack

| Layer      | Choice                                                                                 |
| ---------- | -------------------------------------------------------------------------------------- |
| Frontend   | **React 19 + Create React App (CRACO)** · **Tailwind CSS 3** · **Framer Motion 11**    |
| 3D         | **@react-three/fiber 9** + **@react-three/drei 9.121** + **three 0.161**               |
| Router     | **react-router-dom 7**                                                                 |
| Icons      | **lucide-react**                                                                       |
| Fonts      | Geist Sans · Inter · JetBrains Mono (loaded via Google Fonts)                          |
| Backend    | **FastAPI 0.110** + **motor 3.3** (async MongoDB driver) — optional, static-first      |
| Database   | **MongoDB** (only needed if you use the backend `/api/status` endpoints)               |
| Pkg mgmt   | **yarn 1.22** (frontend) · **pip** (backend)                                           |

> The site is currently a **pure frontend marketing website** — the FastAPI backend is bundled but not used by any page. You can run just the frontend if you don't need the backend.

---

## Prerequisites

Install the following on your machine before you start:

| Tool       | Version         | Install                                                                       |
| ---------- | --------------- | ----------------------------------------------------------------------------- |
| Node.js    | **20.x LTS** (18.x also works) | https://nodejs.org/en/download or `nvm install 20`             |
| Yarn 1     | 1.22.x          | `npm i -g yarn`                                                               |
| Python     | **3.11** (3.10–3.12 all fine) | https://www.python.org/downloads/                               |
| MongoDB    | 6.x or 7.x *(only if running backend)* | https://www.mongodb.com/try/download/community        |
| Git        | any             | https://git-scm.com/downloads                                                 |

Verify:

```bash
node -v      # v20.x
yarn -v      # 1.22.x
python3 -V   # 3.11.x
mongod --version   # only if you plan to run the backend
```

---

## Project structure

```
citta/
├── backend/                     # FastAPI backend (optional)
│   ├── server.py                # Main app, / and /api/status routes
│   ├── requirements.txt
│   └── .env                     # MONGO_URL, DB_NAME, CORS_ORIGINS
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── assets/              # ⚡ Real images (logo, badges, team)
│   │       ├── brand/           # logo-square.png, logo-wide.png
│   │       ├── badges/          # iso.png, msme.png, startup-india.png
│   │       └── team/            # 7 headshot JPGs
│   ├── src/
│   │   ├── App.js               # Router entry
│   │   ├── index.css            # Design tokens, glass, aurora, buttons
│   │   ├── data/
│   │   │   └── content.js       # 🔒 Single source of truth for ALL copy
│   │   ├── components/          # Navbar, Footer, HeroCanvas (R3F), etc.
│   │   ├── sections/            # Home sections (Hero, Stack, Solutions…)
│   │   └── pages/               # Home, About, Contact, PSPage, etc.
│   ├── craco.config.js          # Path alias @ = ./src
│   ├── tailwind.config.js       # Brand tokens
│   ├── package.json
│   └── .env                     # REACT_APP_BACKEND_URL
├── memory/
│   └── PRD.md                   # Product requirements / build log
└── README.md                    # ← you are here
```

---

## Quick start (TL;DR)

```bash
# 1) clone
git clone https://github.com/rohan36389/citta.git
cd citta

# 2) frontend
cd frontend
yarn install
yarn start                       # http://localhost:3000

# 3) (optional) backend – separate terminal
cd ../backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

That's it — the frontend runs standalone. If you skip the backend, the site works fully; only the `/api/*` endpoints won't respond.

---

## Detailed setup

### 1. Clone the repo

```bash
git clone https://github.com/rohan36389/citta.git
cd citta
```

### 2. Frontend

```bash
cd frontend
yarn install         # installs all deps (uses resolutions in package.json)
```

Create the environment file **`frontend/.env`** (see [Environment variables](#environment-variables)):

```env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=3000
ENABLE_HEALTH_CHECK=false
```

Start the dev server:

```bash
yarn start
```

Open **http://localhost:3000** — you should see the CittaAI hero with the 3D node network.

### 3. Backend (optional — only if you'll add server-side features)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Create **`backend/.env`**:

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=cittaai_local
CORS_ORIGINS=http://localhost:3000
```

Start MongoDB (in a separate terminal or as a service):

```bash
# macOS (Homebrew)
brew services start mongodb-community
# Ubuntu / Debian
sudo systemctl start mongod
# Windows: use the MongoDB service or `mongod --dbpath <path>`
```

Start the FastAPI server:

```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

Verify:

```bash
curl http://localhost:8001/api/
# {"message":"Hello World"}
```

---

## Environment variables

### `frontend/.env`

| Key                      | Example                          | Purpose                                                          |
| ------------------------ | -------------------------------- | ---------------------------------------------------------------- |
| `REACT_APP_BACKEND_URL`  | `http://localhost:8001`          | Backend base URL. Only used if you call `/api/*` from the UI.    |
| `WDS_SOCKET_PORT`        | `3000`                           | Webpack dev server HMR socket port. Set to `3000` locally.       |
| `ENABLE_HEALTH_CHECK`    | `false`                          | Platform flag — safe to leave `false` locally.                   |

> ⚠️ CRA reads `.env` only at build/dev-server start. **Restart `yarn start` after changing.**

### `backend/.env`

| Key             | Example                                    | Purpose                       |
| --------------- | ------------------------------------------ | ----------------------------- |
| `MONGO_URL`     | `mongodb://localhost:27017`                | Mongo connection string       |
| `DB_NAME`       | `cittaai_local`                            | Database name                 |
| `CORS_ORIGINS`  | `http://localhost:3000`                    | Comma-separated allowed origins |

---

## Available scripts

### Frontend (`cd frontend`)

| Command       | What it does                                                    |
| ------------- | --------------------------------------------------------------- |
| `yarn start`  | Dev server on http://localhost:3000 with hot reload             |
| `yarn build`  | Production build to `frontend/build/`                           |
| `yarn test`   | Runs CRA / Craco tests (none configured by default)             |

### Backend (`cd backend`)

| Command                                                        | What it does                                             |
| -------------------------------------------------------------- | -------------------------------------------------------- |
| `uvicorn server:app --host 0.0.0.0 --port 8001 --reload`       | Dev server on http://localhost:8001                      |
| `uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4`    | Production-style server (no reload, multiple workers)    |

---

## Adding / updating content

All page copy is centralized in **`frontend/src/data/content.js`**.

Update the exported constants there — the components will re-render automatically:

| Constant         | Controls                                                            |
| ---------------- | ------------------------------------------------------------------- |
| `BRAND`          | Logo, wordmark, tagline                                             |
| `CONTACT`        | Phone, email, address (used in Footer + Contact page)               |
| `NAV`            | Nav labels + dropdown items                                         |
| `HOMEPAGE`       | All 11 homepage section contents                                    |
| `PAGE_CONFIGS`   | 8 product / solution pages (name, hero, stats, capabilities, accent)|
| `ACCENT`         | Color tokens per product/solution accent theme                      |
| `RECOGNITION`    | Awards page                                                         |
| `CASESTUDIES`    | Case studies page                                                   |
| `ABOUT`          | About page + team roster (name, title, photo, LinkedIn)             |
| `CONTACT_PAGE`   | Contact page copy                                                   |
| `FOOTER`         | Footer columns, socials, badges, legal links                        |

To add a new product/solution page: add an entry to `PAGE_CONFIGS`, then add a route in `App.js` if you need a custom slug — otherwise `/products/:slug` and `/solutions/:slug` pick it up automatically.

---

## Adding / updating images

Drop new images into `frontend/public/assets/…` and reference them by absolute path (`/assets/…`):

| Folder          | Purpose                                                                 |
| --------------- | ----------------------------------------------------------------------- |
| `brand/`        | `logo-square.png` (favicon + navbar), `logo-wide.png` (footer lockup)   |
| `badges/`       | `iso.png`, `msme.png`, `startup-india.png` (footer certifications)      |
| `team/`         | 7 headshots: `vinay-velivela.jpg`, `saladi-chandra-balaji.jpg`, etc.    |

> For team members: also update the `ABOUT.team` object in `content.js` with the matching filename in the `photo` field.

**Optimizations recommended before commit:**
- Team headshots: 800×1000 max, JPEG q≈85
- Badges: PNG with transparent background, ≤ 200×200
- Logos: prefer SVG when available for crisp rendering at any size

---

## Deployment

### Frontend static hosting (Vercel / Netlify / Cloudflare Pages)

```bash
cd frontend
yarn build         # produces ./build
```

Deploy the contents of `frontend/build/` to any static host.

Set the environment variable in the host UI:

```
REACT_APP_BACKEND_URL=https://api.your-domain.com
```

### Backend Docker & Railway Deployment

#### 1. Docker Build
Build the production-ready FastAPI backend Docker image:
```bash
docker build -t citta-backend .
```

#### 2. Docker Run
Run the container locally with environment variables:
```bash
docker run -d -p 8000:8000 --env-file backend/.env --name citta-backend citta-backend
```
Test health endpoints:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/health
```

#### 3. Docker Compose
Start the complete production backend environment using Docker Compose:
```bash
docker compose up -d
```
Stop the services:
```bash
docker compose down
```

#### 4. Deploying to Railway
1. **Connect Repository**: Link `https://github.com/rohan36389/citta` in your Railway Dashboard.
2. **Build Strategy**: Select **Dockerfile** (Railway automatically detects the root `Dockerfile`).
3. **Environment Variables**: Add required runtime variables in Railway's Variables panel:
   - `LLM_PROVIDER=nvidia`
   - `NVIDIA_API_KEY=your_nvidia_api_key`
   - `NVIDIA_MODEL=meta/llama-3.1-70b-instruct`
   - `CORS_ORIGINS=*`
4. **Port Handling**: Railway automatically injects the `PORT` variable. The container's startup command `uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}` binds dynamically.
5. **Health Checks**: Configure Railway health check path to `/health` or `/api/health`.


---

## Troubleshooting — get rid of all errors

The list below covers **every error you're likely to hit** during local setup, ordered by frequency.

### A. Frontend won't start / build fails

<details>
<summary><b>1. <code>yarn install</code> fails with peer-dependency conflicts</b></summary>

**Cause:** React 19 is very new; some packages advertise older peer ranges.
**Fix:**
```bash
cd frontend
rm -rf node_modules yarn.lock
yarn install                     # yarn honors the resolutions block in package.json
```

If it *still* fails, ensure you're on **Node 20 LTS** (not 22+, not 16):
```bash
nvm install 20 && nvm use 20
```
</details>

<details>
<summary><b>2. <code>Cannot find module '@/…'</code></b></summary>

**Cause:** The `@` path alias to `./src` is provided by CRACO + `jsconfig.json`.
**Fix:** Make sure you start the dev server with **`yarn start`** (which invokes `craco start`), NOT `react-scripts start`.
</details>

<details>
<summary><b>3. <code>ReactCurrentOwner</code> is undefined / R3F crashes on load</b></summary>

**Cause:** React 19 removed `ReactCurrentOwner`. Older `@react-three/fiber` (v8) breaks.
**Fix:** This repo pins `@react-three/fiber 9.0.4` and `@react-three/drei 9.121.5` which support React 19. Do not upgrade past drei 10 unless you also upgrade Node to 22+.
```bash
yarn add @react-three/fiber@9.0.4 @react-three/drei@9.121.5
```
</details>

<details>
<summary><b>4. Blank white screen / hero canvas doesn't render</b></summary>

**Cause 1:** Your browser doesn't have WebGL. Test at https://get.webgl.org/.
**Cause 2:** GPU acceleration disabled in Chrome — go to `chrome://gpu` and confirm hardware acceleration is on.
**Cause 3:** In DevTools console, look for `THREE.WebGLRenderer` errors. If shaders fail, try another browser.
</details>

<details>
<summary><b>5. <code>ENOSPC: System limit for file watchers reached</code> (Linux only)</b></summary>

**Fix:**
```bash
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p
```
</details>

<details>
<summary><b>6. Fonts don't load / typography looks off</b></summary>

**Cause:** Google Fonts blocked (corporate firewall, adblocker).
**Fix:** Self-host by downloading the fonts and pointing `index.html` at local files, or use a font mirror. Alternatively remove the `<link>` in `frontend/public/index.html` and use system fonts.
</details>

<details>
<summary><b>7. Port 3000 already in use</b></summary>

**Fix:**
```bash
PORT=3001 yarn start
# or find the process
lsof -i :3000 | awk 'NR>1 {print $2}' | xargs kill -9
```
</details>

<details>
<summary><b>8. Tailwind classes not applying / styles missing</b></summary>

**Fix:** Ensure `tailwind.config.js` `content` glob includes `./src/**/*.{js,jsx}`. Restart `yarn start` after any change to `tailwind.config.js`.
</details>

<details>
<summary><b>9. Team photos / logo 404</b></summary>

**Cause:** Assets not under `frontend/public/assets/…`.
**Fix:** Verify the tree:
```bash
ls frontend/public/assets/team frontend/public/assets/brand frontend/public/assets/badges
```
If missing, restore from the repo (`git checkout -- frontend/public/assets`) or re-download from the source.
</details>

<details>
<summary><b>10. <code>webpack compiled with 1 warning</code> about source maps for MediaPipe / vision_bundle</b></summary>

Harmless. It's a missing source map for a transitive dep — safe to ignore.
</details>

### B. Backend errors

<details>
<summary><b>1. <code>MongoClient</code> fails with connection refused</b></summary>

**Fix:** MongoDB isn't running. Start it:
```bash
# macOS
brew services start mongodb-community
# Ubuntu
sudo systemctl start mongod
# Windows
net start MongoDB
```
Then test:
```bash
mongosh mongodb://localhost:27017
```
</details>

<details>
<summary><b>2. <code>ModuleNotFoundError</code> after activating venv</b></summary>

**Fix:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```
Ensure your IDE/terminal is using the venv's Python (`which python3` should print a path inside `.venv`).
</details>

<details>
<summary><b>3. CORS error in browser when calling <code>/api/*</code> from the frontend</b></summary>

**Fix:** Set `CORS_ORIGINS` in `backend/.env` to include your frontend origin, then restart the backend:
```env
CORS_ORIGINS=http://localhost:3000
```
</details>

<details>
<summary><b>4. <code>emergentintegrations==0.2.0</code> fails to install</b></summary>

That package is Emergent-platform-internal. If you're running purely locally and don't use LLM integrations, **remove it from `requirements.txt`** and re-install:
```bash
sed -i.bak '/emergentintegrations/d' requirements.txt
pip install -r requirements.txt
```
</details>

<details>
<summary><b>5. Port 8001 in use</b></summary>

**Fix:** Change port when starting: `uvicorn server:app --port 8002`. Also update `REACT_APP_BACKEND_URL` in `frontend/.env`.
</details>

### C. General

<details>
<summary><b>Environment variable changes not picked up</b></summary>

Both Create React App and Uvicorn read `.env` **once at startup**. Restart the dev server after any `.env` edit.
</details>

<details>
<summary><b>Windows: <code>yarn</code> command not found</b></summary>

Install via npm: `npm i -g yarn`. If PATH issues persist, use `npx yarn install` and `npx yarn start`.
</details>

<details>
<summary><b>Hot reload not working</b></summary>

If you're on WSL2 or Docker Desktop, native file events sometimes don't bubble. Force polling:
```bash
CHOKIDAR_USEPOLLING=true yarn start
```
</details>

<details>
<summary><b>Production build is huge / slow first paint</b></summary>

The 3D hero (`three.js` + `@react-three/*`) is lazy-loaded via `React.lazy` — first paint should be under 1s. If the whole bundle is big, run `yarn build` and inspect `build/static/js/*.js` sizes; anything over 300 KB gzip should be split.
</details>

---

## License & credits

- Real photos of leadership, real logo, and real certification badges are the property of **CittaAI Pvt. Ltd.**
- Fonts: [Geist](https://vercel.com/font), [Inter](https://rsms.me/inter/), [JetBrains Mono](https://www.jetbrains.com/lp/mono/) — all under Open Font License.
- Everything else — code, layouts, motion — MIT unless otherwise noted.

---

## Support

If you hit an error that isn't in the [Troubleshooting](#troubleshooting--get-rid-of-all-errors) list:

1. `rm -rf frontend/node_modules frontend/yarn.lock && yarn install` — resolves ~80% of setup issues.
2. Check Node version — must be **20.x LTS**.
3. Open an issue at https://github.com/rohan36389/citta/issues with:
   - Node / Python versions (`node -v`, `python3 -V`)
   - Full error message + stack
   - OS

---

**Elevate. Innovate. Captivate.**
