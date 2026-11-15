# Backend (FastAPI)

## Configuración

Copia `.env.example` a `.env` y rellena los valores. Variables principales:

| Variable | Obligatoria | Descripción |
|---|---|---|
| `DATABASE_URL` | Sí | Cadena de conexión a PostgreSQL. |
| `JWT_SECRET` | Sí en producción | Secreto para firmar los tokens. Si falta se genera uno temporal y las sesiones se pierden al reiniciar. |
| `JWT_TTL_HOURS` | No | Duración de la sesión (por defecto 8 h). |
| `CORS_ORIGINS` | No | Orígenes permitidos, separados por comas. |
| `ENABLE_DOCS` | No | `true` para exponer `/docs` y `/openapi.json` (solo desarrollo). |
| `CLOUDINARY_*` | Para fotos | Credenciales de Cloudinary. |

Nunca escribas credenciales en el código ni en scripts: usa siempre variables de entorno.

## Autenticación

1. `POST /login/` con `{ "username", "password" }` devuelve `access_token` (JWT).
2. Todas las demás rutas exigen el header `Authorization: Bearer <token>`.
3. El usuario se obtiene **del token**, nunca de parámetros enviados por el cliente.
   Un doctor solo accede a sus pacientes; un fisio, a los de su doctora asignada;
   el fisio acuático, a todos.
4. Tras 5 intentos fallidos para un usuario (o 20 desde una IP) el login se bloquea 15 minutos.

Las contraseñas se guardan con bcrypt. Las contraseñas antiguas en texto plano se
convierten a hash automáticamente la primera vez que el usuario inicia sesión.

## Ejecutar en local

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```
