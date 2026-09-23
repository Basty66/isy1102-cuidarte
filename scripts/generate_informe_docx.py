"""Generate ISY1102 Cuidarte+ informe .docx following EP1 template."""
from copy import deepcopy
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Emu, Inches

TEMPLATE = r"C:\Users\crist\Desktop\medina\EP1_ISY1102_Estudiante_Formato_Informe.docx"
OUT = r"C:\Users\crist\Desktop\medina\Informe_Seguridad_Calidad_Cuidarte_ISY1102.docx"

INK = RGBColor(0x0E, 0x27, 0x40)
BLACK = RGBColor(0x00, 0x00, 0x00)
HDR_BG = "D9E2F3"
LBL_BG = "E7E6E6"


def set_run(run, *, font="Arial", size=10, bold=None, color=None, italic=None):
    run.font.name = font
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = color
    # East Asian font
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), font)
    rFonts.set(qn("w:hAnsi"), font)
    rFonts.set(qn("w:cs"), font)
    return run


def body_p(doc, text="", *, size=10, bold=False, color=INK, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6):
    p = doc.add_paragraph()
    p.style = doc.styles["Normal"]
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(0)
    if text:
        set_run(p.add_run(text), size=size, bold=bold, color=color)
    return p


def bullet(doc, text):
    p = doc.add_paragraph(style="List Paragraph")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(3)
    # use numbering if available; fallback to bullet char
    set_run(p.add_run("• " + text), size=10, bold=False, color=INK)
    return p


def h1(doc, text):
    p = doc.add_paragraph(style="Heading 1")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(8)
    set_run(p.add_run(text), size=16, bold=True, color=BLACK)
    return p


def h2(doc, text):
    p = doc.add_paragraph(style="Heading 2")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(6)
    set_run(p.add_run(text), size=12, bold=True, color=BLACK)
    return p


