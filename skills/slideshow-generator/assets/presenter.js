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

  function scriptMarkup(script) {
    const lines = String(script || "")
      .split(/\n+/)
      .map((line) => line.trim())
      .filter(Boolean);
    if (!lines.length) return "<p class='presenter-script'>No script provided.</p>";
    return `<div class="presenter-script">${lines.map((line) => `<p>${esc(line)}</p>`).join("")}</div>`;
  }

  function render() {
    const current = slides[index] || {};
    const next = slides[index + 1] || {};
    const signals = current.signals || {};
    const visualSpec = current.visualSpec || {};

    root.innerHTML = `
      <section class="presenter-grid">
        <div class="card">
          <h1>Presenter View</h1>
          <p class="meta">Slide ${Math.min(index + 1, Math.max(slides.length, 1))} / ${slides.length}</p>
          <h2>Script</h2>
          ${scriptMarkup(current.speakerScript || current.presenterNotes)}
        </div>
        <div>
          <div class="card"><h2>Current</h2><p>${esc(current.title || "None")}</p></div>
          <div class="card"><h2>Next</h2><p>${esc(next.title || "None")}</p></div>
          <div class="card">
            <h2>Slide Signals</h2>
            <p class="meta">Risk: ${esc(signals.riskLevel || "unknown")}</p>
            <p class="meta">Transitions: ${esc(signals.statusTransitions ?? 0)}</p>
            <p class="meta">Depth: ${esc(signals.eventDepth ?? 0)}</p>
            <p class="meta">Blocker: ${esc(Boolean(signals.hasBlocker))}</p>
            <p class="meta">Dependency: ${esc(Boolean(signals.hasDependency))}</p>
          </div>
          <div class="card">
            <h2>Visual Plan</h2>
            <p class="meta">Primary: ${esc(visualSpec.primaryVisual || "none")}</p>
            <p class="meta">Secondary: ${esc(visualSpec.secondaryVisual || "none")}</p>
          </div>
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
