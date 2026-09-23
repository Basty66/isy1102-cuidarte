# Informe de Auditoría de Seguridad — Sistema Cuidarte+

- **Proyecto:** Sistema de Exámenes Médicos Cuidarte+
- **Organización:** CreaLab SpA – Departamento de Desarrollo
- **Asignatura:** ISY1102 – Seguridad y Calidad en el Desarrollo de Software
- **Objeto de análisis:** Código fuente `CodigoFuenteB.zip` (BACKEND Express + PostgreSQL, FRONTEND React/Vite)
- **Método:** Revisión estática de código (SAST manual), mapeo OWASP Top 10 (2021), contraste con ERS v1.1, Ley N° 19.628 y Ley N° 20.584
- **Nota:** `BACKEND/package.json:4` describe el servicio como *"intencionalmente vulnerable"* — hallazgos esperados con fines académicos.

---

## 1. Resumen ejecutivo

| Severidad | Cantidad | IDs |
|---|---|---|
| **Crítica** | 6 | H-01, H-02, H-03, H-04, H-05, H-06 |
| **Alta** | 6 | H-07, H-08, H-09, H-10, H-11, H-12 |
| **Media** | 5 | H-13, H-14, H-15, H-16, H-17 |
| **Total** | **17** | |

**Veredicto:** el sistema **no está listo para producción**. Incumple de forma directa NFR-SEG-2 (bcrypt), NFR-SEG-9 (refresh), RF-3.3 (soft delete), RF-5.1 (auditoría con IP y recurso) y NFR-PERF-1 (<300 ms — imposible con `delay(5000)`). Las consultas SQL sí están parametrizadas (sin SQLi) y el RBAC de lectura de exámenes/documentos por paciente está correctamente implementado.

---

## 2. Hallazgos

### H-01 · Contraseñas almacenadas y comparadas en texto plano
- **Severidad:** Crítica · **OWASP:** A07 Failures in Authentication · **ERS:** NFR-SEG-2
- **Ubicación:** `BACKEND/src/routes/auth.js:21` y `auth.js:110`
- **Descripción:** El login compara `user.contrasena !== password` directamente; el registro inserta la contraseña sin hash. No existe `bcrypt`/`argon2` en `BACKEND/package.json`.
- **Impacto:** Un volcado de BD (`dump-cuidarteplus.sql`) expone todas las contraseñas. Viola NFR-SEG-2 y principio de confidencialidad de la Ley 19.628.
- **Corrección:** `bcrypt.hash(password, 12)` al registrar y `bcrypt.compare` al autenticar; migración de contraseñas existentes.
- **Detecta:** CP-01, CP-03.

### H-02 · Escalada de privilegios: creación de usuarios sin control de rol
- **Severidad:** Crítica · **OWASP:** A01 Broken Access Control · **ERS:** RB-2, NFR-SEG-4
- **Ubicación:** `BACKEND/src/routes/users.js:23-53`
- **Descripción:** `POST /usuarios` solo exige un token válido (cualquier rol) y acepta `rol_id` arbitrario: un Paciente autenticado puede crear un usuario con `rol_id` de administrador.
- **Impacto:** Takeover total del sistema; acceso a todas las fichas clínicas.
- **Corrección:** exigir rol `admin` (o `admin`+`medico` para médicos) y validar `rol_id` contra un catálogo permitido.
- **Detecta:** CP-07, CP-18.

### H-03 · Eliminación de usuarios sin autenticación
- **Severidad:** Crítica · **OWASP:** A01 Broken Access Control · **ERS:** RB-2, NFR-SEG-4
- **Ubicación:** `BACKEND/src/routes/users.js:571-589`
- **Descripción:** `DELETE /usuarios/:id` ejecuta el `DELETE FROM` **antes** de leer el header de autorización; el token solo se usa (ineficazmente) después, para el log.
- **Impacto:** Cualquier visitante sin credenciales puede borrar cualquier cuenta (incluidos admins) desde `curl`.
- **Corrección:** middleware de autenticación + verificación de rol `admin` **antes** de cualquier mutación; idealmente soft delete.
- **Detecta:** CP-18.

