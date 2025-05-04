import gradio as gr
import pandas as pd

def calculate_bmi(weight, height):
    return weight / ((height / 100) ** 2)

def calculate_body_fat(bmi, age, gender):
    if gender == "Male":
        return (1.20 * bmi) + (0.23 * age) - 16.2
    else:
        return (1.20 * bmi) + (0.23 * age) - 5.4

def determine_age_group(age):
    if 18 <= age <= 30:
        return "Young Adult"
    elif 31 <= age <= 50:
        return "Adult"
    elif age >= 51:
        return "Senior"

def generate_plan(weight, height, age, gender, workout_days, goal):
    bmi = calculate_bmi(weight, height)
    body_fat = calculate_body_fat(bmi, age, gender)
    age_group = determine_age_group(age)
    
    # Load workout plans from CSV
    workout_plans_df = pd.read_csv("workout_plans_4.csv")
    
    # Print input parameters for debugging
    print(f"Inputs: weight={weight}, height={height}, age={age}, gender={gender}, workout_days={workout_days}, goal={goal}, age_group={age_group}")
    
    # Filter the workout plan based on goal, days, gender, and age group
    workout_plan_row = workout_plans_df[
        (workout_plans_df["Goal"] == goal) &
        (workout_plans_df["Days"] == workout_days) &
        (workout_plans_df["Gender"] == gender) &
        (workout_plans_df["Age Group"] == age_group)
    ]
    
    # Print filtered DataFrame for debugging
    print("Filtered DataFrame:")
    print(workout_plan_row)
    
    # Handle cases where no plan is found
    if len(workout_plan_row) > 0:
        workout_plan_text = workout_plan_row["Plan"].values[0]
        workout_suggestions = workout_plan_row["Suggestions"].values[0]
        
        # Split the workout plan into individual days and format with new lines
        formatted_plan = ""
        days = [day.strip() for day in workout_plan_text.split(". ") if day.strip()]
        for i, day in enumerate(days, 1):
            formatted_plan += f"{day}\n\n"
    else:
        formatted_plan = "No plan available for the selected combination. Try fewer days, a different goal, or consult a trainer."
        workout_suggestions = "Consider adjusting your workout frequency, goal, or seeking a custom plan from a professional."
    
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
    description="Enter your details to receive a fully customized workout and diet plan with BMI, body fat percentage, and expert suggestions tailored to your gender and age group."
)

interface.launch()