from database import get_user, update_profile

def get_user_profile(email):
    user = get_user(email)
    if user:
        return {
            "name": user[1],
            "email": user[2],
            "age": user[4],
            "gender": user[5],
            "weight": user[6],
            "height": user[7],
            "goal": user[8],
            "experience": user[9],
            "diet": user[10]
        }
    return None

def update_user_profile(email, age, gender, weight, height, goal, experience, diet):
    update_profile(email, age, gender, weight, height, goal, experience, diet)
