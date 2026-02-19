import time
import json
import jsonlines
import pickle
import tempfile
import resources
import random
import tempfile
from typing import Literal
from pydantic import Field
from faker import Faker

from fhir.resources.practitioner import Practitioner
from fhir.resources.practitionerrole import PractitionerRole
from fhir.resources.organization import Organization
from fhir.resources.location import Location
from fhir.resources.bundle import BundleEntry, Bundle

from pathlib import Path

fake = Faker('id_ID')

# class _ResourceGenerator:
#     @staticmethod
#     def generate_patient_event() -> Patient:
#         patient = resources.PatientGenerator()
#         patient_event = Patient(
#             id = patient.id,
#             name = patient.name,
#             gender = patient.gender,
#             birthDate = patient.birth_date,
#             multipleBirthInteger = patient.multiple_birth,
#             link = patient.patient_link
#         )
#         return patient_event

#     @staticmethod
#     def generate_practitioner_event(practitioner: Literal['dr', 'nrs', 'apt', 'lt']) -> Practitioner:
#         practicioner = resources.PracticionerGenerator(practitioner)
#         practitioner_event = Practitioner(
#             id = practicioner.id,
#             name = practicioner.name,
#             qualification = [practicioner.qualification],
#             gender= practicioner.gender,
#             birthDate= practicioner.birth_date
#         )
#         return practitioner_event
    
#     @staticmethod
#     def generate_organization(identifier=str(random.randrange(1000000, 9999999))) -> Organization:
#         organization = resources.OrganizationGenerator(identifier)
#         organization_event = Organization(
#             identifier=organization.identifier,
#             active=organization.active,
#             type=organization.type,
#             name=organization.name,
#             alias=organization.alias,
#             contact=organization.contact
#         )
#         return organization_event

#     @staticmethod
#     def generate_location(_building: Literal['B', 'R'],
#                           _status: str = "active"):
#         location = resources.LocationGenerator(building=_building)
#         location_event = Location(
#             id=location.id,
#             status=_status,
#             name=location.name,
#             form=location.form,
#             extension=location.extension
#         )
#         return location_event

#     @staticmethod
#     def generate_observation(date_of_birth: date, gender: str) -> list[BundleEntry]:
#         observation = resources.ObservationGenerator(age=date_of_birth, gender=gender)
#         return observation('001', '002', '10001', '10002', '10003')

#     def generate_bundle(self) -> Bundle:
#         patient = self.generate_patient_event()
#         practitioner = self.generate_practitioner_event('nrs')
#         observation = self.generate_observation(patient.birthDate, patient.gender)
#         _entry = [
#             BundleEntry(resource=patient, request={"method": "POST", "url": "Patient"}),
#             BundleEntry(resource=practitioner, request={"method": "POST", "url": "Practitioner"})
#         ]
#         _entry.extend(observation)
#         bundle = Bundle(
#             type='transaction',
#             entry=_entry
#             )
#         return bundle

