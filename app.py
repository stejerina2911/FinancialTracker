import streamlit as st
import pandas as pd
import os
import openai

# Load the API key from environment variable (set in GitHub Secrets)
openai.api_key = os.getenv("API_KEY")

# Set the page title
st.title("Personal Expense Tracker with 50/30/20 Rule")

# Define 50/30/20 categories
categories = ["Needs", "Wants", "Savings/Debt Repayment"]

# Function to get category from OpenAI using the latest API
def get_category(description):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": (
                    "You are an assistant that categorizes expenses into one of the following categories: "
                    "Needs, Wants, Savings/Debt Repayment. Only respond with the category name.\n\n"
                    "**Definitions:**\n"
                    "- **Needs**: Essential expenses required for basic living (e.g., rent, utilities, groceries, transportation for work).\n"
                    "- **Wants**: Non-essential expenses for enjoyment (e.g., dining out, entertainment, vacations, hobbies).\n"
                    "- **Savings/Debt Repayment**: Money set aside for savings, investments, or paying off debts."
                )},
                {"role": "user", "content": f"Description: {description}\n\nCategory:"}
            ]
        )
        # Extract the content from the response
        category = response.choices[0].message['content'].strip()
        if category not in categories:
            category = "Others"
        return category
    except Exception as e:
        st.error(f"Error with OpenAI API: {e}")
        return "Others"

# Sidebar for user input
st.sidebar.header("User Profile")
income = st.sidebar.number_input("Enter your monthly after-tax income", min_value=0.0, format="%.2f")

# Header for new expense entry
st.header("Add a New Expense")

# Create a form for expense input
with st.form("expense_form"):
    date = st.date_input("Date")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    description = st.text_input("Description (e.g., 'Dinner with friends')")
    submit = st.form_submit_button("Add Expense")

if submit:
    if description.strip() == "":
        st.warning("Please enter a description.")
    else:
        # Get the category from OpenAI
        category = get_category(description)
        st.write(f"Predicted Category: **{category}**")

        # Create a DataFrame for the new expense
        new_expense = pd.DataFrame({
            "Date": [date],
            "Amount": [amount],
            "Category": [category],
            "Description": [description]
        })

        # Check if the expenses.csv file exists
        if os.path.exists("expenses.csv"):
            expenses = pd.read_csv("expenses.csv")
            expenses = pd.concat([expenses, new_expense], ignore_index=True)
        else:
            expenses = new_expense

        # Save the updated expenses to the CSV file
        expenses.to_csv("expenses.csv", index=False)

        st.success("Expense added successfully!")

# Header for expense history
st.header("Expense History")

# Check if the expenses.csv file exists and display data
if os.path.exists("expenses.csv"):
    expenses = pd.read_csv("expenses.csv")

    # Convert 'Date' column to datetime format
    expenses['Date'] = pd.to_datetime(expenses['Date'])

    # Display the DataFrame
    st.dataframe(expenses.sort_values(by='Date', ascending=False))

    # Display total expenses
    total_expense = expenses['Amount'].sum()
    st.write(f"### Total Expenses: ${total_expense:.2f}")

    # Expenses by Category
    st.subheader("Expenses by Category")
    expenses_by_category = expenses.groupby('Category')['Amount'].sum()
    st.bar_chart(expenses_by_category)

    # 50/30/20 Rule Summary
    if income > 0:
        # Calculate spending in each category
        total_needs = expenses[expenses['Category'] == 'Needs']['Amount'].sum()
        total_wants = expenses[expenses['Category'] == 'Wants']['Amount'].sum()
        total_savings = expenses[expenses['Category'] == 'Savings/Debt Repayment']['Amount'].sum()

        # Calculate percentages
        percent_needs = (total_needs / income) * 100
        percent_wants = (total_wants / income) * 100
        percent_savings = (total_savings / income) * 100

        # Display the summary
        st.header("50/30/20 Rule Summary")
        st.write(f"**Needs:** {percent_needs:.2f}% of income (Recommended: 50%)")
        st.write(f"**Wants:** {percent_wants:.2f}% of income (Recommended: 30%)")
        st.write(f"**Savings/Debt Repayment:** {percent_savings:.2f}% of income (Recommended: 20%)")

        # Determine compliance
        compliance_needs = percent_needs <= 50
        compliance_wants = percent_wants <= 30
        compliance_savings = percent_savings >= 20

        # Display compliance messages
        st.subheader("Compliance with 50/30/20 Rule")
        st.write(f"**Needs:** {'✅ Within recommended percentage.' if compliance_needs else '❌ Exceeds recommended percentage.'}")
        st.write(f"**Wants:** {'✅ Within recommended percentage.' if compliance_wants else '❌ Exceeds recommended percentage.'}")
        st.write(f"**Savings/Debt Repayment:** {'✅ Meets or exceeds recommended percentage.' if compliance_savings else '❌ Below recommended percentage.'}")

        # Visual representation
        st.subheader("Spending Breakdown")
        breakdown = pd.DataFrame({
            'Category': ['Needs', 'Wants', 'Savings/Debt Repayment'],
            'Percentage': [percent_needs, percent_wants, percent_savings]
        })
        st.bar_chart(breakdown.set_index('Category'))
    else:
        st.info("Please enter your monthly after-tax income in the sidebar to see the 50/30/20 rule summary.")

    # Expenses Over Time
    st.subheader("Expenses Over Time")
    expenses_by_date = expenses.groupby('Date')['Amount'].sum()
    st.line_chart(expenses_by_date)
else:
    st.write("No expenses have been added yet.")

