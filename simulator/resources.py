# FHIR General Resources
from fhir.resources.address import Address
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.humanname import HumanName
from fhir.resources.extension import Extension
# Organizatoin
from fhir.resources.organization import Organization
# Patient
from fhir.resources.patient import PatientCommunication
# Practitioner
from fhir.resources.practitioner import PractitionerQualification
# Generator Resources
from faker import Faker
from datetime import datetime
import random
import time
from typing import cast, List, Optional

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
    def __init__ (self):
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
    def __init__(self, building: str) -> None:
        self.building = building
        self.id = self.get_id()
        self.name = self.get_name() 
        self.form = self.get_form()
        self.extension = self.get_extension()

    def get_id(self) -> str:
        id = ''
        letter = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=1))
        if self.building == 'G':
            id = f"LOK-GEDUNG-{letter}"
        elif self.building == 'R':
            id = f"LOK-RUANG-{letter}"
        return id

    def get_name(self) -> str:
        name = self.id[4:].replace('-', ' ').title()
        return name

    def get_form(self) -> CodeableConcept | None:
        form = None
        if self.building:
            _code = ''
            _display = ''
            if self.building == 'G':
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
                        display=_display
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
                    "value": str(random.randint(100000000000000, 99999999999999))
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
        self.id = self.get_id()
        self.birth_date = fake.date_of_birth(minimum_age=25, maximum_age=70)
        self.qualification = self.get_qualification(practitioner)
        self.name = self.get_name(practitioner)
        pass

    def get_ihs(self) -> str:
        ihs_front = random.choice(['1000', '1001'])
        ihs_back = ''.join(random.choices('0123456789', k=7))
        ihs = ihs_front + ihs_back
        return ihs

    def get_id(self) -> str:
        return f'PRAC-{random.randint(1000000, 9999999)}'
    
    def get_qualification(self, practitioner: str) -> PractitionerQualification:
        identify = self.Qualification()
        identifier = identify.get_identifier(practitioner)
        code = identify.get_code(practitioner)
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
        qualification = PractitionerQualification(
            identifier=[identifier],
            code=codeable_concept
        )
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
            suffix = 'Dr.'
            _name = f'{suffix} {_name}'         
        elif practitioner == 'nrs':
            suffix = random.choice(['S.Kep'])
            _name = f'{suffix}'
        elif practitioner == 'apt':
            suffix_front = 'Apt.'
            suffix_back = random.choice(['S.Farm.M.Farm.', 'S.Farm.'])
            _name = f'{suffix_front} {_name} {suffix_back}'
        elif practitioner == 'lt':
            suffix_back = random.choice(['A.Md.Kes', 'S.Keb.'])
            _name = f'{_name} {suffix_back}'
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

class ObservationGenerator:
    def __init__(self) -> None:
        pass