import resources
from fhir.resources.patient import Patient
from fhir.resources.practitioner import Practitioner
from fhir.resources.organization import Organization

def generate_patient_event() -> Patient:
    patient = resources.PatientGenerator()
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

def generate_organization():
    organization = resources.OrganizationGenerator()
    organization_event = Organization(
        identifier=organization.identifier,
        active=organization.active,
        type=organization.type,
        name=organization.name,
        alias=organization.alias,
        contact=organization.contact
    )
    return organization_event