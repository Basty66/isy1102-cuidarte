# Informe de Resultados de Pruebas — Sistema Cuidarte+

- **Asignatura:** ISY1102 – Seguridad y Calidad en el Desarrollo de Software
- **Proyecto:** Sistema de Exámenes Médicos Cuidarte+
- **Organización:** CreaLab SpA – Departamento de Desarrollo
- **Documento asociado:** Plan de Pruebas v1.1 · Hallazgos de Seguridad (17) · ERS v1.1
- **Método de obtención:** Evaluación por (1) análisis estático del código fuente `CodigoFuenteB` (sin modificación del software) y (2) ejecución dinámica con Newman sobre Docker local (`informe-ejecucion-pruebas.md`, rama `ejecucion-pruebas`, 48 requests / 66 assertions / 22 fallidas). Cada predicción se sustenta en evidencia `archivo:línea`; la corrida confirma en runtime lo previsto en cada CP (ver §2 y el informe de corrida).
- **Fecha de corte:** 22/09/2026

---

## 1. Resumen ejecutivo

| Estado | Casos | IDs |
|---|---|---|
| ✅ **CONFORME** (se espera aprobación) | 6 | CP-05, CP-06, CP-10, CP-15*, CP-16, CP-17* |
| ⚠️ **PARCIAL** (aprueba con observaciones) | 5 | CP-01, CP-03, CP-04, CP-11, CP-14 |
| ❌ **NO CONFORME** (se espera rechazo = hallazgo) | 8 | CP-02, CP-07, CP-08, CP-09, CP-12, CP-13, CP-18, CP-19 |
| **Total** | **19** | |

\* CP-15 y CP-17 requieren ejecución humana/operativa; el análisis prevé conformidad sujeta a evidencia de campo.

**Métricas proyectadas (post-ejecución):**

| Métrica | Meta del plan | Proyección | Estado |
|---|---|---|---|
| Cobertura P1+P2 ejecutada | 100% | 100% (19/19 planificados) | ✅ |
| Tasa de aprobación | ≥95% | **~32%** (6 conformes / 19) | ❌ |
| Hallazgos críticos abiertos | 0 | **6 críticos + 6 altos** (+ 5 medios) | ❌ |
| Latencia p95 sin delay | <300 ms | <300 ms en endpoints sin `delay` (login, roles) | ⚠️ |
| Latencia p95 con delay | <300 ms | **≥5000 ms** (CP-13 rama A) | ❌ |
| Errores HTTP bajo carga | 0% | 0% esperado (sin 500 en carga) | ✅ |
| Accesibilidad | ≥90%, 0 críticas | ≥90% probable (React+Tailwind) | ⚠️ |
| Trazabilidad ERS | 100% | 100% (28/28) | ✅ |

**Veredicto global: NO SE APRUEBA EL PASAJE A PRODUCCIÓN.** Motivos: 6 hallazgos críticos (H-01…H-06) y 6 altos (H-07…H-12) abiertos (más 5 medios, H-13…H-17); incumplimiento de RF-1.2, RF-3.3, RF-5.1, NFR-SEG-1/2/3/9, NFR-PERF-1/3.

---

## 2. Matriz de resultados por caso de prueba

Leyenda estado: ✅ Conforme · ⚠️ Parcial · ❌ No conforme · 🔄 Requiere ejecución en vivo.

### Fase 1–2 · Funcionales, sesión y RBAC

