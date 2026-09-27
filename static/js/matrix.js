/* Матрица: падающие 0 и 1 на фоне hero */
(function () {
  const canvas = document.getElementById("matrix");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const FONT = 16;
  let cols, drops, speeds, w, h, dpr;

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    w = canvas.clientWidth; h = canvas.clientHeight;
    canvas.width = w * dpr; canvas.height = h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    cols = Math.ceil(w / FONT);
    drops = Array.from({ length: cols }, () => Math.random() * -h / FONT);
    speeds = Array.from({ length: cols }, () => 0.35 + Math.random() * 0.75);
    ctx.fillStyle = "#03110a"; ctx.fillRect(0, 0, w, h);
  }

  function frame() {
    ctx.fillStyle = "rgba(3, 17, 10, 0.09)";
    ctx.fillRect(0, 0, w, h);
    ctx.font = `700 ${FONT}px "JetBrains Mono", monospace`;

    for (let i = 0; i < cols; i++) {
      const y = drops[i] * FONT;
      const ch = Math.random() > 0.5 ? "1" : "0";
      // голова струи — светлая, хвост остаётся за счёт полупрозрачной заливки
      ctx.fillStyle = Math.random() > 0.94 ? "#eafff4" : (i % 3 ? "#2bb673" : "#3ecf8e");
      ctx.fillText(ch, i * FONT, y);

      drops[i] += speeds[i];
      if (y > h && Math.random() > 0.975) drops[i] = Math.random() * -20;
    }
  }

  let last = 0, running = true;
  function loop(t) {
    if (running && t - last > 45) { frame(); last = t; }
    requestAnimationFrame(loop);
  }

  // не рисуем, когда hero вне экрана
  new IntersectionObserver(([e]) => { running = e.isIntersecting; }).observe(canvas);

  window.addEventListener("resize", resize);
  resize();
  if (reduce) { for (let i = 0; i < 60; i++) frame(); }
  else requestAnimationFrame(loop);
})();
