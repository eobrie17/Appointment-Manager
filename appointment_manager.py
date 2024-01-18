import sqlite3
import pandas as pd
from tabulate import tabulate
from datetime import datetime
import math
import seaborn as sns
import matplotlib.pyplot as plt
import re

def login(password):
    user_password = input("Enter hospital password: ")
    if str(user_password )== password:
        return True
    else:
        print("Incorrect hospital password. Try again.")
        return False
    
def start_menu(con, cur):
    print("Choose an option:")
    print(" 1) Appointments")
    print(" 2) Patients")
    print(" 3) Staff")
    print(" 4) Records")
    print(" 5) Log out")
    action = input("Enter choice => ")
    if action == '1':
        appointments_options(con, cur)
    elif action == '2':
        patients_options(con, cur)
    elif action == '3':
        staff_options(con, cur)
    elif action == '4':
        records_options(con, cur)
    elif action == '5':
        log_out(con)
    else:
        print('Please enter a valid response \n')
    return action

def appointments_options(con, cur):
    print("What would you like to do:")
    print(" 1) See upcoming appointments")
    print(" 2) Schedule new appointment")
    print(" 3) Cancel an appointment")
    print(" 4) Edit an appointment")
    print(" 5) Go back to main menu")
    action = input("Enter choice => ")
    if action == '1':
        display_appointments(con, cur)
    elif action == '2':
        schedule_appointment(con, cur)
    elif action == '3':
        cancel_appointment(con, cur)
    elif action == '4':
        edit_appointment(con, cur)
    elif action == '5':
        return
    else:
        print('Please enter a valid response \n')
    return action

def get_new_id(cur, table):
    #create a new unique id
    cur.execute(f"SELECT id FROM {table}")
    ids = cur.fetchall()
    max_value = max(ids, key=lambda x: x[0])
    return max_value[0] + 1

def check_patient_existence(con, cur, first_name, last_name, dob):
    cur.execute("SELECT id, first_name, last_name, date_of_birth FROM patients")
    patient_info = cur.fetchall()
    for patient in patient_info:
        if patient[1] == str(first_name) and patient[2] == str(last_name) and patient[3] == str(dob):
            print("Patient found")
            p_id = patient[0]
            return True, p_id
    return False, -1

def check_staff_existence(con, cur, first_name, last_name):
    cur.execute("SELECT id, first_name, last_name FROM staff")
    staff_info = cur.fetchall()
    for person in staff_info:
        if person[1] == str(first_name) and person[2] == str(last_name):
            print("Staff member found")
            s_id = person[0]
            return True, s_id
    return False, -1

def check_record_existence(con, cur, p_id):
    cur.execute("SELECT patient_id FROM records")
    patient_ids = cur.fetchall()
    for patient in patient_ids:
        if str(patient[0]) == str(p_id):
            print("Patient's records found")
            return True  
    return False

def check_date_format(date_str, in_future):
    pattern = r'\d{2}-\d{2}-\d{4}'
    if re.search(pattern, date_str):
        parts = date_str.split('-')
        converted_date = f"{parts[2]}-{parts[0]}-{parts[1]}"
        if in_future:
            today = datetime.now().strftime('%Y-%m-%d')
            if not converted_date > today:
                print("Please enter a date in the future.")
                return ''
        return converted_date
    else:
        print("Please enter a date with the format YYYY-MM-DD.")
        return ''
    
def format_date_for_db(date, time):
    date_pieces = date.split('-')
    appointment_datetime = datetime(int(date_pieces[0]), int(date_pieces[1]), int(date_pieces[2]), int(time))
    return appointment_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')

def check_time_format(time_str):
    time_str = str(time_str).strip().lower()
    if time_str[:-2].isdigit() and time_str[-2:] in ['am', 'pm'] and len(time_str) >= 3:
        hour = int(time_str[:-2])
        if time_str[-2:] == 'pm' and hour != 12:
            hour += 12
        elif time_str[-2:] == 'am' and hour == 12:
            hour = 0
        if 8 <= hour <= 17:
            return hour
    print("Invalid. Please enter time between 8am to 5pm in a format like this '9am'.")
    return ''

