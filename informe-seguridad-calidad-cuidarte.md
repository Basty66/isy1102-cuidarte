# Plan de Pruebas — Sistema de Exámenes Médicos Cuidarte+

- **Asignatura:** ISY1102 – Seguridad y Calidad en el Desarrollo de Software
- **Sección:** Sección XX
- **Proyecto:** Sistema de Exámenes Médicos Cuidarte+
- **Organización:** CreaLab SpA – Departamento de Desarrollo
- **Documento Base:** ERS v1.1 + Código fuente `CodigoFuenteB.zip` (análisis estático, sin modificación)
- **Integrantes:** Nombre Apellido Alumno 1 · Nombre Apellido Alumno 2 · Nombre Apellido Alumno 3

## Índice

1. Introducción
2. Criterios de calidad, seguridad y cumplimiento normativo
3. Plan de pruebas (estrategia, tipos, aceptación, métricas, herramientas, recursos)
4. Diseño de casos de prueba (CP-01 a CP-19) — endpoints reales
5. Matriz de trazabilidad y cobertura
6. Conclusión

---

## 1. Introducción

### 1.1 Contexto

Cuidarte+ es una plataforma web médica multicapa para centros de salud: gestión de pacientes, exámenes médicos, documentos clínicos y auditoría.

- **Frontend:** SPA React (v19.1.1) + Material UI (v7.3.4) + Tailwind (v3.4.14), servida con Nginx.
- **Backend:** API RESTful Node.js/Express (v4.19.2) con validaciones `yup`, JWT (`jsonwebtoken`) y cliente `pg` (v8.12.0).
- **Base de datos:** PostgreSQL, esquema en `BACKEND/sql/init.sql`; documentos clínicos en tabla `documentos_examen` (BYTEA) y archivos en `BACKEND/uploads/`.
- **Despliegue:** Docker (`docker-compose.yml`), puertos: backend 4444, frontend 3333, Postgres 15442; en desarrollo backend `PORT=4000`.

Los datos manejados (RUT, fichas clínicas, diagnósticos) son sensibles según Ley N° 19.628 y Ley N° 20.584: confidencialidad, integridad y disponibilidad son críticas.

### 1.2 Propósito

Definir la estrategia de aseguramiento de calidad (SQA) y validación de seguridad que verifique:

1. **Cumplimiento funcional** de cada RF del ERS v1.1 contra los endpoints reales.
2. **No funcionales:** latencia <300 ms, 200 usuarios concurrentes, carga inicial <2 s, uptime 99.5%, WCAG 2.1 AA.
3. **Seguridad:** autenticación, RBAC, OWASP Top 10, sin fuga de información clínica.
4. **Conformidad legal:** Ley 19.628, Ley 20.584 y auditoría trazable (RF-5.1).

### 1.3 Alcance y fuera de alcance

**En alcance:** API Express completa (`/autenticacion`, `/usuarios`, `/pacientes`, `/examenes`, `/documentos`, `/auditoria`, `/roles`, `/docs`), SPA React, esquema PostgreSQL, uploads.

**Fuera de alcance:** infraestructura física del datacenter, modificación del código fuente (este plan es de **solo análisis/prueba**), terceros no auditados.

**Glosario:** RF (funcional), NFR (no funcional), RB (regla de negocio), RBAC, DAST/SAST, UAT, JWT, SPA, soft delete.

### 1.4 Estructura del informe

- Sección 2: criterios (ISO/IEC 25010 + OWASP + legislación chilena) y matriz RBAC esperada.
- Sección 3: estrategia, priorización, riesgos, entrada/salida, métricas, herramientas, recursos y evidencia.
- Sección 4: 19 casos de prueba con los **endpoints y esquema reales** del código.
- Sección 5: trazabilidad ERS → caso (cobertura meta 100%).

---

## 2. Criterios de calidad, seguridad y cumplimiento normativo

```
                 SISTEMA DE EXAMENES MEDICOS CUIDARTE+
                                 |
       +-------------------------+-------------------------+
       |                         |                         |
+------v--------+       +-------v--------+       +--------v-------+
| CALIDAD       |       | SEGURIDAD      |       | CUMPLIMIENTO   |
| ISO/IEC 25010 |       | OWASP + NFR-SEG|       | LEGAL (CHILE)  |
+------v--------+       +-------v--------+       +--------v-------+
 Usabilidad/WCAG 2.1 AA   bcrypt + JWT corto      Ley 19.628
 Rendimiento <300 ms      RBAC backend            Ley 20.584
 Disponibilidad 99.5%     Anti-SQLi/XSS/CSRF      Auditoría inmutable
 Mantenibilidad OpenAPI   TLS + cabeceras         con IP y recurso
```

### 2.1 Calidad de Software (ISO/IEC 25010)

- **Usabilidad (NFR-USAB):** WCAG 2.1 AA; tipografía ≥12 px; contraste ≥4.5:1; etiquetas WAI-ARIA; targets ≥48×48 px; navegación 100% por teclado; foco en adultos mayores (NFR-USAB-1, NFR-USAB-4).
- **Rendimiento (NFR-PERF):** API CRUD <300 ms (NFR-PERF-1); carga inicial de SPA <2 s en red móvil (NFR-PERF-2); 200 usuarios concurrentes (NFR-PERF-3); subida/descarga de adjuntos ≤10 s (RF-4).
- **Disponibilidad (NFR-DIS):** uptime 99.5% mensual (NFR-DIS-1); ventanas de mantenimiento con respaldo y rollback (NFR-DIS-2).
- **Mantenibilidad:** desacoplamiento React ↔ Express ↔ PostgreSQL; OpenAPI vigente (`/docs`, `/openapi.json`).

### 2.2 Seguridad (NFR-SEG)

- **Tránsito (NFR-SEG-1):** TLS 1.2+ obligatorio, redirect HTTP→HTTPS, HSTS, cabeceras `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`.
- **Reposo (NFR-SEG-3):** cifrado de `documentos_examen.documento` y backups.
- **Autenticación (NFR-SEG-2, RF-1.1, NFR-SEG-9):** bcrypt cost ≥12; access JWT ≤15 min + refresh rotativo en cookie `HttpOnly; Secure; SameSite=Strict`; política ≥12 caracteres (mayúsculas, minúsculas, números, símbolos); rate limit de login.
- **RBAC (NFR-SEG-4):** middlewares en backend para `admin`, `medico`, `paciente`; reglas RB-1/RB-2/RB-3; falla por denegación (`401`/`403`).
- **OWASP (NFR-SEG-5):** SQLi vía consultas parametrizadas `pg` ($1); XSS con escape React + CSP; CSRF con `SameSite` + token en mutaciones.
- **Auditoría (RF-5.1, NFR-SEG-7):** tabla `auditoria` con `usuario_id`, `accion`, `recurso_id`, `ip_origen`, `fecha_hora` UTC; escritura atómica con la mutación; `REVOKE UPDATE, DELETE` para todos los roles de aplicación; backups diarios cifrados con prueba de restauración.

