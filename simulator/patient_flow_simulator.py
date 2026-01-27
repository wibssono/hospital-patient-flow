import json
import os
import random
import uuid
import time
import re
from faker import Faker
from datetime import timedelta, datetime
from dotenv import load_dotenv

#Load environment variables from config/settings.env
#load_dotenv(dotenv_path="config/settings.env")

# Departments in hospital
departments = ["Emergency", "Surgery", "ICU", "Pediatrics", "Maternity", "Oncology", "Cardiology"]

# Gender categories 
genders = ["Male", "Female"]

fake = Faker('id_ID')

def get_name(gender:str) -> str:
    if gender == "Male":
        name = fake.name_male()
    else:
        name = fake.name_female()
    return name

def get_age(name:str) -> int:
    pattern = r"\b(Dr\.|dr\.|Hj\.|Ir\.|S\.|M\.)(?!\S)"
    if re.search(pattern, name):
        age = random.randint(21, 100)
    else:
        age = random.randint(0, 100)
    return age

def generate_patient_event() -> dict:
    admission_time = datetime.utcnow() - timedelta(hours=random.randint(0, 72))
    discharge_time = admission_time + timedelta(hours=random.randint(1, 72))

    gender = random.choice(genders)
    name = get_name(gender)
    age = get_age(name)

    event = {
        "patient_id": str(uuid.uuid4()),
        "gender": gender,
        "name": name,
        "age": age,
        "department": random.choice(departments),
        "admission_time": admission_time.isoformat(),
        "discharge_time": discharge_time.isoformat(),
        "bed_id": random.randint(1, 500),
        "hospital_id": random.randint(1, 7)  # Assuming 7 hospitals in network
    }

    return event

if __name__ == "__main__":
    while True:
        time.sleep(1)
        print(generate_patient_event())