from flask import Blueprint, request, jsonify
from app.services.appointment_service import AppointmentService

appointment_api = Blueprint("appointment_api", __name__)
appointment_service = AppointmentService()


def appointment_to_dict(appointment):
    return {
        "appointment_id": appointment.appointment_id,
        "patient_id": appointment.patient_id,
        "doctor_id": appointment.doctor_id,
        "appointment_date": appointment.appointment_date.isoformat(),
        "appointment_time": appointment.appointment_time.isoformat(timespec="minutes"),
        "reason": appointment.reason,
        "status": appointment.status
    }


@appointment_api.route("/appointments", methods=["POST"])
def add_appointment():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    try:
        appointment = appointment_service.add_appointment(
            patient_id=data.get("patient_id"),
            doctor_id=data.get("doctor_id"),
            appointment_date=data.get("appointment_date"),
            appointment_time=data.get("appointment_time"),
            reason=data.get("reason")
        )
        return jsonify({
            "message": "Appointment booked successfully",
            "appointment": appointment_to_dict(appointment)
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@appointment_api.route("/appointments", methods=["GET"])
def get_all_appointments():
    try:
        appointments = appointment_service.get_all_appointments()
        return jsonify([
            appointment_to_dict(a) for a in appointments
        ]), 200
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@appointment_api.route("/appointments/<int:appointment_id>", methods=["GET"])
def get_appointment_by_id(appointment_id):
    try:
        appointments = appointment_service.get_all_appointments()

        for appointment in appointments:
            if appointment.appointment_id == appointment_id:
                return jsonify(appointment_to_dict(appointment)), 200

        return jsonify({"error": "Appointment not found"}), 404

    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@appointment_api.route("/appointments/<int:appointment_id>", methods=["PUT"])
def update_appointment(appointment_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    try:
        appointment = appointment_service.update_appointment(
            appointment_id, data
        )
        return jsonify({
            "message": "Appointment updated successfully",
            "appointment": appointment_to_dict(appointment)
        }), 200

    except ValueError as e:
        message = str(e)
        status_code = 404 if message == "Appointment not found" else 400
        return jsonify({"error": message}), status_code

    except Exception:
        return jsonify({"error": "Internal server error"}), 500

@appointment_api.route("/appointments/<int:appointment_id>", methods=["DELETE"])
def delete_appointment(appointment_id):
    try:
        appointment_service.delete_appointment(appointment_id)

        return jsonify({
            "message": "Appointment deleted successfully",
            "appointment_id": appointment_id
        }), 200

    except ValueError as e:
        message = str(e)
        status_code = 404 if message == "Appointment not found" else 400
        return jsonify({"error": message}), status_code

    except Exception:
        return jsonify({"error": "Internal server error"}), 500

