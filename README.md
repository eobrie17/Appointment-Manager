# Medical Appointment Assistant

A menu-driven Python CLI that runs a small clinic’s scheduling, staffing, and medical-record workflows on top of a SQLite database populated with fully synthetic patient data.​​

## System overview

### Module breakdown
- `appointment_manager.py` – Interactive CLI with authentication, CRUD flows, and analytics dashboards for appointments, patients, staff, and records.
- `create_data.py` – Seeder that synthesizes 300 patients and 30 staff members using Faker-provided demographics and insurance metadata.​
- `clean.py` – Data-engineering layer that normalizes open appointment/record dumps, assigns real IDs, and ensures every patient has associated records.​
- `csv_to_db.py` – Loader that hydrates `HospitalAppointments.db` with the cleaned CSVs for immediate use by the CLI.​

### Data flow
1. `python create_data.py` – Generate fresh synthetic patients and staff.​
2. `python clean.py` – Normalize raw appointment/record datasets and map them to existing IDs.​
3. `python csv_to_db.py` – Load the curated CSVs into SQLite tables (`appointments`, `patients`, `records`, `staff`).​

## Getting started

### Prerequisites
- Python 3.10+
- Packages: `pandas`, `tabulate`, `seaborn`, `matplotlib`, `faker` (use `pip install pandas tabulate seaborn matplotlib faker`).​​

### Launch the CLI
`bash
python appointment_manager.py `

Note: Use the default password aBc1234! to unlock the interface (configurable inside appointment_manager.py).

## What you can do in the CLI

### Appointments
- List the next 15 visits with patient/staff context.
- Schedule, cancel, or reschedule appointments with date/time validation and automatic staff lookups

### Patients
- Add new patients with optional demographic details.
- Edit or remove patients, cascading deletions into their medical records when appropriate.

### Staff
- Onboard clinicians or admin staff, update contact details, and remove departures while preserving referential integrity for appointments.

### Medical records and insights
- Insert new clinical measurements, edit existing records, and compute summary statistics (average, median, standard deviation, etc.) for any numeric attribute.
- Visualize attribute distributions across the practice or compare an individual patient’s metrics against the clinic average using seaborn charts.

### Log out securely
- Close the SQLite connection and exit cleanly when finished.

## Data Ethics
All personally identifiable information is algorithmically generated using Faker; no real patient data ships with the project. Regenerating the CSVs via create_data.py ensures clean, synthetic datasets for every clone.

## Example session
Each submenu walks the user through the relevant CRUD or analytics workflow with contextual prompts and validation messages.

```text
Welcome to Medical Appointment Assistant
Enter hospital password: aBc1234!
Choose an option:
 1) Appointments
 2) Patients
 3) Staff
 4) Records
 5) Log out
