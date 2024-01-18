import sqlite3
import pandas as pd

def load_table(con, filename, table_name):
    df = pd.read_csv(filename)
    df.to_sql(table_name, con, index=False, if_exists='replace')
    con.commit()


def main():
    con = sqlite3.connect("HospitalAppointments.db")
    cur = con.cursor()
    load_table(con, 'appointments.csv', 'appointments')
    load_table(con, 'patients.csv', 'patients')
    load_table(con, 'records.csv', 'records')
    load_table(con, 'staff.csv', 'staff')
    

    con.close()

if __name__ == "__main__":
    main()