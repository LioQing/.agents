/* Theme-neutral presentation behavior. Slide registrations run at DOMContentLoaded. */
(() => {
  'use strict';
  const registrations = new Map();
  let active = null;
  let index = 0;
  let slides = [];
  let sources = [];
  let ready = false;
  let checking = false;
  const status = message => { document.getElementById('deck-status').textContent = message; };
  const report = error => { console.error('Slide lifecycle error', error); status('A custom element could not initialize.'); };
  const invoke = (instance, name) => { try { instance?.[name]?.(); } catch (error) { report(error); } };
  const api = {
    get theme() { return document.documentElement.classList.contains('dark') ? 'dark' : 'light'; },
    get reducedMotion() { return matchMedia('(prefers-reduced-motion: reduce)').matches; },
    announce: status,
    checkLayout: () => requestAnimationFrame(checkLayout)
  };
  window.SlideDeck = {
    register(id, factory) {
      if (registrations.has(id)) throw new Error(`Duplicate slide registration: ${id}`);
      registrations.set(id, { factory, instance: null });
    },
    goTo(number) { if (ready) navigate(number - 1); },
    get current() { return index + 1; },
    checkLayout: () => ready ? checkLayout() : []
  };
  function initialize(slide) {
    const record = registrations.get(slide.id);
    if (!record) return null;
    if (!record.instance) {
      try { record.instance = record.factory(slide, api) || {}; } catch (error) { report(error); record.instance = {}; }
    }
    return record.instance;
  }
  function fit() {
    const stage = document.getElementById('stage');
    const scale = Math.min(stage.clientWidth / 1280, stage.clientHeight / 720);
    document.getElementById('deck').style.transform = `scale(${Math.max(0, scale)})`;
    const fit = document.getElementById('canvas-fit');
    fit.style.width = `${1280 * scale}px`;
    fit.style.height = `${720 * scale}px`;
  }
  function checkLayout() {
    if (!ready || checking) return [];
    checking = true;
    const previous = slides.map(slide => [slide.hidden, slide.inert]);
    const problems = [];
    slides.forEach((slide, position) => {
      slide.hidden = false;
      slide.inert = true;
      const content = slide.querySelector('.slide-content');
      const boundary = slide.getBoundingClientRect();
      const scale = boundary.width / 1280 || 1;
      let overflow = content.scrollHeight > content.clientHeight + 2 || content.scrollWidth > content.clientWidth + 2;
      for (const element of content.querySelectorAll('*')) {
        // Internal scrolling is legitimate for code/tables. Check their container, not descendants.
        if (element.closest('pre, .table-scroll') !== element && element.closest('pre, .table-scroll')) continue;
        const rect = element.getBoundingClientRect();
        if (!rect.width || !rect.height) continue;
        if (rect.left < boundary.left - 2 * scale || rect.top < boundary.top - 2 * scale || rect.right > boundary.right + 2 * scale || rect.bottom > boundary.bottom + 2 * scale) overflow = true;
      }
      if (overflow) problems.push({ slide: position + 1, id: slide.id, type: 'overflow' });
      for (const image of content.querySelectorAll('img')) {
        if (image.complete && !image.naturalWidth) problems.push({ slide: position + 1, id: slide.id, type: 'broken-image', source: image.getAttribute('src') });
      }
      slide.dataset.overflow = String(overflow);
    });
    slides.forEach((slide, position) => { [slide.hidden, slide.inert] = previous[position]; });
    const warning = document.getElementById('layout-warning');
    const current = problems.filter(problem => problem.slide === index + 1);
    warning.hidden = !current.length;
    warning.textContent = current.length ? `Slide ${index + 1} needs review: ${[...new Set(current.map(problem => problem.type))].join(', ')}.` : '';
    window.SlideDeck.layoutProblems = problems;
    checking = false;
    return problems;
  }
  function navigate(target, updateHash = true) {
    target = Math.max(0, Math.min(slides.length - 1, target));
    invoke(active, 'leave');
    index = target;
    slides.forEach((slide, position) => {
      const selected = position === index;
      slide.hidden = !selected;
      slide.inert = !selected;
      slide.setAttribute('aria-hidden', String(!selected));
    });
    const slide = slides[index];
    active = initialize(slide);
    invoke(active, 'enter');
    document.getElementById('slide-counter').textContent = `${index + 1} / ${slides.length}`;
    document.getElementById('previous-slide').disabled = index === 0;
    document.getElementById('next-slide').disabled = index === slides.length - 1;
    document.querySelectorAll('[data-go-slide]').forEach(button => {
      if (button.dataset.goSlide === slide.id) button.setAttribute('aria-current', 'page');
      else button.removeAttribute('aria-current');
    });
    if (updateHash) {
      try { history.replaceState(null, '', `#${slide.id}`); } catch { /* file URL history may be restricted */ }
    }
    status(`Slide ${index + 1}: ${sources[index].title}`);
    requestAnimationFrame(checkLayout);
  }
  function fragmentTarget() {
    let fragment;
    try { fragment = decodeURIComponent(location.hash.slice(1)); } catch { return -1; }
    const element = document.getElementById(fragment);
    const slide = element?.closest('#deck > .slide');
    return slides.findIndex(candidate => candidate === slide);
  }
  document.addEventListener('DOMContentLoaded', () => {
    slides = [...document.querySelectorAll('#deck > .slide')];
    sources = JSON.parse(document.getElementById('deck-source').textContent);
    ready = true;
    const overview = document.getElementById('overview');
    const overviewButton = document.getElementById('overview-toggle');
    const setOverview = open => { overview.hidden = !open; overviewButton.setAttribute('aria-expanded', String(open)); };
    overviewButton.addEventListener('click', () => setOverview(overview.hidden));
    document.getElementById('overview-close').addEventListener('click', () => { setOverview(false); overviewButton.focus(); });
    overview.addEventListener('click', event => {
      const button = event.target.closest('[data-go-slide]');
      if (!button) return;
      navigate(slides.findIndex(slide => slide.id === button.dataset.goSlide));
    });
    const dialog = document.getElementById('source-dialog');
    const sourceButton = document.getElementById('source-toggle');
    sourceButton.addEventListener('click', () => {
      const source = sources[index];
      document.getElementById('source-title').textContent = `Original source: slide ${index + 1}`;
      document.getElementById('source-instruction').textContent = source.annotation || '(No instruction supplied.)';
      document.getElementById('source-markdown').textContent = source.markdown;
      dialog.showModal();
    });
    document.getElementById('source-close').addEventListener('click', () => dialog.close());
    dialog.addEventListener('close', () => sourceButton.focus());
    document.getElementById('previous-slide').addEventListener('click', () => navigate(index - 1));
    document.getElementById('next-slide').addEventListener('click', () => navigate(index + 1));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && !dialog.open && !overview.hidden) { setOverview(false); overviewButton.focus(); return; }
      if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || dialog.open || !overview.hidden) return;
      const interactive = event.target.closest('input, textarea, select, button, a, summary, [contenteditable], [role="textbox"]');
      if (interactive && !interactive.closest('#utilities, #navigation')) return;
      if (String(window.getSelection()).length) return;
      const targets = { ArrowRight: index + 1, ArrowDown: index + 1, PageDown: index + 1, ArrowLeft: index - 1, ArrowUp: index - 1, PageUp: index - 1, Home: 0, End: slides.length - 1 };
      if (event.key in targets) { event.preventDefault(); navigate(targets[event.key]); }
    });
    const themeButton = document.getElementById('theme-toggle');
    themeButton.setAttribute('aria-pressed', String(document.documentElement.classList.contains('dark')));
    themeButton.addEventListener('click', () => {
      const dark = document.documentElement.classList.toggle('dark');
      document.documentElement.style.colorScheme = dark ? 'dark' : 'light';
      try { localStorage.setItem('slides-theme', dark ? 'dark' : 'light'); } catch {}
      themeButton.setAttribute('aria-pressed', String(dark));
      registrations.forEach(record => invoke(record.instance, 'themeChanged'));
      document.dispatchEvent(new CustomEvent('slides:themechange', { detail: { theme: api.theme } }));
      requestAnimationFrame(checkLayout);
    });
    const fullscreen = document.getElementById('fullscreen-toggle');
    fullscreen.disabled = !document.documentElement.requestFullscreen || !document.fullscreenEnabled;
    fullscreen.addEventListener('click', async () => {
      try {
        if (document.fullscreenElement) await document.exitFullscreen();
        else await document.documentElement.requestFullscreen();
      } catch { status('Fullscreen is unavailable in this browser context.'); }
    });
    document.addEventListener('fullscreenchange', () => { fullscreen.textContent = document.fullscreenElement ? 'Exit fullscreen' : 'Fullscreen'; fit(); });
    document.getElementById('print-deck').addEventListener('click', () => window.print());
    let printState = null;
    window.addEventListener('beforeprint', () => {
      if (printState) return;
      printState = [...document.querySelectorAll('.slide details')].map(node => [node, node.open]);
      printState.forEach(([node]) => { node.open = true; });
      // Initialize otherwise hidden slide elements for printing, then allow their own print hooks.
      slides.forEach(slide => { const hidden = slide.hidden; slide.hidden = false; invoke(initialize(slide), 'beforePrint'); slide.hidden = hidden; });
    });
    window.addEventListener('afterprint', () => {
      registrations.forEach(record => invoke(record.instance, 'afterPrint'));
      printState?.forEach(([node, open]) => { node.open = open; });
      printState = null;
      fit();
      requestAnimationFrame(checkLayout);
    });
    window.addEventListener('resize', () => { fit(); requestAnimationFrame(checkLayout); });
    // Wrapping bottom-bar controls can resize the stage without a viewport resize.
    const stageObserver = new ResizeObserver(() => { fit(); requestAnimationFrame(checkLayout); });
    stageObserver.observe(document.getElementById('stage'));
    window.addEventListener('hashchange', () => {
      const target = fragmentTarget();
      if (target >= 0) navigate(target, false);
    });
    window.addEventListener('pagehide', () => { stageObserver.disconnect(); registrations.forEach(record => invoke(record.instance, 'dispose')); });
    document.querySelectorAll('.slide img').forEach(image => { image.addEventListener('load', () => requestAnimationFrame(checkLayout)); image.addEventListener('error', () => requestAnimationFrame(checkLayout)); });
    document.fonts?.ready.then(() => requestAnimationFrame(checkLayout));
    fit();
    const target = fragmentTarget();
    navigate(target >= 0 ? target : 0, false);
    requestAnimationFrame(checkLayout);
  });
})();
