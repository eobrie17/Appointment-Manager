import pandas as pd
import random
from datetime import datetime

def replace_with_real_patient(patient_ids):
    random.shuffle(patient_ids)
    return patient_ids.pop()

def load_patients():
    patients = pd.read_csv('patients.csv')
    return patients['id'].tolist()

def load_medical_staff():
    staff = pd.read_csv('staff.csv')
    staff_ids = []
    for _, row in staff.iterrows():
        if row['role'].lower() in ['nurse', 'doctor']:
            staff_ids.append(row['id'])
    return staff_ids

def add_medical_staff(staff_ids):
    return random.choice(staff_ids)

def create_appt_time():
    # pick random day in dec (31 days)
    random_day = random.randint(1, 31) 
    # pick random hour between 8am and 5pm
    random_hour = random.randint(8, 17) 
    random_date = datetime(2023, 12, random_day, random_hour)
    formatted_date = random_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    return formatted_date

def clean_appointments():
    appointments = pd.read_csv('appointments_dirty.csv')

    # drop unnecessary columns- (drop all medical data -- should be in records)
    appointments = appointments.drop(['Gender', 'Age', 'Hipertension', 'Diabetes', 'Alcoholism', 'Handcap',
                                      'Neighbourhood', 'Scholarship', 'No-show'], axis=1)

    # rename all columns to follow the same conventions
    appointments = appointments.rename(columns={
        'AppointmentID': 'id',
        'PatientId': 'patient_id',
        'ScheduledDay': 'scheduled_day',
        'AppointmentDay': 'appointment_day',
        'SMS_received': 'text_received'
    })

    # generate unique 4 digit id
    appointments['id'] = range(1, len(appointments) + 1)
    appointments['id'] = appointments['id'].apply(lambda x: '{:04d}'.format(x))

    #assign patient_id col to actual people from patients 
    patient_ids = load_patients()
    appointments['patient_id'] = appointments['patient_id'].apply(
        lambda x: replace_with_real_patient(patient_ids)
    )

    #add a staff_id to appointment to show who will be attending
    staff_ids = load_medical_staff()
    appointments['staff_id'] = ''
    appointments['staff_id']=appointments['staff_id'].apply(lambda x: add_medical_staff(staff_ids))

    #make appointment times different days and hours
    appointments['appointment_day']=appointments['appointment_day'].apply(lambda x: create_appt_time())

    appointments.to_csv('appointments.csv', index=False)

def clean_records():
    records = pd.read_csv('records_dirty.csv')

    # Reshape data
    records_reshaped = records.pivot_table(index=['DATE', 'PATIENT', 'ENCOUNTER'],
                                           columns='DESCRIPTION',
                                           values='VALUE',
                                           aggfunc='first').reset_index()

    # rename columns to follow same conventions
    records_reshaped = records_reshaped.drop(['ENCOUNTER'], axis=1)
    records_reshaped = records_reshaped.rename(columns={
        'DATE': 'date',
        'PATIENT': 'patient_id',
        'Are you covered by health insurance or some other kind of health care plan [PhenX]': 'insurance',
        'Abuse Status [OMAHA]': 'abuse_status'
    })
    records_reshaped.columns = records_reshaped.columns.str.replace(' ', '_')
    records_reshaped.columns = records_reshaped.columns.str.lower()

    #too many columns - drop unnecessary 
    cols_to_drop = ["insurance","carbon_dioxide","low_density_lipoprotein_cholesterol","calcium","carbon_dioxide","chloride","creatinine","dxa_[t-score]_bone_density","estimated_glomerular_filtration_rate","hiv_status","hemoglobin_a1c/hemoglobin.total_in_blood","high_density_lipoprotein_cholesterol","history_of_hospitalizations+​outpatient_visits","microalbumin_creatinine_ratio","oral_temperature", "potassium", "sexual_orientation", "triglycerides", "urea_nitrogen"]
    records_reshaped = records_reshaped.drop(cols_to_drop, axis=1)

    #make more data entries so every patient has a record
    more_data = records_reshaped.sample(n=254, replace=True)
    records_reshaped = pd.concat([records_reshaped, more_data])

    # assign patient_id col to actual people from patients 
    patient_ids = load_patients()
    records_reshaped['patient_id'] = records_reshaped['patient_id'].apply(
        lambda x: replace_with_real_patient(patient_ids)
    )

    # generate unique 4 digit id
    records_reshaped['id'] = range(1, len(records_reshaped) + 1)
    records_reshaped['id'] = records_reshaped['id'].apply(lambda x: '{:04d}'.format(x))

    records_reshaped.to_csv('records.csv', index=False)

def main():
    clean_appointments()
    clean_records()

main()