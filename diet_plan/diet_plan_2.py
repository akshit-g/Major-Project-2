import gradio as gr
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import warnings
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')

# Load the Indian food dataset from CSV
try:
    food_df = pd.read_csv('diet_plan\indian_food_data_2.csv')
    print(f"Successfully loaded dataset with {len(food_df)} items")
    
    # Clean and prepare dataset
    required_columns = ['name', 'calories', 'protein', 'carbohydrates', 'fat', 'serving_size', 'food_group', 'meal_type', 'recipe', 'region']
    for col in required_columns:
        if col not in food_df.columns:
            raise ValueError(f"Missing required column: {col}")
    numeric_cols = ['calories', 'protein', 'carbohydrates', 'fat', 'serving_size']
    for col in numeric_cols:
        food_df[col] = pd.to_numeric(food_df[col], errors='coerce')
    food_df = food_df.dropna(subset=['name', 'calories', 'meal_type', 'recipe', 'region'])
except Exception as e:
    print(f"Error loading CSV: {e}")
    raise gr.Error("Failed to load food data. Please ensure 'indian_food_data.csv' is available.")

# Calculate caloric needs (Harris-Benedict Equation)
def calculate_caloric_needs(weight, height, age, gender, activity_level):
    if not all(isinstance(x, (int, float)) and x > 0 for x in [weight, height, age]):
        raise gr.Error("Weight, height, and age must be positive numbers")
    if gender.lower() == 'male':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    activity_multipliers = {'sedentary': 1.2, 'lightly active': 1.375, 'moderately active': 1.55, 
                            'very active': 1.725, 'extra active': 1.9}
    return round(bmr * activity_multipliers[activity_level.lower()])

# Calculate macronutrients
def calculate_macros(caloric_needs, goal):
    macros = {}
    if goal.lower() == 'weight loss':
        caloric_needs = caloric_needs * 0.85
        macros['protein'] = (caloric_needs * 0.30) / 4
        macros['fat'] = (caloric_needs * 0.30) / 9
        macros['carbs'] = (caloric_needs * 0.40) / 4
    elif goal.lower() == 'maintenance':
        macros['protein'] = (caloric_needs * 0.25) / 4
        macros['fat'] = (caloric_needs * 0.30) / 9
        macros['carbs'] = (caloric_needs * 0.45) / 4
    elif goal.lower() == 'muscle gain':
        caloric_needs = caloric_needs * 1.10
        macros['protein'] = (caloric_needs * 0.30) / 4
        macros['fat'] = (caloric_needs * 0.25) / 9
        macros['carbs'] = (caloric_needs * 0.45) / 4
    return {'calories': round(caloric_needs), 'protein': round(macros['protein']), 
            'carbs': round(macros['carbs']), 'fat': round(macros['fat'])}

# Recommend meals
def recommend_meals(caloric_needs, macros, restrictions, meals_per_day, regional_preference):
    filtered_foods = food_df.copy()
    
    # Filter by regional preference
    if regional_preference.lower() != 'all':
        filtered_foods = filtered_foods[filtered_foods['region'].str.contains(regional_preference, case=False, na=False) | 
                                       filtered_foods['region'].str.contains('All', case=False, na=False)]
    
    # Filter by dietary restrictions
    if 'vegetarian' in restrictions:
        filtered_foods = filtered_foods[~filtered_foods['food_group'].str.contains('Non-veg|Meat', case=False, na=False)]
    if 'vegan' in restrictions:
        filtered_foods = filtered_foods[~filtered_foods['food_group'].str.contains('Non-veg|Meat|Dairy', case=False, na=False)]
    
    # Fallback if too few foods remain
    if len(filtered_foods) < 10:
        filtered_foods = food_df.copy()
    
    per_meal_calories = caloric_needs / meals_per_day
    meal_plan = []
    daily_meal_names = ["Breakfast", "Lunch", "Evening Snack", "Dinner"][:meals_per_day]
    if meals_per_day > len(daily_meal_names):
        daily_meal_names.extend([f"Meal {i+1}" for i in range(len(daily_meal_names), meals_per_day)])
    
    for meal_name in daily_meal_names:
        # Filter foods suitable for the meal type
        potential_items = filtered_foods[filtered_foods['meal_type'].str.contains(meal_name, case=False, na=False)]
        if len(potential_items) < 5:
            potential_items = filtered_foods
        num_items = np.random.randint(2, 5)
        selected_food_items = potential_items.sample(min(num_items, len(potential_items)))
        
        selected_items = []
        current_nutrition = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
        for _, food in selected_food_items.iterrows():
            serving_multiplier = 1.0
            food_name = food.get('name', "Unknown")
            serving_size = food.get('serving_size', 100) * serving_multiplier
            item_calories = food.get('calories', 0) * serving_multiplier
            item_protein = food.get('protein', 0) * serving_multiplier
            item_carbs = food.get('carbohydrates', 0) * serving_multiplier
            item_fat = food.get('fat', 0) * serving_multiplier
            current_nutrition['calories'] += item_calories
            current_nutrition['protein'] += item_protein
            current_nutrition['carbs'] += item_carbs
            current_nutrition['fat'] += item_fat
            selected_items.append({'name': food_name, 'serving': round(serving_size), 'calories': item_calories, 
                                   'protein': item_protein, 'carbs': item_carbs, 'fat': item_fat})
        
        if current_nutrition['calories'] > 0:
            scaling_factor = per_meal_calories / current_nutrition['calories']
            for item in selected_items:
                item['serving'] = round(item['serving'] * scaling_factor)
                item['calories'] = item['calories'] * scaling_factor
                item['protein'] = item['protein'] * scaling_factor
                item['carbs'] = item['carbs'] * scaling_factor
                item['fat'] = item['fat'] * scaling_factor
            current_nutrition = {k: sum(item[k] for item in selected_items) for k in ['calories', 'protein', 'carbs', 'fat']}
        
        meal_plan.append({'name': meal_name, 'items': selected_items, 
                          'nutrition': {k: round(v) for k, v in current_nutrition.items()}})
    return meal_plan

