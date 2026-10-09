# Customer Service Chatbot

## Overview

This project is an AI-powered customer service chatbot developed for my CSC-128 capstone project. It helps customers with order status, shipping questions, returns and refunds, and general support.

The chatbot combines Python-based logic for reliable order lookups with a Groq-hosted language model to generate natural, helpful responses.

**Note:** This is a student demonstration project. All order information and store policies are fictional.

## Features

- **Order lookup:** Looks up sample orders and returns their status and estimated delivery date.
- **Shipping assistance:** Answers customer questions about shipping and delayed packages.
- **Returns and refunds:** Explains the store's return policy and clarifies that refund eligibility must be reviewed by a human.
- **General support:** Responds to common customer questions using AI.
- **Conversation history:** Maintains messages during the current Streamlit session so follow-up questions can use previous context.
- **Privacy safeguards:** Instructs the chatbot not to request passwords or full payment card details.
- **Error handling:** Displays a friendly message when the AI service is unavailable.
- **AI disclosure:** Informs users that the chatbot uses AI software.

## Technologies Used

- Python
- Streamlit
- Groq Python SDK
- Groq-hosted language model

## Sample Orders

| Order Number | Status | Estimated Delivery |
|---|---|---|
| ORD1001 | Shipped | October 12, 2026 |
| ORD1002 | Processing | October 15, 2026 |
| ORD1003 | Delivered | October 7, 2026 |

These are fictional records used for demonstration purposes.

## Requirements

- Python 3.11 or a compatible Python version
- pip
- A Groq API key

## How to Run Locally

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd csc128-capstone
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with the URL of your GitHub repository.

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure your API key

Create the Streamlit configuration directory and secrets file:

```bash
mkdir -p .streamlit
nano .streamlit/secrets.toml
```

Add your own Groq API key:

```toml
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
```

Replace the placeholder with your actual key. Keep this file private and never commit it to GitHub.

### 5. Start the chatbot

```bash
python -m streamlit run app.py
```

Open the local URL displayed in your terminal, usually `http://localhost:8501`.

## Example Questions

- Can you check order ORD1001?
- My package hasn't arrived. What can I do?
- I want a refund. Can you guarantee I'll get my money back?
- When will my order arrive?

## Limitations

- Order records are fictional and stored locally in the application code.
- The chatbot does not connect to a real order-management system.
- It cannot actually submit return requests, issue refunds, or contact a human agent.
- AI-generated answers may require verification.
- Order lookup remains dependent on the sample database.

## Security

The Groq API key must be stored in Streamlit secrets or another secure environment variable. The `.streamlit/secrets.toml` file must not be committed to the public repository.

## Author

Created as a CSC-128 capstone project.
