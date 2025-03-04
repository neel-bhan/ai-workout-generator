import pygame
import sys
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

# ---------------------------
# Setup Pygame
# ---------------------------
pygame.init()
window = pygame.display.set_mode((1000, 800))
pygame.display.set_caption("Workout Generator")
font = pygame.font.SysFont(None, 24)


# ---------------------------
# Define a simple Button class with an optional 'code'
# ---------------------------
class Button:
    def __init__(self, text, pos, size=(150, 50), code=None):
        self.text = text
        self.code = code  # numeric code (from dataset encoding)
        self.rect = pygame.Rect(pos, size)
        self.base_color = (200, 200, 200)
        self.selected_color = (100, 200, 100)
        self.color = self.base_color
        self.selected = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surf = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def toggle(self):
        self.selected = not self.selected
        self.color = self.selected_color if self.selected else self.base_color


# ---------------------------
# Load and Preprocess the Dataset
# ---------------------------
DATASET_PATH = r'C:\Users\coolg\PycharmProjects\pythonProject5\gym_exercise_data.csv'
df = pd.read_csv(DATASET_PATH)

# Cleaning: fill missing descriptions/ratings, drop rows missing Equipment
df['Desc'] = df['Desc'].fillna("No description available")
df['RatingDesc'] = df['RatingDesc'].fillna("No rating provided")
df['Rating'] = df['Rating'].fillna(3.0)
df = df.dropna(subset=['Equipment'])

# Encode categorical columns: Type, BodyPart, Equipment, Level
categorical_cols = ['Type', 'BodyPart', 'Equipment', 'Level']
label_encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le

# ---------------------------
# Create Buttons from the Dataset's Unique Values
# ---------------------------
# Muscle Groups (BodyPart)
muscle_buttons = []
# Get the original muscle group names from the label encoder
muscle_groups = label_encoders['BodyPart'].classes_
# Position buttons in a column; adjust positions as needed.
for i, muscle in enumerate(muscle_groups):
    # Pass the numeric code (i) along with the name.
    x, y = 50, 50 + i * 60
    muscle_buttons.append(Button(muscle, (x, y), code=i))

# Equipment buttons
equipment_buttons = []
equipment_items = label_encoders['Equipment'].classes_
for i, equip in enumerate(equipment_items):
    x, y = 250, 50 + i * 60
    equipment_buttons.append(Button(equip, (x, y), code=i))

# Fitness Goal buttons (we define codes: 1=Strength, 2=Hypertrophy, 3=Endurance)
goal_buttons = [
    Button("Strength", (450, 50), code=1),
    Button("Hypertrophy", (450, 120), code=2),
    Button("Endurance", (450, 190), code=3)
]
selected_goal = None  # will store the numeric code for the selected goal

# Submit Button
submit_button = Button("Submit", (450, 500), size=(150, 50))

# Variable to hold recommendation results (list of dicts)
results = None


# ---------------------------
# Recommendation Logic Function
# ---------------------------
def get_recommendations(selected_bodyparts, selected_equipment, goal):
    """
    Given lists of selected muscle group codes, equipment codes, and the fitness goal,
    filter the dataset and return a list of recommended exercises.
    """
    # Define goal-specific parameters.
    goals = {
        1: {"name": "Strength", "rep_range": "1-5 reps", "ex_count": 2},
        2: {"name": "Hypertrophy", "rep_range": "6-12 reps", "ex_count": 3},
        3: {"name": "Endurance", "rep_range": "12+ reps", "ex_count": 2}
    }
    user_goal = goals.get(goal)
    recommendations = []

    for bp in selected_bodyparts:
        bp_name = label_encoders['BodyPart'].inverse_transform([bp])[0]
        # Filter dataset for current muscle group and for exercises with any of the selected equipment.
        filtered = df[(df['BodyPart'] == bp) & (df['Equipment'].isin(selected_equipment))]
        if not filtered.empty:
            n_rec = min(user_goal['ex_count'], len(filtered))
            # Use the exercise Rating as weights (adding a small value so even zero ratings have a chance)
            weights = filtered['Rating'] + 0.1
            probabilities = weights / weights.sum()
            selected_indices = np.random.choice(filtered.index, size=n_rec, replace=False, p=probabilities)
            rec_exercises = filtered.loc[selected_indices]

            for idx, row in rec_exercises.iterrows():
                recommendations.append({
                    'bodypart': bp_name,
                    'title': row['Title'],
                    'desc': row['Desc'],
                    'rating': row['Rating'],
                    'rep_range': user_goal['rep_range']
                })
    return recommendations


# ---------------------------
# Function to Draw Recommendation Results
# ---------------------------
def draw_results(surface, recommendations):
    y_offset = 50
    header = font.render("Recommended Exercises:", True, (0, 0, 0))
    surface.blit(header, (50, y_offset))
    y_offset += 40
    for rec in recommendations:
        text = f"{rec['bodypart']}: {rec['title']} - {rec['rep_range']} (Rating: {rec['rating']:.1f})"
        text_surf = font.render(text, True, (0, 0, 0))
        surface.blit(text_surf, (50, y_offset))
        y_offset += 40


# ---------------------------
# Main Pygame Loop
# ---------------------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            # Check muscle group buttons
            for btn in muscle_buttons:
                if btn.is_clicked(pos):
                    btn.toggle()
            # Check equipment buttons
            for btn in equipment_buttons:
                if btn.is_clicked(pos):
                    btn.toggle()
            # Check goal buttons (only one selected at a time)
            for btn in goal_buttons:
                if btn.is_clicked(pos):
                    selected_goal = btn.code  # store numeric code for the goal
                    # Reset all goal buttons first
                    for b in goal_buttons:
                        b.selected = False
                        b.color = b.base_color
                    btn.selected = True
                    btn.color = btn.selected_color
            # Check submit button
            if submit_button.is_clicked(pos):
                # Gather selected muscle groups and equipment (using the stored numeric codes)
                selected_muscles = [btn.code for btn in muscle_buttons if btn.selected]
                selected_equips = [btn.code for btn in equipment_buttons if btn.selected]
                if not selected_muscles or not selected_equips or not selected_goal:
                    print("Please select at least one muscle group, equipment, and a goal.")
                else:
                    results = get_recommendations(selected_muscles, selected_equips, selected_goal)
                    # For debugging, also print to console.
                    print("Recommendations:")
                    for rec in results:
                        print(rec)

    # Clear the screen
    window.fill((255, 255, 255))

    # Draw UI if no results yet; else, show results.
    if results is None:
        # Draw muscle group buttons
        for btn in muscle_buttons:
            btn.draw(window)
        # Draw equipment buttons
        for btn in equipment_buttons:
            btn.draw(window)
        # Draw goal buttons
        for btn in goal_buttons:
            btn.draw(window)
        # Draw the submit button
        submit_button.draw(window)
    else:
        # If recommendations exist, display them on the screen.
        draw_results(window, results)

    pygame.display.flip()
