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

from fhir.resources.patient import Patient
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

    @staticmethod
    def read_json_lines(file_path, building):
        with jsonlines.open(file_path, mode='r') as reader:
            for row in reader:
                yield row

    def _create_room_cache(self):
        try:
            for building in self.buildings:
                # Making Dicitonary
                room_json_path = self.data_path / 'rooms.ndjson'
                room_cache_path = self.temp_path / building / 'rooms.ndjson'
                with jsonlines.open(room_cache_path, mode='a') as writer:
                    with jsonlines.open(room_json_path) as reader:
                        for row in reader:
                            room_in_building = row['partOf']['reference'][-8:].replace('-', ' ').title()
                            if room_in_building == building:
                                writer.write(row)
        except FileNotFoundError:
            print(f"Directory for {self.temp_path} doesn't exist")
        except PermissionError:
            print(f"No write permission!")
        except TypeError as e:
            print(f"Serialization error: {e}")
        except OSError as e:
            print(f"OS error: {e}")

    def _create_practitioner_cache(self):
        try:
            for building in self.buildings:
                practitioners = {}
                role_id = []
                # Making a list of role IDs
                role_cache_path = self.temp_path / building / 'roles.ndjson'
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
        except FileNotFoundError:
            print(f"Directory for {self.temp_path} doesn't exist")
        except PermissionError:
            print(f"No write permission!")
        except TypeError as e:
            print(f"Serialization error: {e}")
        except OSError as e:
            print(f"OS error: {e}")
        finally:
            self._create_room_cache()

    def _create_role_cache(self):
        try:
            for building in self.buildings:
                building_dir_path = self.temp_path / building
                if not building_dir_path.exists():
                    building_dir_path.mkdir(parents=True, exist_ok=True)
            role_json_path = self.data_path / 'practitioner_role.ndjson'
            with jsonlines.open(role_json_path, mode='r') as reader:
                for row in reader:
                    role_building = row['location'][0]['display']
                    building_index = self.buildings.index(role_building)
                    role_cache = str(self.temp_path / self.buildings[building_index] / 'roles.ndjson')
                    if not role_cache in self.open_file:
                        self.open_file[role_cache] = jsonlines.open(role_cache, 'a')
                    self.open_file[role_cache].write(row)
            for file in self.open_file.values():
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

    def get_patient(self, patient):
        patient_event = Patient(
            id = patient.id,
            name = patient.name,
            gender = patient.gender,
            birthDate = patient.birth_date,
            multipleBirthInteger = patient.multiple_birth,
            link = patient.patient_link
        )
        return patient_event.dict()

    @staticmethod
    def get_practitioner_list(temp_path):
        '''Static Method for reading practitioner cache into a list'''
        practitioners_path = temp_path / 'practitioner.pkl'
        with open(practitioners_path, 'rb') as file:
            practitioner_dict = pickle.load(file)
            dr_list, nrs_list, apt_list, lt_list = [], [], [], []
            for key, value in practitioner_dict.items():
                if key == 'dr':
                    dr_list = value
                elif key == 'nrs':
                    nrs_list = value
                elif key == 'apt':
                    apt_list = value
                elif key == 'lt':
                    lt_list = value
                else:
                    error = f'Key {key} cannot be listed!'
                    raise AttributeError (error)
        return dr_list, nrs_list, apt_list, lt_list

    @staticmethod
    def get_room_list(temp_path) -> list[dict]:
        '''Static Method for reading rooms cache into a list'''
        rooms_path = temp_path / 'rooms.ndjson'
        with jsonlines.open(rooms_path, mode='r') as reader:
            rooms_list = list(reader)
        return rooms_list

    @staticmethod
    def get_role_list(temp_path) -> dict[str, str]:
        '''Static Method for reading roles cache into a hashmap'''
        roles_path = temp_path / 'roles.ndjson'
        roles_dict = {}
        with jsonlines.open(roles_path, mode='r') as reader:
            for row in reader:
                idx = row['practitioner']['reference'].index("/") 
                roles_dict.update({row['practitioner']['reference'][idx+1:] : row})
        return roles_dict

    @staticmethod
    def get_role_encounters(practitioner_encounters, roles_dict) -> list[dict]:
        role_encounters = []
        for practitioner in practitioner_encounters:
            practitioner_id = practitioner["id"]
            if practitioner_id in roles_dict:
                role_encounters.append(roles_dict[practitioner_id])
        return role_encounters

    def bundle_data(self, building_event):
        runtime_init = time.perf_counter()
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                #---Creating Cache---
                cache_time_init = time.perf_counter()
                buildings = self.get_building(self.range_building)
                building_names = [ 'Gedung ' + buildings[i] for i in range(len(buildings))]
                data = Cache(temp_dir, self.path, building_names)
                cache_time_end = time.perf_counter()
                print("Cache made sucessfully!")
                print(f"Elapsed Time: {cache_time_end - cache_time_init}")
                #---Creating Bundle---
                temp_path = Path(temp_dir) / building_event
                # Getting practitioners
                dr_list, nrs_list, apt_list, lt_list = self.get_practitioner_list(temp_path)
                # Getting location
                rooms_list = self.get_room_list(temp_path)
                # Getting roles
                roles_dict = self.get_role_list(temp_path)
                while True:
                    # Getting Patient
                    patient = resources.PatientGenerator()
                    patient_event = self.get_patient(patient)
                    patient_state = random.choice(["diabetic", "normal"]) 
                    # Getting random practitioners
                    practitioner_encounters = []
                    dr_event = random.choice(dr_list)
                    practitioner_encounters.append(dr_event)
                    nrs_event = random.choice(nrs_list)
                    practitioner_encounters.append(nrs_event)
                    lt_event = random.choice(lt_list)
                    practitioner_encounters.append(lt_event)
                    # Getting location event
                    room_encounter = random.choice(rooms_list)
                    role_encounters = self.get_role_encounters(practitioner_encounters, roles_dict)
                    encounter = resources.EncounterGenerator(subject=patient_event,
                                                             practitioner=practitioner_encounters,
                                                             location_building=building_event,
                                                             location_room=room_encounter)
                    encounter_event = encounter.generate_encounter()
                    observation = resources.ObservationGenerator(patient.birth_date,
                                                                 patient.gender,
                                                                 patient_state)
                    observation_event = observation(patient_event,
                                                    encounter_event,
                                                    dr_event,
                                                    nrs_event,
                                                    lt_event)
                    bundle_payload = self.get_bundle(patient_event,
                                                     practitioner_encounters,
                                                     role_encounters,
                                                     encounter_event,
                                                     )
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\nDeleting cache folder...")
        except Exception as e:
            runtime_end = time.perf_counter()
            print(f"Error has occured: {e}")
            print(f"Elapsed runtime: {runtime_end - runtime_init}")
        finally:
            print("\nRuntime finished")

if __name__ == '__main__':
    generate = GenerateHL7(range_building=2,
                           range_room=4,
                           range_doctor=2,
                           range_nurse=4,
                           range_apt=2,
                           range_lt=1)
    #generate.initial_hospital_data()
    generate.bundle_data('Gedung A')