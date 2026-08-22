#!/usr/bin/env python3
"""Build script for 'Estrategias Fiscales de Costa Rica'.

Lee las 50 estrategias fiscales distribuidas en cinco carpetas fuente,
neutraliza toda referencia interna (rutas, nombres de archivo, menciones al
corpus y metadatos de proceso) y produce un sitio web estático autocontenido:

  - web/data/estrategias.js     (window.ESTRATEGIAS para la SPA, funciona por file://)
  - indice.md                   (índice general del repositorio)
  - MANUAL-COMPLETO.md          (todas las estrategias en un solo archivo Markdown)

El sitio publicado no incluye, menciona ni expone rutas, enlaces o referencias
internas a las fuentes de origen utilizadas durante su construcción.

Uso:  python3 web/build.py
"""

import os
import re
import json
from datetime import date
from markdown_it import MarkdownIt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(ROOT, "web")
DATA = os.path.join(WEB, "data")

# Fuente de origen (solo lectura; NO se referencia dentro del sitio publicado).
FUENTE_BASE = os.path.join(ROOT, "..")

md = MarkdownIt("default", {"html": True, "typographer": True})

TITULO = "Estrategias Fiscales de Costa Rica"
SUBTITULO = "Planificación Tributaria"
VERSION = "1.0.0"
MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

# --------------------------------------------------------------------------- #
# Catálogo de categorías (orden de publicación)
# --------------------------------------------------------------------------- #
CATEGORIAS = [
    {
        "key": "general",
        "dir": "estrategias-fiscales-general",
        "titulo": "General",
        "subtitulo": "Estrategias transversales de planificación para personas jurídicas",
        "descripcion": (
            "Deducciones operativas, depreciación acelerada, estructura corporativa, "
            "zonas francas y regímenes especiales aplicables a empresas."
        ),
        "icono": "🏛️",
        "heading_re": re.compile(r"^## Estrategia (\d+):\s*(.*)$", re.MULTILINE),
    },
    {
        "key": "asalariados",
        "dir": "estrategias-fiscales-asalariados",
        "titulo": "Trabajadores asalariados e independientes",
        "subtitulo": "Optimización del impuesto sobre la renta para personas físicas",
        "descripcion": (
            "Escala progresiva, créditos familiares, aguinaldo, indemnizaciones, "
            "cargas sociales y ahorro voluntario para personas físicas."
        ),
        "icono": "👤",
        "heading_re": re.compile(r"^## AS-E(\d+):\s*(.*)$", re.MULTILINE),
    },
    {
        "key": "pymes",
        "dir": "estrategias-fiscales-pymes",
        "titulo": "PYMEs y MIPYMES",
        "subtitulo": "Incentivos, escala reducida y exenciones para micro, pequeñas y medianas empresas",
        "descripcion": (
            "Exención de los primeros años, escala reducida, I+D, capacitación y "
            "deducciones específicas para MIPYMES."
        ),
        "icono": "🏪",
        "heading_re": re.compile(r"^## PY-E(\d+):\s*(.*)$", re.MULTILINE),
    },
    {
        "key": "exportadores",
        "dir": "estrategias-fiscales-exportadores",
        "titulo": "Exportadores",
        "subtitulo": "Regímenes de exportación, zonas francas y comercio exterior",
        "descripcion": (
            "Contratos de exportación, zonas francas, perfeccionamiento activo, "
            "drawback y convenios para evitar la doble imposición."
        ),
        "icono": "🚢",
        "heading_re": re.compile(r"^## EX-E(\d+):\s*(.*)$", re.MULTILINE),
    },
    {
        "key": "tecnologico",
        "dir": "estrategias-fiscales-tecnologico",
        "titulo": "Sector tecnológico",
        "subtitulo": "Software, servicios digitales, propiedad intelectual e innovación",
        "descripcion": (
            "Zonas francas de servicios, desarrollo de software, regalías, "
            "opciones sobre acciones y talento para empresas de tecnología."
        ),
        "icono": "💻",
        "heading_re": re.compile(r"^## TE-E(\d+):\s*(.*)$", re.MULTILINE),
    },
]

