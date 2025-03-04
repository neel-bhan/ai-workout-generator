import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

# Path to your CSV dataset.
DATASET_PATH = r'C:\Users\coolg\PycharmProjects\pythonProject5\gym_exercise_data.csv'


def load_and_prepare_data():
    """
    Load the dataset, clean it, and encode the categorical columns.
    Returns the DataFrame and a dictionary of label encoders.
    """
    df = pd.read_csv(DATASET_PATH)

    # Data Cleaning:
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

    return df, label_encoders


def get_recommendations(df, label_encoders, selected_bodyparts, selected_equipment, goal):
    """
    Given the selected muscle group codes, equipment codes, and fitness goal,
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
        # Convert numeric code back to muscle name.
        bp_name = label_encoders['BodyPart'].inverse_transform([bp])[0]
        # Filter dataset: exercises for the current muscle group and matching selected equipment.
        filtered = df[(df['BodyPart'] == bp) & (df['Equipment'].isin(selected_equipment))]
        if not filtered.empty:
            n_rec = min(user_goal['ex_count'], len(filtered))
            # Use ratings (plus a small epsilon) as weights.
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