### H-04 · API de roles completamente sin autenticación
- **Severidad:** Crítica · **OWASP:** A01 Broken Access Control · **ERS:** NFR-SEG-4
- **Ubicación:** `BACKEND/src/routes/roles.js:18,36,46,57,76`
- **Descripción:** `POST`, `PUT` y `DELETE /roles` no verifican identidad ni rol: se puede crear, renombrar o eliminar el rol `admin` sin token.
- **Impacto:** Manipulación del modelo de autorización global; borrado de roles rompe la asignación `usuario_roles` (CASCADE).
- **Corrección:** exigir JWT + rol `admin` en toda mutación de `/roles`.
- **Detecta:** CP-18.

### H-05 · Fuga de fichas médicas por búsqueda pública de RUT
- **Severidad:** Crítica · **OWASP:** A01 Broken Access Control · **Ley:** N° 20.584, N° 19.628 · **ERS:** RB-1, RF-4.1
- **Ubicación:** `BACKEND/src/routes/pacientes.js:249-273`
- **Descripción:** `GET /pacientes/buscar/rut/:rut` no exige token y devuelve `p.*`: RUT, alergias, enfermedades crónicas, discapacidades, grupo sanguíneo, contacto de emergencia, etc.
- **Impacto:** Conocer o adivinar el RUT de una persona permite extraer su expediente médico completo sin autenticación. Vulneración directa de la reserva clínica.
- **Corrección:** exigir JWT con rol `medico`/`admin`; para pacientes, solo RUT propio.
- **Detecta:** CP-06, CP-19.

### H-06 · Eliminación física de registros (no hay soft delete)
- **Severidad:** Crítica · **OWASP:** A04 Insecure Design · **ERS:** RF-3.3
- **Ubicaciones:**
  - `BACKEND/src/routes/examenes.js:408` → `DELETE FROM examen_medico`
  - `BACKEND/src/routes/pacientes.js:399` → `DELETE FROM pacientes`
  - `BACKEND/src/routes/users.js:574` → `DELETE FROM usuarios`
  - `BACKEND/src/routes/documentos.js:275` → `DELETE FROM documentos_examen`
- **Descripción:** El ERS exige borrado lógico con confirmación modal; el código destruye la fila (y por `ON DELETE CASCADE` en `examenes/documentos`, también sus adjuntos clínicos).
- **Impacto:** Pérdida irreversible de evidencia médica; incumplimiento de RF-3.3 y de la obligación de conservación de la ficha clínica.
- **Corrección:** columna `eliminado BOOLEAN DEFAULT FALSE` + `fecha_eliminacion` + filtrado en todas las consultas.
- **Detecta:** CP-08.

### H-07 · Borrado de usuario anula la trazabilidad de sus acciones
- **Severidad:** Alta · **OWASP:** A04 Insecure Design · **ERS:** RF-5.1
- **Ubicación:** `BACKEND/sql/init.sql:90`
- **Descripción:** `usuario_id BIGINT REFERENCES usuarios(id) ON DELETE SET NULL` en `auditoria`: al borrar un usuario, todos sus logs quedan con autor `NULL`.
- **Impacto:** Pérdida de atribución forense — exactamente lo que la Ley 19.628 y el peritaje informático buscan preservar.
- **Corrección:** copiar `nombre_usuario`/identificador en el log (snapshot) o prohibir borrado físico de usuarios.
- **Detecta:** CP-09.

### H-08 · Secretos comprometidos en el repositorio
- **Severidad:** Alta · **OWASP:** A02 Cryptographic Failures · **ERS:** NFR-SEG-1
- **Ubicaciones:** `BACKEND/.env:1-3`, `.env:1-5` (incluye `JWT_SECRET` real y password de PostgreSQL `alone15`), fallback `JWT_SECRET || "inseguro"` en `auth.js:8` y 5 rutas más.
- **Descripción:** Los `.env` viajan dentro del ZIP/repositorio; además, si la variable falta, el secreto pasa a ser la cadena `"inseguro"` → cualquiera forja un token con `rolNombre: "admin"`.
- **Impacto:** Forja de tokens y acceso directo a la BD.
- **Corrección:** `.env.example` sin valores, `.gitignore` efectivo, abortar el arranque si falta `JWT_SECRET`.
- **Detecta:** CP-01, CP-12.