# --------------------------------------------------------------------------- #
# Renombrado de encabezados de sección (proceso → lenguaje público)
# --------------------------------------------------------------------------- #
HEADING_RENAMES = {
    "### 1. Pregunta jurídica": "### Pregunta jurídica",
    "### 2. Respuesta Detallada": "### Respuesta detallada",
    "### 6. Checklist operativo": "### Checklist operativo",
    "### 7. Riesgos": "### Riesgos",
    "### 8. Recomendación de implementación": "### Recomendación de implementación",
    "### 9. Próximos pasos": "### Próximos pasos",
}


# --------------------------------------------------------------------------- #
# Limpieza de referencias internas
# --------------------------------------------------------------------------- #
def neutralizar_referencias(text):
    """Elimina toda ruta, nombre de archivo o mención a fuentes internas."""
    # 1. Colas «*Fuente: `...`*» (claims en formato de lista).
    text = re.sub(r"\s*\*Fuente:[^*]*\*", "", text)

    # 2. Referencias a archivos internos entre comillas invertidas.
    text = re.sub(r"`data/markdown/[^`]*`", "", text)
    text = re.sub(r"`data/case/[^`]*`", "", text)
    text = re.sub(r"`data/raw/[^`]*`", "", text)
    text = re.sub(r"`article_[A-Za-z0-9]+\.md`", "", text)
    text = re.sub(r"`derecho_[a-z0-9_/-]+\.md`", "", text)
    text = re.sub(r"`intro\.md`", "", text)
    text = re.sub(r"`outro\.md`", "", text)

    # 3. Referencias internas sin comillas (defensivo).
    text = re.sub(r"\s*[—–-]\s*intro\.md\b", "", text)
    text = re.sub(r"\s*[—–-]\s*outro\.md\b", "", text)
    text = re.sub(r"\bintro\.md\b", "", text)
    text = re.sub(r"\boutro\.md\b", "", text)
    text = re.sub(r"\bdata/markdown/[^\s)|]*", "", text)
    text = re.sub(r"\barticle_[A-Za-z0-9]+\.md\b", "", text)
    text = re.sub(r"\bderecho_[a-z0-9_/-]+", "", text)

    # 4. Referencias de línea (solo aparecen ligadas a archivos internos).
    text = re.sub(r"l[ií]neas?\s+[\d\s.,–-]+", "", text)

    # 5. Etiquetas de proceso interno.
    text = text.replace("(conocimiento consolidado)", "")
    text = text.replace(", conocimiento consolidado", "")
    text = re.sub(r"\(consulta[^)]*\)", "", text)

    # 6. Normalización de Decreto Ejecutivo.
    text = re.sub(r"\bDE-(\d{4,5})\b", r"Decreto Ejecutivo N° \1", text)

    # 7. Menciones al «corpus» (fuente interna) — frases específicas primero.
    text = re.sub(r"\by el corpus\b", "", text)
    text = re.sub(r"no verificado en corpus\b", "no verificado en esta revisión", text)
    text = re.sub(r"no disponibles en corpus\b", "no disponibles en esta revisión", text)
    text = re.sub(
        r"no disponibles en el corpus en formato[^)]*",
        "no disponibles en esta revisión",
        text,
    )
    text = re.sub(r"al corpus completo\b", "a la normativa completa", text)
    text = re.sub(r"\bEl corpus no contiene\b", "No se dispone del", text)
    text = re.sub(
        r"el corpus tiene la ley pero no hemos leído todos los artículos",
        "la ley está disponible, aunque no se han leído todos sus artículos",
        text,
    )
    text = re.sub(r"No en corpus\b", "No verificado", text)
    text = re.sub(r"\b[Cc]orpus\b", "", text)

    # 8. Limpieza de residuos de puntuación y espacios.
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def renombrar_encabezados(text):
    for viejo, nuevo in HEADING_RENAMES.items():
        text = text.replace(viejo, nuevo)
    return text