def shade_cell(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def set_cell_text(cell, text, *, size=10, bold=False, color=BLACK, align=WD_ALIGN_PARAGRAPH.LEFT):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    lines = text.split("\n") if text else [""]
    for i, line in enumerate(lines):
        if i > 0:
            p = cell.add_paragraph()
            p.alignment = align
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
        set_run(p.add_run(line), size=size, bold=bold, color=color)


def add_toc_field(doc):
    p = doc.add_paragraph()
    p.style = doc.styles["Normal"]
    run = p.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = r'TOC \o "1-2" \h \z \u'
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t")
    placeholder.text = "Actualice el índice con F9 en Word."
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(placeholder)
    run._r.append(fld_end)
    set_run(run, size=10, color=INK)
    return p


def clear_body_keep_styles(doc):
    body = doc.element.body
    # keep sectPr (last child)
    sectPr = body.find(qn("w:sectPr"))
    for child in list(body):
        if child is not sectPr:
            body.remove(child)


def cover(doc):
    for _ in range(6):
        body_p(doc, "", space_after=0)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run(p.add_run("Cuidarte+\n"), size=72, bold=True, color=BLACK)
    set_run(p.add_run("Informe de seguridad y calidad\nen el desarrollo de software"), size=20, bold=True, color=BLACK)
    for _ in range(4):
        body_p(doc, "", space_after=0)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    set_run(p.add_run("ISY1102 - Seguridad y calidad en el desarrollo de software\n"), size=11, bold=True, color=BLACK)
    set_run(p.add_run("Sección XX"), size=11, bold=False, color=BLACK)
    for _ in range(3):
        body_p(doc, "", space_after=0)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    set_run(p.add_run("Integrantes\n"), size=11, bold=True, color=BLACK)
    for name in (
        "Nombre Apellido Alumno 1",
        "Nombre Apellido Alumno 2",
        "Nombre Apellido Alumno 3",
    ):
        set_run(p.add_run(name + "\n"), size=11, bold=False, color=BLACK)
    # page break
    p = doc.add_paragraph()
    r = p.add_run()
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    r._r.append(br)


def section1(doc):
    h1(doc, "1. Introducción")
    body_p(
        doc,
        "Cuidarte+ es una plataforma web médica multicapa para centros de salud: gestión de pacientes, "
        "exámenes médicos, documentos clínicos y auditoría. El software se compone de una SPA React "
        "(v19.1.1) con Material UI y Tailwind servida por Nginx, una API RESTful Node.js/Express "
        "(v4.19.2) con validaciones yup y JWT, y una base de datos PostgreSQL con documentos clínicos "
        "almacenados en BYTEA. El despliegue se realiza con Docker Compose (backend :4444, frontend :3333, "
        "Postgres :15442)."
    )
    body_p(
        doc,
        "Los datos manejados (RUT, fichas clínicas, diagnósticos) son sensibles según la Ley N° 19.628 "
        "y la Ley N° 20.584: confidencialidad, integridad y disponibilidad son críticas. Por esta razón "
        "es necesario contar con un plan de pruebas que verifique de forma objetiva y reproducible que "
        "el software cumple el ERS v1.1, los criterios de calidad ISO/IEC 25010, OWASP Top 10 y la "
        "legislación chilena aplicable, antes de cualquier paso a producción."
    )
    body_p(
        doc,
        "El propósito de este informe es definir la estrategia de aseguramiento de calidad (SQA) y "
        "validación de seguridad que permita asegurar: (1) el cumplimiento funcional de cada RF del ERS "
        "contra los endpoints reales; (2) los atributos no funcionales (latencia <300 ms, 200 usuarios "
        "concurrentes, carga inicial <2 s, uptime 99.5%, WCAG 2.1 AA); (3) la seguridad de "
        "autenticación, RBAC y controles OWASP sin fuga de información clínica; y (4) la conformidad "
        "legal con las leyes 19.628 y 20.584 y una auditoría trazable (RF-5.1)."
    )
    body_p(doc, "El informe se estructura en cuatro secciones:")
    bullet(doc, "Sección 2 — Criterios de calidad, seguridad y cumplimiento normativo (ISO/IEC 25010, OWASP, legislación chilena y matriz RBAC esperada).")
    bullet(doc, "Sección 3 — Plan de pruebas: estrategia, tipos de prueba, criterios de aceptación transversales y herramientas/recursos.")
    bullet(doc, "Sección 4 — Diseño de 19 casos de prueba (CP-01 a CP-19) sobre los endpoints y esquema reales del código.")
    body_p(
        doc,
        "Alcance: API Express completa (/autenticacion, /usuarios, /pacientes, /examenes, /documentos, "
        "/auditoria, /roles, /docs), SPA React, esquema PostgreSQL y uploads. Fuera de alcance: "
        "infraestructura del datacenter, modificación del código fuente (este plan es de solo "
        "análisis/prueba) y terceros no auditados. Glosario: RF (funcional), NFR (no funcional), RB "
        "(regla de negocio), RBAC, DAST/SAST, UAT, JWT, SPA y soft delete."
    )


def section2(doc):
    h1(doc, "2. Criterios de calidad")
    body_p(
        doc,
        "Los criterios se derivan del ERS v1.1 (especificación de requerimientos de software del "
        "proyecto), de ISO/IEC 25010 para atributos de calidad, de OWASP Top 10 (2021) para seguridad "
        "y de la legislación chilena aplicable al software médico. Estos criterios definen el estándar "
        "que el software debe cumplir y son la base de los casos de prueba de la sección 4."
    )
    h2(doc, "2.1 Calidad de software (ISO/IEC 25010)")
    bullet(doc, "Usabilidad (NFR-USAB): WCAG 2.1 AA; tipografía ≥12 px; contraste ≥4.5:1; etiquetas WAI-ARIA; targets ≥48×48 px; navegación 100% por teclado; foco en adultos mayores (NFR-USAB-1, NFR-USAB-4).")
    bullet(doc, "Rendimiento (NFR-PERF): API CRUD <300 ms (NFR-PERF-1); carga inicial de SPA <2 s en red móvil (NFR-PERF-2); 200 usuarios concurrentes (NFR-PERF-3); subida/descarga de adjuntos ≤10 s (RF-4).")
    bullet(doc, "Disponibilidad (NFR-DIS): uptime 99.5% mensual (NFR-DIS-1); ventanas de mantenimiento con respaldo y rollback (NFR-DIS-2).")
    bullet(doc, "Estabilidad y confiabilidad: cero caídas bajo carga (NFR-PERF-3), pool de PostgreSQL sin agotamiento, respaldos restaurables (NFR-SEG-7).")
    bullet(doc, "Mantenibilidad: desacoplamiento React ↔ Express ↔ PostgreSQL; OpenAPI vigente en /docs y /openapi.json.")
    h2(doc, "2.2 Seguridad")
    bullet(doc, "Protección de datos en tránsito (NFR-SEG-1): TLS 1.2+ obligatorio, redirect HTTP→HTTPS, HSTS y cabeceras Content-Security-Policy, X-Content-Type-Options y X-Frame-Options.")
    bullet(doc, "Protección de datos en reposo (NFR-SEG-3): cifrado de documentos_examen.documento y de los backups.")
    bullet(doc, "Autenticación (NFR-SEG-2, RF-1.1, NFR-SEG-9): bcrypt cost ≥12; access JWT ≤15 min + refresh rotativo en cookie HttpOnly; Secure; SameSite=Strict; política ≥12 caracteres (4 clases); rate limit de login.")
    bullet(doc, "Control de acceso (NFR-SEG-4): middlewares en backend para admin, medico y paciente; reglas RB-1/RB-2/RB-3; falla por denegación (401/403).")
    bullet(doc, "Manejo de errores e integridad (NFR-SEG-5, criterio 'sin stack trace'): SQLi con consultas parametrizadas pg ($1); XSS con escape React + CSP; CSRF con SameSite + token; respuestas 500 genéricas sin err.message de PostgreSQL.")
    bullet(doc, "Auditoría (RF-5.1, NFR-SEG-7): tabla auditoria con usuario_id, acción, recurso_id, ip_origen y fecha_hora UTC; escritura atómica con la mutación; REVOKE UPDATE, DELETE; backups diarios cifrados con prueba de restauración.")
    h2(doc, "2.3 Normativas y cumplimiento legal")
    bullet(doc, "Ley N° 19.628: RUT, nombres, correos y diagnósticos son datos sensibles; principio de finalidad y confidencialidad; solo Médico/Administrador procesa.")
    bullet(doc, "Ley N° 20.584: derecho del paciente a sus propios exámenes (RF-4.1/4.2); reserva clínica absoluta frente a terceros (RB-1); edición reservada al profesional tratante (RF-3.1, RB-3).")
    bullet(doc, "RF-5.1: logs inmutables con usuario, acción, recurso, timestamp UTC e IP para peritaje; retención ≥12 meses.")
    bullet(doc, "Estándares técnicos: ISO/IEC 25010, OWASP Top 10 (2021), WCAG 2.1 AA y OpenAPI como contrato de la API.")
    body_p(
        doc,
        "Matriz RBAC esperada (oracle de las pruebas): la tabla de roles por endpoint del ERS "
        "(admin/medico/paciente/sin token) es la referencia obligatoria de los casos CP-06, CP-07, "
        "CP-18 y CP-19. Celdas denegadas deben responder 403 {\"error\":\"No autorizado\"} y, sin "
        "token, 401."
    )


def section3(doc):
    h1(doc, "3. Plan de pruebas")

    h2(doc, "3.1 Estrategia de pruebas")
    body_p(
        doc,
        "El enfoque es mixto: automatizado para la API (Postman/Newman, JMeter, ZAP) y manual para "
        "flujos de UI, accesibilidad y UAT. Las etapas del proceso son:"
    )
    bullet(doc, "Etapa 1 — Unitarias/integración (Jest + Supertest, a incorporar; hoy el repositorio no tiene tests): validaría validate.js, requireRole y rutas JWT. Prioridad P1.")
    bullet(doc, "Etapa 2 — Funcionales/sistema (Postman/Newman + UI manual): login, CRUD de usuarios/pacientes/exámenes/documentos, RBAC y soft delete. Prioridad P1.")
    bullet(doc, "Etapa 3 — No funcionales (JMeter para carga y OWASP ZAP para DAST): 200 usuarios, SQLi/XSS, cabeceras TLS y latencia vs delayMiddleware. Prioridades P1/P2.")
    bullet(doc, "Etapa 4 — UAT/accesibilidad (Axe DevTools + panel de 5 adultos mayores): WCAG 2.1 AA, legibilidad, teclado y táctil. Prioridad P2.")
    body_p(doc, "Herramientas que se utilizarán (detalle en 3.4): Postman/Newman, Apache JMeter, OWASP ZAP, Axe/Lighthouse, Jest+Supertest, psql/pgAdmin, curl/SSL Labs y Docker Compose.")
    body_p(doc, "Priorización de pruebas:")
    bullet(doc, "P1 – Crítica: login/sesión, RBAC sin fuga, exámenes+adjuntos, auditoría, SQLi/XSS, auth de endpoints mutantes (CP-01, CP-02, CP-04, CP-06, CP-07, CP-08, CP-09, CP-10, CP-11, CP-12, CP-18, CP-19).")
    bullet(doc, "P2 – Alta: rendimiento <300 ms/200 usuarios, accesibilidad, registro de pacientes, contraseñas, carga <2 s y disponibilidad (CP-03, CP-05, CP-13, CP-14, CP-15, CP-17).")
    bullet(doc, "P3 – Media: compatibilidad de navegadores/dispositivos (CP-16).")
    body_p(doc, "Criterios de entrada:")
    bullet(doc, "Código fuente extraído y desplegado en QA/Staging (Docker) sin modificar el software.")
    bullet(doc, "PostgreSQL inicializado con init.sql + dump-cuidarteplus.sql (datos 100% sintéticos).")
    bullet(doc, "ERS v1.1 aprobado y matriz de trazabilidad lista (28 IDs).")
    bullet(doc, "OpenAPI vigente en /docs y colección Postman exportada con los endpoints reales.")
    body_p(doc, "Criterios de salida:")
    bullet(doc, "100% de casos P1 y P2 ejecutados con estado APROBADO/RECHAZADO justificado.")
    bullet(doc, "Cero vulnerabilidades críticas/altas sin registrar en el informe de hallazgos.")
    bullet(doc, "Latencia ≤300 ms en el 95% de peticiones sin delay artificial; endpoints con delay(5000) documentados como incumplimiento de NFR-PERF-1.")
    bullet(doc, "Accesibilidad ≥90% sin violaciones críticas WCAG 2.1 AA y evidencia completa según protocolo de evidencia.")

    h2(doc, "3.2 Tipos de prueba")
    bullet(doc, "Pruebas funcionales: reglas de negocio y casos de uso reales (login, CRUD, adjuntos) contra RF-1.1 a RF-5.1.")
    bullet(doc, "Pruebas de integración: React ↔ Express ↔ PostgreSQL vía REST JSON (ERS secciones 2.1 y 4).")
    bullet(doc, "Pruebas de seguridad (DAST/SAST): SQLi, XSS, CSRF, bypass JWT, cabeceras y RBAC (NFR-SEG-1..9, OWASP).")
    bullet(doc, "Pruebas de rendimiento/carga: latencia y estabilidad con 200 usuarios (NFR-PERF-1/2/3).")
    bullet(doc, "Pruebas de usabilidad/accesibilidad: legibilidad, ARIA, contraste y teclado (NFR-USAB-1/4, WCAG 2.1 AA).")
    bullet(doc, "Pruebas de compatibilidad: Chrome, Firefox, Safari y Edge (2 últimas versiones) en escritorio, tablet y móvil (NFR-COMPAT-1/2).")
    bullet(doc, "Pruebas de auditoría e integridad: log inmutable de acciones críticas (RF-5.1, leyes 19.628/20.584).")
    bullet(doc, "Pruebas de disponibilidad y respaldo: uptime 99.5% y restauración (NFR-DIS-1/2, NFR-SEG-7).")

    h2(doc, "3.3 Criterios de aceptación")
    body_p(
        doc,
        "Los siguientes criterios de aceptación son transversales: se aplican a todos los casos de "
        "prueba y una prueba solo se considera aprobada si cumple la totalidad de los criterios "
        "aplicables a su tipo (funcional, no funcional y reglas de negocio):"
    )
    bullet(doc, "Autorización: ningún endpoint entrega datos sin JWT válido conforme a la matriz RBAC del ERS (RB-1/2/3); denegaciones en backend con 401/403.")
    bullet(doc, "HTTP estandarizado con JSON predecible: 200 OK · 201 creado · 400 {error, glosa, detalles} · 401 token · 403 No autorizado · 404 No encontrado · 500 sin exponer err.message de PostgreSQL.")
    bullet(doc, "Soft delete obligatorio: prohibido DELETE FROM sobre examen_medico, pacientes, usuarios y documentos_examen (RF-3.3), con confirmación modal previa en UI.")
    bullet(doc, "Latencia: consultas/actualizaciones <300 ms en el 95%; adjuntos ≤10 s; delayMiddleware solo si NODE_ENV=development.")
    bullet(doc, "Auditoría incondicional y atómica: toda mutación inserta log (con IP y recurso) en la misma transacción, antes del 200/201.")
    bullet(doc, "Trazabilidad de errores: todo 500 registra ID correlacionable en el log de servidor sin filtrar detalles al cliente.")
    bullet(doc, "Reglas de negocio y legal: reserva clínica (Ley 20.584), confidencialidad de datos (Ley 19.628) y soft delete con modal (RF-3.3) deben cumplirse en todos los flujos sensibles.")

    h2(doc, "3.4 Herramientas utilizadas")
    body_p(
        doc,
        "Herramientas tecnológicas y fundamento de su uso en la ejecución de las pruebas:"
    )
    bullet(doc, "Postman / Newman — pruebas funcionales e de integración: suites HTTP con Authorization: Bearer y validación JSON en CI (ejecutable con npm test).")
    bullet(doc, "Apache JMeter 5.6 — carga/estrés: 200 hilos, ramp-up 10 s y Aggregate Report para NFR-PERF-1/3.")
    bullet(doc, "OWASP ZAP — DAST: spider + active scan de XSS, SQLi, cabeceras y cookies (NFR-SEG-5).")
    bullet(doc, "Axe DevTools / Lighthouse — accesibilidad y carga de SPA: WCAG 2.1 AA y Lighthouse <2 s (NFR-USAB, NFR-PERF-2).")
    bullet(doc, "Jest + Supertest — unitarias/integración (a incorporar; hoy 0 tests en el repo).")
    bullet(doc, "psql / pgAdmin — verificación de BD: soft delete, contenido de auditoría y hashes de contraseñas.")
    bullet(doc, "curl / SSL Labs — TLS y cabeceras: curl -I y enumeración de protocolos (NFR-SEG-1).")
    bullet(doc, "Docker Compose — ambiente QA: réplica aislada del ZIP sin tocar el código fuente.")
    body_p(doc, "Recursos necesarios para la ejecución de las pruebas:")
    bullet(doc, "Recursos humanos (roles involucrados): 1 QA Lead · 1 Pentester · 2 desarrolladores de soporte (corrección de hallazgos fuera de este informe) · 5 adultos mayores (panel UAT).")
    bullet(doc, "Recursos técnicos (software, herramientas, equipos, navegadores, versiones): estación i7/16 GB para JMeter; PCs, tablets y smartphones; Chrome, Firefox, Safari y Edge; certificado SSL/TLS de prueba; Node.js 18+; Docker Desktop.")
    bullet(doc, "Entorno de prueba: QA aislado vía docker-compose.yml (backend :4444, frontend :3333, Postgres :15442), datos sintéticos del dump y sin acceso a la red operativa (Ley 19.628). No se modifica el código de la aplicación.")


# --- CP data: (id, nombre, req, desc, pre, pasos, esperado, criterio, datos) ---
CPS = [
    (
        "CP-01",
        "Autenticación y emisión de JWT",
        "RF-1.1, NFR-SEG-2, NFR-SEG-9",
        "Validar la autenticación con credenciales válidas en /autenticacion/login y la emisión de un token JWT firmado, además del rechazo de credenciales inválidas.",
        "Usuario existe en la tabla usuarios (dump dump-cuidarteplus.sql); API y BD operativas en el entorno QA Docker (backend :4444).",
        "1) Login vía UI (/login) o Postman.\n2) Verificar respuesta {\"token\": \"...\"}.\n3) Decodificar el payload JWT.\n4) Usar el token en GET /examenes.\n5) Login con clave incorrecta.\n6) Revisar que el log del servidor no contenga la contraseña.",
        "200 {token}; payload con usuarioId, rolNombre y exp; el paso 4 responde 200; el paso 5 responde 401 {\"error\":\"Credenciales inválidas\"}. Latencia <300 ms (este endpoint no tiene delayMiddleware).",
        "1) Sesión iniciada sin errores. 2) JWT firmado (HS256); si el ERS exige exp ≤15 min, registrar discrepancia. 3) Latencia <300 ms. 4) La contraseña no aparece en logs ni en claro en BD (si aparece en claro → hallazgo H-01).",
        "POST http://localhost:4444/autenticacion/login\nBody: {\"nombre_usuario\": \"medico\", \"password\": \"medico\"}\nTambién: admin/admin y paciente/paciente (dump-cuidarteplus.sql:288-290).",
    ),
    (
        "CP-02",
        "Sesión: expiración y refresh token",
        "RF-1.2, NFR-SEG-9",
        "Verificar que exista un mecanismo de renovación de sesión (refresh token) y que el access token vencido sea rechazado con 401.",
        "Sesión iniciada (CP-01); vida útil del access token conocida (expiresIn: \"2h\" en auth.js:54).",
        "1) Ejecutar GET /examenes con token expirado o falsificado.\n2) Intentar POST /autenticacion/refresh.\n3) Revisar si existe cookie HttpOnly de refresh.\n4) Revisar localStorage del navegador (AuthContext).",
        "Token vencido ⇒ 401; refresh ⇒ nuevo access token; refresh en cookie HttpOnly; Secure; SameSite=Strict.",
        "1) El token vencido jamás autoriza. 2) Existe mecanismo de refresh (si no existe → incumplimiento RF-1.2, hallazgo H-09). 3) El token no debería vivir en localStorage.",
        "GET /examenes con token vencido.\nPOST /autenticacion/refresh (endpoint requerido por RF-1.2).\nInspección de Application/Storage del navegador.",
    ),
    (
        "CP-03",
        "Política de contraseñas (≥12, 4 clases)",
        "NFR-SEG-2, RF-1.1",
        "Verificar el rechazo de claves débiles en el registro y el cumplimiento de la política ≥12 caracteres con 4 clases de caracteres, más el almacenamiento con hash en BD.",
        "API y BD operativas; endpoint POST /autenticacion/registro accesible.",
        "1) Enviar cada clave débil directo a la API (saltarse UI).\n2) Enviar clave válida.\n3) Verificar en BD el almacenamiento resultante (SELECT contrasena FROM usuarios).",
        "Claves <12 o sin combinación ⇒ 400 con mensaje de política; clave válida ⇒ 201; en BD solo hash bcrypt (nunca texto plano).",
        "1) Validación server-side (si solo existe en UI ⇒ fallo). 2) Si la política real del código es min(6) ⇒ discrepancia ERS (hallazgo H-01). 3) Ninguna clave en texto plano en BD.",
        "POST /autenticacion/registro con: hola123; Cort@12345; abcdefghijkl; Cuidarte2026!# (válida).\nTambién PUT /usuarios/:id con contrasena_hash.",
    ),
    (
        "CP-04",
        "Registro de examen médico con adjunto PDF",
        "RF-3.1, RF-4.3, RF-4.4, RB-3",
        "Verificar que un médico registre un examen y adjunte un PDF asociado al paciente correcto, con auditoría y descarga íntegra.",
        "Token rol medico; paciente ID existente en pacientes; archivo examen_sangre.pdf (fixture ~1.5 MB).",
        "1) UI: ficha paciente ⇒ Registrar Nuevo Examen ⇒ guardar.\n2) Adjuntar PDF (o POST /documentos por Postman).\n3) Cronometrar la operación total.\n4) Verificar examen_medico, documentos_examen y auditoría con psql.\n5) Descargar con GET /documentos/:id.",
        "201 en ambos POST; fila en examen_medico; BYTEA + nombre_archivo en documentos_examen; log EXAMENES_CREAR/DOCUMENTOS_CREAR; descarga 200 con Content-Disposition; total <10 s.",
        "1) 201 Created. 2) Total <10 s (ojo: POST /examenes y POST /documentos tienen delayMiddleware(5000) ⇒ medir y reportar H-13). 3) El examen solo es visible desde la ficha del paciente asignado. 4) Log antes de responder.",
        "POST /examenes body: {\"tipo_examen_medico_id\": 1, \"paciente_id\": 1, \"diagnosis\": \"...\", ...}\nPOST /documentos multipart: campo documento + examen_medico_id + paciente_id.",
    ),
    (
        "CP-05",
        "CRUD de pacientes por rol autorizado",
        "RF-2.1 a RF-2.7, Ley 19.628",
        "Verificar que solo Médico/Admin creen y editen pacientes, con validación de RUT módulo 11 en backend y denegación a rol paciente.",
        "Tokens de medico y paciente; BD operativa.",
        "1) Como medico: crear paciente RUT válido.\n2) RUT inválido ⇒ ¿400?\n3) Editar teléfono.\n4) Como paciente: intentar POST /pacientes.\n5) Como paciente: GET /pacientes/:id de otro ⇒ 403.",
        "1) 201; 2) 400; 3) 200; 4) 403; 5) 403.",
        "1) Validación de RUT módulo 11 en backend. 2) Ningún dato de terceros en respuestas a paciente. 3) Toda mutación genera auditoría (PACIENTES_*).",
        "POST /pacientes con RUT válido 12.345.678-9 e inválido 12.345.678-0.\nPUT /pacientes/:id\nGET /pacientes/:id",
    ),
    (
        "CP-06",
        "RBAC: paciente solo ve sus propios exámenes y documentos",
        "RF-4.1, RF-4.2, RB-1, NFR-SEG-4, Ley 20.584",
        "Verificar que el rol paciente descargue solo lo suyo y sea bloqueado (403) hacia pacientes, exámenes y documentos ajenos.",
        "Token rol paciente; existen examen propio y de otro paciente; IDs de documento propio y ajeno.",
        "1) Login paciente.\n2) GET /examenes ⇒ solo suyos (filtro examenes.js:144-162).\n3) GET /examenes/paciente/:id_ajeno ⇒ 403 \"Solo puede ver sus propios exámenes\".\n4) GET /documentos/:id_ajeno ⇒ 403.\n5) Repetir sin Authorization ⇒ 401.",
        "Paso 2: solo registros propios; pasos 3-4: 403 {\"error\":\"No autorizado\"}; paso 5: 401. Cero datos clínicos de terceros en el body.",
        "1) Cero fuga inter-paciente (Ley 20.584). 2) Denegación en backend (manipular URL no basta). 3) Los intentos denegados quedan auditables.",
        "GET /examenes (lista filtrada)\nGET /examenes/paciente/:id_ajeno\nGET /documentos/examen/:examen_ajeno_id\nGET /examenes sin Authorization",
    ),
    (
        "CP-07",
        "RBAC: paciente no muta exámenes ni escala privilegios",
        "RB-2, RB-3, RF-3.1, NFR-SEG-4",
        "Verificar que el rol paciente no cree/edite/borre exámenes ni usuarios, no se auto-promueva a admin ni altere usuario_id de su ficha clínica.",
        "Token de paciente (y de medico para la prueba de escalada de rol); BD con datos sintéticos.",
        "1) Enviar cada mutación con JWT de paciente.\n2) Verificar BD tras cada intento.\n3) Intento de auto-promoción vía PUT /usuarios/:id con rol_id de admin (como medico).",
        "Todo ⇒ 403; BD intacta; usuario_id sin cambios; el médico no puede cambiar su rol_id a admin.",
        "1) Rol evaluado en backend. 2) Si POST /usuarios devuelve 201 ⇒ H-02; si PUT /pacientes cambia usuario_id ⇒ H-10; si el médico puede cambiar rol_id ⇒ H-11. 3) Cobertura de la matriz RBAC para el rol paciente.",
        "Con token paciente: POST /examenes; PUT /examenes/:id; DELETE /examenes/:id; POST /usuarios con rol_id de admin; PUT /pacientes/:id cambiando usuario_id; DELETE /usuarios/:id.\nCon token medico: PUT /usuarios/2 con rol_id 1.",
    ),
    (
        "CP-08",
        "Eliminación de examen: soft delete + auditoría",
        "RF-3.3, RF-5.1, Ley 19.628",
        "Confirmar el borrado lógico (soft delete) previo a un modal de confirmación y el registro completo del evento en la tabla auditoría.",
        "Token rol admin o medico; examen existente; acceso psql a la BD de QA.",
        "1) UI: ficha ⇒ Eliminar Examen.\n2) Verificar modal de confirmación.\n3) Confirmar.\n4) Verificar desaparición en UI.\n5) psql: SELECT id, eliminado FROM examen_medico WHERE id=…; SELECT * FROM auditoria WHERE accion LIKE '%…%'.\n6) Cancelar el modal en otro examen ⇒ nada cambia.",
        "Fila actualizada eliminado=true (sin DELETE FROM); log con usuario, acción=ELIMINACION_LOGICA_EXAMEN, recurso_id, timestamp UTC e ip_origen; el GET tras DELETE sigue accesible con eliminado=true.",
        "1) Si el código usa DELETE FROM examen_medico (examenes.js:408) ⇒ RECHAZADO, hallazgo H-06. 2) Si el esquema auditoria no tiene recurso_id ni ip_origen (init.sql:88-93) ⇒ H-12. 3) Modal presente en UI. 4) Log antes del 200.",
        "DELETE /examenes/:id con admin.\nGET /examenes/:id tras el DELETE (soft delete).\nSQL: SELECT id, eliminado FROM examen_medico WHERE id=…;\nSELECT * FROM auditoria WHERE accion LIKE '%…%';",
    ),
    (
        "CP-09",
        "Inmutabilidad de la tabla auditoría",
        "RF-5.1, NFR-SEG-7, Ley 19.628",
        "Verificar que ni la aplicación ni un usuario Admin puedan modificar o borrar registros de la bitácora de auditoría.",
        "Acceso psql con credenciales de la aplicación; registro existente en auditoria.",
        "1) Identificar un registro existente.\n2) Ejecutar UPDATE/DELETE con credenciales de la app.\n3) Releer el registro.\n4) Verificar REVOKE en information_schema.\n5) Borrar un usuario (DELETE /usuarios/:id) y verificar si sus logs quedan con usuario_id NULL.",
        "Ambas sentencias denegadas (permission denied); registro idéntico tras el intento; la trazabilidad del autor se conserva al borrar usuarios.",
        "1) append-only real (si no hay REVOKE ⇒ H-12). 2) Si la FK usa ON DELETE SET NULL y anula la atribución ⇒ H-07. 3) REVOKE documentado en el DDL.",
        "UPDATE auditoria SET accion='HACK' WHERE id=1;\nDELETE FROM auditoria WHERE id=1;\nSELECT * FROM information_schema.role_table_grants WHERE table_name='auditoria';",
    ),
    (
        "CP-10",
        "Inyección SQL en login",
        "NFR-SEG-2, NFR-SEG-5, OWASP A03",
        "Verificar que las cadenas maliciosas en el login se traten como literales (consultas parametrizadas $1) y no alteren la BD.",
        "API operativa; tabla usuarios con datos del dump.",
        "1) Enviar payloads por Postman.\n2) Active scan de ZAP sobre /autenticacion.\n3) Revisar respuestas y logs.\n4) Verificar integridad de usuarios (SELECT count(*)).",
        "401 {\"error\":\"Credenciales inválidas\"} ante todos los payloads; cero 500; sin mensajes de PostgreSQL; tabla intacta.",
        "1) 401 uniforme. 2) Sin stack traces (si glosa trae err.message ⇒ H-15). 3) ZAP sin SQLi ≥media. 4) DROP no ejecutado. El código usa $1 ⇒ se espera PASS.",
        "POST /autenticacion/login con payloads:\n{\"nombre_usuario\":\"' OR '1'='1\", \"password\":\"' OR '1'='1\"}\nadmin'--\n'; DROP TABLE usuarios;--",
    ),
    (
        "CP-11",
        "XSS en campos clínicos",
        "NFR-SEG-5, OWASP A03",
        "Verificar que payloads XSS en campos clínicos (diagnosis, observaciones, notas) se almacenen como texto literal y no se ejecuten, con cabecera CSP presente.",
        "Token rol medico; navegador para inspección.",
        "1) Crear registros con payload (rol medico).\n2) Abrir la ficha en el navegador.\n3) ¿Se dispara alert?\n4) Revisar el JSON crudo y la cabecera CSP.",
        "Payload como texto literal; sin ejecución de JS; cabecera Content-Security-Policy presente.",
        "1) Cero ejecución de JS (React escapa por defecto ⇒ probable PASS en UI). 2) Sin cabecera CSP ⇒ H-14. 3) Backend también escapa/rechaza (defensa en profundidad).",
        "POST /examenes con \"diagnosis\": \"<script>alert('XSS')</script>\"\nPOST /pacientes con \"observaciones_medicas_generales\": \"<img src=x onerror=alert(1)>\"",
    ),
    (
        "CP-12",
        "TLS y cabeceras de seguridad",
        "NFR-SEG-1, OWASP A05",
        "Verificar cifrado en tránsito (TLS 1.2+), redirect HTTP→HTTPS, cabeceras de seguridad mínimas y CORS restringido a una allowlist.",
        "Entorno QA accesible por HTTP y (si aplica) HTTPS; herramienta curl.",
        "1) HTTP ⇒ redirect 301.\n2) HTTPS ⇒ TLS ≥1.2.\n3) Inspeccionar Strict-Transport-Security, X-Content-Type-Options, X-Frame-Options, Content-Security-Policy y Referrer-Policy.\n4) Revisar CORS con Origin: https://evil.example.",
        "Redirect; TLS 1.2/1.3; todas las cabeceras presentes; CORS solo con orígenes de la allowlist.",
        "1) Sin HTTP aceptado sin redireccionar. 2) 100% de cabeceras (si están ausentes ⇒ H-14; si cors() es abierto ⇒ H-14). 3) TLS <1.2 deshabilitado.",
        "curl -I http://localhost:4444/examenes\ncurl -I https://<qa>/examenes\nSSL Labs\nGET / y GET /openapi.json",
    ),
    (
        "CP-13",
        "Carga concurrente de 200 usuarios",
        "NFR-PERF-1, NFR-PERF-3",
        "Medir la latencia y estabilidad de la API con 200 hilos concurrentes y cuantificar el impacto de delayMiddleware(5000) mediante una prueba A/B.",
        "QA Docker aislado; plan Cuidarte_LoadTest_200.jmx; tokens pregenerados.",
        "1) JMeter ⇒ cargar el plan.\n2) Corrida A: GET /examenes (con delay 5 s).\n3) Corrida B: endpoint sin delay (GET /roles o GET /).\n4) Aggregate Report + CPU/memoria.",
        "Promedio <300 ms; 0% error; CPU <80%.",
        "1) Corrida B <300 ms ⇒ base sana. 2) Corrida A ≥5000 ms ⇒ confirma H-13 e incumplimiento NFR-PERF-1/3. 3) Cero 500 y cero caídas. 4) Sin agotamiento del Pool de pg.",
        "200 hilos · ramp-up 10 s · 5 min.\nGET /examenes (con delay)\nGET /roles o GET / (sin delay)\nAuthorization: Bearer.",
    ),
    (
        "CP-14",
        "Carga de SPA y transferencia de adjuntos",
        "NFR-PERF-2, RF-4",
        "Medir el render inicial de la SPA (<2 s en red móvil) y la subida/descarga de adjuntos (≤10 s) con verificación de integridad byte a byte.",
        "Frontend desplegado (:3333); archivo PDF de prueba; throttle Slow 4G en DevTools.",
        "1) Lighthouse ×3 corridas en red móvil.\n2) Cronometrar la subida desde UI.\n3) Cronometrar la descarga.\n4) Comparar hash MD5 del archivo subido vs descargado.",
        "Carga <2 s promedio; transferencias ≤10 s; hash idéntico.",
        "1) Promedio de Lighthouse <2 s. 2) Transferencias ≤10 s (la subida tiene delay 5 s ⇒ medir). 3) Integridad byte a byte. 4) Verificar que uploads/ sea un volumen persistente en Docker.",
        "URL raíz del frontend (:3333) con throttle Slow 4G.\nPOST /documentos (PDF 1.5 MB)\nGET /documentos/:id\nMD5 del archivo subido vs descargado.",
    ),
    (
        "CP-15",
        "Accesibilidad y UAT con adultos mayores",
        "NFR-USAB-1, NFR-USAB-4, RF-4.1",
        "Verificar que 5 adultos mayores (>65) completen el flujo login → paciente → exámenes → descargar PDF sin ayuda, y que la UI cumpla WCAG 2.1 AA.",
        "Credenciales sintéticas; módulos Login, PacientesList y MisResultados; Axe DevTools; tablet y laptop; panel de 5 evaluadores.",
        "1) Axe en /login, lista de pacientes y MisResultados.\n2) Cada evaluador inicia sesión.\n3) Busca paciente/examen.\n4) Descarga PDF.\n5) Registrar tiempos/dudas; probar solo teclado (Tab/Enter/Esc).",
        "0 violaciones críticas en Axe; 5/5 completan; texto >12 px; contraste ≥4.5:1; targets ≥48 px.",
        "1) 5/5 sin asistencia. 2) Score de Axe ≥90% sin críticas. 3) Flujo 100% por teclado (RoleGuard no debe romper la navegación). 4) Video por evaluador.",
        "Credenciales sintéticas del dump.\nAxe DevTools en /login, lista de pacientes y MisResultados.\nTablet + laptop; flujo completo de descarga de PDF.",
    ),
    (
        "CP-16",
        "Compatibilidad de navegadores y dispositivos",
        "NFR-COMPAT-1, NFR-COMPAT-2",
        "Ejecutar un flujo reducido (login ⇒ lista ⇒ descarga) en 4 navegadores × 3 dispositivos (12 combinaciones) y verificar responsividad y consola limpia.",
        "Frontend desplegado; Chrome, Firefox, Safari y Edge (2 últimas versiones) en escritorio, tablet y móvil.",
        "1) Ejecutar el flujo por cada combinación (12).\n2) Verificar responsividad (Tailwind) y modales.\n3) Consola del navegador sin errores JS.",
        "100% de combinaciones operativas.",
        "1) Cero bloqueos. 2) Sin scroll horizontal no intencional. 3) Consola limpia.",
        "Chrome, Firefox, Safari, Edge × escritorio/tablet/móvil.\nFlujo: login ⇒ lista de pacientes ⇒ descarga de PDF.",
    ),
    (
        "CP-17",
        "Disponibilidad 99.5% y restauración de respaldos",
        "NFR-DIS-1, NFR-DIS-2, NFR-SEG-7",
        "Verificar el uptime mensual ≥99.5% mediante healthcheck monitoreado y la restaurabilidad de BD y uploads sin pérdida de datos.",
        "Entorno QA desplegado; dump dump-cuidarteplus.sql; volumen de BACKEND/uploads/; acceso de monitoreo.",
        "1) Extraer el histórico de monitoreo (GET / cada 60 s por 30 días).\n2) Calcular uptime.\n3) Restaurar dump en BD descartable.\n4) Verificar conteos (usuarios, pacientes, examen_medico, documentos_examen).\n5) Verificar que uploads/ sobrevive restart de Docker (volumen).",
        "Uptime ≥99.5% (máx. ~3 h 39 min caído/mes); restauración sin pérdida; uploads persistentes.",
        "1) ≥99.5%. 2) Checksums/conteos idénticos. 3) Si uploads/ se pierde al redesplegar ⇒ riesgo confirmado. 4) Runbook de rollback documentado.",
        "GET / (healthcheck {\"name\":\"cuidarteplus\",\"status\":\"ok\"}) monitoreado cada 60 s por 30 días.\ndump-cuidarteplus.sql\nVolumen BACKEND/uploads/.",
    ),
    (
        "CP-18",
        "Autenticación obligatoria en endpoints mutantes",
        "NFR-SEG-4, RB-2",
        "Verificar que toda operación de mutación exija JWT y rol adecuado según la matriz RBAC, sin token ⇒ 401 y con rol insuficiente ⇒ 403.",
        "Colección/curl sin header Authorization; tokens de paciente y medico; BD con datos sintéticos.",
        "1) Enviar cada petición con curl sin token.\n2) Con token de paciente: POST /usuarios con rol_id admin.\n3) Con token de medico: PUT /usuarios/:id cambiando su rol_id a admin.\n4) Verificar BD después de cada intento.",
        "Todo ⇒ 401 sin token / 403 con rol insuficiente; cero cambios en BD.",
        "1) DELETE /usuarios sin token debe dar 401 (si ejecuta el borrado ⇒ H-03 CRÍTICO). 2) Mutaciones en /roles sin token ⇒ 401 (si responde 200/201 ⇒ H-04). 3) Búsqueda RUT sin token ⇒ 401 (si devuelve ficha completa ⇒ H-05). 4) POST /usuarios con paciente ⇒ 403 (si responde 201 ⇒ H-02). 5) Auto-promoción del médico ⇒ 403 (si es posible ⇒ H-11).",
        "Sin Authorization:\nDELETE /usuarios/999999\nDELETE /roles/999999\nPOST /roles {\"nombre\":\"hacker\"}\nPUT /roles/1\nGET /usuarios\nGET /auditoria\nGET /pacientes/buscar/rut/11111111-1\nCon token paciente: POST /usuarios con rol_id 1.\nCon token medico: PUT /usuarios/2 con rol_id 1.",
    ),
    (
        "CP-19",
        "Exposición de información y configuración",
        "NFR-SEG-1, NFR-SEG-5",
        "Cuantificar qué información expone la API sin autenticación (Swagger, endpoints públicos) y en las respuestas de error 500 (glosa del cliente), además de secretos en el paquete.",
        "API accesible; ZIP del código fuente para revisar archivos .env.",
        "1) Catalogar endpoints públicos vía /openapi.json.\n2) Enviar body inválido ⇒ leer detalles.\n3) GET /examenes/abc (cast a BIGINT) ⇒ leer glosa.\n4) Revisar .env presentes en el ZIP entregado.",
        "Swagger puede ser público en QA; errores 500 genéricos; cero secretos en el paquete entregado.",
        "1) Si glosa trae err.message de PostgreSQL ⇒ H-15. 2) Endpoints públicos coherentes con la matriz RBAC (/roles GET aceptable, mutaciones no). 3) Si hay .env con JWT_SECRET y password de BD en el ZIP ⇒ H-08.",
        "GET /, GET /openapi.json, GET /docs\nPOST /pacientes con campo faltante\nGET /examenes/abc (id no numérico)\nListado de archivos .env del ZIP.",
    ),
]


def cp_table(doc, cp):
    cid, nombre, req, desc, pre, pasos, esperado, criterio, datos = cp
    table = doc.add_table(rows=14, cols=3)
    try:
        table.style = "Grid Table 4"
    except KeyError:
        try:
            table.style = "Table Grid"
        except KeyError:
            pass
    # row 0 header
    for i, txt in enumerate(("ID", "NOMBRE", "REQUERIMIENTO")):
        set_cell_text(table.rows[0].cells[i], txt, size=10, bold=True)
        shade_cell(table.rows[0].cells[i], HDR_BG)
    # row 1 values
    for i, txt in enumerate((cid, nombre, req)):
        set_cell_text(table.rows[1].cells[i], txt, size=10, bold=False)

    blocks = [
        (2, "DESCRIPCIÓN", desc),
        (4, "PRECONDICIONES", pre),
        (6, "PASOS", pasos),
        (8, "RESULTADO ESPERADO", esperado),
        (10, "CRITERIO DE ACEPTACIÓN", criterio),
        (12, "DATOS DE PRUEBA", datos),
    ]
    for row_idx, label, content in blocks:
        # merge the 3 cells of the label row and content row
        label_row = table.rows[row_idx]
        content_row = table.rows[row_idx + 1]
        # merge label row
        c0 = label_row.cells[0]
        c0.merge(label_row.cells[1])
        # after first merge the third may already be same; merge again safely
        try:
            c0.merge(label_row.cells[2])
        except Exception:
            pass
        set_cell_text(table.rows[row_idx].cells[0], label, size=10, bold=True)
        shade_cell(table.rows[row_idx].cells[0], LBL_BG)
        # merge content row
        c0 = content_row.cells[0]
        c0.merge(content_row.cells[1])
        try:
            c0.merge(content_row.cells[2])
        except Exception:
            pass
        set_cell_text(table.rows[row_idx + 1].cells[0], content, size=10, bold=False)

    # spacer
    body_p(doc, "", space_after=6)
    return table


def section4(doc):
    h1(doc, "4. Diseño de casos de prueba")
    body_p(
        doc,
        "Los 19 casos de prueba se ejecutan contra el host de pruebas http://localhost:4444 (Docker) "
        "y siguen el formato del template: ID, nombre, requerimiento, descripción, precondiciones, "
        "pasos, resultado esperado, criterio de aceptación y datos de prueba. Cada criterio de "
        "aceptación refleja el ERS v1.1; cuando el código real incumple el esperado, el caso se "
        "considera RECHAZADO y se registra el hallazgo asociado (H-01…H-17) en "
        "hallazgos-seguridad-cuidarte.md."
    )
    for cp in CPS:
        cp_table(doc, cp)


def configure_styles(doc):
    # Ensure Normal is Arial 10
    try:
        st = doc.styles["Normal"]
        st.font.name = "Arial"
        st.font.size = Pt(10)
        rPr = st.element.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.insert(0, rFonts)
        for a in ("w:ascii", "w:hAnsi", "w:cs"):
            rFonts.set(qn(a), "Arial")
    except KeyError:
        pass
    # Heading styles
    for name, size, bold in (("Heading 1", 16, True), ("Heading 2", 12, True)):
        try:
            st = doc.styles[name]
            st.font.name = "Arial"
            st.font.size = Pt(size)
            st.font.bold = bold
            st.font.color.rgb = BLACK
        except KeyError:
            pass


def main():
    doc = Document(TEMPLATE)
    configure_styles(doc)
    clear_body_keep_styles(doc)

    # page setup A4 margins from template already on section
    cover(doc)
    # INDICE
    h1(doc, "INDICE")
    add_toc_field(doc)
    # page break after index
    p = doc.add_paragraph()
    r = p.add_run()
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    r._r.append(br)

    section1(doc)
    section2(doc)
    section3(doc)
    section4(doc)

    doc.save(OUT)
    print("OK", OUT)
    # verify
    v = Document(OUT)
    print("paragraphs", len(v.paragraphs), "tables", len(v.tables))
    h1s = [p.text for p in v.paragraphs if p.style and p.style.name == "Heading 1"]
    h2s = [p.text for p in v.paragraphs if p.style and p.style.name == "Heading 2"]
    print("H1:", h1s)
    print("H2:", h2s)
    if v.tables:
        print("first table rows", len(v.tables[0].rows), "cols", len(v.tables[0].columns))
        print("last table rows", len(v.tables[-1].rows))


if __name__ == "__main__":
    main()
