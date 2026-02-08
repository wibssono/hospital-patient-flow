import resources
from fhir.resources.patient import Patient
from fhir.resources.practitioner import Practitioner

def generate_patient_event() -> Patient:
    patient = resources.GeneralPatient()
    patient_event = Patient(
        id = patient.id,
        name = patient.name,
        gender = patient.gender,
        birthDate = patient.birth_date,
        multipleBirthInteger = patient.multiple_birth,
        link = patient.patient_link
    )
    return patient_event

def generate_practitioner_event(practitioner: str, building: str) -> Practitioner:
    practicioner = resources.PracticionerGenerator(practitioner, building)
    practitioner_event = Practitioner(
        id = practicioner.id,
        name = practicioner.name,
        qualification = [practicioner.qualification],
        gender= practicioner.gender,
        birthDate= practicioner.birth_date
    )
    return practitioner_event