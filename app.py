from flask import Flask, request, jsonify
from rapidfuzz import process
import pandas as pd
import re

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
    user_input = user_input.lower()
    stopwords = {'how', 'many', 'much', 'in', 'is', 'the', 'a', 'an', 'of', 'are', 'what', "what's"}

    words = re.findall(r'\b[a-z]+\b', user_input)
    keywords = [word for word in words if word not in stopwords]

    print(f"[DEBUG] Extracted: {keywords}")

    # Step 1: Prioritize known food-related words
    food_candidates = [w for w in keywords if w in food_tokens]

    print(f"[DEBUG] Filtered food candidates: {food_candidates}")

    if not food_candidates:
        return None

    # Step 2: Try exact match by substring first
    for food in nutrition_df['food']:
        for word in food_candidates:
            if word in food:
                print(f"[DEBUG] Exact match: '{word}' in '{food}'")
                return food

    # Step 3: Try fuzzy match
    for word in food_candidates:
        result = process.extractOne(word, nutrition_df['food'].tolist(), score_cutoff=75)
        if result:
            best_match, score, _ = result
            print(f"[DEBUG] Fuzzy match '{word}' → '{best_match}' (score {score})")
            return best_match

    return None



@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        user_input = request.form.get("message", "").strip().lower()
        matched_food = match_food(user_input)
        focus_nutrient = detect_nutrient(user_input)

        if matched_food:
            row = nutrition_df[nutrition_df['food'] == matched_food].iloc[0]

            nutrient_highlight = ""
            if focus_nutrient and focus_nutrient in row:
                value = row[focus_nutrient]
                unit = NUTRIENT_UNITS.get(focus_nutrient, "")
                nutrient_highlight = f"<h2>The {focus_nutrient} in <em>{matched_food.title()}</em> is <strong>{value} {unit}</strong>!</h2>"

            return f"""
                <h3>Your question:</h3>
                <p>{user_input}</p>
                {nutrient_highlight if nutrient_highlight else ''}
                <h4>Full Nutrition Facts for '{matched_food.title()}'</h4>
                <ul>
                    <li><strong>Calories:</strong> {row['calories']} kcal</li>
                    <li><strong>Protein:</strong> {row['protein']} g</li>
                    <li><strong>Carbohydrates:</strong> {row['carbohydrates']} g</li>
                    <li><strong>Fat:</strong> {row['fat']} g</li>
                </ul>
                <br><a href='/'>Ask another question</a>
            """


        return "<p>Food not found. <a href='/'>Try again</a></p>"

    return '''
        <h1>Nutrition Chatbot</h1>
        <form method="POST">
            <label>Ask a question:</label><br>
            <input type="text" name="message" size="50">
            <input type="submit" value="Submit">
        </form>
    '''


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip().lower()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    matched_food = match_food(user_message)
    if matched_food:
        row = nutrition_df[nutrition_df['food'] == matched_food].iloc[0]
        response = {
            "food": matched_food.title(),
            "calories": row["calories"],
            "protein": row["protein"],
            "carbohydrates": row["carbohydrates"],
            "fat": row["fat"]
        }
        return jsonify(response)

    return jsonify({"error": "Food not found in database"}), 404


if __name__ == "__main__":
    app.run(debug=True)
