# FHIR General Resources
from fhir.resources.address import Address
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.humanname import HumanName
from fhir.resources.extension import Extension
from fhir.resources.reference import Reference
from fhir.resources.quantity import Quantity
from fhir.resources.bundle import BundleEntry
# Observation
from fhir.resources.observation import Observation, ObservationComponent
# Patient
from fhir.resources.patient import PatientCommunication
# Practitioner
from fhir.resources.practitioner import PractitionerQualification
# Encounter
from fhir.resources.encounter import Encounter, EncounterParticipant
# Generator Resources
from faker import Faker
from datetime import datetime, date
from decimal import Decimal
import random
import time

fake = Faker('id_ID')

class IdIteration:
    @staticmethod
    def iteration_gen():
        curr_id = 1
        last_time = time.localtime().tm_hour
        while curr_id != 1000:
            curr_time = time.localtime().tm_hour
            if last_time != curr_time:
                curr_id = 1
                last_time = curr_time
            yield curr_id
            curr_id += 1
        return

class Identifiers:
    """
    Docstring for Identifiers
    """
    def __init__ (self) -> None:
        self.gender = self.get_gender()
        self.birth_date = fake.date_of_birth(maximum_age = 70)
        self.identifier = self.get_identifier()
        self.telcom = self.get_telcom() 
        self.address = self.get_address() 
        self.communication = self.get_communication()

    def get_gender(self) -> str:
        gender = ['male', 'female']
        return random.choice(gender)
    
    def get_ihs(self) -> str:
        digits = [0,1,2,3,4,5,6,7,8,9]
        ihs_number = random.choices(digits, k=11)
        return f'P{''.join(map(str, ihs_number))}'

    def get_nik(self, dob) -> str:
        dob = dob
        province = str(random.randint(31, 36))
        city = str(random.randint(71, 78))
        sub_disctrict = f'{random.randint(1, 9):02d}'
        day = '00'
        if self.gender == 'male':
            day = str(dob.day).zfill(2)
        if self.gender == 'female':
            day = str(int(dob.day) + 40)
        month = str(dob.month).zfill(2)
        year = str(dob.year)[2:]
        registry_num = f'{random.randint(1, 1000):04d}'
        nik = province + city + sub_disctrict + day + month + year + registry_num
        return nik

    def get_passport_number(self) -> str:
        passport_letter = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=1))
        passport_number = ''.join(random.choices('0123456789', k=9))
        return passport_letter + passport_number
    
    def get_identifier(self) -> list[dict[str, str]]:
        identifier = []
        identifier.append({"use": "official", "system": "https://fhir.kemkes.go.id/id/patient-ihs-number", "value": self.get_ihs()})
        identifier.append({"use": "official", "system": "https://fhir.kemkes.go.id/id/nik", "value": self.get_nik(self.birth_date)})
        if random.randint(1, 100) < 10:
            identifier.append({"use": "official", "system": "https://fhir.kemkes.go.id/id/paspor", "value": self.get_passport_number()})
        return identifier

    def get_telcom(self) -> list[dict[str, str]]:
        telcom = []
        chance = random.randint(1, 100)
        if chance < 90:
            phone_contact = {"system": "phone", "value": fake.phone_number(), "use": "mobile"}
            telcom.append(phone_contact)
        elif chance < 30:
            email_contact = {"system": "email", "value": fake.ascii_free_email(), "use": "home"}
            telcom.append(email_contact)
        return telcom

    def get_address(self) -> list[Address]:
        _use = random.choice(['home', 'temporary'])
        _line = []
        _line.append(fake.street_address())
        if random.randint(1, 100) < 50:
            _line.append(fake.street_address())
        _city = fake.city_name()
        _postal_code = fake.postcode()

        # 20% chance to have multiple addresses
        many_address = random.randint(1, 100)
        if many_address < 20:
            addresses = []
            for _ in range(1, 3):
                address = Address(
                    use=_use,
                    line=_line,
                    city=_city,
                    postalCode=_postal_code
                )
                addresses.append(address)
            return addresses

        # Single address
        address = Address(
            use=_use,
            line=_line,
            city=_city,
            postalCode=_postal_code
        )

        return [address]

    def get_communication(self) -> list[PatientCommunication]:
        code = 'id-ID'
        display = 'Indonesian'
        communication = PatientCommunication(
            language=CodeableConcept(
                coding=[{
                    "system": "urn:ietf:bcp:47",
                    "code": code,
                    "display": display
                }] 
            ) 
        )
        return [communication]

    def debug_print(self) -> dict[str, str | int]:
        return self.__dict__