### H-09 · Sesión sin refresh token y JWT de 2 horas en localStorage
- **Severidad:** Alta · **OWASP:** A07 Failures in Authentication · **ERS:** RF-1.2, NFR-SEG-9
- **Ubicaciones:** `auth.js:54` (`expiresIn: "2h"`), `FRONTEND/src/context/AuthContext.jsx:41` y `api.jsx:21` (`localStorage`).
- **Descripción:** No existe endpoint de refresh ni rotación; el token de larga vida vive en `localStorage` (legible por cualquier XSS).
- **Impacto:** Ventana de robo de sesión de 2 horas; incumplimiento explícito del ERS.
- **Corrección:** access token ≤15 min + refresh rotativo en cookie `HttpOnly; Secure; SameSite=Strict`.
- **Detecta:** CP-02.

### H-10 · Paciente puede reasignar su propia ficha clínica
- **Severidad:** Alta · **OWASP:** A01 Broken Access Control · **ERS:** RB-1
- **Ubicación:** `BACKEND/src/routes/pacientes.js:341,344-350`
- **Descripción:** `usuario_id` está dentro de `allowedFields` del `PUT /pacientes/:id`, permitido también al rol Paciente sobre su propio registro → puede vincular su expediente a otra cuenta de usuario (o desvincularlo).
- **Impacto:** Fuga o desvío de historia clínica entre usuarios.
- **Corrección:** excluir `usuario_id` (y campos clínicos sensibles) del conjunto editable por rol Paciente.
- **Detecta:** CP-07.

### H-11 · El rol Médico puede promoverse a Administrador
- **Severidad:** Alta · **OWASP:** A01 Broken Access Control · **ERS:** RB-2, RB-3
- **Ubicación:** `BACKEND/src/routes/users.js:484,522-532`
- **Descripción:** En `updateUsuarioSistemaMedico`, con `isAdminOrMedico` se ejecuta `DELETE FROM usuario_roles` + `INSERT` con el `rol_id` que llegue del body → un médico puede asignarse el rol `admin`.
- **Impacto:** Escalada de privilegios lateral; acceso a auditoría y a todos los usuarios.
- **Corrección:** solo `admin` puede modificar `rol_id`, y solo hacia roles de menor jerarquía.
- **Detecta:** CP-07, CP-18.

### H-12 · Auditoría incompleta, no atómica y con tipos incorrectos
- **Severidad:** Alta · **OWASP:** A09 Security Logging Failures · **ERS:** RF-5.1
- **Ubicaciones:** `sql/init.sql:88-93`, `roles.js:24-27`, `users.js:581-587`, patrón general en todos los routes.
- **Descripción:**
  1. El esquema carece de `ip_origen` y `recurso_id` (que el propio CP-08 exige).
  2. El log se escribe **después** de la mutación y fuera de transacción: si el INSERT falla, la acción quedó hecha sin registro.
  3. `roles.js:25` y `users.js:584` pasan `authUser?.nombreUsuario` (string) a `usuario_id BIGINT` → el INSERT de auditoría falla y nadie se entera.
  4. No hay `REVOKE UPDATE/DELETE` sobre la tabla: es editable por la propia app.
- **Impacto:** Bitácora no confiable para peritaje; incumple RF-5.1.
- **Corrección:** schema `(id, usuario_id, usuario_snapshot, accion, recurso_id, ip_origen, fecha_hora)`; transacción única mutación+log; permisos append-only.
- **Detecta:** CP-08, CP-09.

### H-13 · Latencia artificial de 5 s en endpoints críticos (rompe NFR-PERF-1)
- **Severidad:** Media (calidad) · **ERS:** NFR-PERF-1, RF-4
- **Ubicaciones:** `middleware/delay.js:5-10` aplicado en `examenes.js:46,99,330`, `pacientes.js:145`, `documentos.js:66`.
- **Descripción:** `delayMiddleware(5000)` fuerza 5000 ms antes de procesar. No hay condición `NODE_ENV !== "production"` (a diferencia de lo que asume el análisis estructural).
- **Impacto:** Meta de <300 ms es **imposible**; cualquier prueba de carga (CP-13) fallará masivamente *por diseño*.
- **Corrección:** deshabilitar en producción vía variable de entorno y usar solo en desarrollo.
- **Detecta:** CP-04, CP-13, CP-14.

