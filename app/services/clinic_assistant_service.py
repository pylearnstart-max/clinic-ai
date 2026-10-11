class ClinicAssistantService:
    """Provide basic, predefined answers to common clinic questions."""

    FAQ_RESPONSES = {
        "hello": "Hello! Welcome to ClinicAI. How can I help you?",
        "hi": "Hello! Welcome to ClinicAI. How can I help you?",
        "services": (
            "Please contact the clinic to confirm its available services."
        ),
        "timings": (
            "Please contact the clinic to confirm its working hours."
        ),
        "appointment": (
            "You can ask the clinic reception for help with appointments."
        ),
    }

    def get_response(self, message):
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Message is required")

        question = message.strip().lower()

        for keyword, response in self.FAQ_RESPONSES.items():
            if keyword in question:
                return response

        return (
            "I could not find a verified answer. "
            "Please contact the clinic for assistance."
        )
