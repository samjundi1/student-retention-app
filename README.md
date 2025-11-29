# Student Retention MVC Web App

Collaborative web application for predicting student retention using machine learning.
- **Backend:** FastAPI (Python & ML model)
- **Frontend:** React (with Vite; see [Vite documentation](https://vitejs.dev/))

---

## Folder Structure

```
/backend      # FastAPI, database, ML model serving
/frontend     # React (Vite), user interface
```

---

## Backend Setup (macOS, Bash or Zsh)

1. **Python 3.x required**. Install via [Homebrew](https://brew.sh/) or [python.org](https://python.org).

2. **Create a virtual environment and install dependencies:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate   # For Bash/Zsh
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Run FastAPI server:**
   ```bash
   uvicorn main:app --reload
   # API served at http://localhost:8000
   ```

---

## Frontend Setup (React/Vite, Node.js 20+ required)

1. **Node.js 20.x required for Vite**  
   - Recommended: Use **nvm** to manage Node versions:
     ```bash
     # Install nvm if needed
     curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

     # Activate nvm in new terminal sessions
     export NVM_DIR="$HOME/.nvm"
     [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

     # Install and use Node.js 20
     nvm install 20
     nvm use 20
     ```

2. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   - Opens at [http://localhost:5173](http://localhost:5173)

---

## .gitignore Highlights

```gitignore
# Python
backend/venv/
__pycache__/
*.pyc
*.db
*.joblib
*.keras

# Frontend Node/React
frontend/node_modules/
frontend/build/
frontend/dist/
frontend/.env

# General
.DS_Store
.env
*.log
```

---

## Collaboration & Team Notes

- All team members should use **Node 20+** for the frontend (`nvm use 20`).
- Do **not** commit `node_modules`, `venv`, `.env` files, build/dist outputs.
- Make sure to run `npm install` after pulling frontend changes.
- For new shells, run `nvm use 20` before working in `/frontend`.

---

## Troubleshooting

- **Node.js version errors:** Use nvm to switch to Node 20 (`nvm use 20`).
- **Virtual environment errors:** Remove old `venv/`, recreate, and install dependencies.
- **Any issues:** Ask in team chat or open a GitHub Issue.

---

## Deployment

- Backend: See Dockerfile for production containerization.
- Frontend: Vite app can be built with `npm run build` and deployed on Netlify, Vercel, or similar.

---

**Keep this README up-to-date with project changes. Happy collaborating!**