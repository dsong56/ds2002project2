# 🥗 Nutrition & Recipe Chatbot Assistant

This is a Flask-based chatbot that answers nutrition questions using USDA data and suggests recipes using the Spoonacular API. It is deployed on a Google Cloud VM and publicly accessible.

---

## ✅ What This Project Does

- **Nutrition Q&A:** Answers questions like "How much protein is in eggs?"
- **Recipe Search:** Suggests recipes for questions like "What can I cook with chicken and rice?"
- **Data Sources:**
  - Local: `cleaned_nutrition_data.csv` (ETL-processed from USDA)
  - Live: Spoonacular API
- **Deployed:** Flask app is hosted on a Google Cloud VM with systemd
- **Persistent:** Runs in background and restarts on reboot
- **Styled:** Clean web interface using HTML, CSS, and Flask templates
- **Two Interfaces:**
  - `/` — interactive browser UI
  - `/chat` — JSON API endpoint

---

## 🚀 How It Works

1. **ETL Pipeline** (via `etl.py`) merges:
   - `food.csv`
   - `food_nutrient.csv`
   - `nutrient.csv`
   → into `cleaned_nutrition_data.csv`

2. **Flask App (`app.py`)**
   - Uses fuzzy matching to detect food names
   - Detects if user is asking about a nutrient or a recipe
   - Loads cleaned USDA data locally
   - Calls Spoonacular API for live recipe suggestions

3. **Deployment**
   - Hosted on GCP Compute Engine (Ubuntu VM)
   - Flask runs with `gunicorn` under `systemd`
   - Spoonacular API key set via environment variable in systemd config

---

## 🧭 How to Use It

### Option A: Visit the Live App

You can go to, powered by Google Cloud Platform:

**http://34.86.175.178:5000/**

### Option B: Run Locally

1. **Clone the repo**

```bash
git clone https://github.com/dsong56/ds2002project2.git
cd ds2002project2
```

2. **Install requirements**

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask pandas requests rapidfuzz
```

3. **Set your Spoonacular API key**

```bash
export SPOONACULAR_API_KEY=your_key_here
```

4. **Run the app**

```bash
python app.py
```

Visit: `http://127.0.0.1:5000`

---