### 2.2.1 Matriz RBAC esperada (referencia obligatoria de las pruebas)

Baseline real de rutas (`BACKEND/src/app.js:28-35`):

| Endpoint (real) | admin | medico | paciente | sin token |
|---|---|---|---|---|
| `POST /autenticacion/login` | ✔ | ✔ | ✔ | ✔ |
| `POST /autenticacion/registro` | ✔ | ✔ | ✔ | ✔ |
| `GET/POST /usuarios` | ✔ | ✖ (lista) / ✔ crear* | ✖ | ✖ |
| `GET /usuarios/:id` | ✔ | ✔ | Solo propio | ✖ |
| `PUT /usuarios/:id` | ✔ | ✖ rol ajeno* | Solo propio, sin `rol_id` | ✖ |
| `DELETE /usuarios/:id` | ✔ | ✖ | ✖ | **debe ser ✖** |
| `GET/POST /pacientes` | ✔ | ✔ | ✖ | ✖ |
| `GET /pacientes/:id` | ✔ | ✔ | Solo propio | ✖ |
| `GET /pacientes/buscar/rut/:rut` | ✔ | ✔ | Solo RUT propio | **debe ser ✖** |
| `PUT /pacientes/:id` | ✔ | ✔ | Solo propio, **sin `usuario_id`** | ✖ |
| `DELETE /pacientes/:id` | ✔ | ✖ | ✖ | ✖ |
| `POST /examenes` | ✔ | ✔ | ✖ | ✖ |
| `GET /examenes` | ✔ (todos) | ✔ (todos) | Solo propios | ✖ |
| `GET /examenes/paciente/:id` | ✔ | ✔ | Solo `id` propio | ✖ |
| `PUT /examenes/:id` | ✔ | ✔ | ✖ | ✖ |
| `DELETE /examenes/:id` (soft) | ✔ | ✔* | ✖ | ✖ |
| `POST /documentos` | ✔ | ✔ | ✖ | ✖ |
| `GET /documentos/:id` | ✔ | ✔ | Solo propio | ✖ |
| `DELETE /documentos/:id` (soft) | ✔ | ✖ | ✖ | ✖ |
| `GET /auditoria` | ✔ | ✖ | ✖ | ✖ |
| `POST /auditoria` | ✔ | ✔ | ✔ (solo propio) | ✖ |
| `POST/PUT/DELETE /roles` | ✔ | ✖ | ✖ | **debe ser ✖** |
| `GET /roles`, `/docs`, `/openapi.json` | ✔ | ✔ | ✔ | Catálogo público aceptable |

\* `DELETE /examenes`: el ERS lo reserva al personal clínico con confirmación modal; se prueba como soft delete.

Celdas ✖ ⇒ `403 {"error":"No autorizado"}`; sin token ⇒ `401`. Esta tabla es el **oracle** de los casos CP-06, CP-07, CP-18 y CP-19.

### 2.3 Cumplimiento legal (Chile)

- **Ley N° 19.628:** RUT, nombres, correos y diagnósticos = datos sensibles; principio de finalidad y confidencialidad; solo Médico/Administrador procesa.
- **Ley N° 20.584:** derecho del paciente a sus propios exámenes (RF-4.1/4.2); reserva clínica absoluta frente a terceros (RB-1); edición reservada al profesional tratante (RF-3.1, RB-3).
- **RF-5.1:** logs inmutables con usuario, acción, recurso, timestamp UTC e IP para peritaje; retención ≥12 meses.

---

## 3. Plan de pruebas

### 3.1 Estrategia, priorización y riesgos

```
                     CICLO DE VIDA DE PRUEBAS

+--------------------------------------------------------------------------------+
| 1. UNITARIAS/INTEGRACIÓN — Jest + Supertest (a incorporar; hoy 0 tests)  P1    |
|    Validaría validate.js, requireRole y rutas JWT.                             |
+--------------------------------------------------------------------------------+
                                   |
                                   v
+--------------------------------------------------------------------------------+
| 2. FUNCIONALES/SISTEMA — Postman/Newman + UI manual                   P1      |
|    Login, CRUD usuarios/pacientes/exámenes/documentos, RBAC, soft delete.      |
+--------------------------------------------------------------------------------+
                                   |
                                   v
+--------------------------------------------------------------------------------+
| 3. NO FUNCIONALES — JMeter (carga) + OWASP ZAP (DAST)                  P1/P2  |
|    200 usuarios, SQLi/XSS, cabeceras TLS, latencia vs delayMiddleware.         |
+--------------------------------------------------------------------------------+
                                   |
                                   v
+--------------------------------------------------------------------------------+
| 4. UAT/ACCESIBILIDAD — Axe DevTools + panel 5 adultos mayores          P2     |
|    WCAG 2.1 AA, legibilidad, teclado, táctil.                                  |
+--------------------------------------------------------------------------------+
```

**Metodología**

- *API automatizada:* colecciones Postman → Newman en CI (a incorporar: el repo no tiene tests).
- *Carga:* JMeter 200 hilos contra `/examenes`, `/pacientes` (medirá el efecto real de `delay(5000)`).
- *DAST:* ZAP spider + active scan sobre `/autenticacion/login`, `/pacientes`, `/roles`.
- *Manual:* flujos SPA (modales de borrado, RoleGuard, subida de PDF).
- *UAT:* panel de 5 adultos mayores sin capacitación.

**Priorización**

| Prioridad | Alcance | Casos |
|---|---|---|
| **P1 – Crítica** | Login/sesión, RBAC sin fuga, exámenes+adjuntos, auditoría, SQLi/XSS, auth de endpoints mutantes | CP-01, CP-02, CP-04, CP-06, CP-07, CP-08, CP-09, CP-10, CP-11, CP-12, CP-18, CP-19 |
| **P2 – Alta** | Rendimiento <300 ms/200 usuarios, accesibilidad, registro pacientes, contraseñas, carga <2 s, disponibilidad | CP-03, CP-05, CP-13, CP-14, CP-15, CP-17 |
| **P3 – Media** | Compatibilidad de navegadores/dispositivos | CP-16 |

