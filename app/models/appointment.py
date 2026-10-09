class Appointment:
    def __init__(
        self,
        appointment_id=None,
        patient_id=None,
        doctor_id=None,
        appointment_date=None,
        appointment_time=None,
        reason=None,
        status="Scheduled"
    ):
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.appointment_date = appointment_date
        self.appointment_time = appointment_time
        self.reason = reason
        self.status = status

    def __str__(self):
        return (
            f"Appointment ID: {self.appointment_id}, "
            f"Patient ID: {self.patient_id}, "
            f"Doctor ID: {self.doctor_id}, "
            f"Date: {self.appointment_date}, "
            f"Time: {self.appointment_time}, "
            f"Status: {self.status}"
        )