class Cache:
    def __init__(self,temp_path: str,
                 data_path: str,
                 unique_buiding: list[str]):
        self.temp_path = Path(temp_path)
        self.data_path = Path(data_path)
        self.buildings = unique_buiding
        self.requirements = ['dr', 'nrs', 'apt', 'lt']
        self.open_file = {}
        self._create_role_cache()
    
    @staticmethod
    def get_prac_id(practitioner):
        if practitioner == 'dr':
            prac_id = 'DOC'
        elif practitioner == 'nrs':
            prac_id = 'NRS'
        elif practitioner == 'apt':
            prac_id = 'APT'
        elif practitioner == 'lt':
            prac_id = 'LT'
        else:
            error = f'{practitioner} is not within the scope!'
            raise ValueError (error)
        return prac_id

    def _create_practitioner_cache(self):
        for building in self.buildings:
            practitioners = {}
            role_id = []
            # Making a list of role IDs
            role_cache_path = self.temp_path / building / 'role.ndjson'
            if role_cache_path.exists():
                with open(role_cache_path, 'r') as file:
                    role_id = [json.loads(line)["practitioner"]["reference"][13:] for line in file]
            # Making Dicitonary
            practitioner_json_path = self.data_path / 'practitioner.ndjson'
            for practitioner in self.requirements:
                practitioner_list = []
                id_start = self.get_prac_id(practitioner)
                with jsonlines.open(practitioner_json_path) as reader:
                    for row in reader:
                        if row["id"] in role_id and row["id"].startswith(id_start):
                            practitioner_list.append(row)
                practitioners.update({practitioner: practitioner_list})
            # Making Pickle file
            practitioner_cache_path = self.temp_path / building / 'practitioner.pkl'
            with open(practitioner_cache_path, 'wb') as file:
                pickle.dump(practitioners, file)

    def _create_role_cache(self):
        try:
            for building in self.buildings:
                building_dir_path = self.temp_path / building
                if not building_dir_path.exists():
                    building_dir_path.mkdir(parents=True, exist_ok=True)
            role_json_path = self.data_path / 'practitioner_role.ndjson'
            with open(role_json_path, 'r') as file:
                for line in file:
                    role_building = json.loads(line)['location'][0]['display']
                    building_index = self.buildings.index(role_building)
                    role_cache = str(self.temp_path / self.buildings[building_index] / 'roles.ndjson')
                    if not role_cache in self.open_file:
                        self.open_file[role_cache] = open(role_cache, 'a')
                    if role_cache in self.open_file:
                        self.open_file[role_cache].write(line)
            for file in self.open_file.values():
                if not file.closed:
                    file.close()
        except FileNotFoundError:
            print(f"Directory for {self.temp_path} doesn't exist")
        except PermissionError:
            print(f"No write permission!")
        except TypeError as e:
            print(f"Serialization error: {e}")
        except OSError as e:
            print(f"OS error: {e}")
        finally:
            self.open_file.clear()
            self._create_practitioner_cache()


