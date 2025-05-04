import gradio as gr
import pandas as pd

def calculate_bmi(weight, height):
    return weight / ((height / 100) ** 2)

def calculate_body_fat(bmi, age, gender):
    if gender == "Male":
        return (1.20 * bmi) + (0.23 * age) - 16.2
    else:
        return (1.20 * bmi) + (0.23 * age) - 5.4

def generate_plan(weight, height, age, gender, workout_days, goal):
    bmi = calculate_bmi(weight, height)
    body_fat = calculate_body_fat(bmi, age, gender)
    
    # Load workout plans from CSV
    workout_plans_df = pd.read_csv("workout_plans_3.csv")
    
    # Filter the workout plan based on goal and days
    workout_plan_row = workout_plans_df[
        (workout_plans_df["Goal"] == goal) & (workout_plans_df["Days"] == workout_days)
    ]
    
    # Handle cases where no plan is found
    if len(workout_plan_row) > 0:
        workout_plan_text = workout_plan_row["Plan"].values[0]
        workout_suggestions = workout_plan_row["Suggestions"].values[0]
        
        # Split the workout plan into individual days and format with new lines
        formatted_plan = ""
        # Split by ". " to separate days, but filter out empty strings
        days = [day.strip() for day in workout_plan_text.split(". ") if day.strip()]
        for i, day in enumerate(days, 1):
            formatted_plan += f"{day}\n\n"  # Add each day's exercises on a new line
    else:
        formatted_plan = "No plan available for the selected days. Try fewer days or a different goal."
        workout_suggestions = "Consider adjusting your workout frequency or consulting a trainer for a custom plan."
    
    general_suggestions = "Stay consistent. Sleep well, track progress, and adjust intensity. Recovery & mobility work improves results."
    
    plan = (f"Your BMI: {bmi:.2f}\n"
            f"Your Estimated Body Fat Percentage: {body_fat:.2f}%\n\n"
            f"Workout Plan:\n{formatted_plan}\n"
            f"Suggestions:\n{workout_suggestions}\n{general_suggestions}")
    
    return plan

# Gradio UI
interface = gr.Interface(
    fn=generate_plan,
    inputs=[
        gr.Number(label="Weight (kg)"),
        gr.Number(label="Height (cm)"),
        gr.Number(label="Age"),
        gr.Radio(["Male", "Female"], label="Gender"),
        gr.Slider(1, 7, step=1, label="Workout Days per Week"),
        gr.Radio(["Build Muscle", "Lose Weight"], label="Choose Your Goal")
    ],
    outputs="text",
    title="Personalized Gym & Nutrition Plan",
    description="Enter your details to receive a fully customized workout and diet plan with BMI, body fat percentage, and expert suggestions."
)

interface.launch()