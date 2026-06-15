-- Seed data for employees
INSERT INTO employees (id_employees, name, last_name, username, password, role, fisio_type, assigned_doctor) VALUES
(5, 'Gabriela', 'Ramos', 'Dra.Gabriela', 'password', 'Doctor', NULL, NULL),
(8, 'Valeria', 'Soler', 'Dra.Valeria', 'password', 'Doctor', NULL, NULL),
(6, 'Alejandro', 'Ortiz', 'Fis.Alejandro', 'password', 'Fisio', 'Clínica', 5),
(7, 'Patricia', 'Luna', 'Fis.Patricia', 'password', 'Fisio', 'Clínica', 8),
(9, 'Eduardo', 'Gómez', 'Fis.Eduardo', 'password', 'Fisio', 'Acuática', NULL)
ON CONFLICT (id_employees) DO NOTHING;

-- Restart employee sequence
SELECT setval('employees_id_employees_seq', COALESCE((SELECT MAX(id_employees)+1 FROM employees), 1), false);

-- Seed data for patients
INSERT INTO patients (id_patient, name, last_name, phone, amount_to_pay, imp_data, doctor_charge, aseguradora, doctor_sender) VALUES
(1, 'Roberto', 'Castro', '5512345678', 1150, 'Paciente con dolor crónico en rodilla derecha tras cirugía de menisco. Evitar ejercicios de alto impacto.', 5, 'Axa', 'Dr. Gómez'),
(2, 'Beatriz', 'Mendoza', '5523456789', 800, 'Paciente de la tercera edad con artrosis de cadera. Foco en movilidad y fortalecimiento suave.', 8, 'MetLife', 'Dr. Ruiz'),
(3, 'Fernando', 'Herrera', '5534567890', 350, 'Esguince de tobillo grado 2. Aplicar termoterapia y ejercicios de propiocepción.', 5, '', NULL),
(4, 'Camila', 'Vega', '5545678901', 0, 'Rehabilitación post-fractura de muñeca izquierda. Trabajar en motricidad fina.', 8, 'Seguros Monterrey', NULL),
(5, 'Santiago', 'Silva', '5556789012', 1200, 'Dolor lumbar inespecífico. Trabajar en higiene de columna y fortalecimiento de core.', 5, 'GNP', 'Dr. Salazar'),
(6, 'Valentina', 'Ríos', '5567890123', 400, 'Terapia de hombro doloroso (manguito rotador). Movilizaciones pasivas iniciales.', 8, '', NULL),
(7, 'Mateo', 'Fuentes', '5578901234', 0, 'Hemipléjico izquierdo por secuela de EVC. Reeducación de la marcha.', 5, 'Axa', NULL),
(8, 'Isabella', 'Novoa', '5589012345', 750, 'Escoliosis idiopática adolescente. Ejercicios de Schroth recomendados.', 8, 'MetLife', NULL),
(9, 'Adrián', 'Ortega', '5590123456', 800, 'Lesión de ligamento cruzado anterior. Trabajo de fuerza y estabilidad excéntrica.', 5, '', NULL),
(10, 'Lucía', 'Méndez', '5501234567', 0, 'Lumbalgia mecánica. Terapia manual y estiramientos de cadena posterior.', 8, 'GNP', NULL)
ON CONFLICT (id_patient) DO NOTHING;

-- Restart patient sequence
SELECT setval('patients_id_patient_seq', COALESCE((SELECT MAX(id_patient)+1 FROM patients), 1), false);

-- Clear existing sessions and session records to prevent duplicate key conflicts in this test env
TRUNCATE TABLE session_records CASCADE;
TRUNCATE TABLE sesions CASCADE;

-- Seed data for sessions (using relative dates so they always appear current)
INSERT INTO sesions (id_sesion, entry_date, sesion_type, id_patient, id_employees, entry_time, state) VALUES
-- Past Sessions
(1, CURRENT_DATE - INTERVAL '1 day', 'Consulta', 1, 5, '09:00:00', 'Asistió'),
(2, CURRENT_DATE - INTERVAL '1 day', 'Terapia', 3, 6, '10:30:00', 'Asistió'),
(3, CURRENT_DATE - INTERVAL '2 days', 'Consulta', 2, 8, '11:00:00', 'Asistió'),
(4, CURRENT_DATE - INTERVAL '2 days', 'Alberca', 5, 9, '12:00:00', 'No Asistió'),
(5, CURRENT_DATE - INTERVAL '3 days', 'Terapia', 1, 6, '16:00:00', 'Asistió'),
(6, CURRENT_DATE - INTERVAL '3 days', 'Terapia', 5, 6, '17:00:00', 'Asistió'),