**Riesgos de prueba**

| Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|
| `delayMiddleware(5000)` contamina métricas de latencia | Alta | Alto | Medir y **reportar como hallazgo H-13**, no como defecto del plan; separar endpoints con delay de los sin delay (`/autenticacion/login` no lo tiene) |
| Tokens JWT de 2 h expiran o se roban en la suite | Media | Medio | Suite <2 h o re-login en pre-request |
| Active scan de ZAP altera datos sintéticos | Media | Medio | Re-seeding con `dump-cuidarteplus.sql` entre corridas |
| Falta de panel de adultos mayores | Media | Alto | Agendar con anticipación; respaldo con 3 evaluadores + video |
| Pruebas **destructivas** (DELETE sin auth) sobre datos reales | Alta | Alto | Ejecutar solo contra entorno aislado con copia de BD |

**Criterios de entrada**

1. Código fuente extraído y desplegado en QA/Staging (Docker) — **sin modificar código**.
2. PostgreSQL inicializado con `init.sql` + `dump-cuidarteplus.sql` (datos 100% sintéticos).
3. ERS v1.1 aprobado y matriz de trazabilidad lista.
4. OpenAPI vigente en `/docs`.
5. Colección Postman exportada con los endpoints reales.

**Criterios de salida**

1. 100% de casos P1 y P2 ejecutados con estado APROBADO/RECHAZADO justificado.
2. Cero vulnerabilidades críticas/altas sin registrar en el informe de hallazgos (doc. `hallazgos-seguridad-cuidarte.md`).
3. Latencia ≤300 ms en el 95% de peticiones **sin delay artificial**; endpoints con `delay(5000)` documentados como incumplimiento de NFR-PERF-1.
4. Accesibilidad ≥90% sin violaciones críticas WCAG 2.1 AA.
5. Evidencia completa según protocolo 3.6.

### 3.2 Tipos de prueba

| Tipo | Propósito | Requerimiento/norma |
|---|---|---|
| Funcionales | Reglas de negocio y casos de uso reales (login, CRUD, adjuntos) | RF-1.1 a RF-5.1 |
| Integración | React ↔ Express ↔ PostgreSQL vía REST JSON | ERS 2.1 y 4 |
| Seguridad DAST/SAST | SQLi, XSS, CSRF, bypass JWT, cabeceras, RBAC | NFR-SEG-1..9, OWASP |
| Rendimiento/carga | Latencia y estabilidad con 200 usuarios | NFR-PERF-1/2/3 |
| Usabilidad/accesibilidad | Legibilidad, ARIA, contraste, teclado | NFR-USAB-1/4, WCAG 2.1 AA |
| Compatibilidad | Chrome, Firefox, Safari, Edge (2 últimas versiones) + móviles | NFR-COMPAT-1/2 |
| Auditoría/integridad | Log inmutable de acciones críticas | RF-5.1, Ley 19.628/20.584 |
| Disponibilidad/respaldo | Uptime 99.5% y restauración | NFR-DIS-1/2, NFR-SEG-7 |

### 3.3 Criterios de aceptación transversales

1. **Autorización:** ningún endpoint entrega datos sin JWT válido conforme a la matriz 2.2.1 (RB-1/2/3).
2. **HTTP estandarizado con JSON predecible:** `200` OK · `201` creado · `400 {"error","glosa","detalles"}` · `401` token · `403 "No autorizado"` · `404 "No encontrado"` · `500` **sin** exponer `err.message` de PostgreSQL.
3. **Soft delete obligatorio:** prohibido `DELETE FROM` sobre `examen_medico`, `pacientes`, `usuarios`, `documentos_examen` (RF-3.3) — confirmación modal previa en UI.
4. **Latencia:** consultas/actualizaciones <300 ms en el 95%; adjuntos ≤10 s. `delayMiddleware` solo si `NODE_ENV=development`.
5. **Auditoría incondicional y atómica:** toda mutación inserta log (con IP y recurso) en la **misma transacción**, antes del `200/201`.
6. **Trazabilidad de errores:** todo `500` registra ID correlacionable en log de servidor sin filtrar detalles al cliente.

### 3.4 Métricas de calidad

| Métrica | Fuente | Meta |
|---|---|---|
| Cobertura de casos P1+P2 | ejecutados/planificados | 100% |
| Tasa de aprobación | aprobados/ejecutados | ≥95% |
| Hallazgos críticos abiertos | informe de hallazgos | 0 para aprobar salida |
| Latencia p95 API (sin delay) | JMeter Aggregate Report | <300 ms |
| Errores HTTP bajo carga | JMeter | 0% |
| Score accesibilidad | Axe/Lighthouse | ≥90%, 0 críticas |
| Disponibilidad mensual | monitoreo externo | ≥99.5% |
| Trazabilidad ERS | matriz sección 5 | 100% de ID |

### 3.5 Herramientas, recursos y ambiente

| Herramienta | Uso | Justificación |
|---|---|---|
| Postman / Newman | Funcional e integración | Suites HTTP con `Authorization: Bearer`, validación JSON en CI |
| Apache JMeter 5.6 | Carga/estrés | 200 hilos, ramp-up 10 s, Aggregate Report |
| OWASP ZAP | DAST | Spider + active scan: XSS, SQLi, cabeceras, cookies |
| Axe DevTools / Lighthouse | Accesibilidad | WCAG 2.1 AA automatizado en navegador |
| Jest + Supertest | Unitarias/integración | A incorporar (hoy 0 tests en repo) |
| psql / pgAdmin | Verificación BD | Soft delete, contenido de `auditoria`, hashes |
| curl / SSL Labs | TLS y cabeceras | `curl -I`, enumeración de protocolos |
| Docker Compose | Ambiente QA | Réplica aislada del ZIP sin tocar código |

**Recursos humanos:** 1 QA Lead · 1 Pentester · 2 desarrolladores de soporte (corrección de hallazgos fuera de este informe) · 5 adultos mayores (UAT).

**Recursos técnicos:** estación i7/16 GB para JMeter; PCs, tablets y smartphones; Chrome/Firefox/Safari/Edge; certificado SSL/TLS de prueba.

**Entorno:** QA aislado vía `docker-compose.yml` (backend :4444, frontend :3333, Postgres :15442), datos sintéticos del dump, sin acceso a la red operativa (Ley 19.628).