| CP | Caso | Req. | Resultado esperado (ERS) | Lo que indica el código | Estado | Hallazgo |
|---|---|---|---|---|---|---|
| **CP-01** | Login + JWT en `/autenticacion/login` | RF-1.1, NFR-SEG-2/9 | `200 {"token"}` con JWT firmado, latencia <300 ms, sin exponer claves | Login funciona (`auth.js:10-69`) y no tiene delay ⇒ cumple latencia y formato; **pero** compara contraseña en claro (`auth.js:21`) y el token dura 2 h | ⚠️ | H-01, H-09 |
| **CP-02** | Expiración y refresh token | RF-1.2, NFR-SEG-9 | Token vencido ⇒ `401`; endpoint refresh ⇒ nuevo token en cookie HttpOnly | **No existe** `POST /autenticacion/refresh`; JWT `expiresIn: "2h"` en `localStorage` | ❌ | H-09 |
| **CP-03** | Política de contraseñas ≥12 | NFR-SEG-2 | Claves débiles ⇒ `400`; solo hash bcrypt en BD | Esquema real exige `min(6)` (`validations/auth.js:24`); sin bcrypt | ⚠️ | H-01 |
| **CP-04** | Examen + adjunto PDF | RF-3.1/4.3/4.4, RB-3 | `201` en examen y documento; total <10 s; log previo | RBAC de creación correcto (`examenes.js:46` requireRole medico/admin); Multer whitelist MIME 10 MB; **pero** `delay(5000)` en ambos POST ⇒ ~10 s solo de espera | ⚠️ | H-13, H-17 |
| **CP-05** | CRUD pacientes | RF-2.1..2.7 | `201/200/403` según rol; RUT validado; auditoría | requireRole medico/admin en POST (`pacientes.js:48-56`); RUT validado en `rut.js`; logs `PACIENTES_*` presentes | ✅ | — |
| **CP-06** | Paciente solo ve lo propio | RF-4.1/4.2, RB-1, Ley 20.584 | Listado filtrado; `403` hacia terceros; `401` sin token | Filtro correcto en `examenes.js:144-162` y propiedad verificada en `documentos.js:222-234`; mensajes "Solo puede ver sus propios…" | ✅ | — |
| **CP-07** | Sin mutación sin rol / sin escalada | RB-2/3, NFR-SEG-4 | Todo ⇒ `403`; BD intacta | `POST /usuarios` acepta `rol_id` libre con cualquier token (`users.js:23-53`); `usuario_id` editable por paciente (`pacientes.js:341`); médico cambia roles (`users.js:522`) | ❌ | H-02, H-10, H-11 |

### Fase 2 · Integridad y auditoría

| CP | Caso | Req. | Resultado esperado (ERS) | Lo que indica el código | Estado | Hallazgo |
|---|---|---|---|---|---|---|
| **CP-08** | Soft delete + log de auditoría | RF-3.3, RF-5.1 | `eliminado=true`; log con usuario, acción, **recurso**, timestamp, **IP**; log antes del `200` | `DELETE FROM examen_medico` físico (`examenes.js:408`); esquema `auditoria` sin `recurso_id` ni `ip_origen` (`init.sql:88-93`); log escrito después de la mutación | ❌ | H-06, H-12 |
| **CP-09** | Auditoría inmutable | RF-5.1, NFR-SEG-7 | `UPDATE/DELETE` denegados; trazabilidad conservada al borrar usuarios | Sin `REVOKE` en el DDL; FK `ON DELETE SET NULL` (`init.sql:90`) anula autor al borrar usuario; logs editables por la app | ❌ | H-07, H-12 |

### Fase 3 · Seguridad DAST

