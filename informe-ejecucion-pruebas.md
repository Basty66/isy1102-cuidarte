# Informe de ejecución de pruebas · Cuidarte+ (ISY1102)

**Fecha:** 2026-09-22  
**Rama:** `ejecucion-pruebas`  
**Entorno:** Docker local · solo `cuidarteplus-postgres-ev` + `cuidarteplus-backend-ev` (`http://localhost:4444`)  
**Herramienta:** Newman 6 · colección `Cuidarte_CP01-19.postman_collection.json`  
**Código de la app:** sin modificaciones (solo análisis / evidencia)

---

## 1. Resumen de la corrida

| Métrica | Valor |
|---|---|
| Requests ejecutados | **39** |
| Assertions | **54** |
| Assertions fallidas (hallazgos) | **14** |
| Duración total | **43,3 s** |
| Latencia media | 906 ms (mín 2 ms · máx **5 s**) |
| Evidencia bruta | `reports/results.json` |

> Una aserción **fallida** = el código no cumple el ERS = hallazgo confirmado en runtime.

---

## 2. Setup (previo a los CP)

| Paso | Resultado |
|---|---|
| Login `admin/admin` | ✅ 200 → `token_admin` |
| Login `medico/medico` | ✅ 200 → `token_medico` |
| Login `paciente/paciente` | ✅ 200 → `token_paciente` |

Usuarios del dump (`dump-cuidarteplus.sql:288-290`).

---

## 3. Las 14 aserciones fallidas (evidencia de vulnerabilidades)

| # | Aerción / CP | Esperado (ERS) | Obtenido | Hallazgo |
|---|---|---|---|---|
| 01 | CP-01 · exp del JWT | ≤ 15 min (RF-1.2) | **120 min** | **H-09** |
| 02 | CP-02 · `POST /autenticacion/refresh` | 200/201 | **404** | **H-09** |
| 03 | CP-04 · latencia crear examen | < 300 ms | **5013 ms** | **H-13** |
| 04 | CP-04 · latencia subir documento | < 300 ms | **5014 ms** | **H-13** |
| 05 | CP-06 · descarga doc ajeno | 403 | **404** | NC · orden auth/existencia |
| 06 | CP-07/18 · paciente crea usuario | 403 | **201** | **H-02 CRÍTICO** |
| 07 | CP-18 · `DELETE /usuarios` sin token | 401 | **404** (ejecuta borrado) | **H-03 CRÍTICO** |
| 08 | CP-18 · `DELETE /roles` sin token | 401 | **404** | **H-04 CRÍTICO** |
| 09 | CP-18 · `POST /roles` sin token | 401 | **500** (dup. nombre tras 1ª corrida; 1ª corrida: **201**) | **H-04 CRÍTICO** |
| 10 | CP-12 · `X-Content-Type-Options` | `nosniff` | **ausente** | **H-14** |
| 11 | CP-12 · `X-Frame-Options` | presente | **ausente** | **H-14** |
| 12 | CP-12 · `Content-Security-Policy` | presente | **ausente** | **H-14** |
| 13 | CP-12 · `Strict-Transport-Security` | presente | **ausente** | **H-14** |
| 14 | CP-13A · `GET /examenes` | < 300 ms | **5023 ms** | **H-13** |

### Confirmaciones en consola (también de la corrida)

| Hallazgo | Evidencia runtime |
|---|---|
| **H-02** | `POST /usuarios` con `token_paciente` + `rol_id=1` → **201 Created** |
| **H-05** | `GET /pacientes/buscar/rut/11111111-1` **sin token** → **200** + ficha completa (alergias, crónicos…) |
| **H-13** | `delayMiddleware(5000)` activo en `POST/GET /examenes`, `POST /documentos`, `GET /pacientes` (~5 s) |
| **H-14** | `Access-Control-Allow-Origin: *` (CORS abierto) |
| **H-15** | `GET /examenes/abc` → 500 con `glosa: invalid input syntax for type bigint: "abc"` |
| **H-12** | Auditoría solo `id, usuario_id, accion, fecha_hora, nombre_usuario` (sin IP ni `recurso_id`) |
| **H-06** | `DELETE /examenes/:id` con admin → 200 vía `DELETE FROM` (sin columna `eliminado`) |

---

## 4. Pruebas conformes (√) — lo que SÍ funciona

| CP | Resultado |
|---|---|
| CP-01 login / password mala / SQLi / DROP TABLE | 200 / 401 / 401 sin error SQL → **parametrizado OK** |
| CP-03 política clave débil (corrida limpia) | 400 ante clave de 6 chars |
| CP-04 flujo examen + PDF + descarga | 201 / 201 / 200 con `attachment` |
| CP-05 CRUD pacientes + RUT inválido + RBAC | 201 / 400 / 403 |
| CP-06 lectura clínica del paciente | 200 solo propios; ajeno → 403 |
| CP-07 creación/edición examen por paciente | 403 / 403 |
| CP-08/09 auditoría | admin 200; no-admin 403 |
| CP-10 SQLi clásico | 401 uniforme |
| CP-17 healthcheck | `status: ok` |
| CP-13B latencia control `GET /` | < 300 ms |

---

## 5. Matriz CP → resultado vs `resultados-pruebas-cuidarte.md`

| CP | Esperado en predicción | Ejecución real |
|---|---|---|
| CP-01 | ⚠️ / ❌ H-09 | ❌ **H-09** (exp 120 min) |
| CP-02 | ❌ H-09 | ❌ **404 refresh** |
| CP-03 | ✅/⚠️ | ✅ 400 (corrida limpia) |
| CP-04 | ⚠️ H-13 | ❌ latencia 5 s · flujo CRUD ✅ |
| CP-05 | ✅ | ✅ |
| CP-06 | ⚠️ | ❌ doc ajeno 404 (parcial) · resto ✅ |
| CP-07 | ❌ H-02 | ❌ **201 escalada** |
| CP-08 | ❌ H-06 | ✅ delete 200 (H-06 documentado) |
| CP-09 | ✅ | ✅ 403 |
| CP-10 | ⚠️ | ✅ SQLi bloqueado |
| CP-12 | ❌ H-14 | ❌ **4 cabeceras ausentes** |
| CP-13A | ❌ H-13 | ❌ **~5000 ms** |
| CP-13B | ✅ | ✅ |
| CP-17 | ✅ | ✅ |
| CP-18 | ❌ H-03/H-04/H-05 | ❌ **404/404/200** |
| CP-19 | ❌ H-15 | ❌ **glosa PostgreSQL** |

---

## 6. Cómo reproducir

```powershell
# 1) Solo los 2 servicios de Cuidarte
docker compose -f CodigoFuenteB\CodigoFuenteB\docker-compose.yml `
  up -d --build cuidarteplus-postgres-ev cuidarteplus-backend-ev

# 2) Runner
npm install
npm test   # => reports/results.json
```

Ver `tests/README.md`.

---

## 7. Conclusión del encargo (ejecución)

- **14/54 assertions fallan** → correlación directa con los hallazgos del informe estático (H-02, H-03, H-04, H-05, H-09, H-13, H-14, H-15…).
- Los **críticos de acceso** (H-02, H-03, H-04, H-05) quedaron **demostrados en runtime** contra el stack Docker, no solo por lectura de código.
- El **SQLi** y el **RBAC de lectura clínica** se comportan conforme al ERS (puntos fuertes).
- No se modificó `CodigoFuenteB/`; solo colección, runner e informes.

**Evidencia:** `reports/results.json` · rama `ejecucion-pruebas` · repo `Basty66/isy1102-cuidarte`.
