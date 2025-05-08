import pandas as pd

NUTRIENTS_OF_INTEREST = {
    "Energy": "calories",
    "Protein": "protein",
    "Carbohydrate, by difference": "carbohydrates",
    "Total lipid (fat)": "fat"
}

def extract_data():
    food_df = pd.read_csv("food.csv", low_memory=False)
    nutrient_df = pd.read_csv("nutrient.csv", low_memory=False)
    food_nutrient_df = pd.read_csv("food_nutrient.csv", low_memory=False)
    return food_df, nutrient_df, food_nutrient_df

def transform_data(food_df, nutrient_df, food_nutrient_df):
    nutrient_df = nutrient_df.rename(columns={"id": "nutrient_id"}) # renaming 'id' in nutrient_df to match food_nutrient_df
    nutrients_filtered = nutrient_df[nutrient_df['name'].isin(NUTRIENTS_OF_INTEREST.keys())]

    merged = pd.merge(food_nutrient_df, nutrients_filtered, on="nutrient_id") # merging nutrient info
    merged = pd.merge(merged, food_df[['fdc_id', 'description']], on="fdc_id") # merging food descriptions

    pivot = merged.pivot_table(
        index="description",
        columns="name",
        values="amount",
        aggfunc="first"
    ).reset_index()

    pivot = pivot.rename(columns=NUTRIENTS_OF_INTEREST)
    pivot['food'] = pivot['description'].str.strip().str.lower()
    pivot.dropna(subset=NUTRIENTS_OF_INTEREST.values(), inplace=True)

    return pivot[['food'] + list(NUTRIENTS_OF_INTEREST.values())]

def load_data(df, output_file):
    df.to_csv(output_file, index=False)
    print(f"Saved cleaned data to {output_file}")

def run_etl():
    food_df, nutrient_df, food_nutrient_df = extract_data()
    cleaned_df = transform_data(food_df, nutrient_df, food_nutrient_df)
    load_data(cleaned_df, "cleaned_nutrition_data.csv")

if __name__ == "__main__":
    run_etl()