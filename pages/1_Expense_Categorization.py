import streamlit as st
import torch
import re
from transformers import BertTokenizer, BertForSequenceClassification
import numpy as np
import pandas as pd
from datetime import datetime
import altair as alt

# Load the pre-trained BERT model and tokenizer
model_path = "./models/expense_categorization_bert"  # Replace with actual path if different
model = BertForSequenceClassification.from_pretrained(model_path)
tokenizer = BertTokenizer.from_pretrained(model_path)

categories = [
    "Automobile Maintenance",  # 0
    "Bills",                   # 1
    "Charitable Donations",    # 2
    "Childcare Expenses",      # 3
    "Clothing and Accessories",# 4
    "Dining",                  # 5
    "Education",               # 6
    "Electronics",             # 7
    "Entertainment",           # 8
    "Furniture",               # 9
    "Groceries",               # 10
    "Gym Memberships",         # 11
    "Health",                  # 12
    "Hobby Supplies",          # 13
    "Home Improvement",        # 14
    "Home Insurance",          # 15
    "Insurance",               # 16
    "Internet Services",       # 17
    "Investment",              # 18
    "Laundry Services",        # 19
    "Legal Fees",              # 20
    "Loan Payment",            # 21
    "Luxury Purchases",        # 22
    "Medical Insurance",       # 23
    "Mobile Services",         # 24
    "Mortgage Payments",       # 25
    "Office Supplies",         # 26
    "Personal Care",           # 27
    "Pet Expenses",            # 28
    "Professional Services",   # 29
    "Property Tax",            # 30
    "Rent",                    # 31
    "Repairs",                 # 32
    "Retirement Savings",      # 33
    "Savings Deposits",        # 34
    "School Supplies",         # 35
    "Security Services",       # 36
    "Shopping",                # 37
    "Special Occasions",       # 38
    "Sports Equipment",        # 39
    "Streaming Services",      # 40
    "Subscription Services",   # 41
    "Tax Payments",            # 42
    "Transportation",          # 43
    "Travel",                  # 44
    "Tuition Fees",            # 45
    "Utilities",               # 46
    "Vacation Expenses",       # 47
    "Vehicle Lease",           # 48
    "Wellness and Spa"         # 49
]

def clean_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', str(text))
    text = text.lower().strip()
    return text

def predict_expense_category(description):
    cleaned_desc = clean_text(description)
    inputs = tokenizer(cleaned_desc, return_tensors="pt", padding=True, truncation=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=1).numpy()[0]
    predicted_idx = np.argmax(probabilities)
    predicted_category = categories[predicted_idx]
    return predicted_category

