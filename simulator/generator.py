import resources
from fhir.resources.patient import Patient
from fhir.resources.practitioner import Practitioner
from fhir.resources.organization import Organization
from fhir.resources.location import Location

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

def generate_organization() -> Organization:
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

def generate_location(_status: str= "active", _building: str = 'G'):
    location = resources.LocationGenerator(building=_building)
    location_event = Location(
        id=location.id,
        status=_status,
        name=location.name,
        form=location.form,
        extension=location.extension 
    )
    return location_event

if __name__ == '__main__':
    print(generate_location().json(indent=2))