### 3.6 Protocolo de evidencia

| Tipo | Evidencia obligatoria |
|---|---|
| Funcional/API | Captura Postman (status + body), export de colección Newman |
| Seguridad | Reporte HTML ZAP, payloads enviados (`curl`/Postman) |
| Rendimiento | `.jtl` + Aggregate Report, captura CPU/mem, medición con/sin delay |
| Accesibilidad | Reporte Axe + video corto de UAT |
| Auditoría | `SELECT` con `psql` de `auditoria` + intento de `UPDATE` denegado |
| Defectos | ID, caso asociado, pasos, esperado/obtenido, severidad, evidencia |

---

## 4. Diseño de casos de prueba (endpoints reales)

Host de pruebas: `http://localhost:4000` (dev) o `http://localhost:4444` (Docker). Formato uniforme: ID · Nombre · Requerimiento · Prioridad · Objetivo · Precondiciones · Datos · Pasos · Resultado esperado · Criterios · Tipo · Evidencia.

### CP-01 · Autenticación y emisión de JWT

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-01 · Login exitoso y JWT en `/autenticacion/login` |
| **Requerimiento** | RF-1.1, NFR-SEG-2, NFR-SEG-9 · P1 |
| **Objetivo** | Validar autenticación con credenciales válidas y emisión de token firmado. |
| **Precondiciones** | Usuario existe en `usuarios` (dump); API y BD operativas en QA. |
| **Datos** | `POST http://localhost:4000/autenticacion/login` · Body: `{"nombre_usuario": "dr_rojas", "password": "<clave sintética del dump>"}` |
| **Pasos** | 1) Login vía UI (`/login`) o Postman. 2) Verificar respuesta `{"token": "..."}`. 3) Decodificar payload JWT. 4) Usar token en `GET /examenes`. 5) Login con clave incorrecta. 6) Revisar que el log del servidor no contenga la contraseña. |
| **Esperado** | `200 {"token"}`; payload con `usuarioId`, `rolNombre`, `exp`; paso 4 ⇒ `200`; paso 5 ⇒ `401 {"error":"Credenciales inválidas"}`. |
| **Criterios** | 1) Sesión iniciada sin errores. 2) JWT firmado (HS256), `exp` ≤2 h según código actual — **si el ERS exige ≤15 min, registrar discrepancia**. 3) Latencia <300 ms (este endpoint **no** tiene `delayMiddleware`). 4) Contraseña no aparece en logs (**si aparece en BD en claro → hallazgo H-01**). |
| **Tipo/Evidencia** | Funcional + Seguridad · Captura Postman + decodificación JWT + `SELECT contrasena` (¿hash?) |

### CP-02 · Sesión: expiración y refresh token

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-02 · Expiración de JWT y renovación (RF-1.2) |
| **Requerimiento** | RF-1.2, NFR-SEG-9 · P1 |
| **Objetivo** | Verificar que exista renovación de sesión y que el token vencido sea rechazado. |
| **Precondiciones** | Sesión iniciada (CP-01); vida útil del access token conocida (`expiresIn: "2h"` en `auth.js:54`). |
| **Datos** | `GET /examenes` con token vencido · endpoint de refresh: **no existe en el código** — probar `POST /autenticacion/refresh`. |
| **Pasos** | 1) Ejecutar `GET /examenes` con token expirado/falsificado. 2) Intentar `POST /autenticacion/refresh`. 3) Revisar si existe cookie `HttpOnly` de refresh. 4) Revisar `localStorage` del navegador (AuthContext). |
| **Esperado (ERS)** | Token vencido ⇒ `401`; refresh ⇒ nuevo access token; refresh en cookie HttpOnly. |
| **Criterios** | 1) Token vencido jamás autoriza. 2) Existe mecanismo de refresh (RS=**no existe** → incumplimiento RF-1.2, hallazgo H-09). 3) El token no debería vivir en `localStorage`. |
| **Tipo/Evidencia** | Funcional + Seguridad · Traza Postman + inspección de Application/Storage |

### CP-03 · Política de contraseñas (≥12, 4 clases de caracteres)

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-03 · Validación de política de contraseña |
| **Requerimiento** | NFR-SEG-2, RF-1.1 · P2 |
| **Objetivo** | Verificar rechazo de claves débiles en registro/cambio. |
| **Datos** | `POST /autenticacion/registro` con: `hola123` (min(6) pasa en frontend/backend según `validations/auth.js:24` ⇒ **debe fallar por ERS**), `Cort@12345` (<12), `abcdefghijkl`, `Cuidarte2026!#` (válida). También `PUT /usuarios/:id` con `contrasena_hash`. |
| **Pasos** | 1) Enviar cada clave débil directo a la API (saltarse UI). 2) Enviar clave válida. 3) Verificar en BD el almacenamiento resultante. |
| **Esperado (ERS)** | Claves <12 o sin combinación ⇒ `400` con mensaje de política; válida ⇒ `201`; en BD solo hash bcrypt. |
| **Criterios** | 1) Validación server-side (si solo existe en UI ⇒ fallo). 2) Política real del código es `min(6)` ⇒ **discrepancia ERS**. 3) Ninguna clave en texto plano (ver H-01). |
| **Tipo/Evidencia** | Funcional + Seguridad · Capturas 400/201 + `SELECT contrasena FROM usuarios` |

### CP-04 · Registro de examen médico con adjunto PDF

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-04 · Crear examen + subir documento PDF |
| **Requerimiento** | RF-3.1, RF-4.3, RF-4.4, RB-3 · P1 |
| **Objetivo** | Médico registra examen y adjunta PDF asociado al paciente correcto. |
| **Precondiciones** | Token rol `medico`; paciente ID existente en `pacientes`; archivo `examen_sangre.pdf` 1.5 MB. |
| **Datos** | `POST /examenes` body: `{"tipo_examen_medico_id": 1, "paciente_id": 104, "diagnosis": "...", ...}` · `POST /documentos` multipart: campo `documento` + `examen_medico_id` + `paciente_id`. |
| **Pasos** | 1) UI: ficha paciente ⇒ "Registrar Nuevo Examen" ⇒ guardar. 2) Adjuntar PDF (o `POST /documentos` por Postman). 3) Cronometrar operación total. 4) Verificar `examen_medico`, `documentos_examen` y `auditoria` con `psql`. 5) Descargar con `GET /documentos/:id`. |
| **Esperado** | `201` en ambos; fila en `examen_medico`; BYTEA + `nombre_archivo` en `documentos_examen`; log `EXAMENES_CREAR`/`DOCUMENTOS_CREAR`; descarga `200` con `Content-Disposition`. |
| **Criterios** | 1) `201 Created`. 2) Total <10 s (**ojo:** `POST /examenes` y `POST /documentos` tienen `delayMiddleware(5000)` ⇒ medir y reportar H-13). 3) Examen solo visible desde ficha del paciente asignado. 4) Log antes de responder. |
| **Tipo/Evidencia** | Funcional/Integración · Capturas 201 + `SELECT` + cronómetro |

