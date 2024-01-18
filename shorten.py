import pandas as pd

#shorten data base for requirments
patients = pd.read_csv('patients_first.csv')
staff = pd.read_csv('staff_first.csv')
records = pd.read_csv('observations_first.csv')
appointments = pd.read_csv('appointment_first.csv')

p = patients.head(500)
s = staff.head(30)
r = records.head(500)
a = appointments.head(250)

p.to_csv('patients_dirty.csv', index=False)
s.to_csv('staff_dirty.csv', index=False)
r.to_csv('records_dirty.csv', index=False)
a.to_csv('appointments_dirty.csv', index=False)