st.markdown(
    """
    <style>
        .title { font-size: 36px; color: #4CAF50; font-weight: bold; }
        .section-title { font-size: 24px; color: #3f51b5; font-weight: bold; }
        .highlight { background-color: #ffeb3b; padding: 5px; border-radius: 4px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="title">Expense Categorization using BERT</div>', unsafe_allow_html=True)
st.write("This app uses a pre-trained BERT model to categorize expense descriptions into different categories.")

st.info("💡 Provide a brief description of your expense and the amount:")

col1, col2 = st.columns(2)
with col1:
    expense_input = st.text_area("Expense Description", height=150)
with col2:
    amount_input = st.number_input("Expense Amount", min_value=0.0, format="%.2f")
date_input = st.date_input("Expense Date", datetime.today())
expense_type = st.radio("Is this a Fixed or Variable Expense?", options=["Fixed", "Variable"])

if 'expense_data' not in st.session_state:
    st.session_state.expense_data = []

progress_bar = st.progress(0)

if st.button("🚀 Categorize Expense"):
    if expense_input.strip() and amount_input > 0:
        progress_bar.progress(50)
        category = predict_expense_category(expense_input)
        progress_bar.progress(100)
        st.session_state.expense_data.append([expense_input, f"${amount_input:.2f}", expense_type, category, date_input.strftime("%Y-%m-%d")])
        st.success(f"🎯 Predicted Category: {category}")
        st.write(f"💰 Expense Amount: ${amount_input:.2f}")

if st.session_state.expense_data:
    df = pd.DataFrame(st.session_state.expense_data, columns=["Description", "Amount", "Expense Type", "Predicted Category", "Date"])
    st.markdown('<div class="section-title">Expense Categorization Results:</div>', unsafe_allow_html=True)
    st.dataframe(df)

    st.markdown('<div class="section-title">Filter Expenses by Month</div>', unsafe_allow_html=True)
    df["Month"] = pd.to_datetime(df["Date"]).dt.strftime("%B")
    month_names = df["Month"].unique()
    month_selected = st.selectbox("Select a Month", ["All"] + list(month_names))

    filtered_df = df if month_selected == "All" else df[df["Month"] == month_selected]

    if not filtered_df.empty:
        st.write("📊 Filtered Expenses:")
        st.dataframe(filtered_df)
        
        # Calculate totals for variable and fixed expenses
        monthly_fixed = filtered_df[filtered_df["Expense Type"] == "Fixed"]["Amount"].str.replace("$", "").astype(float).sum()
        monthly_variable = filtered_df[filtered_df["Expense Type"] == "Variable"]["Amount"].str.replace("$", "").astype(float).sum()

        # Store the totals in session state
        st.session_state.monthly_fixed = monthly_fixed
        st.session_state.monthly_variable = monthly_variable

        st.markdown('<div class="section-title">Monthly Expense Summary</div>', unsafe_allow_html=True)
        st.write(f"🔒 **Total Fixed Expenses** for {month_selected}: ${monthly_fixed:.2f}")
        st.write(f"⚡ **Total Variable Expenses** for {month_selected}: ${monthly_variable:.2f}")
        
    else:
        st.warning("⚠️ No expenses for the selected month.")

    st.markdown('<div class="section-title">Monthly Expense Trends</div>', unsafe_allow_html=True)
    monthly_totals = df.groupby("Month")["Amount"].apply(lambda x: x.str.replace("$", "").astype(float).sum()).reset_index()
    chart = alt.Chart(monthly_totals).mark_line(point=True).encode(
        x="Month", y="Amount", tooltip=["Month", "Amount"]
    ).properties(width=700)
    st.altair_chart(chart, use_container_width=True)

    st.markdown('<div class="section-title">Expense Distribution by Category</div>', unsafe_allow_html=True)
    category_totals = df.groupby("Predicted Category")["Amount"].apply(lambda x: x.str.replace("$", "").astype(float).sum()).reset_index()
    pie_chart = alt.Chart(category_totals).mark_arc().encode(
        theta=alt.Theta(field="Amount", type="quantitative"),
        color=alt.Color(field="Predicted Category", type="nominal"),
        tooltip=["Predicted Category", "Amount"]
    )
    st.altair_chart(pie_chart, use_container_width=True)

    st.markdown('<div class="section-title">Average Amount Spent by Category</div>', unsafe_allow_html=True)
    category = st.selectbox("Select Category", ["All"] + list(df["Predicted Category"].unique()))
    month_for_category = st.selectbox("Select Month for Category", ["All"] + list(month_names))

    if month_for_category == "All":
        category_filtered_df = df if category == "All" else df[df["Predicted Category"] == category]
    else:
        category_filtered_df = df[
            (df["Predicted Category"] == category) & (df["Month"] == month_for_category)
        ] if category != "All" else df[df["Month"] == month_for_category]

    avg_spending = category_filtered_df["Amount"].str.replace("$", "").astype(float).mean() if not category_filtered_df.empty else 0
    st.write(f"📈 Average spending for {category if category != 'All' else 'all categories'} in {month_for_category if month_for_category != 'All' else 'all months'}: ${avg_spending:.2f}")
else:
    st.warning("⚠️ No expense data available yet.")