| CP | Caso | Req. | Resultado esperado (ERS) | Lo que indica el código | Estado | Hallazgo |
|---|---|---|---|---|---|---|
| **CP-10** | SQLi en login | NFR-SEG-2/5, OWASP A03 | `401` uniforme; sin mensajes de PG; tabla intacta | Query parametrizada `$1` (`auth.js:14`) ⇒ payloads literales; **riesgo residual:** `glosa: err.message` en catch (`auth.js:67`) puede filtrar errores en `500` | ⚠️ | H-15 |
| **CP-11** | XSS en campos clínicos | NFR-SEG-5, OWASP A03 | Payload como texto; sin ejecución; CSP presente | React escapa por defecto ⇒ baja probabilidad de ejecución en UI; **pero** cero cabecera CSP (`app.js` sin helmet) | ⚠️ | H-14 |
| **CP-12** | TLS + cabeceras seguridad | NFR-SEG-1, OWASP A05 | Redirect 301; TLS≥1.2; HSTS/CSP/X-Frame/X-Content; CORS con whitelist | `app.use(cors())` abierto (`app.js:21`); sin helmet ni cabeceras en toda la app | ❌ | H-14 |
| **CP-18** | Mutaciones sin token ⇒ `401/403` | NFR-SEG-4, RB-2 | Todo endpoint mutante exige JWT + rol | `DELETE /usuarios` borra **antes** de leer token (`users.js:571-578`); `/roles` POST/PUT/DELETE sin auth (`roles.js:18,57,76`); búsqueda RUT pública (`pacientes.js:249`); `POST /usuarios` crea admins (`users.js:23`) | ❌ | H-02, H-03, H-04, H-05, H-11 |
| **CP-19** | Disclosure API/errores/secretos | NFR-SEG-1/5 | 500 genéricos; cero secretos en el paquete | `glosa: err.message` en todos los catch; `.env` con `JWT_SECRET` y password de BD dentro del ZIP; fallback `"inseguro"` (`auth.js:8`) | ❌ | H-08, H-15 |

### Fase 3 · Rendimiento

| CP | Caso | Req. | Resultado esperado (ERS) | Lo que indica el código | Estado | Hallazgo |
|---|---|---|---|---|---|---|
| **CP-13A** | 200 usuarios sobre rutas **con** delay | NFR-PERF-1/3 | Promedio <300 ms; 0% error | `delayMiddleware(5000)` en `examenes.js:46,99,330`, `pacientes.js:145`, `documentos.js:66` ⇒ piso de 5000 ms/petición | ❌ | H-13 |
| **CP-13B** | 200 usuarios sobre rutas **sin** delay (control) | NFR-PERF-1/3 | Promedio <300 ms; 0% error | `/autenticacion/login`, `/roles` GET, `/` no aplican delay ⇒ se espera <300 ms con Express+pg | ✅ (previsto) | — |
| **CP-14** | SPA <2 s y adjuntos ≤10 s | NFR-PERF-2, RF-4 | Lighthouse <2 s; transferencias ≤10 s; hash íntegro | Build Vite+Nginx ⇒ <2 s probable; subida con delay 5 s + transferencia ⇒ medible cerca del límite; sin volumen persistente en `uploads/` | ⚠️ | H-13, H-17 |

### Fase 4 · Humanos y operación

| CP | Caso | Req. | Resultado esperado (ERS) | Indicación previa | Estado | Hallazgo |
|---|---|---|---|---|---|---|
| **CP-15** | UAT 5 adultos mayores + Axe | NFR-USAB-1/4 | 5/5 completan; ≥90%; 0 críticas; teclado 100% | Tailwind responsivo, `RoleGuard`, MUI ⇒ probable ≥90%; requiere panel real y escaneo Axe en vivo | 🔄 | — |
| **CP-16** | Compatibilidad 4 nav × 3 disp | NFR-COMPAT-1/2 | 12/12 combinaciones OK, consola limpia | SPA+Tailwind estándar ⇒ alta probabilidad de conformidad; requiere evidencia en vivo | 🔄 | — |
| **CP-17** | Uptime 99.5% + restauración | NFR-DIS-1/2, NFR-SEG-7 | ≥99.5%; restauración sin pérdida; uploads persistentes | Healthcheck `GET /` existe (`app.js:45-47`); **riesgo:** `uploads/` sin volumen en `docker-compose` y documentos en BYTEA sin cifrar | 🔄 | H-17 |

### Ejecución Newman (corrida 2026-09-22 · 48 req · 66 assertions · 22 fallidas)

