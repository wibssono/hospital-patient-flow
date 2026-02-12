import resources
from typing import Annotated, Literal
from pydantic import Field
from faker import Faker

from fhir.resources.patient import Patient
from fhir.resources.practitioner import Practitioner
from fhir.resources.observation import Observation
from fhir.resources.organization import Organization
from fhir.resources.location import Location
from fhir.resources.bundle import BundleEntry, Bundle

fake = Faker('id_ID')

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

def generate_practitioner_event(practitioner: Literal['dr', 'nrs', 'apt', 'lt']) -> Practitioner:
    practicioner = resources.PracticionerGenerator(practitioner)
    practitioner_event = Practitioner(
        id = practicioner.id,
        name = practicioner.name,
        qualification = [practicioner.qualification],
        gender= practicioner.gender,
        birthDate= practicioner.birth_date
    )
    return practitioner_event

def generate_organization() -> Organization:
    organization = resources.OrganizationGenerator(identifier="10000004")
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

def generate_observation() -> list[BundleEntry]:
    observation = resources.ObservationGenerator(age=fake.date_of_birth(minimum_age=20, maximum_age=30), gender='male')
    return observation('001', '002', '10001', '10002', '10003')

if __name__ == '__main__':
    # print(generate_organization().json(indent=2))
    # print(generate_patient_event().json(indent=2))
    # ALLOWED_PRACTITIONERS: tuple[Literal['dr', 'nrs', 'apt', 'lt'], ...] = ('dr', 'nrs', 'apt')
    # for practitioner in ALLOWED_PRACTITIONERS:
    #     print(generate_practitioner_event(practitioner).json(indent=2))
    # for location in ['G', 'R']:
    #     print(generate_location(location).json(indent=2))
    patient = generate_patient_event()
    print('DEBUG PATIENT ID ATTRIBUTE:', patient.id)
    practitioner = generate_practitioner_event('nrs')
    observation = generate_observation()
    _entry = [
        BundleEntry(resource=patient, request={"method": "POST", "url": "Patient"}),
        BundleEntry(resource=practitioner, request={"method": "POST", "url": "Practitioner"})
    ]
    _entry.extend(observation)
    bundle = Bundle(
        type='transaction',
        entry=_entry
        )
    print(bundle.json(indent=2))