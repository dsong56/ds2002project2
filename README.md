# 🥗 Nutrition & Recipe Chatbot Assistant

This is a Flask-based chatbot that can answer nutrition questions and suggest recipes based on ingredients.

## ✅ Features

- Ask nutrition questions like:  
  - *"How much protein is in eggs?"*  
  - *"What are the calories in almonds?"*
- Ask for recipes using ingredients:  
  - *"What can I cook with chicken and spinach?"*
- Highlights specific nutrients if mentioned
- Fetches recipes using live data from Spoonacular
- Uses USDA nutrition data via a custom ETL pipeline
- Clean, styled HTML interface and a `/chat` API route
- Fully deployable on Google Cloud

---

## 🧾 Data Sources

- **Nutrition dataset:**  
  [USDA FoodData Central](https://fdc.nal.usda.gov/download-datasets)  
  Files used: `food_nutrient.csv`, `food.csv`, `nutrient.csv`

- **Recipe API:**  
  [Spoonacular Food API](https://spoonacular.com/food-api)

---

## 🛠️ Setup Instructions

### 1. Clone the repo and install dependencies

```bash
pip install flask pandas requests rapidfuzz
```

### 2. Get a Spoonacular API Key

Sign up at [Spoonacular](https://spoonacular.com/food-api) and get your API key.

### 3. Configure your API key

You can then replace `"YOUR_API_KEY_HERE"` directly in `app.py`