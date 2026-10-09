from flask import Blueprint, request, jsonify
from app.services.patient_service import PatientService

patient_api = Blueprint(
    "patient_api",
    __name__,
    url_prefix="/api"
)

patient_service = PatientService()


@patient_api.route("/patients", methods=["POST"])
def add_patient():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    try:
        patient_service.add_patient(
            name=data.get("name"),
            age=data.get("age"),
            gender=data.get("gender"),
            phone=data.get("phone"),
            address=data.get("address")
        )
        return jsonify({"message": "Patient added successfully"}), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@patient_api.route("/patients", methods=["GET"])
def get_all_patients():
    try:
        patients = patient_service.get_all_patients()
        patient_list = []

        for patient in patients:
            patient_list.append({
                "patient_id": patient.patient_id,
                "name": patient.name,
                "age": patient.age,
                "gender": patient.gender,
                "phone": patient.phone,
                "address": patient.address
            })

        return jsonify(patient_list), 200

    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@patient_api.route("/patients/<int:patient_id>", methods=["GET"])
def get_patient_by_id(patient_id):
    try:
        patient = patient_service.get_patient_by_id(patient_id)

        if patient is None:
            return jsonify({"error": "Patient not found"}), 404

        return jsonify({
            "patient_id": patient.patient_id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "phone": patient.phone,
            "address": patient.address
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@patient_api.route("/patients/<int:patient_id>", methods=["PUT"])
def update_patient(patient_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    try:
        updated = patient_service.update_patient(
            patient_id=patient_id,
            name=data.get("name"),
            age=data.get("age"),
            gender=data.get("gender"),
            phone=data.get("phone"),
            address=data.get("address")
        )

        if not updated:
            return jsonify({"error": "Patient not found"}), 404

        return jsonify({"message": "Patient updated successfully"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@patient_api.route("/patients/<int:patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    try:
        deleted = patient_service.delete_patient(patient_id)

        if not deleted:
            return jsonify({"error": "Patient not found"}), 404

        return jsonify({"message": "Patient deleted successfully"}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500