### H-14 · Sin cabeceras de seguridad ni límite de CORS
- **Severidad:** Media · **OWASP:** A05 Security Misconfiguration · **ERS:** NFR-SEG-1, NFR-SEG-5
- **Ubicación:** `BACKEND/src/app.js:21` (`app.use(cors())` sin origen permitido); ausencia total de `helmet`, CSP, HSTS, `X-Frame-Options`, `X-Content-Type-Options`.
- **Impacto:** Cualquier origen puede llamar a la API; no hay mitigación de clickjacking ni MIME-sniffing; imposible pasar CP-12.
- **Corrección:** `helmet()` + CORS con whitelist de orígenes.
- **Detecta:** CP-12.

### H-15 · Fuga de errores internos de PostgreSQL al cliente
- **Severidad:** Media · **OWASP:** A05 Security Misconfiguration · **ERS:** criterio "no revelar stack trace"
- **Ubicaciones:** todos los `catch` con `glosa: err.message` (ej. `auth.js:67`, `examenes.js:94`, `documentos.js:115`).
- **Descripción:** Mensajes reales de la BD (tabla, constraint, a veces columna) se devuelven en el JSON 500.
- **Impacto:** Reconocimiento facilitado para ataques posteriores; viola el criterio transversal del propio plan.
- **Corrección:** loguear en servidor con ID correlable, responder `{"error": "Error interno", "id": "..."}`.
- **Detecta:** CP-10, CP-11.

### H-16 · Sin límite de intentos de login (fuerza bruta)
- **Severidad:** Media · **OWASP:** A07 Failures in Authentication · **ERS:** NFR-SEG-2
- **Ubicación:** `BACKEND/src/routes/auth.js:10` (no hay `express-rate-limit` ni bloqueo).
- **Impacto:** Con contraseñas en texto plano (H-01), la fuerza bruta es trivial y silenciosa; los intentos fallidos tampoco se auditan.
- **Corrección:** rate limit (ej. 5 intentos/min por IP+usuario) + log de intentos fallidos.
- **Detecta:** CP-01, CP-10.

### H-17 · Subida/descarga de archivos con controles débiles
- **Severidad:** Media · **OWASP:** A04 Insecure Design · **ERS:** RF-4.3, NFR-SEG-3
- **Ubicaciones:** `documentos.js:10-28` (MIME declarado por el cliente, sin validar contenido/magic bytes), `documentos.js:248-251` (`nombre_archivo` sin sanitizar en header `Content-Disposition` — inyección CRLF), `init.sql:82` (BYTEA en la BD, sin cifrado).
- **Impacto:** Bypass del filtro con MIME falsificado; posible header injection; incumplimiento de NFR-SEG-3 (cifrado en reposo) y de la supuesta "storage interno" del ERS (no hay volumen persistente en `docker-compose` para `uploads/`).
- **Corrección:** validar firma binaria del archivo, sanitizar nombre (solo `[a-zA-Z0-9._-]`), cifrar en reposo, volumen persistente.
- **Detecta:** CP-04, CP-14.

---

## 3. Mapeo OWASP Top 10 (2021)

| Categoría | Hallazgos | Estado |
|---|---|---|
| A01 Broken Access Control | H-02, H-03, H-04, H-05, H-10, H-11 | ❌ Grave |
| A02 Cryptographic Failures | H-01, H-08 | ❌ Grave |
| A03 Injection | — (SQL parametrizado con `$1`) | ✅ Sin hallazgos |
| A04 Insecure Design | H-06, H-07, H-12, H-17 | ❌ Grave |
| A05 Security Misconfiguration | H-14, H-15 | ⚠️ Parcial |
| A06 Vulnerable Components | Sin `npm audit` ejecutado; multer 1.4.5-lts | ⚠️ Revisar |
| A07 Identification & Auth Failures | H-09, H-16 | ❌ Grave |
| A08 Software & Data Integrity | — | ⚠️ Sin CI/CD ni tests |
| A09 Logging & Monitoring Failures | H-12 | ❌ Grave |
| A10 SSRF | — | ✅ No aplica |

---

## 4. Cumplimiento ERS (veredicto por requisito)

