# Presentación — Seguridad y Calidad en el Desarrollo de Software

**ISY1102 · Sistema de Exámenes Médicos Cuidarte+ · CreaLab SpA**

Slides separados por `---` (formato Marp/reveal; importable a PowerPoint o Google Slides: copiar cada bloque como una diapositiva).

---

## 1. Portada

**Seguridad y Calidad en el Desarrollo de Software**

- Asignatura: ISY1102
- Proyecto: Sistema de Exámenes Médicos **Cuidarte+**
- Organización: CreaLab SpA – Departamento de Desarrollo
- Sección: XX
- Integrantes:
  - Nombre Apellido Alumno 1
  - Nombre Apellido Alumno 2
  - Nombre Apellido Alumno 3

Documento base: ERS v1.1 + análisis estático de `CodigoFuenteB` (solo lectura)

---

## 2. Qué es Cuidarte+

Plataforma web médica multicapa para centros de salud:

- **Gestión de pacientes** con ficha clínica completa (RUT, alergias, crónicos)
- **Exámenes médicos** con documentos adjuntos (PDF/JPG/PNG)
- **Auditoría** de acciones críticas
- **3 roles:** admin · medico · paciente

> Los datos son sensibles: **Ley N° 19.628** (datos personales) y **Ley N° 20.584** (reserva de la ficha clínica).

---

## 3. Arquitectura general

```
CodigoFuenteB/
├── BACKEND/    API REST Node.js/Express
│   ├── sql/        init.sql, dump-cuidarteplus.sql
│   ├── src/        routes · middleware · validations
│   └── uploads/    contratos y documentos
├── FRONTEND/   SPA React + Vite + Tailwind (Nginx en prod)
│   └── src/        pages · context (AuthContext) · RoleGuard
└── docker-compose.yml   (backend :4444 · frontend :3333 · pg :15442)
```

- API REST desacoplada, documentada con **OpenAPI/Swagger** (`/docs`)
- Validaciones centralizadas con `yup` (`/validations`) + `rut.js` chileno
- `AuthContext` + `RoleGuard` restringen la UI según rol

---

## 4. Puntos fuertes

| Aspecto | Detalle |
|---|---|
| Arquitectura desacoplada | API ↔ SPA con contratos OpenAPI |
| Anti-SQLi | Todas las consultas parametrizadas `$1` (pg) — **0 hallazgos de inyección** |
| RBAC de lectura clínica | Paciente solo ve sus exámenes y documentos (`examenes.js`, `documentos.js`) |
| Validación de entrada | Middleware `validate.js` + esquemas `yup` |
| Trazabilidad | Módulo de auditoría explícito (`audit.js` / `AuditoriaList.jsx`) |
| Integridad del código | Análisis **sin modificar** el software del profesor |

---

## 5. Metodología del análisis

1. **Revisión estática de código (SAST manual)** — todos los routes, middlewares, esquema SQL y frontend
2. **Mapeo OWASP Top 10 (2021)** — cada hallazgo clasificado
3. **Contraste con ERS v1.1** — RF/NFR ↔ código real
4. **Marco normativo** — ISO/IEC 25010, OWASP, Ley 19.628 y 20.584

Entregables:
- 📄 Informe de hallazgos (17 vulnerabilidades con evidencia `archivo:línea`)
- 📄 Plan de pruebas (19 casos, cobertura ERS 100%)
- 📄 Esta presentación

---

## 6. Criterios de calidad (ISO/IEC 25010)

- **Usabilidad:** WCAG 2.1 AA · tipografía ≥12 px · contraste ≥4.5:1 · ARIA · teclado 100% · foco en adultos mayores
- **Rendimiento:** API <300 ms · carga inicial <2 s · 200 usuarios concurrentes · adjuntos ≤10 s
- **Disponibilidad:** uptime 99.5% mensual · backups y rollback
- **Mantenibilidad:** capas desacopladas · Swagger vigente

## Criterios de seguridad (NFR-SEG)

- TLS 1.2+ y cabeceras de seguridad
- bcrypt + JWT corto con refresh token
- RBAC en backend (admin/medico/paciente)
- Anti-SQLi / XSS / CSRF (OWASP Top 10)
- Auditoría inmutable con IP y recurso
- Cifrado en reposo de documentos clínicos

---

## 7. Plan de pruebas — estrategia en 4 fases

