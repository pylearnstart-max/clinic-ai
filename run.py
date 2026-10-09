from flask import Flask

from app.api.patient_api import patient_api
from app.api.doctor_api import doctor_api
from app.api.appointment_api import appointment_api

app = Flask(__name__)

app.register_blueprint(patient_api)
app.register_blueprint(doctor_api)
app.register_blueprint(appointment_api)


@app.route("/")
def home():
    return {"message": "ClinicAI API is running"}


if __name__ == "__main__":
    app.run(debug=True)
