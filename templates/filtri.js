// Il filtro dell'indice. I dati delle voci sono nella pagina (window.VOCI): il
// filtro lavora nel browser, senza server. Ogni gruppo di chip e' un filtro;
// ogni gruppo ammette una scelta sola; la prima chip vuol dire "nessun filtro".
(function () {
  function avvia() {
    var dati = window.VOCI, tabella = document.getElementById("tabella-voci");
    if (!dati || !tabella || tabella.dataset.avviato) return;   // una volta sola per pagina
    tabella.dataset.avviato = "1";
    var perId = {}; dati.forEach(function (v) { perId[v.id] = v; });
    var testo = document.getElementById("f-testo"), conta = document.getElementById("f-conta");
    var gruppi = Array.prototype.slice.call(document.querySelectorAll(".filtri-gruppo"));

    function scelte(nome) {                         // i valori accesi di un gruppo
      var g = document.querySelector('.filtri-gruppo[data-gruppo="' + nome + '"]');
      return Array.prototype.slice.call(g.querySelectorAll('.chip[aria-pressed="true"]')).map(function (b) { return b.dataset.valore; });
    }

    function passa(v) {                             // la voce supera tutti i filtri?
      var q = testo.value.trim().toLowerCase(), rel = scelte("relazione")[0], std = scelte("standard")[0], pro = scelte("prospettiva")[0];
      if (q && v.testo.indexOf(q) < 0) return false;
      if (pro && v.prospettiva.indexOf(pro) < 0) return false;
      if (rel === "bt" && !v.bt) return false;
      if (rel === "nt" && !v.nt) return false;
      if (rel === "rt" && !v.rt) return false;
      if (rel === "radice" && v.bt) return false;
      if (std === "*" && v.standard.length === 0) return false;
      if (std && std !== "*" && v.standard.indexOf(std) < 0) return false;
      return true;
    }

    function applica() {
      var lingua = scelte("lingua")[0], altra = lingua === "en" ? "it" : "en", visibili = 0;
      var righe = Array.prototype.slice.call(tabella.tBodies[0].rows);
      righe.forEach(function (r) {
        var v = perId[r.dataset.id];
        r.style.display = passa(v) ? "" : "none"; if (passa(v)) visibili++;
        r.cells[0].firstChild.textContent = v[lingua] || v.en;   // il termine nella lingua scelta
        r.cells[1].textContent = v[altra] || "";
      });
      righe.sort(function (a, b) { return (perId[a.dataset.id][lingua] || perId[a.dataset.id].en).localeCompare(perId[b.dataset.id][lingua] || perId[b.dataset.id].en, lingua); })
           .forEach(function (r) { tabella.tBodies[0].appendChild(r); });
      conta.textContent = visibili + " voci su " + dati.length;
    }

    gruppi.forEach(function (g) {                   // un clic su una chip
      g.addEventListener("click", function (e) {
        var chip = e.target.closest(".chip"); if (!chip) return;
        var chips = g.querySelectorAll(".chip"), eraAccesa = chip.getAttribute("aria-pressed") === "true";
        chips.forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
        // un secondo clic sulla chip accesa la spegne: si torna alla prima, "nessun filtro"
        (eraAccesa && chip !== chips[0] ? chips[0] : chip).setAttribute("aria-pressed", "true");
        applica();
      });
    });
    testo.addEventListener("input", applica);
    document.getElementById("f-azzera").addEventListener("click", function () {
      testo.value = "";
      gruppi.forEach(function (g) {
        g.querySelectorAll(".chip").forEach(function (b, i) { b.setAttribute("aria-pressed", i === 0 ? "true" : "false"); });
      });
      applica();
    });
    applica();
  }
  if (document.readyState !== "loading") avvia(); else document.addEventListener("DOMContentLoaded", avvia);
  if (window.document$) window.document$.subscribe(avvia);   // navigazione istantanea di Material
})();