def display_appointments(con, cur):
    cur.execute("SELECT strftime('%Y-%m-%dT%H:%M:%SZ', 'now')")
    formatted_current_time = cur.fetchone()[0]

    # get appointments after the current time
    cur.execute('''
        SELECT patients.first_name, patients.last_name, appointment_day, staff.first_name, staff.last_name
        FROM appointments 
        JOIN patients ON appointments.patient_id = patients.id
        JOIN staff ON appointments.staff_id = staff.id
        WHERE appointments.appointment_day > ?
        ORDER BY appointments.appointment_day
    ''', (formatted_current_time,))
    appt_info = cur.fetchall()

    print("Here are the next 15 appointments:")
    
    # make appointment info into table format
    formatted_appts = []
    for appt in appt_info:
        date_time = pd.to_datetime(appt[2])
        formatted_date = date_time.strftime('%B %d, %Y at %I:%M %p')
        formatted_appts.append([formatted_date, f"{appt[0]} {appt[1]}", f"{appt[3]} {appt[4]}"])
    headers = ["Date and Time", "Patient", "Staff"]
    table = tabulate(formatted_appts[:15], headers=headers, tablefmt="grid")
    print(table)
    
def schedule_appointment(con, cur):
    print("Please enter the following info...")
    p_first=''
    p_last=''
    while len(p_first)==0 or len(p_last)==0:
        p_first = input("Enter patient first name: ")
        p_last = input("Enter patient last name: ")
    p_birthday=''
    while p_birthday=='':
        p_birthday = input("Patient date of birth (MM-DD-YYYY): ")
        p_birthday = check_date_format(p_birthday, False)
    day=''
    while day=='':
        day = input("Date of new appointment (MM-DD-YYYY): ")
        day = check_date_format(day, True)
    time=''
    while time=='': 
        time = input("Time of new appointment (8am - 5pm): ")
        time = check_time_format(time)
    s_first=''
    s_last=''
    while len(s_first)==0 or len(s_last)==0:
        s_first = input("Enter staff member first name: ")
        s_last = input("Enter staff member last name: ")

    appointment_time = format_date_for_db(day, time)

    p_exists, p_id = check_patient_existence(con, cur, p_first, p_last, p_birthday)
    if not p_exists:
        print("Patient not found. Please try again")
        return

    #get staff id from staff name
    s_exists, s_id = check_staff_existence(con, cur, s_first, s_last)
    if not s_exists:
        print("Staff member not found. Please try again.")
        schedule_appointment(con, cur)

    #get the scheduled date
    cur.execute("SELECT strftime('%Y-%m-%dT%H:%M:%SZ', 'now')")
    scheduled_time = cur.fetchone()[0]

    new_id = get_new_id(cur, 'appointments')
    #ADD APPT
    add= '''INSERT INTO appointments (id, patient_id, scheduled_day, appointment_day, text_received, staff_id) VALUES (?, ?, ?, ?, ?, ?)'''
    cur.execute(add, (new_id, p_id, scheduled_time, appointment_time, 0, s_id))
    con.commit()
    print('Appointment scheduled!')

def cancel_appointment(con, cur):
    #cancel from name, day of appointment
    date=''
    while date=='':
        date = input("Please enter the date of the appointment to cancel (MM-DD-YYYY): ")
        date = check_date_format(date, True)
    time=''
    while time=='': 
        time = input("Please enter the time of the appointment (8am - 5pm): ")
        time = check_time_format(time)
    f_name=''
    l_name=''
    while len(f_name)==0 or len(l_name)==0:
        f_name = input("Enter patient first name: ")
        l_name = input("Enter patient last name: ")

    #format the date like in the table
    appointment_time = format_date_for_db(date, time)

    cur.execute('''SELECT first_name, last_name, appointment_day, appointments.id 
                FROM appointments JOIN patients ON appointments.patient_id = patients.id''')
    all_appointments = cur.fetchall()

    for appointment in all_appointments:
        if appointment[0] == f_name and appointment[1] == l_name and appointment[2] == appointment_time:
            #found the appointment
            appt_id = appointment[3]
            cur.execute(f'''DELETE FROM appointments WHERE id = {appt_id}''')
            con.commit()
            print("Appointment cancelled!")