| Requerimiento | Estado | Evidencia |
|---|---|---|
| RF-1.1 Login | ⚠️ | Funciona, pero sin bcrypt (H-01) |
| RF-1.2 Refresh token | ❌ | No existe (H-09) |
| RF-2.x Gestión usuarios | ❌ | Sin auth en DELETE; escalada (H-02, H-03) |
| RF-3.1 CRUD exámenes | ⚠️ | RBAC de creación correcto; delay 5 s (H-13) |
| RF-3.3 Soft delete | ❌ | `DELETE FROM` físico (H-06) |
| RF-4.1/4.2 Acceso paciente | ✅/❌ | Lectura protegida bien; búsqueda RUT pública la rompe (H-05) |
| RF-4.3/4.4 Adjuntos | ⚠️ | Multer con límite 10 MB; sin cifrado (H-17) |
| RF-5.1 Auditoría | ❌ | Sin IP/recurso, no atómica, editable (H-12) |
| NFR-SEG-1 TLS/cabeceras | ❌ | Sin helmet/HSTS (H-14) |
| NFR-SEG-2 bcrypt | ❌ | Texto plano (H-01) |
| NFR-SEG-3 Cifrado en reposo | ❌ | BYTEA sin cifrar (H-17) |
| NFR-SEG-4 RBAC | ⚠️ | Bueno en lectura clínica; roto en usuarios/roles (H-02/03/04/11) |
| NFR-SEG-5 Anti-SQLi/XSS | ✅/⚠️ | SQL parametrizado ✅; headers ausentes ⚠️ |
| NFR-SEG-9 Sesión JWT | ❌ | 2 h sin refresh (H-09) |
| NFR-PERF-1 <300 ms | ❌ | Imposible con `delay(5000)` (H-13) |
| NFR-PERF-3 200 usuarios | ❌ | Degradará por H-13 |
| RB-1 / RB-2 / RB-3 | ❌ | Rotos por H-02, H-03, H-05, H-11 |

---

## 5. Puntos fuertes confirmados

| Aspecto | Detalle |
|---|---|
| Arquitectura desacoplada | API REST ↔ SPA con contratos OpenAPI (`openapi.json`, `/docs`) |
| Anti-SQLi | Todas las consultas usan placeholders `$1` de `pg` — **0 hallazgos de inyección SQL** |
| RBAC de lectura clínica | `examenes.js:277-289` y `documentos.js:222-234` verifican propiedad del paciente correctamente (CP-06 pasará) |
| Validación de entrada | Middleware `validate.js` + esquemas `yup` centralizados en `/validations` |
| Validación de RUT | `utils/rut.js` con normalización y regex de formato |
| Filtro de tipos de archivo | `fileFilter` con whitelist MIME en Multer (mejorable: ver H-17) |
| Organización del código | Rutas por recurso, middlewares y validaciones separados |

---

## 6. Recomendaciones priorizadas

**Inmediatas (antes de cualquier despliegue):**
1. bcrypt en registro/login + rotar `JWT_SECRET` y password de BD; quitar `.env` del repo (H-01, H-08).
2. Autenticación+autorización en `DELETE /usuarios`, `/roles` completo y `POST /usuarios` (H-02, H-03, H-04).
3. Proteger `GET /pacientes/buscar/rut/:rut` (H-05).
4. Soft delete en usuarios, pacientes, exámenes y documentos (H-06).
5. Eliminar `delay(5000)` de producción (H-13).

**Corto plazo:**
6. Refresh token + JWT ≤15 min (H-09); rate limit en login (H-16).
7. Esquema de auditoría completo + transacción atómica + `REVOKE` (H-12, H-07).
8. `helmet` + CORS whitelist (H-14); respuestas 500 genéricas (H-15).

**Estructurales:**
9. Suite Jest+Supertest desde cero (hoy: 0 tests), CI con ZAP y `npm audit`.
10. Volumen persistente para `uploads/` y cifrado en reposo (H-17).

---

## 7. Conclusión

La revisión del código real confirma que el sistema Cuidarte+ está **diseñado con vulnerabilidades deliberadas** y que, en su estado actual, incumple la mayoría de los controles de seguridad, integridad y rendimiento declarados en el ERS. El plan de pruebas asociado debe ejecutarse sobre estos endpoints reales para demostrar, con evidencia reproducible, tanto los controles que sí funcionan (anti-SQLi, RBAC de lectura) como los 17 hallazgos que impiden la certificación de calidad.