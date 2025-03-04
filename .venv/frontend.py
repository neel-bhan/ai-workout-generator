import pygame
import sys
import numpy as np
from backend import load_and_prepare_data, get_recommendations

# Initialize Pygame.
pygame.init()
window = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("Workout Generator")
font = pygame.font.SysFont(None, 32)


# ---------------------------
# Simple Button class.
# ---------------------------
class Button:
    def __init__(self, text, pos, size=(150, 50), code=None):
        self.text = text
        self.code = code  # Numeric code (from dataset encoding or goal ID).
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
# Load dataset and label encoders from backend.
# ---------------------------
df, label_encoders = load_and_prepare_data()

# ---------------------------
# Screen 0: Goal Selection.
# ---------------------------
goal_buttons = [
    Button("Strength", (300, 200), size=(200, 70), code=1),
    Button("Hypertrophy", (300, 300), size=(200, 70), code=2),
    Button("Endurance", (300, 400), size=(200, 70), code=3)
]
selected_goal = None  # Will store the numeric goal code.

# ---------------------------
# Screen 1: Equipment Selection.
# ---------------------------
equipment_items = label_encoders['Equipment'].classes_
equipment_buttons = []
# Arrange equipment buttons in two columns.
col_count = 2
margin_x = 100
margin_y = 150
gap_x = 250
gap_y = 80
for i, equip in enumerate(equipment_items):
    col = i % col_count
    row = i // col_count
    x = margin_x + col * gap_x
    y = margin_y + row * gap_y
    equipment_buttons.append(Button(equip, (x, y), size=(200, 50), code=i))

# ---------------------------
# Screen 2: Muscle Group Selection.
# ---------------------------
muscle_groups = label_encoders['BodyPart'].classes_
muscle_buttons = []
# Arrange muscle group buttons in three columns.
col_count_muscles = 3
margin_x_muscles = 100
margin_y_muscles = 150
gap_x_muscles = 300
gap_y_muscles = 80
for i, muscle in enumerate(muscle_groups):
    col = i % col_count_muscles
    row = i // col_count_muscles
    x = margin_x_muscles + col * gap_x_muscles
    y = margin_y_muscles + row * gap_y_muscles
    muscle_buttons.append(Button(muscle, (x, y), size=(250, 50), code=i))

# ---------------------------
# Navigation Buttons: Next and Back.
# ---------------------------
next_button = Button("Next", (950, 700), size=(150, 50))
back_button = Button("Back", (50, 700), size=(150, 50))

# ---------------------------
# Application state.
# ---------------------------
# current_screen:
#  0: Goal selection
#  1: Equipment selection
#  2: Muscle group selection
#  3: Display recommendations
current_screen = 0
results = None


def draw_title(surface, title):
    title_surf = font.render(title, True, (0, 0, 0))
    title_rect = title_surf.get_rect(center=(600, 50))
    surface.blit(title_surf, title_rect)


def draw_results(surface, recommendations):
    y_offset = 100
    header = font.render("Recommended Exercises:", True, (0, 0, 0))
    surface.blit(header, (50, 80))
    for rec in recommendations:
        text = f"{rec['bodypart']}: {rec['title']} - {rec['rep_range']} (Rating: {rec['rating']:.1f})"
        text_surf = font.render(text, True, (0, 0, 0))
        surface.blit(text_surf, (50, y_offset))
        y_offset += 40


# ---------------------------
# Main Pygame Loop.
# ---------------------------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if current_screen == 0:
                # Goal selection screen.
                for btn in goal_buttons:
                    if btn.is_clicked(pos):
                        selected_goal = btn.code
                        # Reset selection on all goal buttons.
                        for b in goal_buttons:
                            b.selected = False
                            b.color = b.base_color
                        btn.selected = True
                        btn.color = btn.selected_color
                if next_button.is_clicked(pos):
                    if selected_goal is None:
                        print("Please select a fitness goal.")
                    else:
                        current_screen = 1
            elif current_screen == 1:
                # Equipment selection screen.
                for btn in equipment_buttons:
                    if btn.is_clicked(pos):
                        btn.toggle()
                if next_button.is_clicked(pos):
                    if not any(btn.selected for btn in equipment_buttons):
                        print("Please select at least one equipment.")
                    else:
                        current_screen = 2
                if back_button.is_clicked(pos):
                    current_screen = 0
            elif current_screen == 2:
                # Muscle group selection screen.
                for btn in muscle_buttons:
                    if btn.is_clicked(pos):
                        btn.toggle()
                if next_button.is_clicked(pos):
                    if not any(btn.selected for btn in muscle_buttons):
                        print("Please select at least one muscle group.")
                    else:
                        # Gather selections and get recommendations.
                        selected_muscles = [btn.code for btn in muscle_buttons if btn.selected]
                        selected_equips = [btn.code for btn in equipment_buttons if btn.selected]
                        results = get_recommendations(df, label_encoders, selected_muscles, selected_equips,
                                                      selected_goal)
                        current_screen = 3
                if back_button.is_clicked(pos):
                    current_screen = 1
            elif current_screen == 3:
                # Results screen: allow going back to muscle selection.
                if back_button.is_clicked(pos):
                    current_screen = 2

    # Draw current screen.
    window.fill((255, 255, 255))
    if current_screen == 0:
        draw_title(window, "Select Your Fitness Goal")
        for btn in goal_buttons:
            btn.draw(window)
        next_button.draw(window)
    elif current_screen == 1:
        draw_title(window, "Select Available Equipment")
        for btn in equipment_buttons:
            btn.draw(window)
        next_button.draw(window)
        back_button.draw(window)
    elif current_screen == 2:
        draw_title(window, "Select Targeted Muscle Groups")
        for btn in muscle_buttons:
            btn.draw(window)
        next_button.draw(window)
        back_button.draw(window)
    elif current_screen == 3:
        draw_title(window, "Your Workout Recommendations")
        if results:
            draw_results(window, results)
        back_button.draw(window)

    pygame.display.flip()
