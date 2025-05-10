# ui_app.py

import streamlit as st
import os
from database import authenticate_user, add_user, get_user
from user_profile import get_user_profile, update_user_profile
from email_validator import validate_email
from rag_engine import get_response

def show_login():
    st.title("💪 Welcome to FitBot: Your Fitness Coach")
    
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        user_data = authenticate_user(email, password)
        if user_data:
            st.session_state["user_email"] = email
            st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")
    
    if st.button("Don't have an account? Create one"):
        create_account()

def create_account():
    st.title("Create Account")
    
    email = st.text_input("Email", key="signup_email")
    name = st.text_input("Name", key="signup_name")
    password = st.text_input("Password", type="password", key="signup_password")
    
    if st.button("Create Account"):
        if not validate_email(email):
            st.error("Please enter a valid email address.")
            return

        existing_user = get_user(email)
        if existing_user:
            st.error("Email already registered. Please log in.")
        else:
            add_user(email, name, password)
            st.success("Account created successfully! Redirecting to home page...")
            st.session_state["user_email"] = email
            st.rerun()

def show_profile_setup():
    email = st.session_state["user_email"]
    profile = get_user_profile(email)
    
    if profile is None:
        st.warning("Please complete your profile setup!")
        gender_value = st.selectbox("Gender", ["Male", "Female", "Other"], key="edit_gender")
        age = st.number_input("Age", min_value=10, max_value=100, value=18)
        weight = st.number_input("Weight (kg)", min_value=0, value=60.0)
        height = st.number_input("Height (cm)", min_value=0, value=170)
        goal = st.selectbox("Fitness Goal", ["Weight Loss", "Muscle Gain", "General Fitness"])
        experience = st.selectbox("Experience Level", ["Beginner", "Intermediate", "Advanced"])
        diet = st.selectbox("Diet Preference", ["Vegetarian", "Non-Vegetarian", "Vegan"])
        
        if st.button("Save Profile"):
            update_user_profile(email, age, gender_value, weight, height, goal, experience, diet)
            st.success("Profile updated successfully!")
            st.rerun()
    
    else:
        st.write(f"Welcome back, {profile['name']}!")
        
        st.text_input("Name", profile['name'], key="edit_name")
        st.number_input("Age", value=profile['age'], key="edit_age")
        
        gender_value = profile['gender'] if profile['gender'] in ["Male", "Female", "Other"] else "Male"
        st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(gender_value), key="edit_gender")
        
        st.number_input("Weight (kg)", value=profile['weight'], key="edit_weight")
        st.number_input("Height (cm)", value=profile['height'], key="edit_height")
        
        goal_value = profile['goal'] if profile['goal'] in ["Weight Loss", "Muscle Gain", "General Fitness"] else "Weight Loss"
        experience_value = profile['experience'] if profile['experience'] in ["Beginner", "Intermediate", "Advanced"] else "Beginner"
        diet_value = profile['diet'] if profile['diet'] in ["Vegetarian", "Non-Vegetarian", "Vegan"] else "Vegetarian"
        
        st.selectbox("Goal", ["Weight Loss", "Muscle Gain", "General Fitness"], index=["Weight Loss", "Muscle Gain", "General Fitness"].index(goal_value), key="edit_goal")
        st.selectbox("Experience Level", ["Beginner", "Intermediate", "Advanced"], index=["Beginner", "Intermediate", "Advanced"].index(experience_value), key="edit_experience")
        st.selectbox("Diet", ["Vegetarian", "Non-Vegetarian", "Vegan"], index=["Vegetarian", "Non-Vegetarian", "Vegan"].index(diet_value), key="edit_diet")
        
        if st.button("Save Changes"):
            updated_data = {
                'name': st.session_state["edit_name"],
                'age': st.session_state["edit_age"],
                'gender': st.session_state["edit_gender"],
                'weight': st.session_state["edit_weight"],
                'height': st.session_state["edit_height"],
                'goal': st.session_state["edit_goal"],
                'experience': st.session_state["edit_experience"],
                'diet': st.session_state["edit_diet"],
            }
            update_user_profile(email, **updated_data)
            st.success("Profile updated successfully!")
            st.rerun()

        query = st.text_input("Ask your fitness-related question:")
        if query:
            response = get_response(query, profile)
            st.write(response)

if __name__ == "__main__":
    if "user_email" not in st.session_state or not st.session_state["user_email"]:
        show_login()
    else:
        show_profile_setup()
