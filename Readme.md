
---

````markdown
# 🍳 Recipe Blog
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Build](https://img.shields.io/github/actions/workflow/status/kashan16/Recipe_Blog/ci.yml)](https://github.com/kashan16/Recipe_Blog/actions)
[![Issues](https://img.shields.io/github/issues/kashan16/Recipe_Blog)](https://github.com/kashan16/Recipe_Blog/issues)

> **AI-powered recipe discovery platform** to find, generate, and manage recipes based on available ingredients.  
> Built with a React TypeScript frontend and Flask backend.

---

## 📌 Quick Links
- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 📖 Overview
Recipe Blog is a modern cooking companion where you can:
- Search recipes by name, cuisine, or dietary needs.
- Input ingredients you have and get AI-powered recipe suggestions.
- Manage your pantry and favorite recipes.
- Generate entirely new recipes using AI.

---

## 🌟 Features

### Core
- 🔍 **Smart Recipe Search** — by name, cuisine, or dietary preferences.
- 🛒 **Ingredient-Based Discovery** — find what you can cook with what you have.
- 📋 **My Pantry** — manage your ingredient inventory.
- ❤️ **Favorites System** — save and organize recipes.

### AI-Powered
- 🤖 **Recipe Generation from Ingredients**.
- 🔄 **Ingredient Substitutions**.
- 🎯 **Personalized Recommendations**.
- ⚡ **Dietary Restriction Filtering**.


## 🛠 Tech Stack

**Frontend**
- React (TypeScript)
- Tailwind CSS
- React Router
- Axios
- React Hook Form

**Backend**
- Flask
- SQLAlchemy
- PostgreSQL
- Redis
- JWT Auth
- OpenAI API

---

## 🚀 Getting Started

### Prerequisites
- Node.js ≥ 16
- Python ≥ 3.8
- PostgreSQL ≥ 12
- Redis (for caching)
- OpenAI API key

### Installation

Clone the repo:
```bash
git clone https://github.com/kashan16/Recipe_Blog.git
cd Recipe_Blog
````

**Backend**

```bash
cd backend
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env
flask db upgrade
flask run
```

**Frontend**

```bash
cd frontend
npm install
npm start
```

Frontend: [http://localhost:3000](http://localhost:3000)
Backend API: [http://localhost:5000](http://localhost:5000)

---

## 📱 Usage

**For Users**

1. Sign up / log in.
2. Add ingredients to **My Pantry**.
3. Get AI suggestions or search recipes.
4. Save favorites for later.


## 🤝 Contributing

We welcome contributions!
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for:

* Setting up your dev environment
* Coding style guidelines
* PR process

---

## 🗺 Roadmap

* [ ] Mobile app development
* [ ] Recipe video integration
* [ ] Social sharing features
* [ ] Meal planning calendar
* [ ] Grocery delivery integration
* [ ] Voice command support
* [ ] Nutrition tracking
* [ ] Community recipe sharing

---

## 📄 License

MIT © [Kashan](https://github.com/kashan16)

---

## 🙏 Acknowledgments

* OpenAI for AI recipe generation
* Food APIs and recipe data providers
* Open-source libraries and tools

---

```