# Format meal plan with recipes
def format_meal_plan(meal_plan, daily_targets):
    output = "# Your Personalized Indian Meal Plan\n\n"
    output += f"## Daily Targets: {daily_targets['calories']} kcal, {daily_targets['protein']}g protein, {daily_targets['carbs']}g carbs, {daily_targets['fat']}g fat\n\n"
    total_nutrition = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}
    
    for meal in meal_plan:
        output += f"### {meal['name']}\n"
        for item in meal['items']:
            output += f"- {item['name']} ({item['serving']}g) - {round(item['calories'])} kcal\n"
            recipe = food_df.loc[food_df['name'] == item['name'], 'recipe'].iloc[0] if item['name'] in food_df['name'].values else "Recipe not available."
            output += f"  *Recipe*: {recipe}\n"
        nutrition = meal['nutrition']
        total_nutrition = {k: total_nutrition[k] + v for k, v in nutrition.items()}
        output += f"\n**Nutrition:** {nutrition['calories']} kcal, {nutrition['protein']}g protein, {nutrition['carbs']}g carbs, {nutrition['fat']}g fat\n\n"
    
    output += f"## Summary: {total_nutrition['calories']} kcal, {total_nutrition['protein']}g protein, {total_nutrition['carbs']}g carbs, {total_nutrition['fat']}g fat\n"
    return output

# Main function
def create_nutrition_plan(weight, height, age, gender, activity_level, goal, dietary_restrictions, meals_per_day, regional_preference):
    caloric_needs = calculate_caloric_needs(weight, height, age, gender, activity_level)
    macros = calculate_macros(caloric_needs, goal)
    restrictions = dietary_restrictions.lower().split(', ') if dietary_restrictions else []
    meal_plan = recommend_meals(macros['calories'], macros, restrictions, meals_per_day, regional_preference)
    return format_meal_plan(meal_plan, macros)

# Progress tracking (simple example)
progress_data = {'dates': [], 'calories': []}
def track_progress(calories_consumed):
    progress_data['dates'].append(pd.Timestamp.now().strftime('%Y-%m-%d'))
    progress_data['calories'].append(float(calories_consumed))
    fig, ax = plt.subplots()
    ax.plot(progress_data['dates'], progress_data['calories'], marker='o')
    ax.set_xlabel("Date")
    ax.set_ylabel("Calories Consumed")
    plt.xticks(rotation=45)
    return fig

# Social sharing
def share_plan(plan):
    return f"Check out my Indian Meal Plan!\n\n{plan}"

# Gradio Interface
with gr.Blocks(theme=gr.themes.Soft(primary_hue="orange", secondary_hue="green"), 
               css=".gr-button {border-radius: 10px;} .header {color: #FF5733; font-size: 2em;}") as app:
    gr.Markdown("# Indian Cuisine Nutrition Planner", elem_classes="header")
    gr.Markdown("Plan your meals with authentic Indian flavors!")
    
    with gr.Row():
        with gr.Column(scale=1, min_width=300):
            weight = gr.Number(label="Weight (kg)", value=70)
            height = gr.Number(label="Height (cm)", value=170)
            age = gr.Number(label="Age", value=30)
            gender = gr.Radio(["Male", "Female"], label="Gender", value="Male")
            activity_level = gr.Dropdown(["Sedentary", "Lightly Active", "Moderately Active", 
                                        "Very Active", "Extra Active"], label="Activity Level", 
                                        value="Moderately Active")
        
        with gr.Column(scale=1, min_width=300):
            goal = gr.Radio(["Weight Loss", "Maintenance", "Muscle Gain"], label="Goal", value="Maintenance")
            dietary_restrictions = gr.Textbox(label="Dietary Restrictions (e.g., vegetarian)", value="")
            meals_per_day = gr.Slider(2, 6, value=3, step=1, label="Meals per Day")
            regional_preference = gr.Dropdown(["All", "North Indian", "South Indian", "East Indian", 
                                             "West Indian"], label="Regional Preference", value="All")
            submit_btn = gr.Button("Generate Plan", variant="primary")

    with gr.Row():
        output = gr.Markdown(label="Your Meal Plan")
    
    with gr.Tab("Track Progress"):
        calories_input = gr.Number(label="Log Today's Calories")
        track_btn = gr.Button("Add to Progress")
        progress_plot = gr.Plot(label="Calorie Progress")
    
    with gr.Tab("Share"):
        share_btn = gr.Button("Generate Shareable Plan")
        share_output = gr.Textbox(label="Share this with friends!")

    submit_btn.click(fn=create_nutrition_plan, 
                     inputs=[weight, height, age, gender, activity_level, goal, dietary_restrictions, 
                             meals_per_day, regional_preference], 
                     outputs=output)
    track_btn.click(fn=track_progress, inputs=calories_input, outputs=progress_plot)
    share_btn.click(fn=share_plan, inputs=output, outputs=share_output)

app.launch(debug=True)