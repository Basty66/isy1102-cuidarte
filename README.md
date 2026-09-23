# ISY1102 · Evaluación Cuidarte+ — Plan de pruebas, hallazgos y ejecución

Paquete de evaluación de calidad y seguridad del **Sistema de Exámenes Médicos Cuidarte+**
(código fuente de la evaluación, sin modificaciones).

## Contenido (rama `master`)

| Archivo | Descripción |
|---|---|
| `informe-seguridad-calidad-cuidarte.md` | Plan de pruebas: criterios ISO 25010 / OWASP, matriz RBAC, 19 casos CP-01…CP-19, trazabilidad 28/28 (IE5) |
| `Informe_Seguridad_Calidad_Cuidarte_ISY1102.docx` | Informe final en Word (template EP1: portada, índice, secciones 1–4, 19 tablas CP) |
| `EP1_ISY1102_Estudiante_Formato_Informe.docx` | Template oficial del curso (formato de referencia) |
| `hallazgos-seguridad-cuidarte.md` | 17 hallazgos (6 críticos, 6 altos, 5 medios) con `archivo:línea` y mapeo OWASP |
| `resultados-pruebas-cuidarte.md` | Matriz de resultados (predictivo + ejecución) y plan de remediación |
| `informe-ejecucion-pruebas.md` | Informe de la corrida Newman (evidencia dinámica) |
| `presentacion-cuidarte.md` | Presentación de la evaluación (16 slides) |
| `guia-estudio-cuidarte.html` | Guía interactiva de estudio (flashcards, quiz, checklist) |
| `Cuidarte_CP01-19.postman_collection.json` | Colección Postman alineada a los casos de prueba |
| `scripts/generate_informe_docx.py` | Generador del `.docx` final a partir del template EP1 |
| `scripts/read_docx_format.py` | Extrae estilos/estructura del template Word |
| `CodigoFuenteB/` | Código fuente analizado (BACKEND + FRONTEND) |

## Rama `ejecucion-pruebas`

Runner con **Newman** que levanta solo los servicios necesarios
(`postgres` + `backend` de `CodigoFuenteB/CodigoFuenteB/docker-compose.yml`),
ejecuta la colección completa y deja evidencia en `reports/`.

```powershell
# desde la rama ejecucion-pruebas
npm install
npm test
```

> ⚠️ El código está **intencionalmente vulnerable** (tipo DVWA). Usar solo en entorno local aislado.
> Los `.env` del ZIP original **no** se versionan (ver hallazgo H-08).
