CREATE TABLE employees(
  id_employees SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  password TEXT NOT NULL,
  username TEXT NOT NULL,
  role role_enum,
  fisio_type role_fisio,
  assigned_doctor INTEGER,
  profile_picture TEXT DEFAULT NULL
);

CREATE TABLE patients(
  id_patient SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  phone TEXT NOT NULL,
  amount_to_pay INTEGER NOT NULL,
  imp_data TEXT,
  doctor_charge INTEGER,
  aseguradora VARCHAR(255) DEFAULT '',
  doctor_sender VARCHAR(255) DEFAULT NULL
);

CREATE TABLE sesions(
  id_sesion SERIAL PRIMARY KEY,
  entry_date DATE NOT NULL,
  sesion_type sesion_options,
  id_patient INTEGER,
  id_employees INTEGER,
  entry_time TIME NOT NULL,
  state sesion_state
);

CREATE TABLE payments(
  id_payments SERIAL PRIMARY KEY,
  payments_date DATE NOT NULL,
  mount NUMERIC(10, 2) NOT NULL,
  id_sesion INTEGER
);

CREATE TABLE session_records(
  id_record SERIAL PRIMARY KEY,
  id_sesion INTEGER REFERENCES sesions(id_sesion) ON DELETE SET NULL,
  entry_date DATE NOT NULL,
  entry_time TIME NOT NULL,
  sesion_type VARCHAR(50) NOT NULL,
  id_patient INTEGER REFERENCES patients(id_patient) ON DELETE SET NULL,
  id_employees INTEGER REFERENCES employees(id_employees) ON DELETE SET NULL,
  state VARCHAR(50) NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);