class OrganizationGenerator:
    def __init__ (self, identifier: str, active: bool = True):
        self.identifier = self.get_identifier(identifier)
        self.active = active
        self.name = self.get_org_name()
        self.alias = self.get_org_alias()
        self.type = self.get_type()
        self.contact = self.get_contact()
    
    def get_identifier(self, value) -> list[dict[str, str]]:
        identifier = []
        identifier.append({
            "use": "official", 
            "system": "http://sys-ids.kemkes.go.id/organization/str", 
            "value": value
                           })
        return identifier   

    def get_org_name(self) -> str:
        org_suffix = random.choice(['RSUD', 'RSIA', 'RSPP'])
        org_name = f'{org_suffix} {fake.city_name()}'
        return org_name

    def get_org_alias(self) -> list[str | None] | None:
        alias = None
        chance = random.randint(0, 100)
        if not self.name:
            return alias
        if chance <= 50:
            return alias
        else:
            alias = []
            name = self.get_org_name()
            _name = [name.split()[0]]
            shortned = [w[0] for w in name.split()][1:]
            shortned = ''.join(shortned)
            _name.append(shortned)
            _name = '-'.join(_name)
            alias.append(_name)
            return alias

    def get_type(self) -> list[CodeableConcept]:
        code = CodeableConcept(
            coding=[{
                "system": "http://terminology.hl7.org/CodeSystem/organization-type",
                "code": "prov",
                "display": "Healthcare Provider"
            }]
        )
        return [code]

    def get_telcom(self) -> list[dict[str, str]]:
        telcom = []
        if self.alias == None:
            name = self.name.replace(" ", "-").lower()
            phone_contact = {"system": "phone", "value": f"021-{random.randint(1000000, 9999999)}", "use": "work"}
            telcom.append(phone_contact)
            email_contact = {"system": "email", "value": f"info@{name}.go.id", "use": "work"}
            telcom.append(email_contact)
            url_contact = {"system": "url", "value": f"http://www.{name}.go.id", "use": "work"}
            telcom.append(url_contact)
        elif isinstance(self.alias[0], str):
            phone_contact = {"system": "phone", "value": f"021-{random.randint(1000000, 9999999)}", "use": "work"}
            telcom.append(phone_contact)
            email_contact = {"system": "email", "value": f"info@{self.alias[0].lower()}.go.id", "use": "work"}
            telcom.append(email_contact)
            url_contact = {"system": "url", "value": f"http://www.{self.alias[0].lower()}.go.id", "use": "work"}
            telcom.append(url_contact)
        else:
            return telcom
        return telcom
    
    def get_address(self) -> Address:
        _line = []
        _line.append(fake.street_address())
        if random.randint(1, 100) < 50:
            _line.append(fake.street_address())
        _city = fake.city_name()
        _postal_code = fake.postcode()

        address = Address(
            use="work",
            type="both",
            line=_line,
            city=_city,
            postalCode=_postal_code,
            country="ID",
            extension=[
                {
                    "url": "https://fhir.kemkes.go.id/id/extension/province-code",
                    "valueString": str(random.randint(31, 36))
                },
                {
                    "url": "https://fhir.kemkes.go.id/id/extension/city-code",
                    "valueString": str(random.randint(71, 78))
                },
                {
                    "url": "https://fhir.kemkes.go.id/id/extension/district-code",
                    "valueString": f'{random.randint(1, 9):02d}'
                },
                {
                    "url": "https://fhir.kemkes.go.id/id/extension/village-code", 
                    "valueString": f'{random.randint(1, 99):02d}'
                }
            ]
        )
        return address

    def get_contact(self) -> list[dict[str, str | list[Address]]]:
        contact = []
        purpose = CodeableConcept(coding=[{"system": "http://terminology.hl7.org/CodeSystem/contactentity-type",
                                           "code": "ADMIN",
                                           "display": "Administrative"}])
        contact_dict = {
            "purpose": purpose,
            "name": [{"text": "Bagian Administrasi"}],
            "telecom": self.get_telcom(),
            "address": self.get_address()
        }
        contact.append(contact_dict)
        return contact

