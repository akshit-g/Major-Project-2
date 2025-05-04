import gradio as gr

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
    
    workout_plan = {
        "Build Muscle": {
            1: "Full-body workout: Squats (4x8), Deadlifts (3x6), Bench Press (4x8), Pull-ups (3x10), Planks (3x60s). Use compound movements for maximal strength.",
            3: "Day 1: Chest & Triceps - Bench Press (4x8), Dips (3x10), Triceps Pushdown (3x12).\nDay 2: Back & Biceps - Deadlifts (4x6), Lat Pulldown (3x10), Bicep Curls (3x12).\nDay 3: Legs & Core - Squats (4x8), Leg Press (3x12), Hanging Leg Raises (3x15).",
            4: "Day 1: Chest & Triceps - Bench Press (4x8), Dumbbell Flys (3x12).\nDay 2: Back & Biceps - Barbell Rows (4x8), Hammer Curls (3x12).\nDay 3: Legs - Squats (4x8), Calf Raises (3x15).\nDay 4: Shoulders & Abs - Overhead Press (4x8), Side Planks (3x60s).",
            5: "Day 1: Chest - Incline Bench (4x8), Cable Crossovers (3x12).\nDay 2: Back - Deadlifts (4x6), Lat Pulldown (3x10).\nDay 3: Legs - Squats (4x8), Leg Press (3x12).\nDay 4: Arms - Bicep Curls (3x12), Skull Crushers (3x10).\nDay 5: Shoulders & Core - Overhead Press (4x8), Hanging Leg Raises (3x15).",
            6: "Day 1: Chest - Bench Press (4x8), Dumbbell Flys (3x12).\nDay 2: Back - Pull-ups (3x10), Deadlifts (4x6).\nDay 3: Legs - Squats (4x8), Calf Raises (3x15).\nDay 4: Arms - Hammer Curls (3x12), Triceps Dips (3x10).\nDay 5: Shoulders - Overhead Press (4x8), Face Pulls (3x12).\nDay 6: Core & Active Recovery - Planks (3x60s), Mobility Drills.",
            7: "Advanced structured split with progressive overload tracking, incorporating mobility and recovery work."
        },
        "Lose Weight": {
            1: "Full-body HIIT: Jump Squats (3x15), Burpees (3x12), Mountain Climbers (3x30s), Core Planks (3x45s). High-intensity to maximize fat burn.",
            3: "Day 1: HIIT + Strength - Kettlebell Swings (3x15), Sprint Intervals (4x30s).\nDay 2: Cardio + Core - Jump Rope (5 min), Hanging Leg Raises (3x12).\nDay 3: Full-body circuit - Deadlifts (3x8), Burpees (3x12), Side Lunges (3x10).",
            4: "Day 1: Strength + Cardio - Squats (4x8), Rowing Machine (10 min).\nDay 2: HIIT - Box Jumps (3x12), Kettlebell Swings (3x15).\nDay 3: Strength + Cardio - Deadlifts (4x6), Battle Ropes (3x30s).\nDay 4: Full-body HIIT - Burpees (3x12), Sprint Intervals (4x30s).",
            5: "Structured progressive routine with increased caloric burn and mobility drills."
        },
    }
    
    diet_plan = {
        "Build Muscle": "High protein (chicken, eggs, lean beef, fish). Carbs: Whole grains, sweet potatoes. Fats: Avocado, nuts. Eat every 3-4 hours for muscle gain.",
        "Lose Weight": "Calorie deficit: Lean proteins (chicken, tofu, fish), low carbs (brown rice, quinoa), healthy fats (olive oil, nuts). Avoid sugar and processed carbs.",
    }
    
    suggestions = "Stay consistent. Sleep well, track progress, and adjust intensity. Recovery & mobility work improves results."
    
    plan = (f"Your BMI: {bmi:.2f}\n"
            f"Your Estimated Body Fat Percentage: {body_fat:.2f}%\n\n"
            f"Workout Plan:\n{workout_plan[goal][workout_days]}\n\n"
            f"Diet Plan:\n{diet_plan[goal]}\n\n"
            f"Suggestions:\n{suggestions}")
    
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