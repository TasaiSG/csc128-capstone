#Tasai Smith-Gandy

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
        "order", "track my order", "where is my order",
    ],
    "shipping": [
        "shipping", "delivery", "tracking", "package",
        "shipped", "arrive",
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
    """Classify a customer message using keyword rules."""
    text = message.lower()

    # Check specific intents before general support.
    for intent in (
        "returns_refunds",
        "order_status",
        "shipping",
        "general_support",
    ):
        if any(term in text for term in INTENTS[intent]):
            return intent

    return "general_support"


def find_order_number(message):
    """Extract an order number such as ORD1001."""
    for word in message.upper().split():
        candidate = word.strip(".,!?;:#()")

        if (
            candidate.startswith("ORD")
            and candidate[3:].isdigit()
        ):
            return candidate

    return None


def lookup_order(order_number):
    """Look up an order using deterministic Python code."""
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

Detected intent: {intent}

Store policies:
{POLICIES}

Verified order information:
{order_context}

Rules:
- Respond naturally and helpfully.
- Never invent order statuses or delivery dates.
- If order information is unavailable, ask for an order number.
- Never promise that a refund has been approved.
- Refer refund decisions and account-specific problems to a human.
- Never ask for passwords or full payment card details.
- Disclose that you are AI software when relevant.
- Never claim to submit, initiate, or complete a return,
  refund, or other action unless the application actually
  performs that action.
- If no return-submission tool exists, explain that you can
  provide guidance but a human agent must handle the request.
- Do not claim to have contacted a human or submitted a request.
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


# Maintain conversation history across Streamlit reruns.
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

# Display conversation history.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Handle new customer messages.
if prompt := st.chat_input("Type your question here..."):
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    intent = detect_intent(prompt)
    order_number = find_order_number(prompt)

    # Reuse a previously mentioned order number if needed.
    if not order_number:
        for previous_message in reversed(
            st.session_state.messages[:-1]
        ):
            order_number = find_order_number(
                previous_message["content"]
            )
            if order_number:
                break

    order = lookup_order(order_number)

    order_context = "No verified order information available."

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

    # Deterministic order lookup does not depend on the AI API.
    if order_number and (
        "order" in prompt.lower()
        or "arrive" in prompt.lower()
        or "delivery" in prompt.lower()
        or "status" in prompt.lower()
        or "track" in prompt.lower()
        or "shipping" in prompt.lower()
    ):
        if order:
            response = (
                f"Order {order_number} was found! "
                f"Status: {order['status']}. "
                f"Estimated delivery: {order['delivery']}."
            )
        else:
            response = (
                f"I couldn't find order {order_number} "
                "in our sample database. Please check the number."
            )

    else:
        # Check for a configured API key only when AI is needed.
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

        except Exception as e:
            response = (
                "I'm sorry, the AI service is temporarily "
                "unavailable. Please try again shortly. "
                "Your order lookup feature is still available. "
                "For refund decisions, please contact a human agent."
            )
            print(f"Groq API error: {type(e).__name__}: {e}")

    # Display and save the response.
    with st.chat_message("assistant"):
        st.write(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

st.divider()
st.caption(
    "Student capstone demonstration. "
    "All order records and policies are fictional. "
    "This chatbot uses AI software."
)
