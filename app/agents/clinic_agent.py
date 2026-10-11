from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# 1. Define workflow state
class ClinicState(TypedDict):
    message: str
    response: str
    category: str


# 2. Router: identify the message type
def classify_message(state: ClinicState):
    message = state["message"].strip().lower()

    if not message:
        category = "empty"

    elif message in ("hi", "hello", "hey"):
        category = "greeting"

    elif message in ("how are you", "how r u", "how are u"):
        category = "greeting"

    elif any(word in message for word in (
        "appointment", "appoinment", "appoint"
    )):
        category = "appointment"

    elif any(phrase in message for phrase in (
        "thank you", "thank u", "than u",
        "than k", "thanks", "thankyou"
    )):
        category = "thanks"

    elif "doctor" in message:
        category = "doctor"

    elif any(word in message for word in (
        "timing", "working hours", "clinic hours"
    )):
        category = "timings"

    elif message in ("bye", "goodbye"):
        category = "goodbye"

    else:
        category = "general"

    return {"category": category}


# 3. Greeting node
def greeting_node(state: ClinicState):
    message = state["message"].strip().lower()

    if message in ("how are you", "how r u", "how are u"):
        response = (
            "I'm doing well, thank you! "
            "How can I help you with your clinic-related questions?"
        )
    else:
        response = (
            "Hello! Welcome to ClinicAI. "
            "How can I help you?"
        )

    return {"response": response}


# 4. Appointment node
def appointment_node(state: ClinicState):
    return {
        "response": (
            "I can help you with appointment information. "
            "Please provide your preferred date and time, "
            "or contact clinic reception to confirm availability."
        )
    }


# 5. Doctor node
def doctor_node(state: ClinicState):
    return {
        "response": (
            "I can help with doctor-related information. "
            "Please contact clinic reception to confirm details."
        )
    }


# 6. Clinic timings node
def timings_node(state: ClinicState):
    return {
        "response": (
            "Please contact clinic reception to confirm "
            "the clinic's working hours."
        )
    }


# 7. Thank-you node
def thanks_node(state: ClinicState):
    return {
        "response": "You're welcome! How else can I help you?"
    }


# 8. Goodbye node
def goodbye_node(state: ClinicState):
    return {
        "response": (
            "Goodbye! Thank you for contacting ClinicAI."
        )
    }


# 9. General message node - Day 26 practice
def general_node(state: ClinicState):
    user_message = state["message"].strip()

    return {
        "response": (
            f"You said: '{user_message}'. "
            "Please tell me how I can help you with your clinic-related questions."
        )
    }


# 10. Empty message node
def empty_node(state: ClinicState):
    return {"response": "Please enter a message."}


# 11. Build the graph
builder = StateGraph(ClinicState)

builder.add_node("router", classify_message)
builder.add_node("greeting", greeting_node)
builder.add_node("appointment", appointment_node)
builder.add_node("doctor", doctor_node)
builder.add_node("timings", timings_node)
builder.add_node("thanks", thanks_node)
builder.add_node("goodbye", goodbye_node)
builder.add_node("general", general_node)
builder.add_node("empty", empty_node)


# 12. Connect the router
builder.add_edge(START, "router")

builder.add_conditional_edges(
    "router",
    lambda state: state["category"],
    {
        "greeting": "greeting",
        "appointment": "appointment",
        "doctor": "doctor",
        "timings": "timings",
        "thanks": "thanks",
        "goodbye": "goodbye",
        "general": "general",
        "empty": "empty",
    },
)


# 13. Connect all response nodes to END
for node_name in (
    "greeting",
    "appointment",
    "doctor",
    "timings",
    "thanks",
    "goodbye",
    "general",
    "empty",
):
    builder.add_edge(node_name, END)


# 14. Compile the graph
clinic_graph = builder.compile()


# 15. Run the assistant
if __name__ == "__main__":
    print("ClinicAI Assistant")
    print("Type 'exit' to stop.")
    print("-" * 40)

    while True:
        user_message = input("You: ")

        if user_message.strip().lower() == "exit":
            print("ClinicAI: Goodbye!")
            break

        result = clinic_graph.invoke({
            "message": user_message,
            "response": "",
            "category": "",
        })

        print("ClinicAI:", result["response"])
        print("-" * 40)