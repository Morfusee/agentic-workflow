(function () {
  const deck = window.SLIDE_DATA || { slides: [] };
  const slides = Array.isArray(deck.slides) ? deck.slides : [];
  const root = document.getElementById("presenter-app");
  const channelName = "generic-slideshow-sync";
  const channel = typeof BroadcastChannel !== "undefined" ? new BroadcastChannel(channelName) : null;
  let index = 0;

  function esc(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function render() {
    const current = slides[index] || {};
    const next = slides[index + 1] || {};
    const layout = current.renderPlan?.layout || deck.renderDefaults?.defaultLayout || "two-column";
    const visuals = Array.isArray(current.renderPlan?.visuals) ? current.renderPlan.visuals.map((v) => v.type).join(", ") : "legacy";
    const emphasis = Array.isArray(current.renderPlan?.emphasis) ? current.renderPlan.emphasis.join(", ") : "none";

    root.innerHTML = `
      <section class="presenter-grid">
        <div class="card">
          <h1>Presenter View</h1>
          <p class="meta">Slide ${Math.min(index + 1, Math.max(slides.length, 1))} / ${slides.length}</p>
          <h2>Script</h2>
          <p class="presenter-script">${esc(current.presenterNotes || "No presenter notes for this slide.")}</p>
        </div>
        <div>
          <div class="card"><h2>Current</h2><p>${esc(current.title || "None")}</p></div>
          <div class="card"><h2>Next</h2><p>${esc(next.title || "None")}</p></div>
          <div class="card"><h2>Render Plan</h2><p class="meta">Layout: ${esc(layout)}</p><p class="meta">Visuals: ${esc(visuals)}</p><p class="meta">Emphasis: ${esc(emphasis)}</p></div>
          <div class="card"><p class="meta">Navigate from audience window with keyboard.</p></div>
        </div>
      </section>`;
  }

  function setIndex(i) {
    if (!slides.length) {
      index = 0;
      render();
      return;
    }
    index = Math.max(0, Math.min(slides.length - 1, i));
    render();
  }

  if (channel) {
    channel.onmessage = (event) => {
      const payload = event.data || {};
      if (payload.type === "slide-change") setIndex(payload.index);
    };
  }

  window.addEventListener("storage", (event) => {
    if (event.key !== channelName || !event.newValue) return;
    try {
      const payload = JSON.parse(event.newValue);
      if (payload.type === "slide-change") setIndex(payload.index);
    } catch (_) {}
  });

  render();
})();