### CP-05 · CRUD de pacientes por rol autorizado

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-05 · Alta/consulta/edición de pacientes |
| **Requerimiento** | RF-2.1 a RF-2.7, RF-2.2, Ley 19.628 · P2 |
| **Objetivo** | Solo Médico/Admin crean y editan pacientes; RUT validado con `rut.js`. |
| **Datos** | `POST /pacientes` (RUT válido `12.345.678-9` e inválido `12.345.678-0`) · `PUT /pacientes/:id` · `GET /pacientes/:id`. |
| **Pasos** | 1) Como `medico`: crear paciente RUT válido. 2) RUT inválido ⇒ ¿`400`? 3) Editar teléfono. 4) Como `paciente`: intentar `POST /pacientes`. 5) Como `paciente`: `GET /pacientes/:id` de otro ⇒ `403`. |
| **Esperado** | 1) `201`; 2) `400`; 3) `200`; 4) `403`; 5) `403`. |
| **Criterios** | 1) Validación de RUT módulo 11 en backend. 2) Ningún dato de terceros en respuestas a paciente. 3) Toda mutación genera `auditoria` (`PACIENTES_*`). |
| **Tipo/Evidencia** | Funcional + RBAC · Traza Postman de 5 requests |

### CP-06 · RBAC: paciente solo ve sus propios exámenes y documentos

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-06 · Denegación de acceso a datos de terceros (RB-1) |
| **Requerimiento** | RF-4.1, RF-4.2, RB-1, NFR-SEG-4, Ley 20.584 · P1 |
| **Objetivo** | `paciente_juan` descarga lo suyo y es bloqueado hacia pacientes/exámenes ajenos. |
| **Precondiciones** | Token rol `paciente`; existen examen propio y de otro paciente; IDs de documento propio y ajeno. |
| **Datos** | `GET /examenes` (lista filtrada) · `GET /examenes/paciente/105` · `GET /examenes/:id_ajeno` · `GET /documentos/:id_ajeno` · sin token. |
| **Pasos** | 1) Login paciente. 2) `GET /examenes` ⇒ solo suyos (línea `examenes.js:144-162`). 3) `GET /examenes/paciente/105` ⇒ `403 "Solo puede ver sus propios exámenes"`. 4) `GET /documentos/:id_ajeno` ⇒ `403`. 5) Repetir sin Authorization ⇒ `401`. |
| **Esperado** | 2) solo registros propios; 3)-4) `403 {"error":"No autorizado"}`; 5) `401`. Cero datos clínicos de terceros en el body. |
| **Criterios** | 1) Cero fuga inter-paciente (Ley 20.584). 2) Denegación en backend (manipular URL no basta). 3) Intentos denegados auditables. |
| **Tipo/Evidencia** | Seguridad/RBAC · Traza Postman de 5 requests + respuesta JSON |

### CP-07 · RBAC: paciente no muta exámenes ni escala privilegios

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-07 · Restricción de mutaciones y escalada de privilegios |
| **Requerimiento** | RB-2, RB-3, RF-3.1, NFR-SEG-4 · P1 |
| **Objetivo** | Paciente no crea/edita/borra exámenes ni usuarios, y no puede alterar `usuario_id` de su ficha. |
| **Datos** | Con token `paciente`: `POST /examenes`, `PUT /examenes/:id`, `DELETE /examenes/:id`, `POST /usuarios` con `rol_id` de admin, `PUT /pacientes/:id` cambiando `usuario_id`, `DELETE /usuarios/:id`. |
| **Pasos** | 1) Enviar cada mutación con JWT de paciente. 2) Verificar BD tras cada intento. 3) Intento de auto-promoción vía `PUT /usuarios/:id` con `rol_id`. |
| **Esperado (ERS)** | Todo ⇒ `403`; BD intacta; `usuario_id` sin cambios. |
| **Criterios** | 1) Rol evaluado en backend. 2) **Si `POST /usuarios` devuelve `201` ⇒ H-02**; **si `PUT /pacientes` cambia `usuario_id` ⇒ H-10**; **si `DELETE /usuarios` responde `200` sin token ⇒ H-03**. 3) Cobertura matriz 2.2.1 para `paciente`. |
| **Tipo/Evidencia** | Seguridad/RBAC · Traza Postman + `SELECT` posterior |

### CP-08 · Eliminación de examen: soft delete + auditoría

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-08 · Borrado lógico con modal y log en `auditoria` |
| **Requerimiento** | RF-3.3, RF-5.1, Ley 19.628 · P1 |
| **Objetivo** | Confirmar soft delete previo modal y registro completo del evento. |
| **Datos** | `DELETE /examenes/:id` · modal "Sí, confirmar eliminación" · SQL: `SELECT id, eliminado FROM examen_medico WHERE id=88;` y `SELECT * FROM auditoria WHERE accion LIKE '%88%';` |
| **Pasos** | 1) UI: ficha ⇒ "Eliminar Examen". 2) Verificar modal. 3) Confirmar. 4) Verificar desaparición en UI. 5) `psql`: examen y auditoría. 6) Cancelar modal en otro examen ⇒ nada cambia. |
| **Esperado (ERS)** | Fila actualizada `eliminado=true` (sin `DELETE FROM`); log con `id_usuario`, `accion="ELIMINACION_LOGICA_EXAMEN"`, `recurso_id`, `timestamp` UTC, `ip_origen`. |
| **Criterios** | 1) **El código usa `DELETE FROM examen_medico` (`examenes.js:408`) ⇒ RECHAZADO, hallazgo H-06**. 2) **Esquema `auditoria` no tiene `recurso_id` ni `ip_origen` (`init.sql:88-93`) ⇒ H-12**. 3) Modal presente en UI. 4) Log antes del `200`. |
| **Tipo/Evidencia** | Auditoría/Integridad · Capturas UI + dumps `psql` antes/después |

