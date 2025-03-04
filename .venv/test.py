import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score


def recommend_exercises(df, label_encoders):
    """
    Prompts the user to input targeted muscle groups (BodyParts) and available equipment,
    then asks for their fitness goal. Based on the selections, it filters the exercises
    and outputs 2 or 3 recommended variations per muscle group. Exercises with higher ratings
    have a higher chance of being selected.
    """
    # Display available BodyPart options
    print("\nAvailable BodyParts:")
    bodypart_mapping = {i: label_encoders['BodyPart'].inverse_transform([i])[0]
                        for i in range(len(label_encoders['BodyPart'].classes_))}
    for code, name in bodypart_mapping.items():
        print(f"  {code}: {name}")

    # Display available Equipment options
    print("\nAvailable Equipment:")
    equipment_mapping = {i: label_encoders['Equipment'].inverse_transform([i])[0]
                         for i in range(len(label_encoders['Equipment'].classes_))}
    for code, name in equipment_mapping.items():
        print(f"  {code}: {name}")

    # Get user input for multiple body parts and equipment (comma-separated)
    try:
        bodyparts_input = input("\nEnter the codes for your targeted BodyParts (comma-separated): ")
        user_bodyparts = [int(code.strip()) for code in bodyparts_input.split(",") if code.strip().isdigit()]

        equipment_input = input("Enter the codes for the Equipment you have available (comma-separated): ")
        user_equipment = [int(code.strip()) for code in equipment_input.split(",") if code.strip().isdigit()]
    except ValueError:
        print("Invalid input. Please enter valid integer codes separated by commas.")
        return

    # Get user's fitness goal
    try:
        goal_input = int(input("\nEnter your fitness goal (1: Strength, 2: Hypertrophy, 3: Endurance): "))
    except ValueError:
        print("Invalid input. Please enter a valid integer code for your goal.")
        return

    # Define goals with rep ranges and recommended number of exercises per muscle group
    goals = {
        1: {"name": "Strength", "rep_range": "1-5 reps", "ex_count": 2},
        2: {"name": "Hypertrophy", "rep_range": "6-12 reps", "ex_count": 3},
        3: {"name": "Endurance", "rep_range": "12+ reps", "ex_count": 2}
    }

    if goal_input not in goals:
        print("Invalid goal selection.")
        return

    user_goal = goals[goal_input]
    print(f"\nYour selected fitness goal is: {user_goal['name']}")
    print(f"Recommended rep range: {user_goal['rep_range']}")

    # For each targeted BodyPart, recommend exercises
    for bp in user_bodyparts:
        bp_name = label_encoders['BodyPart'].inverse_transform([bp])[0]
        # Filter dataset based on current BodyPart and available Equipment
        filtered = df[(df['BodyPart'] == bp) & (df['Equipment'].isin(user_equipment))]

        if filtered.empty:
            print(f"\nNo exercises found for {bp_name} with the available equipment.")
        else:
            n_rec = min(user_goal['ex_count'], len(filtered))
            weights = filtered['Rating'] + 0.1  # Small epsilon so even zero-rated exercises have a chance
            probabilities = weights / weights.sum()
            selected_indices = np.random.choice(filtered.index, size=n_rec, replace=False, p=probabilities)
            recommended = filtered.loc[selected_indices]

            print(f"\nRecommended exercises for {bp_name}:")
            for idx, row in recommended.iterrows():
                print(f"\nTitle: {row['Title']}")
                print(f"Description: {row['Desc']}")
                print(f"Rating: {row['Rating']:.1f}")
                print(f"Suggested rep range for {user_goal['name']}: {user_goal['rep_range']}")


def main():
    # Load the dataset using the absolute path
    dataset_path = r'C:\Users\coolg\PycharmProjects\pythonProject5\gym_exercise_data.csv'
    df = pd.read_csv(dataset_path)

    # Data Cleaning
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

    # Preview the cleaned & encoded dataset (first 5 rows)
    print("Cleaned & Encoded Dataset Preview:")
    print(df.head())

    # (Optional) Build a Decision Tree model (predicting 'Level') for demonstration purposes
    X = df[['Type', 'BodyPart', 'Equipment']]
    y = df['Level']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = DecisionTreeClassifier(random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nDecision Tree accuracy: {accuracy:.2f}")

    # Call the updated recommendation function that integrates goals
    recommend_exercises(df, label_encoders)


if __name__ == "__main__":
    main()
