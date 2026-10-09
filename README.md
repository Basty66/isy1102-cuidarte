# ISY1102 · Evaluación de seguridad y calidad — Sistema Cuidarte+

Paquete completo de evaluación del **Sistema de Exámenes Médicos Cuidarte+**: plan de pruebas,
auditoría de código, ejecución automatizada y evidencia. El código fuente evaluado se entrega
**sin ninguna modificación** (la evaluación es de análisis y prueba, no de corrección).

- **Asignatura:** ISY1102 – Seguridad y Calidad en el Desarrollo de Software
- **Entregable principal:** `Informe_Seguridad_Calidad_Cuidarte_ISY1102.docx` (formato EP1) y su PDF
- **Repositorio:** https://github.com/Basty66/isy1102-cuidarte

---

## 1. Qué se entrega

### Entregable evaluado

| Archivo | Contenido |
|---|---|
| `Informe_Seguridad_Calidad_Cuidarte_ISY1102.docx` | **Informe final** con el formato del template EP1: portada, índice automático, secciones 1–4 (introducción, criterios de calidad, plan de pruebas, 19 casos CP-01…CP-19) y **Anexos A/B/C** con trazabilidad, hallazgos y evidencia de ejecución |
| `Informe_Seguridad_Calidad_Cuidarte_ISY1102.pdf` | El mismo informe exportado a PDF, con el índice ya paginado |
| `EP1_ISY1102_Estudiante_Formato_Informe.docx` | Template oficial del curso (referencia de formato) |

> **Antes de subir:** la portada trae **resaltados en amarillo** los datos que debes completar
> (`Sección XX` y los nombres de los integrantes). Complétalos, quita el resaltado y actualiza el
> índice con `Ctrl+E` → `F9` (o `Referencias ▸ Actualizar tabla`).

### Documentos de respaldo

| Archivo | Contenido |
|---|---|
| `informe-seguridad-calidad-cuidarte.md` | Plan de pruebas extendido: criterios ISO/IEC 25010 y OWASP, matriz RBAC, 19 casos y matriz de trazabilidad 28/28 |
| `hallazgos-seguridad-cuidarte.md` | 17 hallazgos (6 críticos, 6 altos, 5 medios) con `archivo:línea`, mapeo OWASP Top 10 (2021) y corrección propuesta |
| `resultados-pruebas-cuidarte.md` | Matriz de resultados por caso y por criterio transversal, más el plan de remediación priorizado |
| `informe-ejecucion-pruebas.md` | Informe de la corrida Newman: 48 requests, 66 aserciones, 22 fallidas |
| `presentacion-cuidarte.md` | Presentación de la evaluación (16 diapositivas) |
| `guia-estudio-cuidarte.html` | Guía interactiva de estudio (flashcards, quiz y checklist) para la defensa |

### Artefactos ejecutables

| Ruta | Contenido |
|---|---|
| `Cuidarte_CP01-19.postman_collection.json` | Colección Postman alineada a los 19 casos de prueba |
| `tests/environment.json`, `tests/fixtures/` | Entorno y datos de prueba de la colección |
| `reports/results.json` | Evidencia bruta de la última corrida de Newman |
| `scripts/generate_informe_docx.py` | Genera el `.docx` final a partir del template EP1 |
| `scripts/finalize_informe.ps1` | Actualiza el índice en Word y exporta el PDF |
| `scripts/read_docx_format.py` | Extrae estilos y estructura del template Word |
| `CodigoFuenteB/` | Código fuente analizado (BACKEND Express + PostgreSQL, FRONTEND React/Vite) |

---

## 2. Resultado de la evaluación

| Dimensión | Resultado |
|---|---|
| Casos de prueba diseñados | 19 (CP-01 … CP-19) |
| Trazabilidad ERS | 28/28 identificadores (11 RF + 14 NFR + 3 RB) = **100%** |
| Hallazgos de seguridad | **17** — 6 críticos · 6 altos · 5 medios |
| Ejecución automatizada | 48 requests · 66 aserciones · **22 fallidas** (incumplimientos del ERS) |
| Veredicto | **No se aprueba el paso a producción** |

Controles que **sí** cumplen: consultas SQL parametrizadas (sin inyección SQL, OWASP A03),
control de acceso de lectura clínica del rol paciente, validación de entrada centralizada con
`yup` y validación de RUT módulo 11.

Incumplimientos principales: contraseñas en texto plano (H-01), endpoints mutantes sin
autenticación (H-02…H-05), borrado físico en lugar de lógico (H-06), auditoría incompleta
(H-12) y latencia artificial de 5 s que hace imposible el NFR-PERF-1 (H-13).

---

## 3. Reproducir la evaluación

### 3.1 Ejecutar las pruebas (Newman)

Requiere Docker Desktop y Node.js 18+, con el puerto `4444` libre.

```bash
docker compose -f CodigoFuenteB/CodigoFuenteB/docker-compose.yml up -d --build cuidarteplus-postgres-ev cuidarteplus-backend-ev
```

```bash
npm install && npm test
```

Los resultados quedan en `reports/results.json`. El detalle del entorno, los usuarios de prueba
y los casos no automatizados están en [tests/README.md](tests/README.md).

### 3.2 Regenerar el informe Word y el PDF

Requiere Python 3 con `python-docx` (`pip install python-docx`) y, para el PDF, Microsoft Word.

```bash
python scripts/generate_informe_docx.py
```

```bash
powershell -ExecutionPolicy Bypass -File scripts/finalize_informe.ps1
```

El primer comando construye el `.docx` desde el template EP1; el segundo actualiza el índice con
los números de página reales y exporta el PDF. Sin Word instalado el `.docx` sigue siendo válido:
el índice se actualiza solo al abrirlo.

---

## 4. Ramas

`master` y `ejecucion-pruebas` contienen el mismo paquete completo (plan, hallazgos, runner y
evidencia). `master` es la rama de entrega.

---

> ⚠️ El código de `CodigoFuenteB/` es **intencionalmente vulnerable** (así lo declara su propio
> `package.json`). Ejecutarlo solo en un entorno local aislado, nunca expuesto a la red.
> Los archivos `.env` del ZIP original **no** se versionan: son parte del hallazgo H-08.