def edit_appointment(con, cur):
    date=''
    while date=='':
        date = input("Please enter the date of the appointment to change (MM-DD-YYYY): ")
        date = check_date_format(date, True)
    time=''
    while time=='': 
        time = input("Please enter the time of the appointment (8am - 5pm): ")
        time = check_time_format(time)
    f_name=''
    l_name=''
    while len(f_name)==0 or len(l_name)==0:
        f_name = input("Enter patient first name: ")
        l_name = input("Enter patient last name: ")

    appointment_time = format_date_for_db(date, time)

    cur.execute('''SELECT first_name, last_name, appointment_day, appointments.id 
                FROM appointments JOIN patients ON appointments.patient_id = patients.id''')
    all_appointments = cur.fetchall()

    found = False
    for appointment in all_appointments:
        if appointment[0] == f_name and appointment[1] == l_name and appointment[2] == appointment_time:
            #found the appointment
            a_id = appointment[3]
            print("Found appointment: ")
            found=True
            date_object = datetime.strptime(appointment[2], "%Y-%m-%dT%H:%M:%SZ")
            appointment_date = date_object.strftime("%B %d, %Y")
            print(f"Appointment on {appointment_date} for {appointment[0]} {appointment[1]}")
    if not found:
        print("We could not find this appointment. Please try again.")
        return
    check = input ("Is this the appointment to change? Enter Y or N: ")
    if check == 'Y' or check == 'y':
        column_to_edit = input("Would you like to change the date or time? Enter 'Date' or 'Time': ")

        while column_to_edit != 'Date' and column_to_edit != 'date' and column_to_edit != 'Time' and column_to_edit != 'time':
            print("Invalid entry. Please enter 'Date' or 'Time'.")
        if column_to_edit == 'Date' or column_to_edit == 'date':
            new_date = ''
            while new_date=='':
                new_date = input("What date would you like to move the appointment to (MM-DD-YYYY): ")
                new_date = check_date_format(new_date, True)
            new_date_formatted = format_date_for_db(new_date, time)
            print(new_date_formatted)
            edit = f"UPDATE appointments SET appointment_day = '{new_date_formatted}' WHERE appointments.id = '{a_id}'"
            cur.execute(edit)
            con.commit()
            print("Appointment changed!")
        elif column_to_edit == 'Time' or column_to_edit == 'time':
            new_time=''
            while new_time=='': 
                new_time = input("What time would you like to move the appointment to (8am-5pm): ")
                new_time = check_time_format(new_time)
            new_date_formatted = format_date_for_db(date, new_time)
            print(new_date_formatted)
            edit = f"UPDATE appointments SET appointment_day = '{new_date_formatted}' WHERE appointments.id = '{a_id}'"
            cur.execute(edit)
            con.commit()
            print("Appointment changed!")
        else:
            print("Something went wrong.")

    else: 
        print("Please try to find your appointment again.")
        return


def patients_options(con, cur):
    print("What would you like to do:")
    print(" 1) Add new patient to the practice")
    print(" 2) Edit patient info")
    print(" 3) Remove patient from practice")
    print(" 4) Go back to main menu")
    action = input("Enter choice => ")
    if action == '1':
        add_patient(con, cur)
    elif action == '2':
        edit_patient(con, cur)
    elif action == '3':
        remove_patient(con, cur)
    elif action == '4':
        return
    else:
        print('Please enter a valid response \n')
    return action