class LocationGenerator:
    def __init__(self, building: str, name: str) -> None:
        self.building = building
        self.name = name
        self.id = self.get_id()
        self.name = self.get_name() 
        self.form = self.get_form()
        self.extension = self.get_extension()

    def get_id(self) -> str:
        id = ''
        if self.building == 'B':
            id = f"LOK-GEDUNG-{self.name}"
        elif self.building == 'R':
            id = f"LOK-RUANG-{self.name}"
        return id

    def get_name(self) -> str:
        name = self.id[4:].replace('-', ' ').title()
        return name

    def get_form(self) -> CodeableConcept | None:
        form = None
        if self.building:
            _code = ''
            _display = ''
            if self.building == 'B':
                _code = "bd"
                _display = "Building"
            elif self.building == 'R':
                _code = "ro"
                _display = "Room"
            form = CodeableConcept(
                coding=[Coding(
                    system="http://terminology.hl7.org/CodeSystem/location-physical-type",
                    code=_code,
                    display=_display
                )]
            )
        return form

    def get_extension(self) -> list[Extension] | None:
        extension = None
        if self.building == 'R':
            _code = "100"
            _display = "Non Kelas"
            _extension = Extension(
                url="https://fhir.kemkes.go.id/id/extension/location-serviceClass",
                valueCodeableConcept=CodeableConcept(
                    coding=[Coding(
                        system="http://terminology.kemkes.go.id/CodeSystem/location-serviceClass",
                        code=_code,
                        display=_display,
                    )]
                )
            )
            extension = []
            extension.append(_extension)
            return extension
        return extension
        
class PracticionerGenerator(Identifiers):
    class Qualification:
        @staticmethod
        def get_identifier(practitioner: str) -> dict[str, str]:
            practitioner = practitioner
            identifier_dict = {}
            if practitioner == 'dr':
                identifier_dict = {
                    "system": "http://sys-ids.kemkes.go.id/qualification/str",
                    "value": str(random.randint(1000000000000000, 9999999999999999))
                    }
            if practitioner == 'nrs':
                identifier_dict = {
                    "system": "http://sys-ids.kemkes.go.id/qualification/str",
                    "value": str(random.randint(1000000000000000, 9999999999999999))
                    }
            if practitioner == 'apt':
                identifier_dict = {
                    "system": "http://sys-ids.kemkes.go.id/qualification/str",
                    "value": str(random.randint(1000000000000000, 9999999999999999))
                    }
            if practitioner == 'lt':
                identifier_dict = {
                    "system": "http://sys-ids.kemkes.go.id/qualification/str",
                    "value": str(random.randint(100000000000000, 999999999999999))
                    }
            return identifier_dict
        
        @staticmethod
        def get_code(practitioner: str) -> dict[str, str]:
            practitioner = practitioner
            code_dict = {}
            if practitioner == 'dr':
                code_dict = {
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0360/2.7",
                    "code": "MD",
                    "display": "Doctor of Medicine"
                    }
            if practitioner == 'nrs':
                code_dict = {
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0360/2.7",
                    "code": "RN",
                    "display": "Registered Nurse"
                    }
            if practitioner == 'apt':
                code_dict = {
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0360/2.7",
                    "code": "AP",
                    "display": "Apt."
                    }
            if practitioner == 'lt':
                code_dict = {
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0360/2.7",
                    "code": "MT",
                    "display": "Medical Technologist"
                    }
            return code_dict

    def __init__ (self, practitioner: str):
        super().__init__()
        self.id = self.get_id(practitioner)
        self.birth_date = fake.date_of_birth(minimum_age=25, maximum_age=70)
        self.qualification = self.get_qualification(practitioner)
        self.name = self.get_name(practitioner)
        pass

    def get_ihs(self) -> str:
        ihs_front = random.choice(['1000', '1001'])
        ihs_back = ''.join(random.choices('0123456789', k=7))
        ihs = ihs_front + ihs_back
        return ihs

    def get_id(self, practitioner) -> str:
        practitioner_id = None
        if practitioner == 'dr':
            practitioner_id = f'DOC-{random.randint(1000000, 9999999)}'
        elif practitioner == 'nrs':
            practitioner_id = f'NRS-{random.randint(1000000, 9999999)}'
        elif practitioner == 'apt':
            practitioner_id = f'APT-{random.randint(1000000, 9999999)}'
        elif practitioner == 'lt':
            practitioner_id = f'LT-{random.randint(1000000, 9999999)}'
        else:
            error = f"{practitioner} is not in the scope of this chart!"
            raise AttributeError (error)
        return practitioner_id
    
    def get_qualification(self, practitioner: str) -> list[PractitionerQualification]:
        identify = self.Qualification()
        identifier = identify.get_identifier(practitioner)
        code = identify.get_code(practitioner)
        qualification = []
        # Build Identifier
        identifier = {
            "use": "official",
            "system": identifier["system"],
            "value": identifier["value"]
        }
        # Build CodeableConcept
        codeable_concept = CodeableConcept(
            coding=[Coding(
                system=code["system"],
                code=code["code"],
                display=code["display"]
            )]
        )
        # Build Qualification
        _qualification = PractitionerQualification(
            identifier=[identifier],
            code=codeable_concept
        )
        qualification.append(_qualification)
        return qualification

    def get_name(self, practitioner: str) -> list[HumanName]:
        _name = ''
        gender = self.gender
        # Generate name
        if gender == 'male':
            first_name = fake.first_name_male()
            last_name = fake.last_name_male()
            _name = f'{first_name} {last_name}'
        elif gender == 'female':
            first_name = fake.first_name_female()
            last_name = fake.last_name_female()
            _name = f'{first_name} {last_name}'
        # Generate Suffix
        if practitioner == 'dr':
            _name = f'Dr. {_name}, S.Ked.'         
        elif practitioner == 'nrs':
            _name = f'Ns. {_name}, S.Kep.'
        elif practitioner == 'apt':
            suffix_back = random.choice(['S.Farm., M.Farm.', 'S.Farm.'])
            _name = f'apt. {_name}, {suffix_back}'
        elif practitioner == 'lt':
            suffix_back = random.choice(['A.Md.Kes', 'S.Keb.'])
            _name = f'{_name}, {suffix_back}'
        name = HumanName(
            use="official",
            text=_name
        )
        return [name]

