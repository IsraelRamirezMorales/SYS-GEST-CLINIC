-- Employees constraints
ALTER TABLE employees ADD CONSTRAINT fk_doctor_asignado FOREIGN KEY (assigned_doctor) REFERENCES employees(id_employees);
ALTER TABLE employees ADD CONSTRAINT chk_doctor_asignado CHECK ((((role = 'Doctor'::role_enum) AND (assigned_doctor IS NULL)) OR (role = 'Fisio'::role_enum)));
ALTER TABLE employees ADD CONSTRAINT chk_fisio_type CHECK ((((role = 'Doctor'::role_enum) AND (fisio_type IS NULL)) OR (role = 'Fisio'::role_enum)));

-- Patients constraints
ALTER TABLE patients ADD CONSTRAINT fk_patients_doctor_in_charge FOREIGN KEY (doctor_charge) REFERENCES employees(id_employees);

-- Sesions constraints
ALTER TABLE sesions ADD CONSTRAINT fk_sesions_employees FOREIGN KEY (id_employees) REFERENCES employees(id_employees);
ALTER TABLE sesions ADD CONSTRAINT fk_sesions_patient FOREIGN KEY (id_patient) REFERENCES patients(id_patient);

-- Payments constraints
ALTER TABLE payments ADD CONSTRAINT fk_sesions_sesions FOREIGN KEY (id_sesion) REFERENCES sesions(id_sesion);
