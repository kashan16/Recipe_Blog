# 🍳 Recipe Blog — AI-powered Recipe Discovery

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Issues](https://img.shields.io/github/issues/kashan16/Recipe_Blog)](https://github.com/kashan16/Recipe_Blog/issues) [![Build Status](https://img.shields.io/github/actions/workflow/status/kashan16/Recipe_Blog/ci.yml)]()

> **Find, generate, and cook great recipes from the ingredients you already have — powered by AI.**

---

## 📌 Quick links

* [Features](#-features)
* [Quick Start](#-quick-start)
* [Tech Stack](#-tech-stack)
* [Project Structure](#-project-structure)
* [Usage](#-usage)
* [Docs](#-docs)
* [Contributing](#-contributing)
* [Roadmap](#-roadmap)
* [License](#-license)

---

## 🌟 Features

**Core**

* 🔍 Smart search by name, cuisine, or dietary filters
* 🧺 "My Pantry" — manage your available ingredients
* 📄 Recipe pages with instructions, nutrition, and metadata
* ⭐ Favorites and organized recipe collections

**AI-powered**

* 🤖 Generate complete recipes from a list of ingredients
* 🔁 Suggest ingredient substitutions and variations
* 🎯 Personalized recommendations and dietary filtering
* ⚡ Caching for fast AI responses (Redis)

---

## 🚀 Quick Start

Get the app running locally in \~5 minutes.

### Prerequisites

* Node.js >= 16
* Python >= 3.8
* PostgreSQL >= 12
* Redis (optional but recommended for AI caching)
* OpenAI API key (for AI features)

### Clone

```bash
git clone https://github.com/kashan16/Recipe_Blog.git
cd Recipe_Blog
```

### Backend (minimal)

```bash
cd backend
python -m venv venv
source venv/bin/activate      # macOS / Linux
# venv\Scripts\activate     # Windows
pip install -r requirements.txt
cp .env.example .env          # edit .env values
flask db upgrade              # apply migrations
flask run                     # runs at http://localhost:5000
```

### Frontend (minimal)

```bash
cd frontend
npm install
npm start                     # runs at http://localhost:3000
```

**API base URLs**

* Frontend: `http://localhost:3000`
* Backend: `http://localhost:5000`

---

## ⚙️ Environment (example `.env`)

Place these in `/backend/.env` (use `.env.example` as a template).

```env
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=postgresql://username:password@localhost/recipe_blog
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=sk-...
JWT_SECRET_KEY=your_jwt_secret_key
```

---

## 🗂 Project Structure

```
Recipe_Blog/
├── frontend/                 # React + TypeScript SPA
│   ├── src/
│   ├── public/
│   └── package.json
├── backend/                  # Flask API
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── __init__.py
│   ├── migrations/
│   └── requirements.txt
├── docs/                     # API, DB schema, screenshots
└── README.md
```

> Move long reference material into `docs/` (API reference, DB schema, deployment notes).

---

## 🔌 API / Integration (quick)

Full API reference is in `docs/API.md`. Keep the README lean — put only examples here.

**AI Recipe Generation (example)**

```
POST /api/ai/generate-recipe
{
  "ingredients": ["chicken", "rice", "broccoli"],
  "dietary_restrictions": ["gluten-free"],
  "cuisine_type": "asian",
  "cooking_time": "30"
}
```

Response: JSON recipe object with `title`, `ingredients`, `instructions`, `nutrition`.

---

## 🧪 Testing

**Backend**

```bash
cd backend
pytest
```

**Frontend**

```bash
cd frontend
npm test
```

---

## 📦 Deployment (short)

**Backend**: export env vars in your host (Railway, Render, Heroku). Build `requirements.txt` with `pip freeze > requirements.txt` and point the platform to `backend/`.

**Frontend**: `npm run build` then deploy `frontend/build` to Vercel, Netlify, or static hosting.

Add a full `docs/deploy.md` for provider-specific instructions.

---

## 🤝 Contributing

We welcome contributions! Keep the README focused — add contribution rules to `CONTRIBUTING.md`.

Minimal guidance:

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Run tests & linters
4. Open a pull request with a clear description

See `CONTRIBUTING.md` for coding style, commit message format, and PR checklist.

---

## 🗺 Roadmap

* [ ] Mobile app (React Native)
* [ ] Recipe video integration
* [ ] Meal planning & calendar
* [ ] Grocery delivery integration
* [ ] Nutrition tracking & analytics

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

## 👥 Authors & Acknowledgments

**Kashan** — [@kashan16](https://github.com/kashan16)

Thanks to OpenAI for the generative APIs and the open-source ecosystem for tooling.

---

## 📬 Support

If you find issues or want to request features:

* Search or open an issue: `https://github.com/kashan16/Recipe_Blog/issues`

Happy cooking! 🍽️
