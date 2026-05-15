(function () {
  const deck = window.SLIDE_DATA || { slides: [] };
  const slides = Array.isArray(deck.slides) ? deck.slides : [];
  const policy = deck.presentationPolicy || {};
  const app = document.getElementById("app");
  const channelName = "generic-slideshow-sync";
  const channel = typeof BroadcastChannel !== "undefined" ? new BroadcastChannel(channelName) : null;
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

  function tokenize(value) {
    return String(value || "")
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, " ")
      .split(/\s+/)
      .filter((t) => t.length > 2);
  }

  function overlapRatio(text, source) {
    const textTokens = tokenize(text);
    if (!textTokens.length) return 0;
    const sourceSet = new Set(tokenize(source));
    if (!sourceSet.size) return 0;
    const matches = textTokens.filter((t) => sourceSet.has(t)).length;
    return matches / textTokens.length;
  }

  function hasCausalValue(sentence) {
    const text = String(sentence || "").toLowerCase();
    const cues = [
      "because",
      "therefore",
      "impact",
      "risk",
      "decision",
      "next",
      "block",
      "dependency",
      "if ",
      "unless",
      "due to",
      "so that",
    ];
    return cues.some((cue) => text.includes(cue));
  }

  function antiRestatement(text, slide) {
    if (!text) return "";
    if (policy.textPolicy !== "strict-summary") return text;
    const visible = [slide.title || "", slide.status || "", (slide.meta && JSON.stringify(slide.meta)) || ""].join(" ");
    const sentences = String(text)
      .split(/(?<=[.!?])\s+/)
      .map((s) => s.trim())
      .filter(Boolean);
    const kept = sentences.filter((sentence) => {
      const ratio = overlapRatio(sentence, visible);
      if (ratio < 0.7) return true;
      return hasCausalValue(sentence);
    });
    if (kept.length) return kept.join(" ");
    return hasCausalValue(text) ? text : "";
  }

  function shouldRenderDiagram(slide) {
    const s = slide.signals || {};
    const policyMatch = policy.diagramPolicy === "signal-required";
    if (!policyMatch) return true;
    return Boolean(s.hasBlocker || s.hasDependency || Number(s.statusTransitions || 0) >= 2 || Number(s.eventDepth || 0) >= 3);
  }

  function chipList(values) {
    if (!Array.isArray(values) || !values.length) return "";
    return `<div class="chip-list">${values.map((item) => `<span class="chip">${esc(item)}</span>`).join("")}</div>`;
  }

  function renderStateLaneFlow(slide) {
    const steps = slide.visualSpec?.entities?.flowSteps || [];
    if (!Array.isArray(steps) || !steps.length) return "";
    const nodes = steps.slice(0, 5);
    return `<div class="diagram state-lane">${nodes
      .map((step, idx) => `<div class="lane-step"><span class="lane-index">${idx + 1}</span><p>${esc(step)}</p></div>${idx < nodes.length - 1 ? '<span class="lane-arrow">→</span>' : ""}`)
      .join("")}</div>`;
  }

  function renderDependencyMap(slide) {
    const deps = slide.visualSpec?.entities?.dependencies || [];
    if (!Array.isArray(deps) || !deps.length) return "";
    return `<div class="diagram dependency-map">${deps
      .slice(0, 5)
      .map((dep) => `<div class="dep-node"><h4>${esc(dep.from || "Current")}</h4><span>depends on</span><p>${esc(dep.to || "Unknown")}</p></div>`)
      .join("")}</div>`;
  }

  function renderIssueImpactChain(slide) {
    const chain = slide.visualSpec?.entities?.issueImpact || {};
    return `<div class="diagram issue-chain">
      <div><h4>Issue</h4><p>${esc(chain.issue || antiRestatement(slide.context || "", slide) || "No explicit issue detected.")}</p></div>
      <div><h4>Impact</h4><p>${esc(chain.impact || antiRestatement(slide.decision || "", slide) || "Impact currently bounded.")}</p></div>
      <div><h4>Mitigation</h4><p>${esc(chain.mitigation || (Array.isArray(slide.actions) ? slide.actions[0] : "") || "Continue active monitoring.")}</p></div>
    </div>`;
  }

  function renderContextChips(slide) {
    const chips = slide.visualSpec?.entities?.chips || [];
    return `<div class="diagram context-chips">${chipList(chips)}</div>`;
  }

  function renderActionLadder(slide) {
    const actions = Array.isArray(slide.actions) ? slide.actions.slice(0, 4) : [];
    if (!actions.length) return "";
    return `<ol class="diagram action-ladder">${actions.map((item) => `<li>${esc(item)}</li>`).join("")}</ol>`;
  }

  function renderVisualByType(slide, visualType) {
    if (!visualType || visualType === "none") return "";
    if (visualType === "state-lane-flow") return renderStateLaneFlow(slide);
    if (visualType === "dependency-map") return renderDependencyMap(slide);
    if (visualType === "issue-impact-chain") return renderIssueImpactChain(slide);
    if (visualType === "context-chips") return renderContextChips(slide);
    if (visualType === "action-ladder") return renderActionLadder(slide);
    return "";
  }

  function renderPrimaryVisual(slide) {
    const primary = slide.visualSpec?.primaryVisual || "none";
    const secondary = slide.visualSpec?.secondaryVisual || "none";
    const forceDiagram = shouldRenderDiagram(slide);
    const primaryMarkup = renderVisualByType(slide, primary);
    const secondaryMarkup = renderVisualByType(slide, secondary);

    if (!forceDiagram && (primary === "state-lane-flow" || primary === "dependency-map" || primary === "issue-impact-chain")) {
      return renderContextChips(slide) + secondaryMarkup;
    }
    return primaryMarkup + secondaryMarkup;
  }

  function renderContentSlide(slide, position, total) {
    const insight = antiRestatement(slide.insight || "", slide);
    const context = antiRestatement(slide.context || "", slide);
    const decision = antiRestatement(slide.decision || "", slide);
    const actions = Array.isArray(slide.actions) ? slide.actions : [];
    const chips = [
      `Risk: ${slide.signals?.riskLevel || "unknown"}`,
      `Transitions: ${slide.signals?.statusTransitions ?? 0}`,
      `Depth: ${slide.signals?.eventDepth ?? 0}`,
    ];
    if (slide.signals?.hasBlocker) chips.push("Blocker");
    if (slide.signals?.hasDependency) chips.push("Dependency");

    return `
      <section class="slide content-slide">
        <header>
          <h1 class="title">${esc(slide.title || "Untitled")}</h1>
          <div class="header-chips">${chipList(chips)}</div>
        </header>
        <section class="deck-grid">
          <article class="card insight-card"><h3>Insight</h3><p>${esc(insight || "No non-obvious insight found.")}</p></article>
          <article class="card context-card"><h3>Why This Matters</h3><p>${esc(context || "Context is stable; no escalation signal in this update.")}</p></article>
          <article class="card decision-card"><h3>Decision Needed</h3><p>${esc(decision || "No immediate decision needed.")}</p></article>
          <article class="card actions-card"><h3>Next Actions</h3><ul>${actions.slice(0, 4).map((item) => `<li>${esc(item)}</li>`).join("")}</ul></article>
          <article class="card visual-card">${renderPrimaryVisual(slide)}</article>
        </section>
        <footer class="footer">Slide ${position} / ${total} | Left/Right move | F fullscreen | P presenter</footer>
      </section>`;
  }

  function renderGenericSlide(slide, position, total) {
    return `
      <section class="slide">
        <header><h1 class="title">${esc(slide.title || "Untitled")}</h1></header>
        <section class="card intro-card">
          <p>${esc(antiRestatement(slide.insight || slide.body || "", slide) || "No additional detail.")}</p>
        </section>
        <footer class="footer">Slide ${position} / ${total}</footer>
      </section>`;
  }

  function emitState() {
    const payload = { type: "slide-change", index };
    if (channel) channel.postMessage(payload);
    localStorage.setItem(channelName, JSON.stringify(payload));
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

  function render() {
    if (!slides.length) {
      app.innerHTML = '<section class="slide"><h1 class="title">No slides available</h1></section>';
      return;
    }

    const slide = slides[index];
    const position = index + 1;
    if (slide.type === "content") {
      app.innerHTML = renderContentSlide(slide, position, slides.length);
      return;
    }
    app.innerHTML = renderGenericSlide(slide, position, slides.length);
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