### CP-09 · Inmutabilidad de la tabla `auditoria`

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-09 · Imposibilidad de alterar la bitácora |
| **Requerimiento** | RF-5.1, NFR-SEG-7, Ley 19.628 · P1 |
| **Objetivo** | Ni la app ni un Admin pueden modificar/borrar registros de auditoría. |
| **Datos** | `UPDATE auditoria SET accion='HACK' WHERE id=1;` `DELETE FROM auditoria WHERE id=1;` con el rol de la aplicación · `SELECT * FROM information_schema.role_table_grants WHERE table_name='auditoria';` |
| **Pasos** | 1) Identificar registro existente. 2) Ejecutar UPDATE/DELETE con credenciales de la app. 3) Releer el registro. 4) Verificar `REVOKE`. 5) Borrar un usuario (`DELETE /usuarios/:id`) y verificar si sus logs quedan `usuario_id NULL`. |
| **Esperado (ERS)** | Ambas sentencias denegadas; registro idéntico; trazabilidad conservada. |
| **Criterios** | 1) append-only real (**hoy no hay REVOKE ⇒ H-12**). 2) FK `ON DELETE SET NULL` anula atribución (**H-07**). 3) Revoke documentado en DDL. |
| **Tipo/Evidencia** | Auditoría/Seguridad · Capturas `psql` + script de permisos |

### CP-10 · Inyección SQL en login

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-10 · SQLi en `/autenticacion/login` |
| **Requerimiento** | NFR-SEG-2, NFR-SEG-5, OWASP A03 · P1 |
| **Objetivo** | Las cadenas maliciosas deben tratarse como literales (consultas parametrizadas `$1`). |
| **Datos** | `POST /autenticacion/login` payloads: `{"nombre_usuario":"' OR '1'='1","password":"' OR '1'='1"}`, `admin'--`, `'; DROP TABLE usuarios;--`. |
| **Pasos** | 1) Enviar payloads por Postman. 2) Active scan ZAP sobre `/autenticacion`. 3) Revisar respuestas y logs. 4) Verificar integridad de `usuarios` (`SELECT count(*)`). |
| **Esperado** | `401 {"error":"Credenciales inválidas"}` ante todos; cero `500`; sin mensajes de PG; tabla intacta. |
| **Criterios** | 1) `401` uniforme. 2) Sin stack traces (**si `glosa` trae `err.message` ⇒ H-15**). 3) ZAP sin SQLi ≥media. 4) `DROP` no ejecutado. **Código usa `$1` ⇒ se espera PASS**. |
| **Tipo/Evidencia** | Seguridad/DAST · Reporte ZAP + capturas |

### CP-11 · XSS en campos clínicos

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-11 · Sanitización anti-XSS en formularios |
| **Requerimiento** | NFR-SEG-5, OWASP A03 · P1 |
| **Objetivo** | Payloads en `diagnosis`, `observaciones`, `notas`, `primer_nombre` no deben ejecutarse. |
| **Datos** | `POST /examenes` con `"diagnosis": "<script>alert('XSS')</script>"` · `POST /pacientes` con `"observaciones_medicas_generales": "<img src=x onerror=alert(1)>"`. |
| **Pasos** | 1) Crear registros con payload ( rol `medico`). 2) Abrir ficha en navegador. 3) ¿Se dispara alert? 4) Revisar JSON crudo y cabecera CSP. |
| **Esperado** | Payload como texto literal; sin ejecución; CSP presente. |
| **Criterios** | 1) Cero ejecución de JS (React escuta ⇒ probable PASS en UI). 2) **Sin cabecera CSP ⇒ H-14**. 3) Backend también escapa/rechaza (defensa en profundidad). |
| **Tipo/Evidencia** | Seguridad/DAST · Captura navegador + reporte ZAP |

### CP-12 · TLS y cabeceras de seguridad

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-12 · TLS 1.2+ y cabeceras HTTP |
| **Requerimiento** | NFR-SEG-1, OWASP A05 · P1 |
| **Objetivo** | Cifrado en tránsito y cabeceras mínimas. |
| **Datos** | `curl -I http://localhost:4000/examenes` · `curl -I https://<qa>/examenes` · SSL Labs · `GET /` y `GET /openapi.json`. |
| **Pasos** | 1) HTTP ⇒ redirect 301. 2) HTTPS ⇒ TLS ≥1.2. 3) Inspeccionar `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`, `Referrer-Policy`. 4) Revisar CORS: respuesta a `Origin: https://evil.example`. |
| **Esperado (ERS)** | Redirect, TLS 1.2/1.3, todas las cabeceras, CORS solo con orígenes de la allowlist. |
| **Criterios** | 1) Sin HTTP aceptado. 2) 100% cabeceras (**hoy: ausentes ⇒ H-14; `cors()` abierto ⇒ H-14**). 3) TLS <1.2 deshabilitado. |
| **Tipo/Evidencia** | Seguridad/Infra · Salidas `curl -I` + informe SSL Labs |

### CP-13 · Carga concurrente de 200 usuarios

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-13 · Latencia y estabilidad con 200 hilos |
| **Requerimiento** | NFR-PERF-1, NFR-PERF-3 · P2 |
| **Objetivo** | Medir API bajo carga; cuantificar el impacto de `delayMiddleware(5000)`. |
| **Precondiciones** | QA Docker aislado; `Cuidarte_LoadTest_200.jmx`; tokens pregenerados. |
| **Datos** | 200 hilos · ramp-up 10 s · 5 min · `GET /autenticacion/login` no aplica (POST); endpoints: `GET /examenes`, `GET /usuarios` (admin), `GET /roles` · con `Authorization: Bearer`. |
| **Pasos** | 1) JMeter ⇒ cargar plan. 2) Corrida A: `GET /examenes` (con delay 5 s). 3) Corrida B: endpoint sin delay (`GET /roles` o `GET /`). 4) Aggregate Report + CPU/memoria. |
| **Esperado (ERS)** | Promedio <300 ms; 0% error; CPU <80%. |
| **Criterios** | 1) Corrida B <300 ms ⇒ base sana. 2) Corrida A ≥5000 ms ⇒ **confirma H-13, incumplimiento NFR-PERF-1/3**. 3) Cero `500` y cero caídas. 4) Sin agotamiento del `Pool` de `pg`. |
| **Tipo/Evidencia** | Rendimiento/Carga · `.jtl` + Aggregate Report A/B + capturas de monitor |