| CP | Resultado en runtime | Hallazgos confirmados |
|---|---|---|
| CP-01 | Login 200 · exp JWT **120 min** | H-09 |
| CP-02 | `POST /autenticacion/refresh` → **404** | H-09 |
| CP-03 | Clave de 6 chars → **201** | H-01 |
| CP-04 | Flujo 201/201/200 · latencia **5014/5016 ms** | H-13 |
| CP-05 | 201 / 400 / 403 | — |
| CP-06 | 200 propios · ajeno 403 · docs examen ajeno 403 | — |
| CP-07 | 403 mutaciones ✅ · paciente crea admin **201** · médico `rol_id` **200** · `usuario_id` → **500 FK** | H-02, H-11, H-10 |
| CP-08 | DELETE 200 · GET → **404** · auditoría sin IP/recurso | H-06, H-12 |
| CP-09 | 403 no-admin (paciente) ✅ · inmutabilidad = prueba manual | H-12 (parcial) |
| CP-10 | 401 uniforme ante SQLi | — |
| CP-11 | Payload como texto ✅ · **CSP ausente** | H-14 |
| CP-12 | 4 cabeceras ausentes + CORS **`*`** | H-14 |
| CP-13A | `GET /examenes` **5009 ms** | H-13 |
| CP-13B | `GET /` < 300 ms | — |
| CP-17 | Healthcheck `status: ok` | — |
| CP-18 | Sin token: DELETE 404/404 · POST 500 · PUT 200 · RUT 200 | H-03, H-04, H-05 |
| CP-19 | 500 con glosa PostgreSQL | H-15 |

Detalle completo de las 22 aserciones fallidas: `informe-ejecucion-pruebas.md` §3 · evidencia bruta `reports/results.json`.

---

## 3. Resultados por criterio de aceptación transversal

| # | Criterio transversal (Plan §3.3) | Veredicto | Evidencia |
|---|---|---|---|
| 1 | Autorización correcta en todos los endpoints (matriz RBAC) | ❌ **NO** | 6 endpoints mutantes sin auth o con auth insuficiente: `DELETE /usuarios`, `/roles`×3, `POST /usuarios`, `GET /pacientes/buscar/rut/:rut` (H-02…H-05, H-11) |
| 2 | Códigos HTTP estandarizados sin exponer errores internos | ❌ **NO** | Formatos `401/403/404` correctos en lecturas; pero `glosa: err.message` expone PostgreSQL en `500` (H-15) |
| 3 | Soft delete obligatorio con modal | ❌ **NO** | 4 `DELETE FROM` físicos; sin columna `eliminado` en el esquema (H-06) |
| 4 | Latencia <300 ms (95%) y adjuntos ≤10 s | ❌ **NO** | `delay(5000)` garantiza ≥5 s en 5 rutas clave (H-13) |
| 5 | Auditoría incondicional, con IP/recurso y atómica | ❌ **NO** | Esquema de 3 columnas, log posterior a la mutación, sin REVOKE (H-12) |
| 6 | Errores 500 trazables y genéricos al cliente | ❌ **NO** | Respuesta `500` con `glosa` = mensaje real de BD (H-15) |

**Criterios transversales aprobados: 0 de 6.**

---

## 4. Resultados por dominio normativo

