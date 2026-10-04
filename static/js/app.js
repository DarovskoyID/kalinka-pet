/* Планировщик: модалки, сайдбар, фильтры, drag&drop доски, календарь */
(function () {
  /* ---------- модалки ---------- */
  const openModal = (id) => {
    const m = document.getElementById(id);
    if (!m) return;
    m.hidden = false;
    const first = m.querySelector("input:not([type=hidden]), textarea");
    first && setTimeout(() => first.focus(), 50);
  };
  document.addEventListener("click", (e) => {
    const opener = e.target.closest("[data-open]");
    if (opener) { openModal(opener.dataset.open); return; }
    if (e.target.closest("[data-close]")) e.target.closest(".modal").hidden = true;
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") document.querySelectorAll(".modal").forEach((m) => (m.hidden = true));
    const typing = /INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName);
    if (e.key === "/" && !typing) { e.preventDefault(); document.querySelector("[data-filter-search], .side-search input")?.focus(); }
  });

  /* ---------- мобильный сайдбар ---------- */
  const shell = document.querySelector(".shell");
  document.querySelectorAll("[data-toggle-side]").forEach((b) =>
    b.addEventListener("click", () => shell.classList.toggle("side-is-open")));

  /* ---------- сегментированные фильтры (визуально) ---------- */
  document.querySelectorAll(".segmented[role=tablist]").forEach((seg) =>
    seg.addEventListener("click", (e) => {
      const b = e.target.closest("button"); if (!b) return;
      seg.querySelectorAll("button").forEach((x) => x.classList.toggle("is-active", x === b));
    }));

  /* ---------- чекбоксы задач ---------- */
  document.addEventListener("change", (e) => {
    const cb = e.target.closest(".check-round input"); if (!cb) return;
    cb.closest(".row, tr")?.classList.toggle("is-done", cb.checked);
  });

  /* ---------- фильтры проекта: поиск и приоритет ---------- */
  const search = document.querySelector("[data-filter-search]");
  const prio = document.querySelector("[data-filter-priority]");
  function applyFilters() {
    const q = (search?.value || "").trim().toLowerCase(), p = prio?.value || "";
    document.querySelectorAll(".card, .table tbody tr").forEach((el) => {
      const okText = !q || el.textContent.toLowerCase().includes(q);
      const okPrio = !p || el.dataset.priority === p;
      el.classList.toggle("is-hidden", !(okText && okPrio));
    });
  }
  search?.addEventListener("input", applyFilters);
  prio?.addEventListener("change", applyFilters);

  /* ---------- drag & drop доски ---------- */
  const board = document.getElementById("board");
  if (board) {
    let dragged = null, fromZone = null, fromNext = null;
    const csrf = board.querySelector("[name=csrfmiddlewaretoken]")?.value;
    const recount = () => board.querySelectorAll("[data-col]").forEach((col) => {
      col.querySelector(".col-count").textContent = col.querySelectorAll(".card").length;
    });

    // сохраняем новый статус; при ошибке возвращаем карточку на место
    async function saveStatus(card, zone, backZone, backNext) {
      const status = zone.dataset.status;
      card.classList.add("is-saving");
      try {
        const resp = await fetch(board.dataset.statusUrl.replace("/0/", `/${card.dataset.taskId}/`), {
          method: "POST",
          headers: { "X-CSRFToken": csrf, "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({ status }),
        });
        if (!resp.ok) throw new Error(resp.status);
        card.dataset.status = status;
        card.classList.toggle("is-done", status === "complete");
      } catch (err) {
        backZone.insertBefore(card, backNext);
        recount();
        alert("Не удалось сменить статус задачи. Попробуйте ещё раз.");
      } finally {
        card.classList.remove("is-saving");
      }
    }

    board.addEventListener("dragstart", (e) => {
      dragged = e.target.closest(".card"); if (!dragged) return;
      fromZone = dragged.parentElement;
      fromNext = dragged.nextElementSibling;
      dragged.classList.add("is-dragging");
      e.dataTransfer.effectAllowed = "move";
    });
    board.addEventListener("dragend", () => {
      if (!dragged) return;
      const card = dragged, zone = card.parentElement;
      card.classList.remove("is-dragging");
      board.querySelectorAll(".is-over").forEach((z) => z.classList.remove("is-over"));
      recount();
      if (zone !== fromZone && zone.dataset.status) saveStatus(card, zone, fromZone, fromNext);
      dragged = fromZone = fromNext = null;
    });
    board.addEventListener("dragover", (e) => {
      const zone = e.target.closest("[data-dropzone]"); if (!zone || !dragged) return;
      e.preventDefault();
      board.querySelectorAll(".is-over").forEach((z) => z !== zone && z.classList.remove("is-over"));
      zone.classList.add("is-over");
      const after = [...zone.querySelectorAll(".card:not(.is-dragging)")]
        .find((c) => e.clientY < c.getBoundingClientRect().top + c.offsetHeight / 2);
      after ? zone.insertBefore(dragged, after) : zone.appendChild(dragged);
    });
    board.addEventListener("drop", (e) => e.preventDefault());
  }

  /* ---------- календарь ---------- */
  const cal = document.getElementById("calendar");
  if (cal) {
    const MONTHS = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"];
    const events = JSON.parse(cal.dataset.events || "[]");
    const grid = document.getElementById("calGrid"), title = document.getElementById("calTitle");
    const today = new Date();
    let view = new Date(today.getFullYear(), today.getMonth(), 1);
    const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

    function render() {
      title.textContent = `${MONTHS[view.getMonth()]} ${view.getFullYear()}`;
      const shift = (view.getDay() + 6) % 7; // понедельник — первый день
      const start = new Date(view); start.setDate(1 - shift);
      grid.innerHTML = "";
      for (let i = 0; i < 42; i++) {
        const d = new Date(start); d.setDate(start.getDate() + i);
        const cell = document.createElement("div");
        cell.className = "day";
        if (d.getMonth() !== view.getMonth()) cell.classList.add("is-other");
        if (iso(d) === iso(today)) cell.classList.add("is-today");
        cell.innerHTML = `<span class="day-num">${d.getDate()}</span>
          <button class="icon-btn day-add" data-open="taskModal" data-date="${iso(d)}" aria-label="Добавить задачу">
            <svg class="icon" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg></button>`;
        events.filter((ev) => ev.d === iso(d)).forEach((ev) => {
          const el = document.createElement("div");
          el.className = "ev"; el.style.setProperty("--c", `var(--${ev.c})`); el.textContent = el.title = ev.t;
          cell.appendChild(el);
        });
        grid.appendChild(cell);
      }
    }
    cal.addEventListener("click", (e) => {
      const b = e.target.closest("[data-cal]");
      if (b) {
        const a = b.dataset.cal;
        view = a === "today" ? new Date(today.getFullYear(), today.getMonth(), 1)
          : new Date(view.getFullYear(), view.getMonth() + (a === "next" ? 1 : -1), 1);
        render();
      }
      // клик по «+» в дне подставляет дату в форму
      const add = e.target.closest(".day-add");
      if (add) {
        const f = document.querySelector('#taskModal [name="end_date"]');
        if (f) f.value = add.dataset.date;
      }
    });
    render();
  }

  /* ---------- форма проекта: свой цвет и живое превью ---------- */
  document.querySelectorAll("[data-project-form]").forEach((form) => {
    const preview = form.querySelector("[data-color-preview]");
    const titlePreview = form.querySelector("[data-title-preview]");
    const custom = form.querySelector("[data-color-custom]");
    const picker = form.querySelector("[data-color-picker]");
    const paint = (c) => preview?.style.setProperty("--c", c);

    form.addEventListener("change", (e) => {
      if (e.target.name === "color") paint(e.target.value);
    });
    picker?.addEventListener("input", () => {
      custom.value = picker.value;
      custom.checked = true;
      custom.nextElementSibling.style.setProperty("--c", picker.value);
      paint(picker.value);
    });
    form.querySelector('[name="title"]')?.addEventListener("input", (e) => {
      titlePreview.textContent = e.target.value.trim() || "Новый проект";
    });
  });

  /* ---------- подтверждение опасных действий ---------- */
  document.addEventListener("submit", (e) => {
    const msg = e.target.dataset.confirm;
    if (msg && !confirm(msg)) e.preventDefault();
  });
})();
