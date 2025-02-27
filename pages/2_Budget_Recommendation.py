import streamlit as st
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import altair as alt

with open("./models/q_table (2).pkl", "rb") as f:
    q_table = pickle.load(f)
with open("./models/scaler (1).pkl", "rb") as f:
    scaler = pickle.load(f)
with open("./models/label_encoder (1).pkl", "rb") as f:
    label_encoder = pickle.load(f)
with open("./models/training_states (1).pkl", "rb") as f:
    training_states = pickle.load(f)

def predict_budget_recommendation(income, fixed_expenses, variable_expenses, savings_goal):
    scaled_input = scaler.transform([[income, fixed_expenses, variable_expenses, savings_goal]])
    state_index = np.argmin(np.sum(np.abs(training_states - scaled_input), axis=1))
    action = np.argmax(q_table[state_index])
    return label_encoder.inverse_transform([action])[0]

st.markdown("""
    <style>
        .title { font-size: 36px; color: #2196F3; font-weight: bold; }
        .section-title { font-size: 24px; color: #FF5722; font-weight: bold; }
        .highlight { background-color: #F0F4C3; padding: 5px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">💰 Smart Budget Recommendation System</div>', unsafe_allow_html=True)
st.write("This app uses a trained Q-learning model to provide tailored budget plans based on your financial details.")
st.info("💡 Enter your income, expenses, and savings goal to receive recommendations.")

col1, col2 = st.columns(2)
with col1:
    income = st.number_input("Monthly Income:", min_value=1000, max_value=1000000, value=50000, step=500)
    savings_goal = st.number_input("Savings Goal:", min_value=0, max_value=1000000, value=15000, step=500)
with col2:
    if 'monthly_fixed' in st.session_state and 'monthly_variable' in st.session_state:
        fixed_expenses = st.number_input("Fixed Expenses:", min_value=0, value=int(st.session_state.monthly_fixed))
        variable_expenses = st.number_input("Variable Expenses:", min_value=0, value=int(st.session_state.monthly_variable))
    else:
        fixed_expenses = st.number_input("Fixed Expenses:", min_value=0, value=15000)
        variable_expenses = st.number_input("Variable Expenses:", min_value=0, value=10000)

progress_bar = st.progress(0)
if st.button("🚀 Get Budget Recommendation"):
    progress_bar.progress(50)
    recommendation = predict_budget_recommendation(income, fixed_expenses, variable_expenses, savings_goal)
    progress_bar.progress(100)
    st.success(f"💡 Recommended Budget Plan: **{recommendation}**")
    data = pd.DataFrame({
        'Category': ["Fixed Expenses", "Variable Expenses", "Savings"],
        'Amount': [fixed_expenses, variable_expenses, income - (fixed_expenses + variable_expenses)]
    })
    chart = alt.Chart(data).mark_arc(innerRadius=50).encode(
        theta='Amount',
        color='Category',
        tooltip=['Category', 'Amount']
    ).properties(title="Income Distribution")
    st.altair_chart(chart, use_container_width=True)