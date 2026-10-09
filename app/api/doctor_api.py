from flask import Blueprint, request, jsonify
from app.services.doctor_service import DoctorService

doctor_api = Blueprint("doctor_api", __name__)
doctor_service = DoctorService()


def doctor_to_dict(doctor):
    return {
        "doctor_id": doctor.doctor_id,
        "name": doctor.name,
        "specialization": doctor.specialization,
        "phone": doctor.phone,
        "email": doctor.email,
        "consultation_fee": (
            float(doctor.consultation_fee)
            if doctor.consultation_fee is not None else None
        ),
        "is_available": doctor.is_available
    }


@doctor_api.route("/doctors", methods=["POST"])
def add_doctor():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    try:
        success = doctor_service.add_doctor(
            name=data.get("name"),
            specialization=data.get("specialization"),
            phone=data.get("phone"),
            email=data.get("email"),
            consultation_fee=data.get("consultation_fee", 0)
        )
        if success:
            return jsonify({"message": "Doctor added successfully"}), 201
        return jsonify({"error": "Doctor could not be added"}), 500
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@doctor_api.route("/doctors", methods=["GET"])
def get_all_doctors():
    try:
        doctors = doctor_service.get_all_doctors()
        return jsonify([doctor_to_dict(d) for d in doctors]), 200
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@doctor_api.route("/doctors/<int:doctor_id>", methods=["GET"])
def get_doctor_by_id(doctor_id):
    try:
        doctor = doctor_service.get_doctor_by_id(doctor_id)
        if doctor is None:
            return jsonify({"error": "Doctor not found"}), 404
        return jsonify(doctor_to_dict(doctor)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@doctor_api.route("/doctors/<int:doctor_id>", methods=["PUT"])
def update_doctor(doctor_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    try:
        available = data.get("is_available", True)
        if not isinstance(available, bool):
            return jsonify({"error": "is_available must be true or false"}), 400

        updated = doctor_service.update_doctor(
            doctor_id=doctor_id,
            name=data.get("name"),
            specialization=data.get("specialization"),
            phone=data.get("phone"),
            email=data.get("email"),
            consultation_fee=data.get("consultation_fee", 0),
            is_available=available
        )
        if not updated:
            return jsonify({"error": "Doctor not found"}), 404
        return jsonify({"message": "Doctor updated successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@doctor_api.route("/doctors/<int:doctor_id>", methods=["DELETE"])
def delete_doctor(doctor_id):
    try:
        deleted = doctor_service.delete_doctor(doctor_id)
        if not deleted:
            return jsonify({"error": "Doctor not found"}), 404
        return jsonify({"message": "Doctor deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500