### CP-14 · Carga de SPA y transferencia de adjuntos

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-14 · Carga inicial <2 s y adjuntos ≤10 s |
| **Requerimiento** | NFR-PERF-2, RF-4 · P2 |
| **Objetivo** | Medir render inicial (Nginx + Vite build) y subida/descarga de PDF. |
| **Datos** | URL raíz del frontend (:3333) con throttle Slow 4G · `POST /documentos` (PDF 1.5 MB) · `GET /documentos/:id`. |
| **Pasos** | 1) Lighthouse ×3 corridas en red móvil. 2) Cronometrar subida desde UI. 3) Cronometrar descarga. 4) Comparar hash MD5 del archivo subido vs descargado. |
| **Esperado** | Carga <2 s promedio; transferencias ≤10 s; hash idéntico. |
| **Criterios** | 1) Promedio Lighthouse <2 s. 2) Transferencias ≤10 s (**subida tiene delay 5 s ⇒ medir**). 3) Integridad byte a byte. 4) Verificar volumen `uploads/` persistente en Docker (riesgo de pérdida = análisis sección 4). |
| **Tipo/Evidencia** | Rendimiento · Reportes Lighthouse + cronometrajes + `certutil -hashfile` |

### CP-15 · Accesibilidad y UAT con adultos mayores

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-15 · WCAG 2.1 AA y usabilidad con panel de 5 |
| **Requerimiento** | NFR-USAB-1, NFR-USAB-4, RF-4.1 · P2 |
| **Objetivo** | 5 adultos mayores (>65) completan "login → paciente → exámenes → descargar PDF" sin ayuda. |
| **Datos** | Credenciales sintéticas; módulos: `Login.jsx`, `PacientesList.jsx`, `MisResultados.jsx`; Axe DevTools; tablet + laptop. |
| **Pasos** | 1) Axe en `/login`, lista de pacientes y `MisResultados`. 2) Cada evaluador inicia sesión. 3) Busca paciente/examen. 4) Descarga PDF. 5) Registrar tiempos/dudas; probar solo teclado (Tab/Enter/Esc). |
| **Esperado** | 0 violaciones críticas Axe; 5/5 completan; texto >12 px; contraste ≥4.5:1; targets ≥48 px. |
| **Criterios** | 1) 5/5 sin asistencia. 2) Score Axe ≥90% sin críticas. 3) Flujo 100% por teclado (`RoleGuard.jsx` no debe romper la navegación). 4) Video por evaluador. |
| **Tipo/Evidencia** | Usabilidad/Accesibilidad · Reporte Axe + videos + fichas de observación |

### CP-16 · Compatibilidad de navegadores y dispositivos

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-16 · Matriz de compatibilidad |
| **Requerimiento** | NFR-COMPAT-1, NFR-COMPAT-2 · P3 |
| **Objetivo** | Flujo reducido en 4 navegadores × 3 dispositivos. |
| **Datos** | Chrome, Firefox, Safari, Edge (2 últimas versiones) × escritorio/tablet/móvil; flujo: login ⇒ lista ⇒ descarga. |
| **Pasos** | 1) Ejecutar flujo por combinación (12). 2) Verificar responsividad (Tailwind) y modales. 3) Consola del navegador sin errores JS. |
| **Esperado** | 100% combinaciones operativas. |
| **Criterios** | 1) Cero bloqueos. 2) Sin scroll horizontal no intencional. 3) Consola limpia. |
| **Tipo/Evidencia** | Compatibilidad · Matriz de resultados + capturas |

### CP-17 · Disponibilidad 99.5% y restauración de respaldos

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-17 · Uptime y prueba de backup |
| **Requerimiento** | NFR-DIS-1, NFR-DIS-2, NFR-SEG-7 · P2 |
| **Objetivo** | Verificar disponibilidad mensual y restaurabilidad de BD + uploads. |
| **Datos** | `GET /` (healthcheck `{"name":"cuidarteplus","status":"ok"}`) monitoreado cada 60 s por 30 días · dump `dump-cuidarteplus.sql` · volumen de `BACKEND/uploads/`. |
| **Pasos** | 1) Extraer histórico de monitoreo. 2) Calcular uptime. 3) Restaurar dump en BD descartable. 4) Verificar conteos (`usuarios`, `pacientes`, `examen_medico`, `documentos_examen`). 5) Verificar que `uploads/` sobrevive restart de Docker (volumen). |
| **Esperado** | Uptime ≥99.5% (máx. ~3 h 39 min caído/mes); restauración sin pérdida; uploads persistentes. |
| **Criterios** | 1) ≥99.5%. 2) Checksums/conteos idénticos. 3) **Si `uploads/` se pierde al redesplegar ⇒ riesgo confirmado del análisis estructural**. 4) Runbook de rollback. |
| **Tipo/Evidencia** | Disponibilidad/Operación · Dashboard + log de restauración |

### CP-18 · Autenticación obligatoria en endpoints mutantes

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-18 · Endpoints de mutación sin token ⇒ `401/403` |
| **Requerimiento** | NFR-SEG-4, RB-2 · P1 |
| **Objetivo** | Verificar que **toda** mutación exija JWT + rol adecuado (matriz 2.2.1). |
| **Datos** | **Sin header Authorization:** `DELETE /usuarios/1`, `DELETE /roles/1`, `POST /roles {"nombre":"hacker"}`, `PUT /roles/1`, `GET /usuarios`, `GET /auditoria`, `GET /pacientes/buscar/rut/12.345.678-9`. |
| **Pasos** | 1) Enviar cada petición con `curl` sin token. 2) Con token de `paciente`: `POST /usuarios` con `rol_id` admin. 3) Con token de `medico`: `PUT /usuarios/:id` cambiando su `rol_id` a admin. 4) Verificar BD después de cada intento. |
| **Esperado (ERS)** | Todo ⇒ `401` sin token / `403` con rol insuficiente; cero cambios en BD. |
| **Criterios** | 1) `DELETE /usuarios` sin token **debe** dar `401` (**hoy ejecuta el borrado ⇒ H-03 CRÍTICO**). 2) `/roles` mutaciones sin token ⇒ `401` (**hoy `200/201` ⇒ H-04**). 3) Búsqueda RUT sin token ⇒ `401` (**hoy devuelve ficha completa ⇒ H-05**). 4) `POST /usuarios` con paciente ⇒ `403` (**hoy `201` ⇒ H-02**). 5) Auto-promoción médico ⇒ `403` (**hoy posible ⇒ H-11**). |
| **Tipo/Evidencia** | Seguridad/Penetración · Traza `curl`/Postman con y sin token + `SELECT` de BD |