def add_patient(con, cur):
    f_name=''
    l_name=''
    while len(f_name)==0 or len(l_name)==0:
        f_name = input("Enter patient first name: ")
        l_name = input("Enter patient last name: ")
    dob=''
    while dob=='':
        dob = input("Patient date of birth (MM-DD-YYYY): ")
        dob = check_date_format(dob, False)
    #these variables can be null
    gender = input("Enter patient gender: ")
    address = input("Enter patient address: ")
    state = input("Enter patient state: ")
    number = input("Enter patient phone number: ")
    email = input("Enter patient email: ")
    insurance = input("Enter patient insurance: ")

    # process the potentially empty strings to None so they will be null in the table
    gender = gender if gender else None
    address = address if address else None
    state = state if state else None
    number = number if number else None
    email = email if email else None
    insurance = insurance if insurance else None

    new_id = get_new_id(cur, 'patients')

    #ADD PATIENT
    add= '''INSERT INTO patients (id, first_name, last_name, date_of_birth, gender, address, state, phone_number, email, insurance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    cur.execute(add, (new_id, f_name, l_name, dob, gender, address, state, number, email, insurance))
    con.commit()
    print('Patient added to the practice!')


def edit_patient(con, cur):
    print("Here is the patient information you can update...")
    cur.execute("PRAGMA table_info(patients)")
    columns = cur.fetchall()
    column_names = [col[1] for col in columns]
    for i in range(4, len(column_names)):
        print(column_names[i])
    f_name=''
    l_name=''
    while len(f_name)==0 or len(l_name)==0:
        f_name = input("Enter the first name of the patient whose info you want to edit: ")
        l_name = input("Enter the patient's last name: ")
    dob=''
    while dob=='':
        dob = input("Patient date of birth (MM-DD-YYYY): ")
        dob = check_date_format(dob, False)

    #check if this patient exists
    exists, p_id = check_patient_existence(con, cur, f_name, l_name, dob)
    if not exists:
        print("Cannot find patient. Please try again.")
        return

    while True:
        update_col = input("Enter the column you want to change: ")
        if update_col in column_names:
            break
        else:
            print("Please enter a valid column name")
    #TODO - input val on this 
    new_info = input('Enter new information: ')

    update = f"UPDATE patients SET {update_col} = ? WHERE id = ?"
    cur.execute(update, (new_info, p_id))
    con.commit()
    print('Patient info updated!')

def remove_patient(con, cur):
    #this will also remove their records
    f_name=''
    l_name=''
    while len(f_name)==0 or len(l_name)==0:
        f_name = input("Enter the first name of the patient to remove: ")
        l_name = input("Enter the last name of the patient: ")
    dob=''
    while dob=='':
        dob = input("Patient date of birth (MM-DD-YYYY): ")
        dob = check_date_format(dob, False)

    exists, p_id = check_patient_existence(con, cur, f_name, l_name, dob)
    if not exists:
        print("Patient not found. Please try again.")
    else:
        cur.execute(f'''DELETE FROM patients WHERE id = {p_id}''')
        cur.execute(f'''DELETE FROM records WHERE patient_id = {p_id}''')
        con.commit()
        print("Patient removed!")

def staff_options(con, cur):
    print("What would you like to do:")
    print(" 1) Add new employee to the practice")
    print(" 2) Edit employee info")
    print(" 3) Remove employee from practice")
    print(" 4) Go back to main menu")
    action = input("Enter choice => ")
    if action == '1':
        add_employee(con, cur)
    elif action == '2':
        edit_employee(con, cur)
    elif action == '3':
        remove_employee(con, cur)
    elif action == '4':
        return
    else:
        print('Please enter a valid response \n')
    return action

def add_employee(con, cur):
    f_name=''
    l_name=''
    while len(f_name)==0 or len(l_name)==0:
        f_name = input("Enter new employee's first name: ")
        l_name = input("Enter the last name: ")
    
    role = input("Enter the employee's role: ")
    specialty = input("Enter the employee's specialty (or skip): ")
    email = input("Enter the employee's email: ")
    phone = input("Enter the employee's phone number: ")

    #make sure any unknown info goes into the table as null
    role = role if role else None
    specialty = specialty if specialty else None
    email = email if email else None
    phone = phone if phone else None

    new_id = get_new_id(cur, 'staff')

    #ADD staff member
    add= '''INSERT INTO staff (id, first_name, last_name, role, specialty, email, phone_number) VALUES (?, ?, ?, ?, ?, ?, ?)'''
    cur.execute(add, (new_id, f_name, l_name, role, specialty, email, phone))
    con.commit()
    print('New employee added to the practice!')

def edit_employee(con, cur):
    print("Here is the employee information you can update...")
    cur.execute("PRAGMA table_info(staff)")
    columns = cur.fetchall()
    column_names = [col[1] for col in columns]
    for i in range(3, len(column_names)):
        print(column_names[i])
    f_name=''
    l_name=''
    while len(f_name)==0 or len(l_name)==0:
        f_name = input("Enter the first name of the employee you want to edit: ")
        l_name = input("Enter the employee's last name: ")
    
    #check if this employee exists
    exists, s_id = check_staff_existence(con, cur, f_name, l_name)
    if not exists:
        print("Cannot find staff member. Please try again.")
        return

    while True:
        update_col = input("Enter the column you want to change: ")
        if update_col in column_names:
            break
        else:
            print("Please enter a valid column name \n")

    new_info = input('Enter new information: ')
    #make sure if empty it goes into the table as null
    new_info = new_info if new_info else None

    update = f"UPDATE staff SET {update_col} = ? WHERE id = ?"
    cur.execute(update, (new_info, s_id))
    con.commit()
    print('Employee info updated!')

def remove_employee(con, cur):
    f_name=''
    l_name=''
    while len(f_name)==0 or len(l_name)==0:
        f_name = input("Enter the first name of the employee to remove: ")
        l_name = input("Enter the last name of the employee: ")

    exists, s_id = check_staff_existence(con, cur, f_name, l_name)
    if not exists:
        print("Employee not found. Please try again.")
    else:
        cur.execute(f'''DELETE FROM staff WHERE id = {s_id}''')
        con.commit()
        print("Staff member removed!")

def records_options(con, cur):
    print("What would you like to do:")
    print(" 1) Add new medical record")
    print(" 2) Edit a medical record")
    print(" 3) Get hospital statistics")
    print(" 4) Visualize hospital health")
    print(" 5) Visualize health of patient")
    print(" 6) Go back to main menu")
    action = input("Enter choice => ")
    if action == '1':
        add_record(con, cur)
    elif action == '2':
        edit_record(con, cur)
    elif action == '3':
        hospital_statistics(con, cur)
    elif action == '4':
        visualize_hospital_health(con, cur)
    elif action == '5':
        visualize_patient_health(con, cur)
    else:
        print('Please enter a valid response \n')
    return action

def add_record(con, cur):
    f_name=''
    l_name=''
    while len(f_name)==0 or len(l_name)==0:
        f_name = input("Enter the first name of the patient who you are adding a record: ")
        l_name = input("Enter the last name of the patient: ")
    
    dob=''
    while dob=='':
        dob = input("Patient date of birth (MM-DD-YYYY): ")
        dob = check_date_format(dob, False)

    exists, p_id = check_patient_existence(con, cur, f_name, l_name, dob)
    if not exists:
        print("Patient not found. Please try again.")
    else:
        new_id = get_new_id(cur, 'records')
        #get the date
        cur.execute("SELECT strftime('%Y-%m-%dT%H:%M:%SZ', 'now')")
        current_date = cur.fetchone()[0]

        print("Please fill in all known info and skip the rest...")
        abuse = input("Enter abuse status: ")
        height = input("Enter height in cm: ")
        bmi = input("Enter body mass index: ")
        weight= input("Enter weight in lbs: ")
        d_pressure = input("Enter diastolic blood pressure: ")
        s_pressure = input("Enter systolic blood pressure: ")
        glucose = input("Enter glucose level: " )
        sodium= input("Enter sodium level: ")
        cholesterol = input("Enter cholesterol: ")
        housing_status = input("Enter housing status: ")

        #if any of these are empty, make sure they go into the table as null
        abuse = abuse if abuse else None
        height = height if height else None
        bmi = bmi if bmi else None
        weight = weight if weight else None
        d_pressure = d_pressure if d_pressure else None
        s_pressure = s_pressure if s_pressure else None
        glucose = glucose if glucose else None
        sodium = sodium if sodium else None
        cholesterol = cholesterol if cholesterol else None
        housing_status = housing_status if housing_status else None

        #add patient record
        add= '''INSERT INTO records (id, date, patient_id, abuse_status, body_height, body_mass_index, body_weight, diastolic_blood_pressure, glucose, housing_status, sodium, systolic_blood_pressure, total_cholesterol) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        cur.execute(add, (new_id, current_date, p_id, abuse, height, bmi, weight, d_pressure, glucose, housing_status, sodium, s_pressure, cholesterol))
        con.commit()
        print('New patient record added!')