def procesar_html(html, convertir_h3=False):
    """Post-procesa el HTML renderizado: envuelve tablas, marca ítems ✅/⚠️
    y nivela los encabezados de sección h3→h2."""
    html = re.sub(
        r"<table>.*?</table>",
        lambda mt: '<div class="envoltorio-tabla">' + mt.group(0) + "</div>",
        html,
        flags=re.DOTALL,
    )
    html = html.replace("<li>✅", '<li class="verificado">✅')
    html = html.replace("<li>⚠️", '<li class="pendiente">⚠️')
    if convertir_h3:
        html = html.replace("<h3>", "<h2>").replace("</h3>", "</h2>")
    return html


def md_a_texto_plano(text):
    """Conversión ligera Markdown → texto plano (para el resumen)."""
    text = re.sub(r"```[^\n]*\n(.*?)```", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*-{3,}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\|?[\s:|-]+\|?\s*$", "", text, flags=re.MULTILINE)
    text = text.replace("|", " ")
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"^\s*> ?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return " ".join(text.split())


# --------------------------------------------------------------------------- #
# Carga y transformación de estrategias
# --------------------------------------------------------------------------- #
def cargar_estrategias():
    categorias = []
    for cat in CATEGORIAS:
        carpeta = os.path.join(FUENTE_BASE, cat["dir"])
        archivos = sorted(
            f for f in os.listdir(carpeta)
            if f.endswith(".md") and not f.lower().startswith("resumen")
        )
        estrategias = []
        comparativo_html = None
        for fn in archivos:
            with open(os.path.join(carpeta, fn), encoding="utf-8") as fh:
                raw = fh.read()
            m = cat["heading_re"].search(raw)
            if not m:
                print(f"  [aviso] sin título de estrategia: {cat['dir']}/{fn}")
                continue
            numero = int(m.group(1))
            titulo = m.group(2).strip()

            # El cuerpo inicia después del título; el encabezado de proceso
            # (H1 + metadatos) queda descartado.
            body = raw[m.end():]

            # Separa el cuadro comparativo (si existe) del cuerpo de la estrategia.
            comp = re.search(r"^## Resumen Comparativo.*$", body, flags=re.MULTILINE)
            if comp:
                comparativo_md = body[comp.start():]
                body = body[:comp.start()]
                comparativo_md = re.sub(
                    r"^## Resumen Comparativo.*$", "", comparativo_md, flags=re.MULTILINE
                )
                comparativo_md = re.sub(
                    r"^## Anexo: Fuentes del Corpus.*$", "", comparativo_md,
                    flags=re.MULTILINE | re.DOTALL,
                )
                comparativo_md = re.sub(
                    r"^>\s*\*\*[^*]+\*\*.*$", "", comparativo_md, flags=re.MULTILINE
                )
                comparativo_md = re.sub(r"^\s*-{3,}\s*$", "", comparativo_md, flags=re.MULTILINE)
                if comparativo_html is None:
                    comparativo_html = procesar_html(
                        md.render(neutralizar_referencias(comparativo_md))
                    )

            # Descarta la sección de tareas (Kanban / Gherkin).
            body = re.sub(
                r"### 📋 Task Kanban.*?(?=### 1\. Pregunta jurídica)",
                "",
                body,
                flags=re.DOTALL,
            )
            # Descarta cualquier pie de metadatos residual.
            body = re.sub(r"^>\s*\*\*[^*]+\*\*.*$", "", body, flags=re.MULTILINE)
            body = re.sub(r"^\s*-{3,}\s*$", "", body, flags=re.MULTILINE)

            # Elimina las secciones de verificación y fuentes (proceso interno):
            # se descartan por completo del contenido publicado.
            body = re.sub(
                r"### 3\. Claims verificados.*?(?=### 6\. Checklist operativo)",
                "",
                body,
                flags=re.DOTALL,
            )

            # Extrae la pregunta jurídica como resumen.
            resumen = ""
            rp = re.search(r"### 1\. Pregunta jurídica(.*?)(?=### 2\. )", body, re.DOTALL)
            if rp:
                resumen = neutralizar_referencias(md_a_texto_plano(rp.group(1)))

            # Neutraliza referencias internas.
            body = neutralizar_referencias(body)
            body = renombrar_encabezados(body)
            html = procesar_html(md.render(body), convertir_h3=True)

            estrategias.append({
                "numero": numero,
                "titulo": titulo,
                "slug": f"{cat['key']}-{numero}",
                "resumen": resumen,
                "html": html,
                "md": body,
            })

        estrategias.sort(key=lambda e: e["numero"])
        categorias.append({
            "key": cat["key"],
            "titulo": cat["titulo"],
            "subtitulo": cat["subtitulo"],
            "descripcion": cat["descripcion"],
            "icono": cat["icono"],
            "comparativo_html": comparativo_html,
            "estrategias": estrategias,
        })
    return categorias


# --------------------------------------------------------------------------- #
# Portada (página de inicio)
# --------------------------------------------------------------------------- #
def tarjetas_categorias(categorias):
    cards = []
    for cat in categorias:
        n = len(cat["estrategias"])
        slug = cat["estrategias"][0]["slug"] if n else "inicio"
        cards.append(
            '<a class="tarjeta" href="#/' + slug + '">'
            '<span class="icono">' + cat["icono"] + "</span>"
            "<h3>" + cat["titulo"] + "</h3>"
            '<p class="desc">' + cat["descripcion"] + "</p>"
            '<span class="conteo">' + str(n) + " estrategias →</span>"
            "</a>"
        )
    return '<div class="tarjetas">' + "\n".join(cards) + "</div>"


def secciones_comparativas(categorias):
    bloques = []
    for cat in categorias:
        if cat["comparativo_html"]:
            bloques.append(
                '<section class="comparativo">'
                "<h2>" + cat["titulo"] + "</h2>"
                + cat["comparativo_html"]
                + "</section>"
            )
    return "\n".join(bloques)


def fecha_es():
    hoy = date.today()
    return f"{hoy.day} de {MESES[hoy.month - 1]} de {hoy.year}"


def bloque_versionado(categorias):
    """Bloque de versión y actualización con todas las categorías y la fecha."""
    total = sum(len(c["estrategias"]) for c in categorias)
    filas = "".join(
        '<li><span class="icono">' + c["icono"] + "</span>"
        "<span>" + c["titulo"] + "</span>"
        '<span class="conteo">' + str(len(c["estrategias"])) + " estrategias</span>"
        "</li>"
        for c in categorias
    )
    return (
        '<div class="versionado">'
        '<h2>Versión y actualización</h2>'
        '<p class="meta-linea">'
        '<span class="version">Versión ' + VERSION + "</span>"
        '<span class="divisor">·</span>'
        '<span class="fecha">Actualizado el ' + fecha_es() + "</span>"
        '<span class="divisor">·</span>'
        '<span class="total"><strong>' + str(total) + " estrategias</strong> en "
        + str(len(categorias)) + " categorías</span>"
        "</p>"
        '<ul class="lista-version">' + filas + "</ul>"
        "</div>"
    )


def portada_md(categorias):
    total = sum(len(c["estrategias"]) for c in categorias)
    return (
        "# " + TITULO + "\n\n"
        "*" + SUBTITULO + "*\n\n"
        "Esta obra reúne **" + str(total) + " estrategias de planificación "
        "tributaria lícita** organizadas en cinco perfiles para personas y "
        "empresas en Costa Rica: estrategias generales, trabajadores asalariados "
        "e independientes, PYMEs, exportadores y el sector tecnológico.\n\n"
        "Cada estrategia presenta su pregunta jurídica, el análisis detallado, un "
        "checklist operativo, los riesgos y una recomendación de implementación.\n\n"
    )


def construir_portada(categorias):
    html = md.render(portada_md(categorias))
    html += tarjetas_categorias(categorias)
    html += "<h2>Cuadros comparativos</h2>\n" + secciones_comparativas(categorias)
    html += md.render(
        "\n\n## Método y alcance\n\n"
        "- Toda estrategia cita su fundamento normativo (ley, artículo e inciso) "
        "directamente en el análisis.\n"
        "- Las cifras y umbrales se presentan con el período fiscal al que corresponden.\n\n"
        "## Nota profesional\n\n"
        "Esta obra tiene fines informativos y de estudio. No sustituye el criterio "
        "profesional del abogado, contador público autorizado ni asesor tributario "
        "responsable.\n"
    )
    html += bloque_versionado(categorias)
    return html


# --------------------------------------------------------------------------- #
# Emisión de artefactos
# --------------------------------------------------------------------------- #
def build_bundle(categorias, portada_html):
    capitulos = [
        {
            "slug": "inicio",
            "parte": "",
            "parte_key": "",
            "numero": 0,
            "titulo": "Inicio",
            "resumen": SUBTITULO,
            "html": portada_html,
            "prev": None,
            "next": None,
        }
    ]
    for cat in categorias:
        for e in cat["estrategias"]:
            capitulos.append({
                "slug": e["slug"],
                "parte": cat["titulo"],
                "parte_key": cat["key"],
                "numero": e["numero"],
                "titulo": e["titulo"],
                "resumen": e["resumen"],
                "html": e["html"],
                "prev": None,
                "next": None,
            })
    # Encadenamiento global: inicio → general-1 → … → tecnológico-10 → inicio.
    for i, ch in enumerate(capitulos):
        ch["prev"] = capitulos[i - 1]["slug"] if i > 0 else None
        ch["next"] = capitulos[i + 1]["slug"] if i < len(capitulos) - 1 else "inicio"

    payload = {
        "titulo": TITULO,
        "subtitulo": SUBTITULO,
        "version": VERSION,
        "fecha": fecha_es(),
        "categorias": [
            {
                "key": c["key"],
                "titulo": c["titulo"],
                "subtitulo": c["subtitulo"],
                "descripcion": c["descripcion"],
                "icono": c["icono"],
                "n": len(c["estrategias"]),
            }
            for c in categorias
        ],
        "capitulos": capitulos,
    }
    return "window.ESTRATEGIAS = " + json.dumps(payload, ensure_ascii=False, indent=1) + ";\n"


def build_indice(categorias):
    lineas = [
        "# " + TITULO,
        "",
        "*" + SUBTITULO + "*",
        "",
        "## Índice",
        "",
    ]
    for cat in categorias:
        lineas.append("\n### " + cat["titulo"] + "\n")
        for e in cat["estrategias"]:
            lineas.append(
                f"{e['numero']:02d}. [{e['titulo']}](web/index.html#/{e['slug']})"
            )
    lineas.append("\n## Sitio web\n")
    lineas.append("- [Leer en el navegador](web/index.html)")
    return "\n".join(lineas) + "\n"


def build_manual(categorias):
    lineas = [
        "# " + TITULO,
        "",
        "## " + SUBTITULO,
        "",
        "> Obra unificada generada automáticamente. Versión de lectura enriquecida: "
        "`web/index.html`.",
        "",
        "---",
        "",
    ]
    for cat in categorias:
        lineas.append("\n\n# " + cat["titulo"] + "\n")
        for e in cat["estrategias"]:
            lineas.append(f"\n## Estrategia {e['numero']:02d}: {e['titulo']}\n")
            lineas.append(e["md"].strip() + "\n")
    return "\n".join(lineas) + "\n"


def main():
    os.makedirs(DATA, exist_ok=True)
    categorias = cargar_estrategias()
    total = sum(len(c["estrategias"]) for c in categorias)
    portada_html = construir_portada(categorias)

    with open(os.path.join(DATA, "estrategias.js"), "w", encoding="utf-8") as fh:
        fh.write(build_bundle(categorias, portada_html))
    with open(os.path.join(ROOT, "indice.md"), "w", encoding="utf-8") as fh:
        fh.write(build_indice(categorias))
    with open(os.path.join(ROOT, "MANUAL-COMPLETO.md"), "w", encoding="utf-8") as fh:
        fh.write(build_manual(categorias))

    print(f"OK: {total} estrategias en {len(categorias)} categorías -> estrategias.js")


if __name__ == "__main__":
    main()
