from flask import Flask, request, jsonify, request, render_template, redirect, url_for
from rapidfuzz import process
import pandas as pd
import re
import requests
import os

app = Flask(__name__)

nutrition_df = pd.read_csv("cleaned_nutrition_data.csv")
nutrition_df['food'] = nutrition_df['food'].str.strip().str.lower()
food_tokens = set()
for food in nutrition_df['food']:
    for word in food.split():
        food_tokens.add(word.strip(",().").lower())

NUTRIENT_UNITS = {
    "calories": "kcal",
    "protein": "g",
    "carbohydrates": "g",
    "fat": "g"
}
NUTRIENT_TERMS = set(NUTRIENT_UNITS.keys())

# nutrition stat functionality

def detect_nutrient(user_input):
    nutrients = {
        "calories": "calories",
        "protein": "protein",
        "carbs": "carbohydrates",
        "carbohydrates": "carbohydrates",
        "fat": "fat",
        "fats": "fat"
    }
    for word in user_input.lower().split():
        if word in nutrients:
            return nutrients[word]
    return None

def match_food(user_input):
    stopwords = {'how', 'many', 'much', 'in', 'is', 'the', 'a', 'an', 'of', 'are', 'what', "what's"}
    words = re.findall(r'\b[a-z]+\b', user_input.lower())
    keywords = [word for word in words if word not in stopwords and word not in NUTRIENT_TERMS]

    print(f"[DEBUG] Extracted: {keywords}")

    food_candidates = [w for w in keywords if w in food_tokens]
    print(f"[DEBUG] Filtered food candidates: {food_candidates}")

    if not food_candidates:
        return None

    # Try exact match
    for food in nutrition_df['food']:
        for word in food_candidates:
            if word in food:
                print(f"[DEBUG] Exact match: '{word}' in '{food}'")
                return food

    # Fuzzy fallback
    for word in food_candidates:
        result = process.extractOne(word, nutrition_df['food'].tolist(), score_cutoff=75)
        if result:
            best_match, _, _ = result
            print(f"[DEBUG] Fuzzy match: '{word}' → '{best_match}'")
            return best_match

    return None


# recipe functionality


def get_recipes(ingredients):
    API_KEY = os.getenv("SPOONACULAR_API_KEY")

    if not API_KEY:
        print("[ERROR] Missing Spoonacular API key.")
        return {"error": "API key not configured."}

    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "ingredients": ingredients,
        "number": 3,
        "ranking": 1,
        "apiKey": API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print("[ERROR] Spoonacular API HTTP Error:", e)
        return {"error": "Invalid Spoonacular API key or quota exceeded."}
    except Exception as e:
        print("[ERROR] Spoonacular API:", e)
        return {"error": "Could not fetch recipes."}

def is_recipe_query(user_input):
    keywords = ["recipe", "cook", "make", "dish", "meal", "dinner", "ingredients"]
    return any(word in user_input.lower() for word in keywords)


# routes

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        user_input = request.form.get("message", "").strip().lower()

        if is_recipe_query(user_input):
            ingredients = ','.join(re.findall(r'\b[a-z]+\b', user_input))
            recipes = get_recipes(ingredients)
            if isinstance(recipes, dict) and "error" in recipes:
                return render_template("result.html", question=user_input, recipes=None, highlight=recipes["error"])
            return render_template("result.html", question=user_input, recipes=recipes, highlight=None)

        matched_food = match_food(user_input)
        focus_nutrient = detect_nutrient(user_input)

        if matched_food:
            row = nutrition_df[nutrition_df['food'] == matched_food].iloc[0]
            highlight = None
            if focus_nutrient and focus_nutrient in row:
                value = row[focus_nutrient]
                unit = NUTRIENT_UNITS.get(focus_nutrient, "")
                highlight = f"The {focus_nutrient} in {matched_food.title()} is {value} {unit}!"

            return render_template("result.html", question=user_input, food=matched_food.title(), highlight=highlight,
                                   calories=f"{row['calories']} kcal",
                                   protein=f"{row['protein']} g",
                                   carbohydrates=f"{row['carbohydrates']} g",
                                   fat=f"{row['fat']} g",
                                   recipes=None)

        return render_template("result.html", question=user_input, highlight="Food not found.", recipes=None)

    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip().lower()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    if is_recipe_query(user_message):
        ingredients = ','.join(re.findall(r'\b[a-z]+\b', user_message))
        recipes = get_recipes(ingredients)
        if recipes:
            return jsonify({
                "type": "recipe",
                "recipes": [
                    {"title": r["title"], "usedIngredientCount": r["usedIngredientCount"]}
                    for r in recipes
                ]
            })
        else:
            return jsonify({"error": "Failed to fetch recipes."}), 500

    matched_food = match_food(user_message)
    focus_nutrient = detect_nutrient(user_message)

    if matched_food:
        row = nutrition_df[nutrition_df['food'] == matched_food].iloc[0]
        response = {
            "food": matched_food.title(),
            "calories": f"{row['calories']} kcal",
            "protein": f"{row['protein']} g",
            "carbohydrates": f"{row['carbohydrates']} g",
            "fat": f"{row['fat']} g"
        }
        if focus_nutrient and focus_nutrient in row:
            response["highlight"] = f"{focus_nutrient.title()}: {row[focus_nutrient]} {NUTRIENT_UNITS[focus_nutrient]}"
        return jsonify(response)

    return jsonify({"error": "Food not found."}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