class GenerateHL7:
    @staticmethod
    def path_req_check(requirements: list, path: Path):
        """Make path for hospital data"""
        # Making folder if it doesn't exist
        try:
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            print(f"Cannot create directory {path}: {e}")
            return
        # Making .ndjson if it doesn't exist
        for i, resource in enumerate(requirements):
            try:
                if not resource.exists():
                    resource.parent.mkdir(parents=True, exist_ok=True)
                    resource.touch()
            except (PermissionError, OSError) as e:
                print(f"Cannot create resource {resource}: {e}")
                return
            except AttributeError:
                print(f"Item {i} in requirements is not a valid Path object")
                return

    @staticmethod
    def write_to_ndjson(path: Path, data: str):
        try:
            with open(path, 'a') as file:
                file.write(data)
                file.write('\n')
        except FileNotFoundError:
            print(f"Directory for {path} doesn't exist")
        except PermissionError:
            print(f"No write permission for {path}")
        except AttributeError:
            print("organization_event has no json() method or is None")
        except TypeError as e:
            print(f"Serialization error: {e}")
        except OSError as e:
            print(f"OS error: {e}")

    def __init__(self,
                 range_building: int,
                 range_room: int,
                 range_doctor: int,
                 range_nurse: int,
                 range_apt: int,
                 range_lt: int,
                 path: str = 'hospital_data'
                 ):
        self.path = path
        self.requirements = ['dr', 'nrs', 'apt', 'lt']
        self.range_building = range_building
        self.range_room = range_room
        self.range_doctor = range_doctor
        self.range_nurse = range_nurse
        self.range_apt = range_apt
        self.range_lt = range_lt

    # -- required function to call --
    def initial_hospital_data(self):
        path = Path(self.path)
        organization_path = path / "organization.ndjson"
        building_path = path / "building.ndjson"
        room_path = path / "rooms.ndjson"
        practitioner_path = path / "practitioner.ndjson"
        practitioner_role_path = path / "practitioner_role.ndjson"
        requirements = [organization_path,
                        building_path,
                        practitioner_path,
                        practitioner_role_path
                        ]
        # Making Paths and json 
        self.path_req_check(requirements, path)
        self.write_organization_data(organization_path)
        self.write_location_data(building_path, room_path)
        self.write_practitioner_data(practitioner_path, practitioner_role_path)

    def write_organization_data(self, organization_path):
        org_identifier = str(random.randint(1000000, 9999999))
        self.organization = resources.OrganizationGenerator(org_identifier)
        organization_event = Organization(
            identifier=self.organization.identifier,
            active=self.organization.active,
            type=self.organization.type,
            name=self.organization.name,
            alias=self.organization.alias,
            contact=self.organization.contact
        )
        self.write_to_ndjson(organization_path,
                             organization_event.json())

    @staticmethod
    def get_building(_range: int) -> list[str]:
        building = []
        for _building in range(_range):
            building.append(chr(65 + _building))
        return building

    @staticmethod
    def get_room(_range: int, _building: list[str]) -> dict[str, list[str]]:
        rooms = {}
        for building in _building:
            _room = []
            for room in range(_range):
                _room.append(chr(65 + room))
            rooms.update({building: _room})
        return rooms

    def write_location_data(self, location_path: Path, room_path: Path):
        buildings = self.get_building(self.range_building)
        rooms = self.get_room(self.range_room, buildings)
        for building in buildings:
            loc_building = resources.LocationGenerator('B', building)
            building_event = Location(
                id=loc_building.id,
                status="active",
                name=loc_building.name,
                form=loc_building.form,
                extension=loc_building.extension
            )
            self.write_to_ndjson(location_path,
                                 building_event.json())
        for building, rooms in rooms.items():
            for room in rooms:
                loc_room = resources.LocationGenerator('R', room)
                room_event = Location(
                    id=loc_room.id,
                    status="active",
                    name=loc_room.name,
                    form=loc_room.form,
                    extension=loc_room.extension,
                    partOf={"reference": f"Location/LOK-GEDUNG-{building}"}
                )
                self.write_to_ndjson(room_path,
                                     room_event.json())

    def get_practitioner_range(self, practitioner: str):
        _range = None
        if practitioner == "dr":
            _range = self.range_doctor
        elif practitioner == "nrs":
            _range = self.range_nurse
        elif practitioner == "apt":
            _range = self.range_apt
        elif practitioner == "lt":
            _range = self.range_lt
        else:
            error = f"{practitioner} is not within the scope of this chart!"
            raise AttributeError (error)
        return _range

    def write_practitioner_data(self,
                                practitioner_path: Path,
                                practitioner_role_path: Path):
        for building in range(self.range_building):
            for practitioner in self.requirements:
                practitioner_range = self.get_practitioner_range(practitioner)
                for _ in range(practitioner_range):
                    # Making Practitioners
                    practitioner_gen = resources.PracticionerGenerator(practitioner)
                    practitioner_event = Practitioner(
                        id = practitioner_gen.id,
                        name = practitioner_gen.name,
                        qualification = practitioner_gen.qualification,
                        gender= practitioner_gen.gender,
                        birthDate= practitioner_gen.birth_date
                    )
                    self.write_to_ndjson(practitioner_path,
                                        practitioner_event.json())
                    # Making Practitioner Roles
                    _building = chr(65 + building)
                    _location_dict = {"reference": f"Location/LOK-GED-{_building}",
                                        "display": f"Gedung {_building}"}
                    _practitioner_dict = {"reference": f"Practitioner/{practitioner_gen.id}",
                                        "display": practitioner_gen.name[0].text}
                    practitioner_role_event = PractitionerRole(practitioner=_practitioner_dict,
                                                                location=[_location_dict])
                    self.write_to_ndjson(practitioner_role_path,
                                            practitioner_role_event.json())

    def bundle_data(self):
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                buildings = self.get_building(self.range_building)
                building_names = [ 'Gedung ' + buildings[i] for i in range(len(buildings))]
                data = Cache(temp_dir, self.path, building_names)
                print("Cache made sucessfully!")
                while True:
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\nDeleting cache folder...")
        finally:
            print("\nRuntime finished")

if __name__ == '__main__':
    generate = GenerateHL7(range_building=2,
                           range_room=4,
                           range_doctor=2,
                           range_nurse=4,
                           range_apt=2,
                           range_lt=1)
    # generate.initial_hospital_data()
    generate.bundle_data()