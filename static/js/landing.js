/* Лендинг: кольцо продуктивности, шапка, параллакс-колода секций */
(function () {
  /* ---------- кольцо ---------- */
  const ring = document.getElementById("ring");
  if (ring) {
    const MIN = +ring.dataset.min || 60;
    const MAX = +ring.dataset.max || 87;
    const INTERVAL = (+ring.dataset.intervalMin || 3) * 60 * 1000; // раз в N минут
    const R = 84, C = 2 * Math.PI * R, COMET = 22;

    const valueEl = document.getElementById("ringValue");
    const cometEl = document.getElementById("ringComet");
    const numEl = document.getElementById("ringNum");
    const textEl = document.getElementById("ringText");
    const timerEl = document.getElementById("ringTimer");

    valueEl.style.strokeDasharray = C;
    valueEl.style.strokeDashoffset = C;
    cometEl.style.strokeDasharray = `${COMET} ${C}`;

    const phrases = [
      [60, 66, ["Хороший старт — ещё пара задач, и неделя закрыта.", "Темп набран. Выберите одну главную задачу на сегодня."]],
      [67, 73, ["Уверенно! Большая часть плана уже позади.", "Команда держит ритм — дедлайны под контролем."]],
      [74, 80, ["Отличный темп: вы опережаете средний план на 12%.", "Почти все задачи закрыты — самое время для сложной."]],
      [81, 87, ["Вы в потоке! Осталось совсем чуть-чуть.", "Рекордная неделя — не забудьте отдохнуть."]],
    ];
    const pick = (v) => {
      const list = phrases.find(([a, b]) => v >= a && v <= b)[2];
      return list[Math.floor(Math.random() * list.length)];
    };

    let current = 0, target = 0, nextAt = 0;

    function countTo(to) {
      const from = current, start = performance.now(), dur = 1600;
      (function step(now) {
        const k = Math.min((now - start) / dur, 1);
        const e = k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
        numEl.textContent = Math.round(from + (to - from) * e);
        if (k < 1) requestAnimationFrame(step); else current = to;
      })(start);
    }

    function update() {
      target = MIN + Math.floor(Math.random() * (MAX - MIN + 1));
      valueEl.style.strokeDashoffset = C * (1 - target / 100);
      countTo(target);
      textEl.classList.add("is-fading");
      setTimeout(() => { textEl.textContent = pick(target); textEl.classList.remove("is-fading"); }, 400);
      nextAt = Date.now() + INTERVAL;
    }

    // «бегающая» комета по заполненной части кольца
    (function comet(t) {
      const arc = C * (target / 100);
      if (arc > COMET) {
        const pos = (t / 12) % (arc - COMET);
        cometEl.style.strokeDashoffset = -pos;
        cometEl.style.opacity = Math.sin((pos / (arc - COMET)) * Math.PI) * .9;
      }
      requestAnimationFrame(comet);
    })(0);

    setInterval(() => {
      const left = Math.max(0, nextAt - Date.now());
      const m = Math.floor(left / 60000), s = Math.floor(left / 1000) % 60;
      timerEl.textContent = `${m}:${String(s).padStart(2, "0")}`;
      if (left === 0) update();
    }, 1000);

    setTimeout(update, 400);
  }

  /* ---------- шапка ---------- */
  const topbar = document.getElementById("topbar");
  const rail = document.getElementById("rail");
  const panels = [...document.querySelectorAll(".panel")];
  const navLinks = [...document.querySelectorAll(".topbar-nav a, .rail a")];

  /* ---------- параллакс: секции наезжают друг на друга ---------- */
  const desktop = window.matchMedia("(min-width: 1001px)");
  let ticking = false;

  function onScroll() {
    const vh = window.innerHeight;
    topbar.classList.toggle("is-solid", window.scrollY > 40);
    rail && rail.classList.toggle("is-visible", window.scrollY > vh * .6);

    let activeId = null;
    panels.forEach((panel, i) => {
      // секция выше экрана не может «залипать» — иначе низ обрежется
      panel.classList.toggle("is-tall", panel.querySelector(".panel-inner").offsetHeight > vh);
      const rect = panel.getBoundingClientRect();
      const next = panels[i + 1];
      // p — насколько секция «въехала» (0 → 1)
      const p = Math.min(Math.max(1 - rect.top / vh, 0), 1);
      // q — насколько её уже накрыла следующая
      const q = next ? Math.min(Math.max(1 - next.getBoundingClientRect().top / vh, 0), 1) : 0;

      if (desktop.matches) {
        panel.style.transform = `scale(${1 - q * .08})`;
        panel.style.setProperty("--dim", (q * .65).toFixed(3));
        panel.style.setProperty("--lift", `${(1 - p) * 120 - q * 60}px`);
      } else {
        panel.style.transform = "";
        panel.style.setProperty("--dim", 0);
        panel.style.setProperty("--lift", "0px");
      }
      const word = panel.querySelector(".panel-bgword");
      if (word) word.style.setProperty("--shift", `${(p + q - 1) * 400 * (+word.dataset.speed || 1)}px`);

      if (p > .5 && q < .5) activeId = panel.id;
    });

    navLinks.forEach((a) => a.classList.toggle("is-active", a.getAttribute("href") === `#${activeId}`));
    ticking = false;
  }

  window.addEventListener("scroll", () => {
    if (!ticking) { requestAnimationFrame(onScroll); ticking = true; }
  }, { passive: true });
  window.addEventListener("resize", onScroll);
  onScroll();

  /* ---------- появление элементов ---------- */
  // проверяем по координатам: IntersectionObserver не видит элементы, скрытые clip-path
  const pending = new Set(document.querySelectorAll("[data-reveal]"));
  function reveal() {
    const vh = window.innerHeight;
    pending.forEach((el) => {
      if (el.getBoundingClientRect().top < vh * .85) { el.classList.add("is-in"); pending.delete(el); }
    });
  }
  window.addEventListener("scroll", reveal, { passive: true });
  reveal();
})();
