import logging

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from app.api.patient_api import patient_api
from app.api.doctor_api import doctor_api
from app.api.appointment_api import appointment_api
from app.auth.auth_api import auth_api
from app.api.clinic_assistant_api import clinic_assistant_api


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = Flask(__name__)

app.register_blueprint(patient_api)
app.register_blueprint(doctor_api)
app.register_blueprint(appointment_api)
app.register_blueprint(auth_api)
app.register_blueprint(clinic_assistant_api)


@app.errorhandler(HTTPException)
def handle_http_error(error):
    return jsonify({
        "error": error.description
    }), error.code


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.exception("Unhandled application error")

    return jsonify({
        "error": "Internal server error"
    }), 500


@app.route("/")
def home():
    return {"message": "ClinicAI API is running"}


if __name__ == "__main__":
    app.run(debug=True)