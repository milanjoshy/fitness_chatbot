from user_profile import get_user_profile, update_user_profile
from rag_engine import get_response
from database import connect_db, authenticate_user, update_profile, add_user, verify_email

# Call the function to connect to the database and create the table if necessary
connect_db()

def get_user_input():
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    user = authenticate_user(email, password)
    if user:
        print(f"Welcome back, {user[1]}!")
        if user[4] == 0:
            print("Please verify your email address to proceed.")
            code = input("Enter the verification code sent to your email: ")
            if verify_email(email, code):
                print("Email verified successfully!")
            else:
                print("Invalid verification code.")
        return email, user
    else:
        print("User not found or invalid password!")
        return None, None

def update_user_details(email):
    print("\nLet's set up or update your profile!")
    age = int(input("Age: "))
    gender = input("Gender (male/female/other): ")
    weight = float(input("Weight: "))
    height = float(input("Height: "))
    goal = input("Fitness goal (weight loss, muscle gain, general fitness): ")
    experience = input("Experience level (beginner/intermediate/advanced): ")
    diet = input("Diet preference (vegetarian/non-vegetarian/vegan): ")

    update_profile(email, age, gender, weight, height, goal, experience, diet)
    print("Profile updated successfully!")

if __name__ == "__main__":
    print("💪 Welcome to FitBot: Your Fitness Coach")

    # Ask the user to log in
    email, user = get_user_input()

    if email:
        # User is authenticated, now fetch and update their profile
        profile = get_user_profile(email)
        if not profile:
            # If profile is empty, guide the user to enter their details
            update_user_details(email)

        while True:
            query = input("\nAsk something (or type 'exit' to quit): ")
            if query.lower() == 'exit':
                print("Goodbye! Stay fit 💚")
                break

            # Get response from the RAG engine based on the query
            response = get_response(query, profile)
            print("\nFitBot:", response)
