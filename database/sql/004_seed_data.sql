INSERT INTO employees (id_employees, name, last_name, username, password, role, fisio_type, assigned_doctor) VALUES
(5, 'Carmen', 'Arellano', 'Dra.Carmen', 'Gab2cardi', 'Doctor', NULL, NULL),
(8, 'Ana', 'Fernadna', 'Dra.Ana', 'Remes2026A$', 'Doctor', NULL, NULL),
(6, 'Hugo', 'Villa', 'Fis.Hugo', 'Remes2026H$', 'Fisio', 'Clínica', 5),
(7, 'Monica', 'Garcia', 'Fis.Monica', 'Remes2026M$', 'Fisio', 'Clínica', 8),
(9, 'Cristian', '', 'Fis.Cristian', 'Remes2026C$', 'Fisio', 'Acuática', NULL)
ON CONFLICT (id_employees) DO NOTHING;