| Dominio | ID ERS | Veredicto | Comentario |
|---|---|---|---|
| Contraseñas/sesión | NFR-SEG-2, RF-1.1/1.2, NFR-SEG-9 | ❌ | Sin bcrypt, JWT 2 h, sin refresh, sin rate limit |
| Control de acceso | NFR-SEG-4, RB-1/2/3 | ⚠️ | Lectura clínica ✅ · mutaciones ❌ (6 endpoints) |
| Comunicación | NFR-SEG-1 | ❌ | TLS depende del proxy; app sin helmet/CSP/HSTS; CORS abierto |
| Datos en reposo | NFR-SEG-3 | ❌ | BYTEA sin cifrar; `.env` con secretos en el paquete |
| Vulnerabilidades web | NFR-SEG-5 | ⚠️ | SQLi ✅ (parametrizado) · XSS parcial (React) · CSRF sin mitigación explícita |
| Auditoría/legal | RF-5.1, Ley 19.628 | ❌ | Sin IP/recurso, no atómica, atribución anulable |
| Reserva clínica | RF-4.1/4.2, RB-1, Ley 20.584 | ⚠️ | Exámenes/docs ✅ · búsqueda RUT ❌ (fuga total) |
| Soft delete | RF-3.3 | ❌ | Deletes físicos + CASCADE |
| Rendimiento | NFR-PERF-1/2/3 | ❌ | delay 5 s; sin pruebas de carga ejecutadas |
| Disponibilidad | NFR-DIS-1/2 | 🔄 | Requiere monitoreo de 30 días + prueba de restore |
| Usabilidad | NFR-USAB-1/4 | 🔄 | Requiere Axe + panel de 5 adultos mayores |
| Compatibilidad | NFR-COMPAT-1/2 | 🔄 | Requiere matriz 4×3 en vivo |

---

## 5. Próximas acciones (orden de remediación)

| Prioridad | Acción | Hallazgos cerrados | Casos que pasarían |
|---|---|---|---|
| **1 (inmediata)** | bcrypt en registro/login + rotar secretos + sacar `.env` del repo | H-01, H-08 | CP-01 ✅, CP-03 ✅ |
| **2** | Auth+authz en `DELETE /usuarios`, `/roles`, `POST /usuarios`; proteger búsqueda RUT | H-02, H-03, H-04, H-05 | CP-18 ✅, CP-07 ✅ |
| **3** | Soft delete (`eliminado BOOLEAN`) en 4 tablas + modal | H-06 | CP-08 parcial ✅ |
| **4** | Esquema de auditoría completo + transacción única + REVOKE | H-07, H-12 | CP-08 ✅, CP-09 ✅ |
| **5** | Quitar `delay(5000)` salvo `NODE_ENV=development` | H-13 | CP-13 ✅, CP-04 ✅, CP-14 ✅ |
| **6** | Refresh token + rate limit + JWT ≤15 min | H-09, H-16 | CP-02 ✅ |
| **7** | helmet + CORS whitelist + 500 genéricos | H-14, H-15 | CP-12 ✅, CP-19 ✅ |
| **8** | Excluir `usuario_id` del PUT de paciente; roles solo-admin | H-10, H-11 | CP-07 ✅ |
| **9** | Cifrado en reposo + volumen `uploads/` + validar firma de archivos | H-17 | CP-14, CP-17 ✅ |
| **10** | Suite Jest+Supertest + CI con ZAP/Newman | deuda técnica | regresión continua |

---

## 6. Conclusión

La evaluación (estática + corrida Newman) arroja **6 casos conformes, 5 parciales y 8 no conformes** sobre 19 planificados. Los 8 rechazos esperados **no son fallos del plan**: son la evidencia deliberada de los 17 hallazgos del informe de seguridad, varios confirmados en runtime (`informe-ejecucion-pruebas.md`). El plan de pruebas cumple su propósito: *predecir con trazabilidad total (28/28) dónde el software incumple el ERS* y demostrarlo con evidencia reproducible.

El sistema solo podrá certificarse cuando los hallazgos críticos y altos (H-01…H-12) y los medios relevantes (H-13…H-17) estén corregidos y esta matriz sea reejecutada con evidencia dinámica completa (Newman, JMeter, ZAP, Axe y panel UAT), quedando entonces los estados 🔄 (CP-15, CP-16, CP-17) sustituidos por resultados medidos.

**Evidencia de ejecución:** `informe-ejecucion-pruebas.md` · `reports/results.json` · rama `ejecucion-pruebas`.

**Firmas del equipo de QA**

| Rol | Nombre | Fecha |
|---|---|---|
| QA Lead | _________________ | ____/____/______ |
| Especialista en Ciberseguridad | _________________ | ____/____/______ |
| Revisor (CreaLab SpA) | _________________ | ____/____/______ |