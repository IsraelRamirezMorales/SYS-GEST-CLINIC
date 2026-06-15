CREATE TYPE sesion_options as ENUM(
  'Alberca',
  'Consulta',
  'Terapia'
);

CREATE TYPE role_enum as ENUM(
  'Doctor',
  'Fisio'
);

CREATE TYPE role_fisio as ENUM(
  'Acuática',
  'Clínica',
  'Deportiva',
  'Ortopédica',
  'Manual'
);

CREATE TYPE sesion_state as ENUM(
  'Sin empezar',
  'Asistió',
  'No Asistió'
);