-- Today's Sessions
(7, CURRENT_DATE, 'Alberca', 1, 9, '08:00:00', 'Asistió'),
(8, CURRENT_DATE, 'Terapia', 2, 7, '09:30:00', 'Sin empezar'),
(9, CURRENT_DATE, 'Alberca', 6, 9, '11:00:00', 'Sin empezar'),
(10, CURRENT_DATE, 'Terapia', 8, 7, '15:00:00', 'Sin empezar'),
(11, CURRENT_DATE, 'Consulta', 9, 5, '16:30:00', 'Sin empezar'),

-- Future Sessions
(12, CURRENT_DATE + INTERVAL '1 day', 'Alberca', 5, 9, '10:00:00', 'Sin empezar'),
(13, CURRENT_DATE + INTERVAL '1 day', 'Consulta', 8, 8, '11:30:00', 'Sin empezar'),
(14, CURRENT_DATE + INTERVAL '2 days', 'Terapia', 3, 6, '09:00:00', 'Sin empezar')
ON CONFLICT (id_sesion) DO NOTHING;

-- Restart session sequence
SELECT setval('sesions_id_sesion_seq', COALESCE((SELECT MAX(id_sesion)+1 FROM sesions), 1), false);

-- Seed data for session_records matching the sessions
INSERT INTO session_records (id_record, id_sesion, entry_date, entry_time, sesion_type, id_patient, id_employees, state, updated_at) VALUES
(1, 1, CURRENT_DATE - INTERVAL '1 day', '09:00:00', 'Consulta', 1, 5, 'Asistió', CURRENT_TIMESTAMP - INTERVAL '1 day'),
(2, 2, CURRENT_DATE - INTERVAL '1 day', '10:30:00', 'Terapia', 3, 6, 'Asistió', CURRENT_TIMESTAMP - INTERVAL '1 day'),
(3, 3, CURRENT_DATE - INTERVAL '2 days', '11:00:00', 'Consulta', 2, 8, 'Asistió', CURRENT_TIMESTAMP - INTERVAL '2 days'),
(4, 4, CURRENT_DATE - INTERVAL '2 days', '12:00:00', 'Alberca', 5, 9, 'No Asistió', CURRENT_TIMESTAMP - INTERVAL '2 days'),
(5, 5, CURRENT_DATE - INTERVAL '3 days', '16:00:00', 'Terapia', 1, 6, 'Asistió', CURRENT_TIMESTAMP - INTERVAL '3 days'),
(6, 6, CURRENT_DATE - INTERVAL '3 days', '17:00:00', 'Terapia', 5, 6, 'Asistió', CURRENT_TIMESTAMP - INTERVAL '3 days'),
(7, 7, CURRENT_DATE, '08:00:00', 'Alberca', 1, 9, 'Asistió', CURRENT_TIMESTAMP),
(8, 8, CURRENT_DATE, '09:30:00', 'Terapia', 2, 7, 'Sin empezar', CURRENT_TIMESTAMP),
(9, 9, CURRENT_DATE, '11:00:00', 'Alberca', 6, 9, 'Sin empezar', CURRENT_TIMESTAMP),
(10, 10, CURRENT_DATE, '15:00:00', 'Terapia', 8, 7, 'Sin empezar', CURRENT_TIMESTAMP),
(11, 11, CURRENT_DATE, '16:30:00', 'Consulta', 9, 5, 'Sin empezar', CURRENT_TIMESTAMP),
(12, 12, CURRENT_DATE + INTERVAL '1 day', '10:00:00', 'Alberca', 5, 9, 'Sin empezar', CURRENT_TIMESTAMP),
(13, 13, CURRENT_DATE + INTERVAL '1 day', '11:30:00', 'Consulta', 8, 8, 'Sin empezar', CURRENT_TIMESTAMP),
(14, 14, CURRENT_DATE + INTERVAL '2 days', '09:00:00', 'Terapia', 3, 6, 'Sin empezar', CURRENT_TIMESTAMP)
ON CONFLICT (id_record) DO NOTHING;

-- Restart session record sequence
SELECT setval('session_records_id_record_seq', COALESCE((SELECT MAX(id_record)+1 FROM session_records), 1), false);
