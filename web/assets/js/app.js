/* ============================================================
   Estrategias Fiscales de Costa Rica — Lógica de la SPA
   ============================================================ */
(function () {
  "use strict";

  var DATA = window.ESTRATEGIAS || { titulo: "", subtitulo: "", categorias: [], capitulos: [] };

  var el = {
    progreso: document.getElementById("progreso"),
    lateral: document.getElementById("lateral"),
    indice: document.getElementById("indice"),
    busqueda: document.getElementById("busqueda"),
    botonTema: document.getElementById("boton-tema"),
    iconoTema: document.getElementById("tema-icono"),
    textoTema: document.getElementById("tema-texto"),
    botonMenu: document.getElementById("boton-menu"),
    ruta: document.getElementById("ruta"),
    capitulo: document.getElementById("capitulo"),
    velo: document.getElementById("velo"),
  };

  var porSlug = {};
  DATA.capitulos.forEach(function (c) { porSlug[c.slug] = c; });

  // ------------------------------------------------------------------ //
  // Utilidades
  // ------------------------------------------------------------------ //
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }
  function pad2(n) { return (n < 10 ? "0" : "") + n; }

  // ------------------------------------------------------------------ //
  // Índice lateral
  // ------------------------------------------------------------------ //
  function construirIndice() {
    var html = "";
    var inicio = porSlug["inicio"];
    if (inicio) {
      html += '<a class="item-indice item-inicio" href="#/inicio" data-slug="inicio">'
        + '<span class="numero">⌂</span>'
        + '<span class="titulo-item">Inicio</span></a>';
    }
    DATA.categorias.forEach(function (cat) {
      html += '<div class="parte-titulo">' + esc(cat.titulo) + "</div>";
      DATA.capitulos.forEach(function (c) {
        if (c.parte_key === cat.key) {
          html += '<a class="item-indice" href="#/' + c.slug + '" data-slug="' + c.slug + '">'
            + '<span class="numero">' + pad2(c.numero) + "</span>"
            + '<span class="titulo-item">' + esc(c.titulo) + "</span></a>";
        }
      });
    });
    el.indice.innerHTML = html;
  }

  // ------------------------------------------------------------------ //
  // Navegación anterior / siguiente
  // ------------------------------------------------------------------ //
  function navHTML(c) {
    var p = c.prev && porSlug[c.prev] ? porSlug[c.prev] : null;
    var n = c.next && porSlug[c.next] ? porSlug[c.next] : null;
    if (!p && !n) return "";
    var nav = '<nav class="navegacion">';
    if (p) {
      nav += '<a class="enlace-nav" href="#/' + p.slug + '">'
        + '<span class="direccion">← Anterior</span>'
        + '<span class="titulo-nav">' + esc(p.titulo) + "</span></a>";
    }
    if (n) {
      nav += '<a class="enlace-nav siguiente" href="#/' + n.slug + '">'
        + '<span class="direccion">Siguiente →</span>'
        + '<span class="titulo-nav">' + esc(n.titulo) + "</span></a>";
    }
    nav += "</nav>";
    return nav;
  }

  // ------------------------------------------------------------------ //
  // Renderizado de capítulo
  // ------------------------------------------------------------------ //
  function renderizar(slug) {
    var c = porSlug[slug];
    if (!c) { c = porSlug["inicio"]; slug = "inicio"; }
    if (!c) return;

    var html = "";
    if (slug === "inicio") {
      html += c.html;
      el.ruta.textContent = "Inicio";
    } else {
      html += '<p class="kicker">' + esc(c.parte) + " · Estrategia " + pad2(c.numero) + "</p>";
      html += "<h1>" + esc(c.titulo) + "</h1>";
      if (c.resumen) { html += '<p class="resumen">' + esc(c.resumen) + "</p>"; }
      html += c.html;
      el.ruta.textContent = c.parte + " · " + pad2(c.numero);
    }
    html += navHTML(c);

    el.capitulo.innerHTML = html;
    window.scrollTo(0, 0);
    actualizarProgreso();
    marcarActivo(slug);
    document.title = (slug === "inicio" ? DATA.titulo : c.titulo + " · " + DATA.titulo);
    cerrarLateral();
  }

  function marcarActivo(slug) {
    var items = el.indice.querySelectorAll(".item-indice");
    items.forEach(function (it) {
      it.classList.toggle("activo", it.getAttribute("data-slug") === slug);
    });
  }

  // ------------------------------------------------------------------ //
  // Progreso de lectura
  // ------------------------------------------------------------------ //
  function actualizarProgreso() {
    var max = document.documentElement.scrollHeight - window.innerHeight;
    var pct = max > 0 ? (window.scrollY / max) * 100 : 0;
    el.progreso.style.width = pct.toFixed(2) + "%";
  }

  // ------------------------------------------------------------------ //
  // Tema claro / oscuro
  // ------------------------------------------------------------------ //
  function aplicarTema(tema) {
    document.documentElement.dataset.tema = tema;
    localStorage.setItem("estrategias.tema", tema);
    if (el.iconoTema) el.iconoTema.textContent = tema === "claro" ? "☀" : "☾";
    if (el.textoTema) el.textoTema.textContent = tema === "claro" ? "Tema claro" : "Tema oscuro";
  }

  // ------------------------------------------------------------------ //
  // Buscador
  // ------------------------------------------------------------------ //
  function filtrar(q) {
    q = (q || "").trim().toLowerCase();
    var items = el.indice.querySelectorAll(".item-indice");
    items.forEach(function (it) {
      var coincide = !q || it.textContent.toLowerCase().indexOf(q) !== -1;
      it.classList.toggle("oculto", !coincide);
    });
    el.indice.querySelectorAll(".parte-titulo").forEach(function (p) {
      var sig = p.nextElementSibling, visible = false;
      while (sig && !sig.classList.contains("parte-titulo")) {
        if (sig.classList.contains("item-indice") && !sig.classList.contains("oculto")) {
          visible = true; break;
        }
        sig = sig.nextElementSibling;
      }
      p.classList.toggle("oculto", !visible);
    });
  }

  // ------------------------------------------------------------------ //
  // Menú lateral (móvil)
  // ------------------------------------------------------------------ //
  function abrirLateral() {
    el.lateral.classList.add("abierta");
    if (el.velo) { el.velo.hidden = false; requestAnimationFrame(function () { el.velo.classList.add("visible"); }); }
  }
  function cerrarLateral() {
    el.lateral.classList.remove("abierta");
    if (el.velo) { el.velo.classList.remove("visible"); el.velo.hidden = true; }
  }

  // ------------------------------------------------------------------ //
  // Enrutado por hash
  // ------------------------------------------------------------------ //
  function resolverRuta() {
    var m = location.hash.match(/^#\/([a-z0-9-]+)/);
    renderizar(m ? m[1] : "inicio");
  }

  // ------------------------------------------------------------------ //
  // Inicialización
  // ------------------------------------------------------------------ //
  construirIndice();
  aplicarTema(document.documentElement.dataset.tema || "oscuro");
  resolverRuta();

  window.addEventListener("hashchange", resolverRuta);
  window.addEventListener("scroll", actualizarProgreso, { passive: true });
  window.addEventListener("resize", actualizarProgreso);

  el.botonTema.addEventListener("click", function () {
    aplicarTema(document.documentElement.dataset.tema === "claro" ? "oscuro" : "claro");
  });

  el.busqueda.addEventListener("input", function () { filtrar(el.busqueda.value); });

  el.botonMenu.addEventListener("click", function () {
    if (el.lateral.classList.contains("abierta")) { cerrarLateral(); } else { abrirLateral(); }
  });
  if (el.velo) el.velo.addEventListener("click", cerrarLateral);

  document.addEventListener("keydown", function (e) {
    if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA")) return;
    var m = location.hash.match(/^#\/([a-z0-9-]+)/);
    var c = porSlug[m ? m[1] : "inicio"];
    if (!c) return;
    if (e.key === "ArrowLeft" && c.prev) location.hash = "#/" + c.prev;
    if (e.key === "ArrowRight" && c.next) location.hash = "#/" + c.next;
  });
})();
