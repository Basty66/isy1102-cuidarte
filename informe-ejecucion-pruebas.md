# Informe de ejecución de pruebas · Cuidarte+ (ISY1102)

**Fecha:** 2026-09-22  
**Rama:** `ejecucion-pruebas`  
**Entorno:** Docker local · solo `cuidarteplus-postgres-ev` + `cuidarteplus-backend-ev` (`http://localhost:4444`)  
**Herramienta:** Newman 6 · colección `Cuidarte_CP01-19.postman_collection.json`  
**Comando:** `npm test` → `reports/results.json`  
**Código de la app:** sin modificaciones (solo análisis / evidencia)

---

## 1. Resumen de la corrida

| Métrica | Valor |
|---|---|
| Requests ejecutados | **48** |
| Requests fallidos (errores de transporte) | 0 |
| Assertions ejecutadas | **66** |
| Assertions fallidas (= hallazgos confirmados) | **22** |
| Duración total | **55,2 s** |
| Latencia media | 947 ms (mín 3 ms · máx **5 s**) |
| Evidencia bruta | `reports/results.json` |

> Una aserción **fallida** = el código no cumple el ERS = hallazgo confirmado en runtime.  
> Las 22 fallas no son “tests rotos”: son el resultado deliberado de validar el *esperado* (ERS) contra el código vulnerable.

---

## 2. Setup (previo a los CP)

| Paso | Resultado |
|---|---|
| Login `admin/admin` | ✅ 200 → `token_admin` |
| Login `medico/medico` | ✅ 200 → `token_medico` |
| Login `paciente/paciente` | ✅ 200 → `token_paciente` |

Usuarios del dump (`dump-cuidarteplus.sql:288-290`).

---

## 3. Las 22 aserciones fallidas (evidencia de vulnerabilidades)

| # | Aserción / CP | Esperado (ERS) | Obtenido | Hallazgo |
|---|---|---|---|---|
| 01 | CP-01 · exp del JWT | ≤ 15 min (RF-1.2) | **120 min** | **H-09** |
| 02 | CP-02 · `POST /autenticacion/refresh` | 200/201 | **404** | **H-09** |
| 03 | CP-03 · clave de 6 chars | **400** (política ≥12) | **201** | **H-01** |
| 04 | CP-04 · latencia crear examen | < 300 ms | **5014 ms** | **H-13** |
| 05 | CP-04 · latencia subir documento | < 300 ms | **5016 ms** | **H-13** |
| 06 | CP-07 · paciente crea usuario admin | **403** | **201** | **H-02** CRÍTICO |
| 07 | CP-07/H-11 · médico cambia `rol_id` | 400/403 | **200** (rol admin) | **H-11** ALTO |
| 08 | CP-08/H-06 · soft delete (GET tras DELETE) | 200 con `eliminado=true` | **404** (borrado físico) | **H-06** CRÍTICO |
| 09 | CP-08/H-12 · auditoría con `ip_origen` + `recurso_id` | presentes | **ausentes** (solo id, usuario_id, accion, fecha_hora, nombre_usuario) | **H-12** ALTO |
| 10 | CP-18 · `DELETE /usuarios` sin token | 401 | **404** (ejecuta borrado) | **H-03** CRÍTICO |
| 11 | CP-18 · `DELETE /roles` sin token | 401 | **404** | **H-04** CRÍTICO |
| 12 | CP-18 · `POST /roles` sin token | 401 | **500** (1ª corrida: **201**) | **H-04** CRÍTICO |
| 13 | CP-18/19 · búsqueda RUT sin token | 401 | **200** + ficha completa | **H-05** CRÍTICO |
| 14 | CP-18 · `PUT /roles/:id` sin token | 401 | **200** | **H-04** CRÍTICO |
| 15 | CP-12 · `X-Content-Type-Options` | `nosniff` | **ausente** | **H-14** |
| 16 | CP-12 · `X-Frame-Options` | presente | **ausente** | **H-14** |
| 17 | CP-12 · `Content-Security-Policy` | presente | **ausente** | **H-14** |
| 18 | CP-12 · `Strict-Transport-Security` | presente | **ausente** | **H-14** |
| 19 | CP-12 · CORS | no `*` | **`Access-Control-Allow-Origin: *`** | **H-14** |
| 20 | CP-19/H-15 · glosa 500 | sin mensaje de PostgreSQL | **`invalid input syntax for type bigint`** | **H-15** |
| 21 | CP-11/H-14 · CSP en respuesta XSS | presente | **ausente** | **H-14** |
| 22 | CP-13A · `GET /examenes` | < 300 ms | **5009 ms** | **H-13** |

