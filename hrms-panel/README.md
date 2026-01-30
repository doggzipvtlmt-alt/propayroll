# HRMS Candidate Tracking + Onboarding Panel

Production-ready MVP for a strict, form-driven candidate tracker and onboarding document system.

## Local Setup
```bash
cd hrms-panel
npm install
npm start
```

The app runs at `http://localhost:3000` by default.

## Environment Variables
Copy the sample environment file and adjust as needed:
```bash
cp .env.example .env
```

- `PORT`: server port (default 3000)
- `HRMS_STORAGE_DIR`: storage folder (default `storage`)

## Excel Storage
Excel files are auto-created if missing:
- `storage/excel/candidates.xlsx` (sheet: `Candidates`)
- `storage/excel/onboarding.xlsx` (sheet: `Onboarding`)

Each write appends a new row (event log style). Candidate updates do not overwrite old rows.

## Candidate ID Generator
Candidate IDs are generated on save as:
`CAND-YYYYMMDD-####`

The system looks at existing candidate rows for the current date (`YYYYMMDD`), finds the
highest daily sequence, and increments it. This guarantees a daily incrementing sequence
that resets each day.

## Key Routes
### Pages
- `/` → Candidate Entry + Candidate Table
- `/candidate/:id` → Candidate detail + onboarding workflow

### API Endpoints
- `POST /api/candidates`
- `GET /api/candidates`
- `GET /api/candidates/:id`
- `POST /api/candidates/:id/onboarding/category`
- `POST /api/candidates/:id/onboarding/self-declaration`
- `POST /api/candidates/:id/upload`
- `POST /api/candidates/:id/onboarding/submit`
- `GET /api/candidates/:id/documents`

## Render Deployment Notes
- **Build Command:** `npm install`
- **Start Command:** `npm start`
- Ensure the Render service root is set to `hrms-panel/` (or update commands to `cd hrms-panel`).
- Configure environment variables from `.env.example`.

## Folder Structure
```
hrms-panel/
├── public/
│   ├── css/styles.css
│   ├── js/app.js
│   ├── js/candidate.js
│   ├── candidate.html
│   └── index.html
├── server.js
├── package.json
├── .env.example
└── README.md
```
