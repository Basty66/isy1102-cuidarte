# Ejecución de pruebas · rama `ejecucion-pruebas`

Levanta **solo** los servicios necesarios de Cuidarte+ y corre la colección
`Cuidarte_CP01-19.postman_collection.json` con Newman.

## Requisitos

- Docker Desktop corriendo
- Node.js 18+
- Puerto libre: `4444` (backend)

## 1. Instalar dependencias de pruebas

```powershell
npm install
```

## 2. Levantar SOLO postgres + backend (sin frontend, sin otros proyectos)

```powershell
docker compose -f CodigoFuenteB\CodigoFuenteB\docker-compose.yml `
  up -d --build cuidarteplus-postgres-ev cuidarteplus-backend-ev
```

Esperar a que el backend responda:

```powershell
Invoke-RestMethod http://localhost:4444/
# => { name: cuidarteplus, status: ok }
```

## 3. Ejecutar pruebas

```powershell
npm test
```

Resultados: `reports/results.json`

## 4. Bajar SOLO estos servicios

```powershell
docker compose -f CodigoFuenteB\CodigoFuenteB\docker-compose.yml `
  stop cuidarteplus-postgres-ev cuidarteplus-backend-ev
```

## Usuarios del dump (prueba)

| Rol | usuario | password |
|---|---|---|
| admin | `admin` | `admin` |
| medico | `medico` | `medico` |
| paciente | `paciente` | `paciente` |

## Qué se evidencia

Cada `pm.test` valida el **ERS** (esperado). Si el código vulnerable falla,
el test **falla** = hallazgo H-01…H-15 documentado en
`hallazgos-seguridad-cuidarte.md`.

> ⚠️ Entorno aislado: el backend es intencionalmente vulnerable.