### Confirmaciones adicionales (console de la corrida)

| Hallazgo | Evidencia runtime |
|---|---|
| **H-10** (parcial) | `PUT /pacientes/1` con solo `usuario_id: 99999` → **500 FK** (el campo llegó a la BD; ERS pide 400/403 sin escribir) |
| **H-11** | `PUT /usuarios/2` con `rol_id: 1` como médico → **200** y rol admin (luego cleanup restaura rol 2) |
| **H-13** | `delayMiddleware(5000)` activo en `POST/GET /examenes`, `POST /documentos`, `GET /pacientes` (~5 s) |

---

## 4. Pruebas conformes (√) — lo que SÍ funciona

| CP | Resultado |
|---|---|
| CP-01 login / password mala / SQLi / DROP TABLE | 200 / 401 / 401 sin error SQL → **parametrizado OK** |
| CP-04 flujo examen + PDF + descarga | 201 / 201 / 200 con `attachment` (latencia falla por H-13) |
| CP-05 CRUD pacientes + RUT inválido + RBAC | 201 / 400 / 403 |
| CP-06 lectura clínica del paciente | 200 solo propios; ajeno → 403 (docs examen ajeno → 403) |
| CP-07 creación/edición examen por paciente | 403 / 403 |
| CP-09 auditoría no-admin | **403** (paciente) |
| CP-10 SQLi clásico | 401 uniforme |
| CP-11 XSS almacenado como texto | payload en respuesta sin ejecución server-side |
| CP-17 healthcheck | `status: ok` |
| CP-13B latencia control `GET /` | < 300 ms |
| Setup + cleanup H-11 | tokens OK; rol médico restaurado a 2 |

---

## 5. Matriz CP → resultado vs `resultados-pruebas-cuidarte.md`

| CP | Esperado en predicción | Ejecución real |
|---|---|---|
| CP-01 | ⚠️ / ❌ H-09 | ❌ **H-09** (exp 120 min) · SQLi ✅ |
| CP-02 | ❌ H-09 | ❌ **404 refresh** |
| CP-03 | ⚠️ H-01 | ❌ **201** con clave de 6 chars |
| CP-04 | ⚠️ H-13 | ❌ latencia 5 s · flujo CRUD ✅ |
| CP-05 | ✅ | ✅ |
| CP-06 | ✅ | ✅ (ficha ajena 403 · docs examen ajeno 403) |
| CP-07 | ❌ H-02/H-10/H-11 | ❌ **201 escalada** · **H-11 200** · **H-10 500 FK** |
| CP-08 | ❌ H-06/H-12 | ❌ **hard delete 404** · **auditoría sin IP/recurso** |
| CP-09 | ❌ H-07/H-12 (parcial) | ⚠️ 403 no-admin ✅ · inmutabilidad manual (REVOKE) |
| CP-10 | ⚠️ | ✅ SQLi bloqueado |
| CP-11 | ⚠️ H-14 | ⚠️ payload como texto ✅ · **CSP ausente** |
| CP-12 | ❌ H-14 | ❌ **4 cabeceras + CORS `*`** |
| CP-13A | ❌ H-13 | ❌ **~5000 ms** |
| CP-13B | ✅ | ✅ |
| CP-17 | 🔄 | ✅ healthcheck OK (uptime manual) |
| CP-18 | ❌ H-02…H-05, H-11 | ❌ **404/404/500/200/201** |
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

- **22/66 assertions fallan** → correlación directa con los hallazgos del informe estático (**H-01, H-02, H-03, H-04, H-05, H-06, H-09, H-10, H-11, H-12, H-13, H-14, H-15**).
- Los **críticos de acceso** (H-02…H-06) y los **altos de sesión/escalada** (H-09, H-11, H-12) quedaron **demostrados en runtime** contra el stack Docker, no solo por lectura de código.
- El **SQLi**, el **RBAC de lectura clínica** y el **healthcheck** se comportan conforme al ERS (puntos fuertes).
- No se modificó `CodigoFuenteB/`; solo colección, runner e informes.

**Evidencia:** `reports/results.json` · rama `ejecucion-pruebas` · repo `Basty66/isy1102-cuidarte`.