| Fase | Enfoque | Herramientas |
|---|---|---|
| 1. Unitarias/Integración | API, middlewares JWT, validaciones | Jest + Supertest *(a incorporar: hoy 0 tests)* |
| 2. Funcionales/Sistema | Login, CRUD, adjuntos, RBAC | Postman / Newman + UI manual |
| 3. No funcionales | Carga 200 usuarios + DAST | JMeter · OWASP ZAP |
| 4. UAT/Accesibilidad | Panel 5 adultos mayores | Axe DevTools · Lighthouse |

**Prioridad P1:** autenticación, RBAC, soft delete, auditoría, SQLi/XSS, endpoints mutantes
**Prioridad P2:** rendimiento, accesibilidad, contraseñas, disponibilidad
**Prioridad P3:** compatibilidad de navegadores

---

## 8. Criterios de entrada y salida

**Entrada**
- Código desplegado en QA con Docker (**sin modificaciones**)
- BD con dump sintético (`dump-cuidarteplus.sql`)
- ERS v1.1 + Swagger vigente en `/docs`

**Salida**
- 100% de casos P1/P2 ejecutados
- Cero vulnerabilidades críticas sin registrar
- Latencia ≤300 ms en el 95% (endpoints sin delay artificial)
- Accesibilidad ≥90% sin violaciones críticas
- Evidencia completa (capturas, .jtl, reportes ZAP, dumps psql)

---

## 9. Casos de prueba — mapa (19 casos)

| Área | Casos |
|---|---|
| Autenticación/sesión | CP-01 login · CP-02 refresh/expiración · CP-03 política de claves |
| Funcional clínico | CP-04 examen+PDF · CP-05 CRUD pacientes |
| RBAC/autorización | CP-06 solo-mis-datos · CP-07 sin-mutación-sin-escalada · **CP-18 endpoints sin token** |
| Auditoría/integridad | CP-08 soft delete + log · CP-09 inmutabilidad |
| Seguridad OWASP | CP-10 SQLi · CP-11 XSS · CP-12 TLS/cabeceras · CP-19 disclosure |
| Rendimiento | CP-13 200 usuarios (A/B delay) · CP-14 SPA <2 s y adjuntos ≤10 s |
| Humanos/operación | CP-15 UAT adultos mayores · CP-16 compatibilidad · CP-17 uptime 99.5% |

**Trazabilidad: 28/28 ID del ERS = 100% de cobertura**

---

## 10. Hallazgos críticos (Top 6 de 17)

| ID | Hallazgo | Evidencia |
|---|---|---|
| **H-01** | Contraseñas en **texto plano** (sin bcrypt) | `auth.js:21,110` |
| **H-02** | `POST /usuarios` sin control de rol → paciente crea admin | `users.js:23-53` |
| **H-03** | `DELETE /usuarios` **sin autenticación** (borra antes de verificar token) | `users.js:571` |
| **H-04** | `/roles` completo sin auth (crea/borra roles libres) | `roles.js:18,76` |
| **H-05** | **Ficha médica pública por RUT** (alergias, crónicos…) | `pacientes.js:249` |
| **H-06** | `DELETE FROM` físico — **no hay soft delete** (RF-3.3 roto) | `examenes.js:408` |

---

## 11. Hallazgos altos y de calidad

| ID | Hallazgo | ERS afectado |
|---|---|---|
| H-07 | Borrar usuario anula sus logs (`ON DELETE SET NULL`) | RF-5.1 |
| H-08 | `.env` con `JWT_SECRET` y password de BD en el ZIP + fallback `"inseguro"` | NFR-SEG-1 |
| H-09 | JWT de **2 h** en `localStorage`, sin refresh token | RF-1.2, NFR-SEG-9 |
| H-10 | Paciente puede reasignar `usuario_id` de su ficha | RB-1 |
| H-11 | Médico puede autopromoverse a admin | RB-2, RB-3 |
| H-12 | Auditoría sin IP/recurso, no atómica, editable | RF-5.1 |
| **H-13** | **`delayMiddleware(5000)`** → meta <300 ms imposible | NFR-PERF-1/3 |

Medios: H-14 sin helmet/CORS abierto · H-15 err. PG al cliente · H-16 sin rate limit · H-17 adjuntos sin cifrar

---

## 12. Veredicto OWASP Top 10 (2021)

