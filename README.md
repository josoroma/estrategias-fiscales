# Estrategias Fiscales de Costa Rica

**Planificación Tributaria.**

**Sitio en vivo:** https://josoroma.github.io/estrategias-fiscales/

Sitio web estático, autocontenido y navegable que reúne **50 estrategias de
planificación tributaria lícita** para personas y empresas en Costa Rica,
organizadas en cinco perfiles:

| Perfil | Estrategias |
| --- | --- |
| 🏛️ General | 10 |
| 👤 Trabajadores asalariados e independientes | 10 |
| 🏪 PYMEs y MIPYMES | 10 |
| 🚢 Exportadores | 10 |
| 💻 Sector tecnológico | 10 |

Cada estrategia presenta su pregunta jurídica, el análisis detallado, el
fundamento normativo verificado, los puntos pendientes de verificación, un
checklist operativo, los riesgos y una recomendación de implementación.

## Cómo leer la obra

Abre [`web/index.html`](web/index.html) en cualquier navegador (funciona
directamente desde el sistema de archivos, sin servidor). También puedes
servirla con cualquier servidor estático.

## Cómo publicar en GitHub Pages

1. Sube este directorio como repositorio de GitHub.
2. En **Settings → Pages**, elige `main` como rama y la raíz (`/`) como carpeta.
3. La portada redirige automáticamente a `web/index.html`.

No se requieren dependencias ni proceso de compilación para servir el sitio:
los datos ya están generados en `web/data/estrategias.js`.

## Regenerar los datos

Para reconstruir el contenido a partir de las estrategias fuente, ejecuta:

```bash
python3 web/build.py
```

Esto produce `web/data/estrategias.js`, `indice.md` y `MANUAL-COMPLETO.md`.

## Nota profesional

Esta obra tiene fines informativos y de estudio. No sustituye el criterio del
abogado, contador público autorizado ni asesor tributario responsable.
