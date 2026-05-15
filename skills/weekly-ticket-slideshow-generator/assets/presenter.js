(function () {
  const data = window.SLIDE_DATA || { slides: [] };
  const slides = data.slides || [];
  const root = document.getElementById("presenter-app");
  const channelName = "weekly-ticket-flow-sync";
  const channel = typeof BroadcastChannel !== "undefined" ? new BroadcastChannel(channelName) : null;
  let index = 0;

  function cardForSlide(slide, label) {
    if (!slide) return `<div class=\"card\"><h2>${label}</h2><p>No slide</p></div>`;
    if (slide.type === "ticket") {
      return `<div class="card"><h2>${label}: ${slide.ticketId}</h2><p>${slide.title}</p><p class="meta">Status: ${slide.status}</p></div>`;
    }
    return `<div class="card"><h2>${label}</h2><p>${slide.title || slide.type}</p></div>`;
  }

  function scriptText(slide) {
    if (!slide) return "No presenter notes available.";
    if (slide.type === "ticket") return slide.presenterScript || "No presenter script generated.";
    if (slide.type === "title") return "Introduce the week, ticket volume, and resolved versus unresolved counts.";
    if (slide.type === "closing") return "Review unresolved items and risks to monitor next week.";
    return "No presenter script for this slide.";
  }

  function render() {
    const current = slides[index];
    const next = slides[index + 1];
    root.innerHTML = `
      <section class="presenter-grid">
        <div class="card">
          <h1>Presenter View</h1>
          <p class="meta">Slide ${index + 1} / ${slides.length}</p>
          <h2>Script</h2>
          <p class="presenter-script">${scriptText(current)}</p>
        </div>
        <div>
          ${cardForSlide(current, "Current")}
          ${cardForSlide(next, "Next")}
          <div class="card"><p class="meta">Navigate from audience window using Left/Right, Home/End.</p></div>
        </div>
      </section>`;
  }

  function apply(payload) {
    if (payload.type !== "slide-change" || typeof payload.index !== "number") return;
    index = Math.max(0, Math.min(slides.length - 1, payload.index));
    render();
  }

  if (channel) {
    channel.onmessage = (event) => apply(event.data || {});
  }

  window.addEventListener("storage", (event) => {
    if (event.key !== channelName || !event.newValue) return;
    try {
      apply(JSON.parse(event.newValue));
    } catch (err) {
      void err;
    }
  });

  render();
})();