| Categoría | Hallazgos | Estado |
|---|---|---|
| A01 Broken Access Control | H-02, H-03, H-04, H-05, H-10, H-11 | ❌ Grave |
| A02 Cryptographic Failures | H-01, H-08 | ❌ Grave |
| A03 Injection | — (SQL parametrizado) | ✅ Sin hallazgos |
| A04 Insecure Design | H-06, H-07, H-12, H-17 | ❌ Grave |
| A05 Misconfiguration | H-14, H-15 | ⚠️ Parcial |
| A07 Auth Failures | H-09, H-16 | ❌ Grave |
| A09 Logging Failures | H-12 | ❌ Grave |

**Total: 17 hallazgos (6 críticos · 6 altos · 5 medios)**

---

## 13. Contradicciones ERS vs código real

| Requerimiento ERS | Realidad en el código | Estado |
|---|---|---|
| bcrypt (NFR-SEG-2) | Comparación directa de texto | ❌ |
| Refresh token ≤15 min (RF-1.2) | JWT 2 h, sin endpoint refresh | ❌ |
| Soft delete (RF-3.3) | `DELETE FROM` físico + CASCADE | ❌ |
| Auditoría con IP y recurso (RF-5.1) | Tabla solo `(usuario_id, accion, fecha_hora)` | ❌ |
| API <300 ms (NFR-PERF-1) | `delayMiddleware(5000)` en endpoints clave | ❌ |
| RBAC total (NFR-SEG-4) | Roto en usuarios, roles y búsqueda RUT | ❌ |
| Anti-SQLi (NFR-SEG-5) | Consultas `$1` parametrizadas | ✅ |
| Paciente solo lo propio (RB-1) | Correcto en exámenes/documentos | ✅ |

---

## 14. Matriz de trazabilidad (resumen)

| Dominio | ID ERS cubiertos | Casos |
|---|---|---|
| Funcionales | RF-1.1/1.2, RF-2.x, RF-3.x, RF-4.x, RF-5.1 | CP-01…CP-08 |
| Seguridad | NFR-SEG-1…9 | CP-01, 02, 03, 06, 07, 10, 11, 12, 18, 19 |
| Rendimiento | NFR-PERF-1/2/3 | CP-13, CP-14 |
| Usabilidad | NFR-USAB-1/4 | CP-15 |
| Compatibilidad | NFR-COMPAT-1/2 | CP-16 |
| Disponibilidad | NFR-DIS-1/2, NFR-SEG-7 | CP-17 |
| Reglas de negocio | RB-1, RB-2, RB-3 | CP-04, 06, 07, 18 |

**28/28 ID = 100%** · Ningún caso sin requerimiento · Ningún ID huérfano

---

## 15. Recomendaciones priorizadas

**Inmediatas (antes de cualquier despliegue):**
1. bcrypt + rotar `JWT_SECRET` y password de BD; `.env` fuera del repo (H-01, H-08)
2. Auth+authz en `DELETE /usuarios`, `/roles` y `POST /usuarios` (H-02/03/04)
3. Proteger `GET /pacientes/buscar/rut/:rut` (H-05)
4. Implementar soft delete (H-06)
5. Deshabilitar `delay(5000)` en producción (H-13)

**Corto plazo:** refresh token + rate limit · auditoría completa y atómica · helmet + CORS whitelist · 500 genéricos

**Estructurales:** suite Jest+Supertest + CI con ZAP · volumen persistente para `uploads/` · cifrado en reposo

---

## 16. Conclusión

- El análisis **solo lectura** del código real permite cerrar la cadena **ERS → criterio → caso → evidencia**.
- **17 hallazgos** documentados con `archivo:línea`, clasificación OWASP y el CP que lo detecta.
- **Plan de 19 casos** ejecutable contra los endpoints reales del Docker, con **cobertura 100%** del ERS.
- Los casos esperados en **RECHAZADO** (CP-02, 07, 08, 09, 18, 19) **son** la evidencia de la evaluación.
- Lo que sí funciona — anti-SQLi y RBAC de lectura clínica — queda demostrado igual que las brechas.

**Cuidarte+ aún no cumple los pilares de seguridad, calidad y cumplimiento legal exigidos: el plan de pruebas es la herramienta para demostrarlo con evidencia reproducible.**

---

*Fin de la presentación — ISY1102 · CreaLab SpA*