def edit_record(con, cur):
    print("Here is the patient record information you can update...")
    cur.execute("PRAGMA table_info(staff)")
    columns = cur.fetchall()
    column_names = [col[1] for col in columns]
    for i in range(2, len(column_names)):
        print(column_names[i])
    f_name=''
    l_name=''
    while len(f_name)==0 or len(l_name)==0:
        f_name = input("Enter the first name of the patient whose records you are updating: ")
        l_name = input("Enter the last name of the patient: ")
    
    dob=''
    while dob=='':
        dob = input("Patient date of birth (MM-DD-YYYY): ")
        dob = check_date_format(dob, False)

    exists, p_id = check_patient_existence(con, cur, f_name, l_name, dob)
    if not exists:
        print("Patient not found. Please try again.")
        return

    while True:
        update_col = input("Enter the column you want to change: ")
        if update_col in column_names:
            break
        else:
            print("Please enter a valid column name \n")
    #TODO - input val on this 
    new_info = input('Enter new information: ')

    update = f"UPDATE record SET {update_col} = ? WHERE patient_id = ?"
    cur.execute(update, (new_info, p_id))
    con.commit()
    print('Patient record updated!')

def hospital_statistics(con, cur):
    print("Please choose a column to learn more about the health of the patients in this practice...")
    cur.execute("PRAGMA table_info(records)")
    columns = cur.fetchall()
    column_names = [col[1] for col in columns]
    for i in range(3, len(column_names)-1):
        if column_names[i] != 'glucose' and column_names[i] != 'sodium' and column_names[i] != 'total_cholesterol' and column_names[i] != 'housing_status':
            print(column_names[i])
    while True:
        chosen_col = input("Enter the column to see a statistical summary: ")
        if chosen_col in column_names:
            break
        else:
            print("Please enter a valid column name \n")
    if chosen_col == 'housing_status' or chosen_col == 'abuse_status':
        #just do a count if categorical data
        cur.execute(f"SELECT {chosen_col}, SUM({chosen_col}) AS counts FROM records GROUP BY {chosen_col}")
        data = cur.fetchall()
        for row in data:
            print(f"Category: {row[0]}, Total Value: {row[1]}")
    else:
        cur.execute(f'''SELECT AVG({chosen_col}) FROM records''')
        avg = cur.fetchall()[0]

        cur.execute(f'''SELECT MIN({chosen_col}) FROM records''')
        min = cur.fetchall()[0]

        cur.execute(f'''SELECT MAX({chosen_col}) FROM records''')
        max = cur.fetchall()[0]

        #median
        cur.execute(f'''SELECT {chosen_col} FROM records''')
        data = cur.fetchall()[0]
        sorted_nums = sorted([row for row in data if row is not None])
        length = len(sorted_nums)
        if length % 2 == 0:
            median = (sorted_nums[length // 2 - 1] + sorted_nums[length // 2]) / 2
        else:
            median = sorted_nums[length // 2]
        #std
        squared = [(row - avg[0]) ** 2 for row in data]
        variance = sum(squared) / len(data)
        std = math.sqrt(variance)
        #display statistical summary
        summary = [
            ["Average", "{:.2f}".format(avg[0])],
            ["Max", "{:.2f}".format(max[0])],
            ["Min", "{:.2f}".format(min[0])],
            ["Median", "{:.2f}".format(median)],
            ["Standard Deviation", "{:.2f}".format(std)]
        ]
        table = tabulate(summary, headers=["Statistic", "Value"], tablefmt="grid")
        print(table)

def visualize_hospital_health(con, cur):
    #histogram of a health attribute
    print("Here are some different health attributes...")
    cur.execute("PRAGMA table_info(records)")
    columns = cur.fetchall()
    column_names = [col[1] for col in columns]
    for i in range(3, len(column_names)-1):
        if column_names[i] != 'housing_status':
            print(column_names[i])
    while True:
        chosen_col = input("Enter an attribute to see it's distribution: ")
        if chosen_col == 'abuse_status' or chosen_col == 'housing_status':
            print("Sorry, this attribute cannot be shown as a histogram.")
            return
        elif chosen_col in column_names:
            break
        else:
            print("Please enter a valid column name \n")

    df = pd.read_sql_query(f"SELECT {chosen_col} FROM records", con)
    #graph
    sns.histplot(data=df, x=f"{chosen_col}")
    plt.title(f"Histogram of {chosen_col}")
    plt.xlabel(f"{chosen_col}")
    plt.ylabel('Number of Patients')
    plt.show()

def visualize_patient_health(con, cur):
    #bar plot of patient health next to bar with the average
    print("Which patient's health would you like to visualize?")
    f_name=''
    l_name=''
    while len(f_name)==0 or len(l_name)==0:
        f_name = input("Enter patient first name: ")
        l_name = input("Enter patient last name: ")
    dob=''
    while dob=='':
        dob = input("Enter patient date of birth (MM-DD-YYYY): ")
        dob = check_date_format(dob, False)
    patient_exists, p_id = check_patient_existence(con, cur, f_name, l_name, dob)
    if not patient_exists:
        print("Patient not found. Please try again.")
        return
    else: 
        record_exists = check_record_existence(con, cur, p_id)
        if not record_exists:
            return
        else:

            cur.execute(f'''SELECT AVG(body_height), AVG(body_mass_index), AVG(body_weight), AVG(diastolic_blood_pressure), 
                        AVG(systolic_blood_pressure), AVG(glucose), AVG(total_cholesterol), AVG(sodium)
                        FROM records JOIN patients ON patients.id = records.patient_id ''')
            average_data = cur.fetchall()

            cur.execute(f'''SELECT body_height, body_mass_index, body_weight, diastolic_blood_pressure, systolic_blood_pressure, glucose, total_cholesterol, sodium
                        FROM records JOIN patients ON records.patient_id=patients.id WHERE patients.id = {p_id}''')
            patient_data = cur.fetchall()

            headers = ['body_height', 'body_mass_index', 'body_weight', 'diastolic_blood_pressure', 
                    ' systolic_blood_pressure', 'glucose', 'total_cholesterol', 'sodium']
            
            average_data_list = list(average_data[0])
            patient_data_list = list(patient_data[0])

            # Create DataFrame for easier plotting
            data = pd.DataFrame({'Category': headers, 'Average Score': average_data_list, 'Individual Score': patient_data_list})
            data= data.dropna()
            
            combined_data = data.melt(id_vars='Category', var_name='Score Type', value_name='Score')

            sns.barplot(data=combined_data, x='Category', y='Score', hue='Score Type', palette={'Average Score': 'blue', 'Individual Score': 'red'})
            plt.xlabel('Health Attribute')
            plt.ylabel('Score')
            plt.title(f'Comparison of {f_name} {l_name}\'s Health to Average from the Practice')
            plt.legend(title='Score Type')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()    

def log_out(con):
    con.close()
    print('Goodbye!')
    exit()

def main():
    con = sqlite3.connect("HospitalAppointments.db")
    cur = con.cursor()

    #set specific password so patient info can only be accessed by those with password
    hospital_password = 'aBc1234!'

    logged_in = False
    while not logged_in:
        print("Welcome to Medical Appointment Assistant")
        logged_in = login(hospital_password)


    action = ''
    while action != 'd' and action != 'D':
        action = start_menu(con, cur)
    # Now the action is D (log out)
    log_out(con)

main()