class PatientGenerator(Identifiers):
    id_itter_gen = IdIteration.iteration_gen()

    def __init__ (self):
        super().__init__()
        self.itter_id = next(self.id_itter_gen) # Best if you use snomed or uuidv7
        self.id = self.get_id()
        self.name = self.get_name()
        self.multiple_birth = self.get_multiple_birth(self.birth_date)
        self.patient_link = self.get_patient_link()

    def get_id(self) -> str:
        curr_itter_id = self.itter_id
        curr_date = datetime.now()
        # Id based on month|day|hour|itteration
        month = str(curr_date.month).zfill(2) 
        day = str(curr_date.day).zfill(2)
        hour = str(curr_date.hour).zfill(2)
        patient_id = str(curr_itter_id).zfill(3)
        return f'PAT-{month}{day}{hour}{patient_id}'

    def get_name(self) -> list[HumanName]:
        _name = ''
        gender = self.gender
        if gender == 'male':
            _name = fake.name_male()
        elif gender == 'female':
            _name = fake.name_female()
        name = HumanName(
            use="official",
            text=_name
        )
        return [name]

    def get_multiple_birth(self, dob) -> int:
        dob = dob
        multiple_birth = 0
        if self.gender == 'male':
            multiple_birth = 0
        elif self.gender == 'female':
            age = (datetime.now() - (datetime.combine(dob, datetime.min.time()))).days // 365
            if random.randint(0, 100) < 50 and age > 25:
                multiple_birth = random.randint(1, 8)
        return multiple_birth

    def get_patient_link(self) -> (list[dict[str, str]]):
        link = {"other": {"reference": "None"}, "type": "None"}
        if random.randint(1, 100) < 10:
            patient_link = {}
            digits = [0,1,2,3,4,5,6,7,8,9]
            patient_number = random.choices(digits, k=11)
            reference = f'Patient/P{''.join(map(str, patient_number))}'
            link = {"other": {"reference": reference}, "type": "replaced-by"}

        return [link]

    def debug_print(self) -> dict[str, str | int]:
        return self.__dict__

