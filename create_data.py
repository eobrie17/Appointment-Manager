
import pandas as pd
from faker import Faker

fake = Faker()

def create_medical_staff(num_records):
    staff_data = []
    for _ in range(num_records):
        staff_record = [
            fake.unique.random_number(digits=4),
            fake.first_name(),  
            fake.last_name(), 
            fake.random_element(["Doctor", "Nurse"]), 
            fake.random_element(["Family Medicine", "Psychiatry", "Internal Medicine", "Sports Medicine"]), 
            fake.email(), 
            fake.phone_number(),  
        ]
        staff_data.append(staff_record)
    return staff_data

def create_admin_staff(staff_list, num_records):
    for _ in range(num_records):
        staff_record = [
            fake.unique.random_number(digits=4),
            fake.first_name(),  
            fake.last_name(), 
            fake.random_element(["Admin", "Technician", "Lab Personnel"]), 
            "NaN",
            fake.email(),  
            fake.phone_number(), 
        ]
        staff_list.append(staff_record)
    return staff_list

def create_vermont_address():
    address = fake.address()
    while 'VT' not in address:
        address = fake.address()
    return address

def create_patients(num):
    patient_data = []
    for _ in range(num):
        patient_record = [
            fake.unique.random_number(digits=4),
            fake.first_name(),
            fake.last_name(),
            fake.date_of_birth(minimum_age=18, maximum_age=100).strftime('%Y-%m-%d'),
            fake.random_element(elements=('Male', 'Female')),
            create_vermont_address(),
            'VT',
            fake.phone_number(),
            fake.email(),
            fake.random_element(elements=('Blue Cross', 'Aetna', 'UnitedHealthcare', 'Cigna'))
        ]
        patient_data.append(patient_record)
    return patient_data


def main():
    headers = ["id", "first_name", "last_name", "role", "specialty", "email", "phone_number"]
    staff_data = create_medical_staff(15)
    staff_data = create_admin_staff(staff_data, 15)
    df = pd.DataFrame(staff_data, columns=headers)
    df.to_csv("staff.csv", index=False)

    headers2 = ["id", "first_name", "last_name", "date_of_birth", "gender", "address", "state", "phone_number", "email", "insurance"]
    patients = create_patients(300)
    df2 = pd.DataFrame(patients, columns=headers2)
    df2.to_csv("patients.csv", index=False)


main()