### CP-19 · Exposición de información y configuración

| Campo | Contenido |
|---|---|
| **ID/Nombre** | CP-19 · Disclosure de API, Swagger y errores |
| **Requerimiento** | NFR-SEG-1, NFR-SEG-5, criterio "sin stack trace" · P2 |
| **Objetivo** | Cuantificar qué información expone la API sin autenticación y en errores. |
| **Datos** | `GET /`, `GET /openapi.json`, `GET /docs` · payloads inválidos `POST /pacientes` campo faltante · trigger de error 500 (id no numérico en `GET /examenes/abc`). |
| **Pasos** | 1) Catalogar endpoints públicos vía `/openapi.json`. 2) Enviar body inválido ⇒ leer `detalles`. 3) `GET /examenes/abc` (cast a BIGINT) ⇒ leer `glosa`. 4) Revisar `.env` presentes en el ZIP entregado. |
| **Esperado (ERS)** | Swagger puede ser público en QA; errores `500` genéricos; cero secretos en el paquete. |
| **Criterios** | 1) `glosa` con `err.message` de PostgreSQL ⇒ **H-15**. 2) Endpoints públicos coherentes con matriz 2.2.1 (`/roles` GET aceptable, mutaciones no). 3) `.env` con `JWT_SECRET` y password de BD en el ZIP ⇒ **H-08**. |
| **Tipo/Evidencia** | Seguridad/Configuración · Capturas de respuestas + listado de archivos `.env` |

---

## 5. Matriz de trazabilidad y cobertura

| ID Requerimiento ERS | Tipo | Tipo de prueba | Control normativo | Caso(s) |
|---|---|---|---|---|
| RF-1.1 (Login) | Funcional | Funcional + Seguridad | NFR-SEG-2/9, bcrypt | CP-01, CP-03, CP-10 |
| RF-1.2 (Refresh) | Funcional | Funcional + Seguridad | NFR-SEG-9 | CP-02 |
| RF-2.1 a RF-2.7 | Funcional | Funcional/Integración + RBAC | Ley 19.628 | CP-05, CP-18 |
| RF-3.1 / RF-3.2 | Funcional | Funcional | Ley 20.584 | CP-04, CP-07 |
| RF-3.3 (Soft delete) | Funcional | Integridad/Auditoría | Modal + soft delete | CP-08 |
| RF-4.1 / RF-4.2 | Funcional | Funcional/RBAC | Ley 20.584 | CP-06, CP-15 |
| RF-4.3 / RF-4.4 | Funcional | Funcional/Almacenamiento | Adjuntos PDF/imagen | CP-04, CP-14 |
| RF-5.1 (Auditoría) | Funcional | Auditoría e integridad | Log inmutable + IP | CP-08, CP-09 |
| NFR-SEG-1 | No funcional | Seguridad DAST | TLS 1.2+, OWASP A05 | CP-12, CP-19 |
| NFR-SEG-2 | No funcional | Seguridad + Funcional | OWASP A07 | CP-01, CP-03, CP-10 |
| NFR-SEG-3 | No funcional | Seguridad/Infra | Datos sensibles reposo | CP-14, CP-17 |
| NFR-SEG-4 | No funcional | Seguridad/RBAC | Ley 20.584, RB-1/2/3 | CP-06, CP-07, CP-18 |
| NFR-SEG-5 | No funcional | Seguridad DAST/SAST | OWASP A03 | CP-10, CP-11, CP-12 |
| NFR-SEG-7 | No funcional | Disponibilidad/Operación | Backups | CP-17 |
| NFR-SEG-9 | No funcional | Seguridad | OWASP A07 | CP-01, CP-02 |
| NFR-PERF-1 | No funcional | Rendimiento | Latencia <300 ms | CP-13 |
| NFR-PERF-2 | No funcional | Rendimiento | Lighthouse móvil | CP-14 |
| NFR-PERF-3 | No funcional | Rendimiento/carga | 200 usuarios | CP-13 |
| NFR-USAB-1 / 4 | No funcional | Usabilidad/Accesibilidad | WCAG 2.1 AA | CP-15 |
| NFR-COMPAT-1 / 2 | No funcional | Compatibilidad | Navegadores/dispositivos | CP-16 |
| NFR-DIS-1 / 2 | No funcional | Disponibilidad | Uptime 99.5%/rollback | CP-17 |
| RB-1 | Regla negocio | Control de acceso | Ley 20.584 | CP-06 |
| RB-2 | Regla negocio | Control de acceso | Ley 19.628 | CP-07, CP-18 |
| RB-3 | Regla negocio | Control de acceso | Ley 20.584 | CP-04, CP-07 |

**Cobertura: 11 RF + 14 NFR + 3 RB = 28/28 ID (100%) en 19 casos.**

---

## 6. Conclusión

El plan se apoya en dos pilares: (1) la especificación ERS v1.1 como **criterio de verdad**, y (2) el análisis estático del código real `CodigoFuenteB` como **conocimiento de los riesgos** — sin modificar una línea del software.

**Fortalezas del plan:**

1. **Trazabilidad cerrada 100%** sin IDs huérfanos ni casos sin requerimiento.
2. **Matriz RBAC 2.2.1 como oracle**: cada denegación es objetiva, no opinable.
3. **Casos sobre endpoints reales** (`/autenticacion/login`, `/examenes/paciente/:id`, `/pacientes/buscar/rut/:rut`…): ejecutables tal cual contra el Docker del ZIP.
4. **Casos destructivos aislados** (CP-18) que convierten los hallazgos críticos en evidencia reproducible.
5. **Rendimiento A/B (CP-13)** que separa la salud real de la API del efecto artificial de `delayMiddleware(5000)`.

**Recomendaciones de ejecución:**

- Correr P1 completo primero: los casos CP-02, CP-07, CP-08, CP-09, CP-18 y CP-19 se esperan **RECHAZADOS** con hallazgos H-02…H-12 — eso es la evidencia de la evaluación, no un error del plan.
- Automatizar lo que hoy no existe: Jest+Supertest y Newman desde el día 1.
- Mantener el dump como seeding reproducible entre corridas de ZAP.
- Re-ejecutar CP-15 (UAT adultos mayores) en cada release: es el control de mayor riesgo reputacional.

Con esta estrategia, CreaLab SpA obtiene un plan de pruebas **verificable, trazable y alineado** con ISO/IEC 25010, OWASP Top 10 y las Leyes N° 19.628 y N° 20.584 de la República de Chile.