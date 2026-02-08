import generator
from resources import time

if __name__ == "__main__":
    print("Which FHIR resource do you want to generate?")
    print("1. Patient")
    print("2. Practitioner")
    choice = input("Enter 1 or 2: ")
    while True:
        patient = generator.generate_patient_event()
        print(patient.json(indent=2))
        time.sleep(1)