class EncounterGenerator:
    id_itter_gen = IdIteration.iteration_gen()

    def __init__(self,
                 subject: dict,
                 practitioner: list[dict],
                 provider: dict,
                 location: dict,
                 ) -> None:
        self.subject = subject
        self.practitioner = practitioner
        self.provider = provider
        self.location = location

    def get_encounter_participant(self,
                                  _reference: dict | None = None,
                                  display: str | None = None,
                                  id: str | None = None):
        if display and id:
            reference = Reference(reference=f"Patient/{id}",
                                  display=display)
        elif _reference:
            reference = _reference
        else:
            error = f"{_reference}, {display}, {id}, can not be referenced!"
            raise AttributeError (error)
        return EncounterParticipant(
            actor=reference
        )
    
    def generate_encounter(self):
        encounters = []
        
        return

class ObservationGenerator:
    @staticmethod
    def create_coding(code, display) -> CodeableConcept:
        return CodeableConcept(coding=[Coding(system="http://loinc.org",
                                              code=code,
                                              display=display)])
    
    @staticmethod
    def create_category(code: str) -> list[CodeableConcept]:
        return [CodeableConcept(coding=[Coding(system="http://terminology.hl7.org/CodeSystem/observation-category",
                                              code=code,
                                              display=code.title())])]

    @staticmethod
    def get_code_category(observation: str):
        code, display, category = None, None, None
        if observation == "Body Weight":
            code = "29463-7"
            display = "Body Weight"
            category = "vital-sign"
        elif observation == "Body Height":
            code = "8302-2"
            display = "Body Height"
            category = "vital-sign"
        elif observation == "Blood Pressure":
            code = "85354-9" 
            display = "Blood pressure panel with all children optional"
            category = "vital-sign"
        elif observation == "Glucose":
            code = "2339-0" 
            display = "Glucose [Mass/volume] in Blood"
            category = "laboratory"
        elif observation == "Insulin":
            code = "20436-2" 
            display = "Insulin [Mass/volume] in Serum or Plasma"
            category = "laboratory"
        elif observation == "Skinfold":
            code = "8280-0" 
            display = "Triceps skinfold"
            category = "exam"
        else:
            error = f"{observation} type is not covered in this chart."
            raise AttributeError (error)
        return {"code": code, "display": display, "category": category}

    def __init__(self, age: date, gender: str) -> None:
        self.age = (datetime.now() - datetime.combine(age, datetime.min.time())).days // 365
        self.gender = gender
        self.status = random.choice(['normal', 'diabetic'])

    def __call__(self, 
                 patient_reference: str,
                 encounter_reference: str,
                 doctor_reference: str,
                 nurse_reference: str,
                 mt_reference: str) -> list[BundleEntry]:
        self.weight = self.weight_generator()
        self.height = self.height_generator()
        self.blood_pressure = self.blood_pressure_generator()
        self.glucose = self.glucose_generator()
        self.insulin = self.insulin_generator()
        self.skin_fold = self.skin_fold_thickness_generator()
        observation_result = self.observation(patient_reference,
                                                   encounter_reference,
                                                   doctor_reference,
                                                   nurse_reference,
                                                   mt_reference)
        return observation_result

    def create_component(self, code: str, display: str):
        component = []
        if display == "Body Height":
            component_value = ObservationComponent(code=self.create_coding(code, display),
                                                   valueQuantity=Quantity(value=self.height,
                                                                          unit="cm",
                                                                          system="http://unitsofmeasure.org",
                                                                          code="cm"))
            component.append(component_value)
        elif display == "Body Weight":
            component_value = ObservationComponent(code=self.create_coding(code, display),
                                                   valueQuantity=Quantity(value=self.weight,
                                                                          unit="Kg",
                                                                          system="http://unitsofmeasure.org",
                                                                          code="Kg"))
        elif display == "Blood pressure panel with all children optional":
            blood_pressure = self.blood_pressure
            component_value_systolic = ObservationComponent(code=self.create_coding(code, display),
                                                   valueQuantity=Quantity(value=blood_pressure["systolic"],
                                                                          unit="mm[Hg]",
                                                                          system="http://unitsofmeasure.org",
                                                                          code="mm[Hg]"))
            component_value_diastolic = ObservationComponent(code=self.create_coding(code, display),
                                                   valueQuantity=Quantity(value=blood_pressure["diastolic"],
                                                                          unit="mm[Hg]",
                                                                          system="http://unitsofmeasure.org",
                                                                          code="mm[Hg]"))
            component.append(component_value_systolic)
            component.append(component_value_diastolic)
        elif display == "Glucose [Mass/volume] in Blood":
            component_value = ObservationComponent(code=self.create_coding(code, display),
                                                   valueQuantity=Quantity(value=self.glucose,
                                                                          unit="mg/dL",
                                                                          system="http://unitsofmeasure.org",
                                                                          code="mg/dL"))
            component.append(component_value)
        elif display == "Insulin [Mass/volume] in Serum or Plasma":
            component_value = ObservationComponent(code=self.create_coding(code, display),
                                                   valueQuantity=Quantity(value=self.insulin,
                                                                          unit="uIU/mL",
                                                                          system="http://unitsofmeasure.org",
                                                                          code="uIU/mL"))
            component.append(component_value)
        elif display == "Triceps skinfold":
            component_value = ObservationComponent(code=self.create_coding(code, display),
                                                   valueQuantity=Quantity(value=self.skin_fold,
                                                                          unit="mm",
                                                                          system="http://unitsofmeasure.org",
                                                                          code="mm"))
            component.append(component_value)
        else:
            error = f"{code} and {display} is not in this chart!"
            raise AttributeError (error)
        return component

    def weight_generator(self) -> Decimal:
        weight_max, weight_min = None, None
        if self.age < 2:                     
            weight_min, weight_max = 3.5, 7.5
        elif self.age < 6:                  
            weight_min, weight_max = 14, 38
        elif self.age < 12:                 
            weight_min, weight_max = 22, 38
        # Gender‑specific (pubescent and up)
        if self.gender == 'male':
            if self.age < 12:             
                weight_min, weight_max = 45, 58
            elif self.age < 40:           
                weight_min, weight_max = 60, 65
            elif self.age < 71:           
                weight_min, weight_max = 65, 70
        elif self.gender == 'female':
            if self.age < 12:             
                weight_min, weight_max = 44, 54
            elif self.age < 40:           
                weight_min, weight_max = 54, 58
            elif self.age < 71:           
                weight_min, weight_max = 58, 64
        if weight_min is None or weight_max is None:
            raise AttributeError(f"Weight chart does not cover age {self.age} or gender '{self.gender}'")
        weight = round(random.uniform(weight_min, weight_max), 2)
        if self.status == 'diabetic':
            weight += random.randint(10, 20)
        return Decimal(str(weight))

    def height_generator(self) -> Decimal:
        height_min, height_max = None, None
        if self.age < 2:
            height_min, height_max = 48, 51
        elif self.age < 6:
            height_min, height_max = 85, 96
        elif self.age < 12:
            height_min, height_max = 96, 148
        # Gender‑specific (pubescent and up)
        if self.gender == 'male':
            if self.age < 12:
                height_min, height_max = 150, 165
            elif self.age < 40:
                height_min, height_max = 163, 168
            elif self.age < 71:
                height_min, height_max = 162, 166
        elif self.gender == 'female':
            if self.age < 12:
                height_min, height_max = 148, 155
            elif self.age < 40:
                height_min, height_max = 152, 157
            elif self.age < 71:
                height_min, height_max = 151, 155
        if height_min is None or height_max is None:
            raise AttributeError(f"Height chart does not cover age {self.age} or gender '{self.gender}'")
        height = random.randint(height_min, height_max)
        return Decimal(str(height))

    def blood_pressure_generator(self) -> dict[str, Decimal]:
        sys_min, dia_min = None, None
        if self.age < 6:  
            sys_min, dia_min = 80, 55
            sys_max, dia_max = 110, 79
        elif self.age < 14: 
            sys_min, dia_min = 90, 60
            sys_max, dia_max = 115, 80
        elif self.age < 20: 
            sys_min, dia_min = 105, 73
            sys_max, dia_max = 120, 81
        elif self.age < 25: 
            sys_min, dia_min = 108, 75
            sys_max, dia_max = 132, 83
        elif self.age < 30: 
            sys_min, dia_min = 109, 76
            sys_max, dia_max = 133, 84
        elif self.age < 35: 
            sys_min, dia_min = 110, 77
            sys_max, dia_max = 134, 85
        elif self.age < 40:
            sys_min, dia_min = 111, 78
            sys_max, dia_max = 135, 86
        elif self.age < 45:
            sys_min, dia_min = 112, 79
            sys_max, dia_max = 137, 87
        elif self.age < 50:
            sys_min, dia_min = 115, 80
            sys_max, dia_max = 139, 88
        elif self.age < 55:
            sys_min, dia_min = 116, 81
            sys_max, dia_max = 142, 89
        elif self.age < 60:
            sys_min, dia_min = 118, 82
            sys_max, dia_max = 144, 90
        elif self.age < 71:
            sys_min, dia_min = 121, 83
            sys_max, dia_max = 147, 91
        else:
            raise AttributeError(f"Blood pressure chart does not cover age {self.age}")
        systolic = random.randint(sys_min, sys_max)
        diastolic = random.randint(dia_min, dia_max)
        if self.status == 'diabetic':
            systolic += random.randint(5, 15)
            diastolic += random.randint(3, 10)
        return {"systolic": Decimal(str(systolic)), "diastolic": Decimal(str(diastolic))}

    def glucose_generator(self) -> Decimal:
        glucose_value = random.randint(70, 99)
        if self.status == "diabetic":
            glucose_value += random.randint(1, 25)
            if random.randint(1, 100) <= 50:
                glucose_value += random.randint(1, 10)
        glucose = Decimal(str(glucose_value))
        return glucose

    def insulin_generator(self) -> Decimal:
        insulin_value = random.uniform(2, 5)
        if self.status == "diabetic":
            insulin_value += random.uniform(1, 9)
            if random.randint(1, 100) <= 50:
                insulin_value += random.uniform(1, 10)
        insulin = Decimal(str(round(insulin_value, 2)))
        return insulin

    def skin_fold_thickness_generator(self) -> Decimal:
        thickness_max, thickness_min = None, None
        if self.age < 3:
            if self.gender == 'male':
                thickness_min, thickness_max = 8, 12
            elif self.gender == 'female':
                thickness_min, thickness_max = 8, 12
        elif self.age < 12:
            if self.gender == 'male':
                thickness_min, thickness_max = 8, 12
            elif self.gender == 'female':
                thickness_min, thickness_max = 10, 15
        elif self.age < 18:
            if self.gender == 'male':
                thickness_min, thickness_max = 8, 14
            elif self.gender == 'female':
                thickness_min, thickness_max = 14, 20
        elif self.age < 40:
            if self.gender == 'male':
                thickness_min, thickness_max = 10, 15
            elif self.gender == 'female':
                thickness_min, thickness_max = 16, 22
        elif self.age < 71:
            if self.gender == 'male':
                thickness_min, thickness_max = 12, 18
            elif self.gender == 'female':
                thickness_min, thickness_max = 20, 26
        if thickness_min is None or thickness_max is None:
            error = f"Skin fold thickness chart does not cover age {self.age} or gender '{self.gender}'"
            raise AttributeError(error)
        thickness = round(random.uniform(thickness_min, thickness_max), 1)
        # If Diabetic
        if self.status == 'diabetic':
            if self.gender == 'male':
                thickness = random.uniform(20, 25)
            elif self.gender == 'female':
                thickness = random.uniform(30, 35)
            thickness = round(thickness, 1)
        return Decimal(str(thickness))

    def observation(self, patient, encounter, doctor, nurse, mt) -> list[BundleEntry]:
        observation = []
        def observe_gen(_patient, _encounter, _performer, _observation) -> BundleEntry:
            data = self.get_code_category(_observation)          
            code, display, category = data["code"], data["display"], data["category"]
            weight_obs = Observation(
                status='final',
                category=self.create_category(category),
                code=self.create_coding(code, display),
                subject=Reference(reference=_patient),
                encounter=Reference(reference=_encounter),
                performer=[Reference(reference=_performer)],
                component=self.create_component(code, display)
            )
            return BundleEntry(resource=weight_obs, request={"method": "POST", "url": "Observation"})
        observation.append(observe_gen(patient, encounter, nurse, "Body Weight"))
        observation.append(observe_gen(patient, encounter, nurse, "Body Height"))
        observation.append(observe_gen(patient, encounter, nurse, "Blood Pressure"))
        observation.append(observe_gen(patient, encounter, mt, "Glucose"))
        observation.append(observe_gen(patient, encounter, mt, "Insulin"))
        observation.append(observe_gen(patient, encounter, doctor, "Skinfold"))
        return observation
