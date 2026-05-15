(function () {
  const deck = window.SLIDE_DATA || { slides: [] };
  const slides = Array.isArray(deck.slides) ? deck.slides : [];
  const app = document.getElementById("app");
  const channelName = "generic-slideshow-sync";
  const channel = typeof BroadcastChannel !== "undefined" ? new BroadcastChannel(channelName) : null;
  const allowedLayouts = ["hero", "two-column", "timeline-focus", "chart-focus", "comparison", "dense-notes"];
  const allowedVisuals = ["kpi-strip", "status-bars", "trend-line", "flow-nodes", "relationship-map", "risk-matrix"];
  let index = 0;
  let presenterWindow = null;

  function esc(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function emitState() {
    const payload = { type: "slide-change", index };
    if (channel) channel.postMessage(payload);
    localStorage.setItem(channelName, JSON.stringify(payload));
  }

  function timelineMarkup(timeline, maxItems) {
    const events = Array.isArray(timeline) ? timeline.slice(0, maxItems) : [];
    if (!events.length) return '<div class="timeline-item">No timeline events.</div>';
    return events.map((ev) => `<div class="timeline-item">${esc(ev.timestamp)} - ${esc(ev.event)}</div>`).join("");
  }

  function listMarkup(items, className, maxItems) {
    if (!Array.isArray(items) || !items.length) return "";
    return `<ul class="${className}">${items.slice(0, maxItems).map((i) => `<li>${esc(i)}</li>`).join("")}</ul>`;
  }

  function normalizedPlan(slide) {
    const defaults = deck.renderDefaults || {};
    const plan = slide.renderPlan || {};
    const layout = allowedLayouts.includes(plan.layout) ? plan.layout : (allowedLayouts.includes(defaults.defaultLayout) ? defaults.defaultLayout : "two-column");
    const visuals = Array.isArray(plan.visuals)
      ? plan.visuals.filter((v) => v && allowedVisuals.includes(v.type)).slice(0, 3)
      : [];
    const constraints = {
      maxMetaItems: Number(plan.constraints?.maxMetaItems ?? defaults.constraints?.maxMetaItems ?? 4),
      maxTimelineItems: Number(plan.constraints?.maxTimelineItems ?? defaults.constraints?.maxTimelineItems ?? 5),
      maxBulletItems: Number(plan.constraints?.maxBulletItems ?? defaults.constraints?.maxBulletItems ?? 6),
    };
    return {
      layout,
      regions: plan.regions && typeof plan.regions === "object" ? plan.regions : {},
      visuals,
      emphasis: Array.isArray(plan.emphasis) ? plan.emphasis : [],
      constraints,
    };
  }

  function statusCounts() {
    return deck.context?.statusCounts && typeof deck.context.statusCounts === "object" ? deck.context.statusCounts : {};
  }

  function dayCounts() {
    return deck.context?.dayCounts && typeof deck.context.dayCounts === "object" ? deck.context.dayCounts : {};
  }

  function renderBars(data) {
    const entries = Object.entries(data);
    if (!entries.length) return "";
    const maxValue = Math.max(...entries.map(([, v]) => Number(v) || 0), 1);
    return `<div class="viz-bars">${entries
      .map(([name, value]) => {
        const safeValue = Number(value) || 0;
        const h = Math.max(10, Math.round((safeValue / maxValue) * 100));
        return `<div class="bar-wrap"><div class="bar" style="height:${h}%"></div><span class="bar-label">${esc(name)}</span><span class="bar-value">${safeValue}</span></div>`;
      })
      .join("")}</div>`;
  }

  function renderTrend(data) {
    const entries = Object.entries(data);
    if (!entries.length) return "";
    const maxValue = Math.max(...entries.map(([, v]) => Number(v) || 0), 1);
    const width = 600;
    const height = 180;
    const step = entries.length === 1 ? 0 : (width - 40) / (entries.length - 1);
    const points = entries
      .map(([, v], i) => {
        const x = 20 + i * step;
        const y = height - 20 - ((Number(v) || 0) / maxValue) * (height - 40);
        return `${x},${y}`;
      })
      .join(" ");
    return `<svg class="viz-trend" viewBox="0 0 ${width} ${height}" role="img" aria-label="Activity trend">
      <polyline points="${points}" />
    </svg>`;
  }

  function renderFlowNodes(timeline) {
    const total = Math.max(1, (Array.isArray(timeline) ? timeline.length : 0));
    return `<div class="viz-flow">${Array.from({ length: total })
      .map((_, i) => `<span class="flow-node ${i === total - 1 ? "flow-node-last" : ""}"></span>${i < total - 1 ? '<span class="flow-link"></span>' : ""}`)
      .join("")}</div>`;
  }

  function renderRelationshipMap(meta, items) {
    const nodes = [...(meta || []), ...(items || [])].slice(0, 5);
    if (!nodes.length) return "";
    return `<div class="viz-map">${nodes.map((n) => `<span class="map-node">${esc(n)}</span>`).join("")}</div>`;
  }

  function renderRiskMatrix(items, unresolvedCount) {
    const risks = Array.isArray(items) ? items.slice(0, 4) : [];
    const riskLevel = unresolvedCount > 0 ? "High" : "Low";
    return `<div class="viz-risk"><div class="risk-header">Risk posture: ${riskLevel}</div>${risks.length ? `<ul>${risks.map((r) => `<li>${esc(r)}</li>`).join("")}</ul>` : "<p>No active risks listed.</p>"}</div>`;
  }

  function visualMarkup(slide, plan) {
    if (!plan.visuals.length && slide.visual === "ticket-flow") {
      return renderFlowNodes(slide.timeline);
    }
    const unresolvedCount = Number(deck.context?.unresolvedCount || 0);
    return plan.visuals
      .map((visual) => {
        if (visual.type === "kpi-strip") {
          const total = Number(deck.context?.ticketCount || 0);
          const unresolved = unresolvedCount;
          const resolved = Math.max(0, total - unresolved);
          return `<div class="kpi-strip"><div class="kpi"><span>Total</span><strong>${total}</strong></div><div class="kpi"><span>Resolved</span><strong>${resolved}</strong></div><div class="kpi"><span>Unresolved</span><strong>${unresolved}</strong></div></div>`;
        }
        if (visual.type === "status-bars") return renderBars(statusCounts());
        if (visual.type === "trend-line") return renderTrend(dayCounts());
        if (visual.type === "flow-nodes") return renderFlowNodes(slide.timeline);
        if (visual.type === "relationship-map") return renderRelationshipMap(slide.meta, slide.items);
        if (visual.type === "risk-matrix") return renderRiskMatrix(slide.items, unresolvedCount);
        return "";
      })
      .join("");
  }

  function render() {
    if (!slides.length) {
      app.innerHTML = '<section class="slide"><h1 class="title">No slides available</h1></section>';
      return;
    }

    const s = slides[index];
    const plan = normalizedPlan(s);
    const metaItems = Array.isArray(s.meta) ? s.meta : [];
    const status = s.status ? `<span class="status">Status: ${esc(s.status)}</span>` : "";
    const emphasis = plan.emphasis.length ? `<div class="emphasis">${plan.emphasis.map((e) => `<span>${esc(e)}</span>`).join("")}</div>` : "";

    app.innerHTML = `
      <section class="slide layout-${plan.layout}">
        <header>
          <h1 class="title">${esc(s.title || "Untitled Slide")}</h1>
          ${status}
          ${emphasis}
        </header>
        <section class="card slide-main">
          <div class="main-text"><p>${esc(s.body || "")}</p></div>
          <div class="main-visuals">${visualMarkup(s, plan)}</div>
          <div class="main-meta">${listMarkup(metaItems, "meta-list", plan.constraints.maxMetaItems)}</div>
          <div class="main-timeline"><div class="timeline">${timelineMarkup(s.timeline, plan.constraints.maxTimelineItems)}</div></div>
          <div class="main-items">${listMarkup(s.items, "item-list", plan.constraints.maxBulletItems)}</div>
        </section>
        <footer class="footer">Slide ${index + 1} / ${slides.length} | Keys: Left/Right, Home/End, F fullscreen, P presenter</footer>
      </section>`;
  }

  function moveTo(nextIndex) {
    if (!slides.length) return;
    index = Math.max(0, Math.min(slides.length - 1, nextIndex));
    render();
    emitState();
  }

  function openPresenter() {
    if (presenterWindow && !presenterWindow.closed) return presenterWindow.focus();
    presenterWindow = window.open("presenter.html", "generic-slideshow-presenter", "width=1280,height=800");
  }

  function toggleFullscreen() {
    if (!document.fullscreenElement) return document.documentElement.requestFullscreen?.();
    document.exitFullscreen?.();
  }

  window.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") moveTo(index + 1);
    if (e.key === "ArrowLeft") moveTo(index - 1);
    if (e.key === "Home") moveTo(0);
    if (e.key === "End") moveTo(slides.length - 1);
    if (e.key.toLowerCase() === "f") toggleFullscreen();
    if (e.key.toLowerCase() === "p") openPresenter();
  });

  window.addEventListener("storage", (event) => {
    if (event.key !== channelName || !event.newValue) return;
    try {
      const payload = JSON.parse(event.newValue);
      if (payload.type === "slide-change") moveTo(payload.index);
    } catch (_) {}
  });

  render();
  emitState();
})();
