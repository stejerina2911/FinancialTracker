import streamlit as st
import pandas as pd
import os
import openai  # Import the OpenAI library

# Set the page title
st.title("Personal Expense Tracker")

# Define expense categories
categories = ["Grocery", "Education", "Car Expenses", "Utilities", "Entertainment", "Dining", "Others"]

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure the API key is set as an environment variable

# Function to get category from OpenAI using gpt-3.5-turbo
def get_category(description):
    messages = [
        {
            "role": "system",
            "content": (
                f"You are an assistant that categorizes expenses into one of the following categories: "
                f"{', '.join(categories)}. Only respond with the category name."
            )
        },
        {"role": "user", "content": f"Description: {description}\n\nCategory:"}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=5,
            temperature=0
        )
        category = response['choices'][0]['message']['content'].strip()
        if category not in categories:
            category = "Others"
        return category
    except Exception as e:
        st.error(f"Error with OpenAI API: {e}")
        return "Others"

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

    # Expenses Over Time
    st.subheader("Expenses Over Time")
    expenses_by_date = expenses.groupby('Date')['Amount'].sum()
    st.line_chart(expenses_by_date)
else:
    st.write("No expenses have been added yet.")
