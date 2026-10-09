#Tasai Smith-Gandy

import re

import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="Customer Service Chatbot",
    page_icon="📦",
)

st.title("📦 Customer Service Chatbot")
st.write("Your AI-powered customer support assistant.")

# Fictional order database
ORDERS = {
    "ORD1001": {
        "status": "Shipped",
        "delivery": "October 12, 2026",
    },
    "ORD1002": {
        "status": "Processing",
        "delivery": "October 15, 2026",
    },
    "ORD1003": {
        "status": "Delivered",
        "delivery": "October 7, 2026",
    },
}

# Fictional store policies
POLICIES = """
Shipping: Delivery estimates depend on order status.
Returns: Return requests may be submitted within 30 days
of delivery. A human agent must confirm eligibility.
Refunds: Never promise a refund before a human confirms it.
Privacy: Never request passwords or full payment card details.
"""

# Four supported intents
INTENTS = {
    "order_status": [
        "order status", "check order", "track my order",
        "where is my order", "order number", "my order",
    ],
    "shipping": [
        "shipping", "delivery", "tracking", "package",
        "shipped", "arrive", "late", "hasn't arrived",
        "has not arrived", "not arrived", "missing package",
    ],
    "returns_refunds": [
        "return", "refund", "money back", "exchange",
    ],
    "general_support": [
        "help", "problem", "issue", "question",
        "support", "hello", "hi",
    ],
}


def detect_intent(message):
    """Identify a supported intent using keyword rules."""
    text = message.lower()

    for intent in (
        "returns_refunds",
        "order_status",
        "shipping",
        "general_support",
    ):
        if any(term in text for term in INTENTS[intent]):
            return intent

    return None


def find_order_number(message):
    """Extract an order number such as ORD1001."""
    match = re.search(r"\bORD\d+\b", message.upper())
    return match.group(0) if match else None


def lookup_order(order_number):
    """Retrieve an order from the sample database."""
    if not order_number:
        return None
    return ORDERS.get(order_number)


def get_ai_response(client, messages, intent, order_context):
    """Generate a response using the Groq language model."""
    system_prompt = f"""
You are a polite customer service chatbot for a fictional store.

Supported intents:
- Order status
- Shipping
- Returns and refunds
- General support

Detected issue type: {intent}

Store policies:
{POLICIES}

Verified order information:
{order_context}

Rules:
- Respond naturally and helpfully.
- Never invent order statuses or delivery dates.
- Never promise that a refund has been approved.
- A human agent must confirm refund eligibility.
- Never request passwords or full payment card details.
- Disclose that you are AI software when relevant.
- Never claim to submit a return or contact a human.
  The application does not perform those actions.
- If order information is unavailable, ask for the order number.
"""

    conversation = [
        {"role": "system", "content": system_prompt}
    ]
    conversation.extend(messages[-10:])

    result = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=conversation,
        temperature=0.3,
        max_tokens=350,
    )

    return result.choices[0].message.content


# Initialize conversation state before using it anywhere.
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi! I'm your AI customer support assistant. "
                "I'm AI software, and I can help with orders, "
                "shipping, returns, and general questions. "
                "How can I help?"
            ),
        }
    ]

# Two explicit slots collected during conversation.
if "slots" not in st.session_state:
    st.session_state.slots = {
        "order_number": None,
        "issue_type": None,
    }

if "awaiting_slot" not in st.session_state:
    st.session_state.awaiting_slot = None

# Always define this variable before the interface uses it.
slots = st.session_state.slots


# Display existing conversation messages.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Handle a new customer message.
if prompt := st.chat_input("Type your question here..."):
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    slots = st.session_state.slots
    awaiting = st.session_state.awaiting_slot
    response = None

    # Slot 1: collect the issue type if requested.
    if awaiting == "issue_type":
        selected_intent = detect_intent(prompt)

        if selected_intent:
            slots["issue_type"] = selected_intent
            st.session_state.awaiting_slot = None
        else:
            response = (
                "What type of issue are you having? "
                "Please choose order status, shipping or delivery, "
                "returns or refunds, or general support."
            )

    # Slot 2: collect the order number if requested.
    elif awaiting == "order_number":
        number = find_order_number(prompt)

        if number:
            slots["order_number"] = number
            st.session_state.awaiting_slot = None
        else:
            response = (
                "I couldn't recognize that order number. "
                "Please enter a number like ORD1001."
            )

    else:
        # Extract entities from the current message.
        number = find_order_number(prompt)

        if number:
            slots["order_number"] = number

        intent = detect_intent(prompt)

        if intent:
            slots["issue_type"] = intent

    # Ask for the first missing required entity.
    if response is None and not slots["issue_type"]:
        st.session_state.awaiting_slot = "issue_type"
        response = (
            "I can help! What type of issue are you having: "
            "order status, shipping or delivery, "
            "returns or refunds, or general support?"
        )

    # Order status and shipping require an order number.
    if (
        response is None
        and slots["issue_type"] in ("order_status", "shipping")
        and not slots["order_number"]
    ):
        st.session_state.awaiting_slot = "order_number"
        response = (
            "Could you please provide your order number? "
            "For example, ORD1001."
        )

    # Answer once the required slots have been collected.
    if response is None:
        intent = slots["issue_type"]
        order_number = slots["order_number"]
        order = lookup_order(order_number)

        order_context = (
            "No verified order information is available."
        )

        if order_number:
            if order:
                order_context = (
                    f"Order {order_number}: "
                    f"status={order['status']}; "
                    f"estimated delivery={order['delivery']}."
                )
            else:
                order_context = (
                    f"Order {order_number} was not found in the "
                    "sample database. Do not claim it exists."
                )

        # Use deterministic Python for verified order information.
        if intent in ("order_status", "shipping"):
            if order:
                response = (
                    f"Order {order_number} was found! "
                    f"Status: {order['status']}. "
                    f"Estimated delivery: {order['delivery']}."
                )
            elif order_number:
                response = (
                    f"I couldn't find order {order_number} "
                    "in our sample database. Please check it."
                )
            else:
                response = (
                    "Please provide your order number so I can "
                    "look up your order."
                )

        else:
            # AI responses with graceful API failure handling.
            try:
                api_key = st.secrets["GROQ_API_KEY"]
                client = Groq(api_key=api_key)

                with st.spinner("Preparing your response..."):
                    response = get_ai_response(
                        client,
                        st.session_state.messages,
                        intent,
                        order_context,
                    )

            except Exception as error:
                response = (
                    "I'm sorry, the AI service is temporarily "
                    "unavailable. Please try again shortly. "
                    "Order lookup is still available. For refund "
                    "decisions, please contact a human agent."
                )
                print(
                    f"Groq API error: "
                    f"{type(error).__name__}: {error}"
                )

    # Save and display the response.
    with st.chat_message("assistant"):
        st.write(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

    # Refresh the local reference to the saved slots.
    slots = st.session_state.slots


st.divider()
st.caption(
    "Student capstone demonstration. "
    "All order records and policies are fictional. "
    "This chatbot uses AI software."
)

# Show slots for testing and demonstration.
with st.expander("Collected information (testing)"):
    slots = st.session_state.slots
    st.write(
        "Issue type:",
        slots["issue_type"] or "Not collected",
    )
    st.write(
        "Order number:",
        slots["order_number"] or "Not collected",
    )
