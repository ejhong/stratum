// Stratum — chart tooltips, table sorting, fate filters and the table/cards toggle.
// Pages work without JavaScript; this only adds convenience.
(function () {
  var tip = document.createElement("div");
  tip.className = "tip";
  tip.setAttribute("role", "tooltip");
  document.body.appendChild(tip);

  function show(el, x, y) {
    tip.innerHTML = "<b></b><span></span>";
    tip.firstChild.textContent = el.dataset.name || "";
    tip.lastChild.textContent = el.dataset.info || "";
    var w = tip.offsetWidth, h = tip.offsetHeight;
    tip.style.left = Math.min(window.innerWidth - w - 10, Math.max(10, x + 12)) + "px";
    tip.style.top = (y - h - 12 < 6 ? y + 16 : y - h - 12) + "px";
    tip.classList.add("on");
  }
  function hide() { tip.classList.remove("on"); }
  document.querySelectorAll(".case-mark").forEach(function (el) {
    el.addEventListener("mousemove", function (e) { show(el, e.clientX, e.clientY); });
    el.addEventListener("mouseleave", hide);
    el.addEventListener("focus", function () { var r = el.getBoundingClientRect(); show(el, r.left + r.width / 2, r.top); });
    el.addEventListener("blur", hide);
  });
  window.addEventListener("scroll", hide, { passive: true });

  // Sortable tables: click a header; numbers sort numerically.
  document.querySelectorAll("table[data-table]").forEach(function (table) {
    var heads = table.querySelectorAll("th[data-sort]");
    heads.forEach(function (th, i) {
      th.addEventListener("click", function () {
        var asc = th.getAttribute("aria-sort") !== "ascending";
        heads.forEach(function (h) { h.removeAttribute("aria-sort"); });
        th.setAttribute("aria-sort", asc ? "ascending" : "descending");
        var body = table.tBodies[0];
        var rows = Array.prototype.slice.call(body.rows);
        rows.sort(function (a, b) {
          var x = a.cells[i].dataset.v || a.cells[i].textContent, y = b.cells[i].dataset.v || b.cells[i].textContent;
          var nx = parseFloat(x), ny = parseFloat(y);
          var c = (!isNaN(nx) && !isNaN(ny)) ? nx - ny : String(x).localeCompare(String(y));
          return asc ? c : -c;
        });
        rows.forEach(function (r) { body.appendChild(r); });
      });
    });
  });

  // Fate filters apply to table rows and cards alike.
  var chips = document.querySelectorAll("[data-filter]");
  function filter(val) {
    document.querySelectorAll("tr[data-status], .card[data-status]").forEach(function (el) {
      el.hidden = !(val === "all" || el.dataset.status === val || el.dataset.type === val);
    });
    chips.forEach(function (c) { c.setAttribute("aria-pressed", String(c.dataset.filter === val)); });
  }
  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      filter(chip.dataset.filter);
      try { history.replaceState(null, "", chip.dataset.filter === "all" ? location.pathname : "#" + chip.dataset.filter); } catch (e) {}
    });
  });
  var hash = location.hash.slice(1);
  if (hash && document.querySelector('[data-filter="' + hash + '"]')) filter(hash);

  // Table / cards toggle, remembered per viewer.
  var holder = document.querySelector("[data-view]");
  var views = document.querySelectorAll("[data-view-btn]");
  function setView(v) {
    if (!holder) return;
    holder.setAttribute("data-view", v);
    views.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.viewBtn === v)); });
    try { localStorage.setItem("stratum-view", v); } catch (e) {}
  }
  views.forEach(function (b) { b.addEventListener("click", function () { setView(b.dataset.viewBtn); }); });
  try { var saved = localStorage.getItem("stratum-view"); if (saved) setView(saved); } catch (e) {}
})();
