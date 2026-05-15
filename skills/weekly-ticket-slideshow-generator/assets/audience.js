(function () {
  const data = window.SLIDE_DATA || { slides: [] };
  const slides = data.slides || [];
  const app = document.getElementById("app");
  const channelName = "weekly-ticket-flow-sync";
  const channel = typeof BroadcastChannel !== "undefined" ? new BroadcastChannel(channelName) : null;
  let index = 0;
  let presenterWindow = null;

  function emitState() {
    const payload = { type: "slide-change", index };
    if (channel) {
      channel.postMessage(payload);
    }
    localStorage.setItem(channelName, JSON.stringify(payload));
  }

  function fmtSlideCounter() {
    return `Slide ${index + 1} / ${slides.length}`;
  }

  function timelineMarkup(timeline) {
    if (!timeline || !timeline.length) {
      return "<div class=\"timeline-item\">No timeline events available.</div>";
    }
    return timeline
      .slice(0, 8)
      .map((ev) => `<div class=\"timeline-item\">${ev.timestamp} - ${ev.event}</div>`)
      .join("");
  }

  function render() {
    if (!slides.length) {
      app.innerHTML = `<section class="slide"><h1 class="title">No slides available</h1></section>`;
      return;
    }
    const slide = slides[index];

    if (slide.type === "title") {
      app.innerHTML = `
        <section class="slide">
          <header>
            <h1 class="title">${slide.title}</h1>
            <p class="meta">Generated: ${data.generatedAt}</p>
          </header>
          <section class="card kpis">
            <div class="kpi"><div class="label">Tickets</div><div class="value">${slide.summary.tickets}</div></div>
            <div class="kpi"><div class="label">Resolved</div><div class="value badge-ok">${slide.summary.resolved}</div></div>
            <div class="kpi"><div class="label">Unresolved</div><div class="value badge-warn">${slide.summary.unresolved}</div></div>
          </section>
          <footer class="footer">${fmtSlideCounter()} | Keys: Left/Right, Home/End, F fullscreen, P presenter</footer>
        </section>`;
      return;
    }

    if (slide.type === "closing") {
      const unresolved = (slide.unresolved || [])
        .map((x) => `<li>${x.ticketId}: ${x.title} (${x.status})</li>`)
        .join("");
      app.innerHTML = `
        <section class="slide">
          <header><h1 class="title">${slide.title}</h1></header>
          <section class="card">
            ${unresolved ? `<ul>${unresolved}</ul>` : "<p>All tracked tickets are resolved.</p>"}
          </section>
          <footer class="footer">${fmtSlideCounter()}</footer>
        </section>`;
      return;
    }

    if (slide.type === "empty") {
      app.innerHTML = `
        <section class="slide">
          <header><h1 class="title">${slide.title}</h1></header>
          <section class="card"><p>${slide.message}</p></section>
          <footer class="footer">${fmtSlideCounter()}</footer>
        </section>`;
      return;
    }

    app.innerHTML = `
      <section class="slide">
        <header>
          <h1 class="title">${slide.ticketId}: ${slide.title}</h1>
          <p class="meta"><span class="status">Status: ${slide.status}</span> | Role: ${slide.role}</p>
        </header>
        <section class="card">
          <p>${slide.flowSummary}</p>
          <div class="timeline">${timelineMarkup(slide.timeline)}</div>
        </section>
        <footer class="footer">${fmtSlideCounter()}</footer>
      </section>`;
  }

  function moveTo(nextIndex) {
    if (!slides.length) return;
    index = Math.max(0, Math.min(slides.length - 1, nextIndex));
    render();
    emitState();
  }

  function openPresenter() {
    if (presenterWindow && !presenterWindow.closed) {
      presenterWindow.focus();
      return;
    }
    presenterWindow = window.open("presenter.html", "weekly-ticket-presenter", "width=1280,height=800");
  }

  function requestFullscreen() {
    const el = document.documentElement;
    if (!document.fullscreenElement) {
      el.requestFullscreen?.();
      return;
    }
    document.exitFullscreen?.();
  }

  window.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") moveTo(index + 1);
    if (e.key === "ArrowLeft") moveTo(index - 1);
    if (e.key === "Home") moveTo(0);
    if (e.key === "End") moveTo(slides.length - 1);
    if (e.key.toLowerCase() === "f") requestFullscreen();
    if (e.key.toLowerCase() === "p") openPresenter();
  });

  window.addEventListener("storage", (event) => {
    if (event.key !== channelName || !event.newValue) return;
    try {
      const payload = JSON.parse(event.newValue);
      if (payload.type === "slide-change" && typeof payload.index === "number") {
        moveTo(payload.index);
      }
    } catch (err) {
      void err;
    }
  });

  render();
  emitState();
})();
