import * as pdfjsLib from "./pdfjs/pdf.min.js";

pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  "./pdfjs/pdf.worker.min.js",
  import.meta.url
).href;

const LABELS = ["relevant", "not", "unsure"];
const LABEL_TEXT = { relevant: "Relevant", not: "Not relevant", unsure: "Unsure" };
const LABEL_SHORT = { relevant: "✓", not: "✕", unsure: "?" };

const state = {
  pdf: null,
  file: null,
  numPages: 0,
  ocGroups: [],
  mode: "pages",
  currentPage: 1,
  zoom: 1,
  previewLayerId: null,
  pageLabels: {},
  layerLabels: {},
  task: "",
  renderToken: 0,
  thumbObserver: null,
  loaded: false,
};

const $ = (id) => document.getElementById(id);
const els = {
  fileInput: $("fileInput"),
  importInput: $("importInput"),
  dropZone: $("dropZone"),
  fileMeta: $("fileMeta"),
  fileName: $("fileName"),
  fileSub: $("fileSub"),
  clearFileBtn: $("clearFileBtn"),
  taskInput: $("taskInput"),
  pagesTab: $("pagesTab"),
  layersTab: $("layersTab"),
  listTitle: $("listTitle"),
  listCount: $("listCount"),
  filterInput: $("filterInput"),
  pageList: $("pageList"),
  layerList: $("layerList"),
  listEmpty: $("listEmpty"),
  progressText: $("progressText"),
  fileState: $("fileState"),
  resetBtn: $("resetBtn"),
  prevBtn: $("prevBtn"),
  nextBtn: $("nextBtn"),
  pageIndicator: $("pageIndicator"),
  previewLabel: $("previewLabel"),
  zoomOutBtn: $("zoomOutBtn"),
  zoomInBtn: $("zoomInBtn"),
  zoomLabel: $("zoomLabel"),
  fitBtn: $("fitBtn"),
  showAllBtn: $("showAllBtn"),
  stage: $("stage"),
  emptyState: $("emptyState"),
  pdfCanvas: $("pdfCanvas"),
  viewerStatus: $("viewerStatus"),
  labelSummary: $("labelSummary"),
  exportJsonBtn: $("exportJsonBtn"),
  exportCsvBtn: $("exportCsvBtn"),
  importBtn: $("importBtn"),
  toast: $("toast"),
};

function storageKey() {
  if (!state.file) return null;
  return `drawing-labeler:v1:${state.file.name}:${state.file.size}:${state.file.lastModified}`;
}

function saveState() {
  const key = storageKey();
  if (!key) return;
  try {
    localStorage.setItem(key, JSON.stringify({
      task: state.task,
      mode: state.mode,
      pageLabels: state.pageLabels,
      layerLabels: state.layerLabels,
      zoom: state.zoom,
    }));
  } catch (err) {
    console.warn("Could not save labels", err);
  }
}

function restoreState() {
  const key = storageKey();
  if (!key) return;
  try {
    const saved = JSON.parse(localStorage.getItem(key) || "null");
    if (!saved) return;
    state.task = saved.task || "";
    state.pageLabels = saved.pageLabels || {};
    state.layerLabels = saved.layerLabels || {};
    if (Number.isFinite(saved.zoom)) state.zoom = saved.zoom;
    if (saved.mode === "layers" && state.ocGroups.length) state.mode = "layers";
    els.taskInput.value = state.task;
    toast("Restored labels for this file");
  } catch (err) {
    console.warn("Could not restore labels", err);
  }
}

function toast(message, duration = 2200) {
  els.toast.textContent = message;
  els.toast.classList.add("show");
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => els.toast.classList.remove("show"), duration);
}

function labelOf(map, key) {
  return map[key] || null;
}

function setLabel(map, key, label) {
  if (map[key] === label) {
    delete map[key];
  } else {
    map[key] = label;
  }
}

function pageLabel(page) {
  return state.pageLabels[String(page)] || null;
}

function layerLabel(id) {
  return state.layerLabels[id] || null;
}

function countLabels(map) {
  return Object.values(map).filter(Boolean).length;
}

function relevantCount(map) {
  return Object.values(map).filter((value) => value === "relevant").length;
}

function updateCounts() {
  const isPages = state.mode === "pages";
  const labeled = isPages ? countLabels(state.pageLabels) : countLabels(state.layerLabels);
  const relevant = isPages ? relevantCount(state.pageLabels) : relevantCount(state.layerLabels);
  const total = isPages ? state.numPages : state.ocGroups.length;
  els.progressText.textContent = `${labeled} / ${total} labeled · ${relevant} relevant`;
  els.fileState.textContent = state.file
    ? `${state.numPages} page${state.numPages === 1 ? "" : "s"}${state.ocGroups.length ? ` · ${state.ocGroups.length} layers` : ""}`
    : "No file";
  els.labelSummary.textContent = `${labeled} labeled, ${relevant} marked relevant`;
}

function setMode(mode) {
  if (mode === "layers" && !state.ocGroups.length) return;
  state.mode = mode;
  els.pagesTab.classList.toggle("active", mode === "pages");
  els.layersTab.classList.toggle("active", mode === "layers");
  els.pagesTab.setAttribute("aria-selected", mode === "pages");
  els.layersTab.setAttribute("aria-selected", mode === "layers");
  els.pageList.hidden = mode !== "pages";
  els.layerList.hidden = mode !== "layers";
  els.listTitle.textContent = mode === "pages" ? "Sheets" : "OCG layers";
  els.listEmpty.hidden = Boolean(state.file);
  els.filterInput.placeholder = mode === "pages" ? "Filter sheets…" : "Filter layers…";
  els.filterInput.value = "";
  els.showAllBtn.hidden = mode !== "layers" || !state.previewLayerId;
  if (mode === "pages") state.previewLayerId = null;
  updateListCount();
  updatePreviewLabel();
  renderMain();
  saveState();
}

function updateListCount() {
  if (!state.file) {
    els.listCount.textContent = "No PDF loaded";
    return;
  }
  if (state.mode === "pages") {
    els.listCount.textContent = `${state.numPages} sheet${state.numPages === 1 ? "" : "s"}`;
  } else {
    els.listCount.textContent = `${state.ocGroups.length} layer${state.ocGroups.length === 1 ? "" : "s"}`;
  }
}

function updatePreviewLabel() {
  if (!state.pdf) {
    els.previewLabel.textContent = "No page loaded";
    return;
  }
  const base = `Sheet ${state.currentPage} of ${state.numPages}`;
  if (state.mode === "layers") {
    if (state.previewLayerId) {
      const group = state.ocGroups.find((g) => g.id === state.previewLayerId);
      els.previewLabel.textContent = `${base} · layer preview · ${group ? group.name : state.previewLayerId}`;
    } else {
      els.previewLabel.textContent = `${base} · all layers`;
    }
  } else {
    els.previewLabel.textContent = base;
  }
}

function clearFile() {
  if (state.thumbObserver) {
    state.thumbObserver.disconnect();
    state.thumbObserver = null;
  }
  state.pdf = null;
  state.file = null;
  state.numPages = 0;
  state.ocGroups = [];
  state.pageLabels = {};
  state.layerLabels = {};
  state.task = "";
  state.mode = "pages";
  state.currentPage = 1;
  state.zoom = 1;
  state.previewLayerId = null;
  state.loaded = false;
  els.fileMeta.hidden = true;
  els.dropZone.hidden = false;
  els.taskInput.value = "";
  els.pagesTab.disabled = false;
  els.layersTab.disabled = true;
  els.pageList.innerHTML = "";
  els.layerList.innerHTML = "";
  els.pageList.hidden = false;
  els.layerList.hidden = true;
  els.pageIndicator.textContent = "—";
  els.zoomLabel.textContent = "100%";
  els.previewLabel.textContent = "No page loaded";
  els.pdfCanvas.classList.remove("visible");
  els.emptyState.hidden = false;
  els.listEmpty.hidden = false;
  els.listEmpty.textContent = "Load a PDF to begin.";
  setMode("pages");
  updateCounts();
  els.viewerStatus.textContent = "Local-only. Files never leave this browser.";
}

async function loadPdf(file) {
  if (!file) return;
  if (!/\.pdf$/i.test(file.name) && file.type !== "application/pdf") {
    toast("Please choose a PDF file");
    return;
  }
  clearFile();
  els.viewerStatus.textContent = "Loading PDF…";
  try {
    const data = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data }).promise;
    state.pdf = pdf;
    state.file = file;
    state.numPages = pdf.numPages;
    state.currentPage = 1;
    state.zoom = 1;
    state.loaded = true;
    state.pageLabels = {};
    state.layerLabels = {};
    state.task = "";

    let groups = [];
    try {
      const config = await pdf.getOptionalContentConfig();
      groups = groupsFromConfig(config);
    } catch (err) {
      console.warn("Could not read optional content groups", err);
    }
    state.ocGroups = groups;
    state.mode = "pages";

    els.fileName.textContent = file.name;
    els.fileSub.textContent = `${pdf.numPages} page${pdf.numPages === 1 ? "" : "s"}${groups.length ? ` · ${groups.length} OCG layers` : " · no OCG layers"}`;
    els.fileMeta.hidden = false;
    els.dropZone.hidden = true;
    els.layersTab.disabled = groups.length === 0;
    els.taskInput.value = "";
    restoreState();
    setMode(state.mode);
    buildPageList();
    buildLayerList();
    updateCounts();
    els.emptyState.hidden = true;
    els.pdfCanvas.classList.add("visible");
    els.viewerStatus.textContent = "Local-only. Files never leave this browser.";
    renderMain();
    toast("PDF loaded");
  } catch (err) {
    console.error(err);
    els.viewerStatus.textContent = "Could not open this PDF.";
    toast(`Could not open PDF: ${err.message || err}`);
    clearFile();
  } finally {
    els.fileInput.value = "";
  }
}

function groupsFromConfig(config) {
  if (!config) return [];
  let raw = null;
  try {
    raw = typeof config.getGroups === "function" ? config.getGroups() : null;
  } catch (err) {
    console.warn("getGroups failed", err);
    return [];
  }
  if (!raw) return [];
  const entries = raw instanceof Map ? [...raw.entries()] : Object.entries(raw);
  return entries
    .filter(([id]) => id != null)
    .map(([id, group]) => ({
      id: String(id),
      name: (group && (group.name || group.text)) || String(id),
      visible: group ? group.visible !== false : true,
    }))
    .sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }));
}

function buildPageList() {
  if (state.thumbObserver) state.thumbObserver.disconnect();
  els.pageList.innerHTML = "";
  if (!state.pdf) return;

  state.thumbObserver = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      const canvas = entry.target;
      state.thumbObserver.unobserve(canvas);
      renderThumbnail(canvas, Number(canvas.dataset.page));
    }
  }, { root: els.pageList, rootMargin: "80px" });

  for (let page = 1; page <= state.numPages; page += 1) {
    const card = document.createElement("article");
    card.className = "page-card";
    card.dataset.page = String(page);
    card.tabIndex = 0;
    card.setAttribute("role", "button");
    card.setAttribute("aria-label", `Sheet ${page}`);

    const wrap = document.createElement("div");
    wrap.className = "page-thumb-wrap";
    const canvas = document.createElement("canvas");
    canvas.dataset.page = String(page);
    canvas.width = 110;
    canvas.height = 80;
    wrap.append(canvas);

    const meta = document.createElement("div");
    meta.className = "page-meta";
    const num = document.createElement("span");
    num.className = "page-num";
    num.textContent = `Sheet ${page}`;
    const stateLabel = document.createElement("span");
    stateLabel.className = "page-state";
    meta.append(num, stateLabel);

    const buttons = document.createElement("div");
    buttons.className = "page-buttons";
    for (const label of LABELS) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "mini-label";
      btn.dataset.label = label;
      btn.textContent = LABEL_SHORT[label];
      btn.title = LABEL_TEXT[label];
      btn.addEventListener("click", (event) => {
        event.stopPropagation();
        setLabel(state.pageLabels, String(page), label);
        updatePageCard(page);
        updateCounts();
        saveState();
      });
      buttons.append(btn);
    }

    card.append(wrap, meta, buttons);
    card.addEventListener("click", () => setCurrentPage(page));
    card.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        setCurrentPage(page);
      }
    });
    els.pageList.append(card);
    state.thumbObserver.observe(canvas);
    updatePageCard(page);
  }
  els.listEmpty.hidden = state.numPages > 0;
}

function updatePageCard(page) {
  const card = els.pageList.querySelector(`.page-card[data-page="${page}"]`);
  if (!card) return;
  card.classList.toggle("current", page === state.currentPage);
  const label = pageLabel(page);
  for (const value of LABELS) card.classList.toggle(value, label === value);
  const stateLabel = card.querySelector(".page-state");
  if (stateLabel) stateLabel.textContent = label ? LABEL_TEXT[label] : "";
  for (const button of card.querySelectorAll(".mini-label")) {
    button.classList.toggle("active", button.dataset.label === label);
  }
}

async function renderThumbnail(canvas, pageNumber) {
  if (!state.pdf) return;
  try {
    const page = await state.pdf.getPage(pageNumber);
    const base = page.getViewport({ scale: 1 });
    const scale = Math.min(0.22, 100 / base.width, 74 / base.height);
    const viewport = page.getViewport({ scale });
    canvas.width = Math.max(1, Math.ceil(viewport.width));
    canvas.height = Math.max(1, Math.ceil(viewport.height));
    const ctx = canvas.getContext("2d", { alpha: false });
    await page.render({ canvasContext: ctx, viewport, background: "#ffffff" }).promise;
  } catch (err) {
    console.warn("Thumbnail failed", pageNumber, err);
  }
}

function buildLayerList() {
  els.layerList.innerHTML = "";
  if (!state.ocGroups.length) {
    els.listEmpty.hidden = state.mode !== "layers";
    els.listEmpty.textContent = "This PDF has no OCG layers. Use Sheets mode.";
    return;
  }
  for (const group of state.ocGroups) {
    const row = document.createElement("div");
    row.className = "layer-row";
    row.dataset.id = group.id;

    const main = document.createElement("button");
    main.type = "button";
    main.className = "layer-main";
    main.title = `Preview only: ${group.name}`;
    const dot = document.createElement("span");
    dot.className = "layer-dot";
    const name = document.createElement("span");
    name.className = "layer-name";
    name.textContent = group.name;
    main.append(dot, name);
    main.addEventListener("click", () => {
      state.previewLayerId = group.id;
      updateLayerRows();
      updatePreviewLabel();
      els.showAllBtn.hidden = false;
      renderMain();
    });

    const buttons = document.createElement("div");
    buttons.className = "layer-buttons";
    for (const label of LABELS) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "mini-label";
      btn.dataset.label = label;
      btn.textContent = LABEL_SHORT[label];
      btn.title = LABEL_TEXT[label];
      btn.addEventListener("click", (event) => {
        event.stopPropagation();
        setLabel(state.layerLabels, group.id, label);
        updateLayerRow(group.id);
        updateCounts();
        saveState();
      });
      buttons.append(btn);
    }

    row.append(main, buttons);
    els.layerList.append(row);
    updateLayerRow(group.id);
  }
  els.listEmpty.hidden = true;
}

function updateLayerRows() {
  for (const group of state.ocGroups) updateLayerRow(group.id);
}

function updateLayerRow(id) {
  const row = els.layerList.querySelector(`.layer-row[data-id="${cssEscape(id)}"]`);
  if (!row) return;
  const label = layerLabel(id);
  row.classList.toggle("previewing", id === state.previewLayerId);
  for (const value of LABELS) row.classList.toggle(value, label === value);
  for (const button of row.querySelectorAll(".mini-label")) {
    button.classList.toggle("active", button.dataset.label === label);
  }
}

function cssEscape(value) {
  if (window.CSS && typeof window.CSS.escape === "function") return window.CSS.escape(value);
  return String(value).replace(/["\\]/g, "\\$&");
}

function setCurrentPage(page) {
  const next = Math.max(1, Math.min(state.numPages, page));
  if (next === state.currentPage) return;
  state.currentPage = next;
  for (let p = 1; p <= state.numPages; p += 1) updatePageCard(p);
  const card = els.pageList.querySelector(`.page-card[data-page="${next}"]`);
  if (card) card.scrollIntoView({ block: "nearest", behavior: "smooth" });
  updatePreviewLabel();
  renderMain();
}

function moveLayer(delta) {
  if (!state.ocGroups.length) return;
  let index = state.ocGroups.findIndex((group) => group.id === state.previewLayerId);
  if (index === -1) index = delta > 0 ? -1 : 0;
  const next = Math.max(0, Math.min(state.ocGroups.length - 1, index + delta));
  const group = state.ocGroups[next];
  if (!group) return;
  state.previewLayerId = group.id;
  els.showAllBtn.hidden = false;
  updateLayerRows();
  updatePreviewLabel();
  const row = els.layerList.querySelector(`.layer-row[data-id="${cssEscape(group.id)}"]`);
  if (row) row.scrollIntoView({ block: "nearest", behavior: "smooth" });
  renderMain();
}

async function renderMain() {
  if (!state.pdf || !state.numPages) return;
  const token = ++state.renderToken;
  const pageNumber = state.currentPage;
  try {
    const page = await state.pdf.getPage(pageNumber);
    if (token !== state.renderToken) return;
    const base = page.getViewport({ scale: 1 });
    const stageWidth = Math.max(240, els.stage.clientWidth - 48);
    const stageHeight = Math.max(240, els.stage.clientHeight - 48);
    const fit = Math.min(stageWidth / base.width, stageHeight / base.height);
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const scale = Math.max(0.1, fit * state.zoom);
    const viewport = page.getViewport({ scale: scale * dpr });

    let ocConfig = null;
    if (state.mode === "layers" && state.previewLayerId) {
      try {
        ocConfig = await state.pdf.getOptionalContentConfig();
        for (const group of state.ocGroups) {
          ocConfig.setVisibility(group.id, group.id === state.previewLayerId);
        }
      } catch (err) {
        console.warn("Could not isolate layer", err);
        ocConfig = null;
      }
    }

    const canvas = els.pdfCanvas;
    canvas.width = Math.max(1, Math.ceil(viewport.width));
    canvas.height = Math.max(1, Math.ceil(viewport.height));
    canvas.style.width = `${Math.round(viewport.width / dpr)}px`;
    canvas.style.height = `${Math.round(viewport.height / dpr)}px`;
    canvas.classList.add("visible");
    const ctx = canvas.getContext("2d", { alpha: false });
    await page.render({
      canvasContext: ctx,
      viewport,
      background: "#ffffff",
      ...(ocConfig ? { optionalContentConfigPromise: Promise.resolve(ocConfig) } : {}),
    }).promise;
    if (token !== state.renderToken) return;

    els.pageIndicator.textContent = `${pageNumber} / ${state.numPages}`;
    els.zoomLabel.textContent = `${Math.round(state.zoom * 100)}%`;
    els.prevBtn.disabled = pageNumber <= 1;
    els.nextBtn.disabled = pageNumber >= state.numPages;
    els.emptyState.hidden = true;
    updatePreviewLabel();
  } catch (err) {
    console.error(err);
    els.viewerStatus.textContent = "Could not render page.";
    toast(`Render error: ${err.message || err}`);
  }
}

function setZoom(next) {
  state.zoom = Math.max(0.25, Math.min(4, next));
  els.zoomLabel.textContent = `${Math.round(state.zoom * 100)}%`;
  renderMain();
  saveState();
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function buildExport() {
  const pages = Array.from({ length: state.numPages }, (_, index) => {
    const page = index + 1;
    const label = pageLabel(page);
    return {
      page,
      label,
      relevant: label === "relevant" ? true : label === "not" ? false : null,
    };
  });
  const layers = state.ocGroups.map((group) => {
    const label = layerLabel(group.id);
    return {
      id: group.id,
      name: group.name,
      label,
      relevant: label === "relevant" ? true : label === "not" ? false : null,
    };
  });
  return {
    schema: "drawing-labeler/v1",
    exported_at: new Date().toISOString(),
    file: state.file ? {
      name: state.file.name,
      size: state.file.size,
      last_modified: state.file.lastModified,
      page_count: state.numPages,
      ocg_count: state.ocGroups.length,
    } : null,
    task_prompt: state.task,
    mode: state.mode,
    pages,
    layers,
  };
}

function exportJson() {
  if (!state.pdf) return toast("Load a PDF first");
  const payload = buildExport();
  const name = (state.file.name.replace(/\.pdf$/i, "") || "labels") + "-labels.json";
  downloadBlob(new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }), name);
  toast("Exported JSON");
}

function exportCsv() {
  if (!state.pdf) return toast("Load a PDF first");
  const rows = [["kind", "page", "id", "name", "label", "relevant"]];
  for (let page = 1; page <= state.numPages; page += 1) {
    const label = pageLabel(page);
    rows.push(["page", String(page), String(page), `Sheet ${page}`, label || "", label === "relevant" ? "true" : label === "not" ? "false" : ""]);
  }
  for (const group of state.ocGroups) {
    const label = layerLabel(group.id);
    rows.push(["layer", "", group.id, group.name, label || "", label === "relevant" ? "true" : label === "not" ? "false" : ""]);
  }
  const csv = rows.map((row) => row.map(csvCell).join(",")).join("\n");
  const name = (state.file.name.replace(/\.pdf$/i, "") || "labels") + "-labels.csv";
  downloadBlob(new Blob([csv], { type: "text/csv" }), name);
  toast("Exported CSV");
}

function csvCell(value) {
  const text = String(value ?? "");
  return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
}

async function importLabels(file) {
  if (!file) return;
  if (!state.pdf) return toast("Load the PDF first, then import labels");
  try {
    const data = JSON.parse(await file.text());
    if (data.file && data.file.name && state.file && data.file.name !== state.file.name) {
      const proceed = window.confirm(`Labels are for "${data.file.name}", but the open file is "${state.file.name}". Import anyway?`);
      if (!proceed) return;
    }
    if (typeof data.task_prompt === "string") {
      state.task = data.task_prompt;
      els.taskInput.value = state.task;
    }
    state.pageLabels = {};
    state.layerLabels = {};
    for (const entry of data.pages || []) {
      if (entry && LABELS.includes(entry.label)) state.pageLabels[String(entry.page)] = entry.label;
    }
    const layerIds = new Set(state.ocGroups.map((g) => g.id));
    const layerNames = new Map(state.ocGroups.map((g) => [g.name, g.id]));
    for (const entry of data.layers || []) {
      if (!entry || !LABELS.includes(entry.label)) continue;
      const id = layerIds.has(String(entry.id)) ? String(entry.id) : layerNames.get(entry.name);
      if (id) state.layerLabels[id] = entry.label;
    }
    saveState();
    for (let page = 1; page <= state.numPages; page += 1) updatePageCard(page);
    updateLayerRows();
    updateCounts();
    toast("Labels imported");
  } catch (err) {
    console.error(err);
    toast("Could not import labels");
  } finally {
    els.importInput.value = "";
  }
}

function resetLabels() {
  if (!state.file) return;
  if (!window.confirm("Clear all labels for this file?")) return;
  state.pageLabels = {};
  state.layerLabels = {};
  state.task = "";
  state.zoom = 1;
  els.taskInput.value = "";
  const key = storageKey();
  if (key) localStorage.removeItem(key);
  for (let page = 1; page <= state.numPages; page += 1) updatePageCard(page);
  updateLayerRows();
  updateCounts();
  renderMain();
  toast("Labels cleared");
}

function applyFilter() {
  const query = els.filterInput.value.trim().toLowerCase();
  if (state.mode === "pages") {
    for (const card of els.pageList.querySelectorAll(".page-card")) {
      const page = card.dataset.page;
      const label = pageLabel(page);
      const hay = `sheet ${page} ${label || ""}`;
      card.hidden = Boolean(query) && !hay.includes(query);
    }
  } else {
    for (const row of els.layerList.querySelectorAll(".layer-row")) {
      const group = state.ocGroups.find((g) => g.id === row.dataset.id);
      const hay = `${group ? group.name : row.dataset.id} ${layerLabel(row.dataset.id) || ""}`.toLowerCase();
      row.hidden = Boolean(query) && !hay.includes(query);
    }
  }
}

function bindEvents() {
  els.fileInput.addEventListener("change", (event) => loadPdf(event.target.files[0]));
  els.importInput.addEventListener("change", (event) => importLabels(event.target.files[0]));
  els.importBtn.addEventListener("click", () => els.importInput.click());
  els.clearFileBtn.addEventListener("click", clearFile);
  els.exportJsonBtn.addEventListener("click", exportJson);
  els.exportCsvBtn.addEventListener("click", exportCsv);
  els.resetBtn.addEventListener("click", resetLabels);
  els.taskInput.addEventListener("input", () => { state.task = els.taskInput.value; saveState(); });
  els.filterInput.addEventListener("input", applyFilter);

  els.pagesTab.addEventListener("click", () => setMode("pages"));
  els.layersTab.addEventListener("click", () => setMode("layers"));

  els.prevBtn.addEventListener("click", () => setCurrentPage(state.currentPage - 1));
  els.nextBtn.addEventListener("click", () => setCurrentPage(state.currentPage + 1));
  els.zoomInBtn.addEventListener("click", () => setZoom(state.zoom * 1.2));
  els.zoomOutBtn.addEventListener("click", () => setZoom(state.zoom / 1.2));
  els.fitBtn.addEventListener("click", () => setZoom(1));
  els.showAllBtn.addEventListener("click", () => {
    state.previewLayerId = null;
    els.showAllBtn.hidden = true;
    updateLayerRows();
    updatePreviewLabel();
    renderMain();
  });

  els.dropZone.addEventListener("click", () => els.fileInput.click());
  els.dropZone.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      els.fileInput.click();
    }
  });
  for (const eventName of ["dragenter", "dragover"]) {
    els.dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      els.dropZone.classList.add("dragover");
    });
  }
  for (const eventName of ["dragleave", "drop"]) {
    els.dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      els.dropZone.classList.remove("dragover");
    });
  }
  els.dropZone.addEventListener("drop", (event) => {
    const file = event.dataTransfer.files[0];
    if (file) loadPdf(file);
  });

  window.addEventListener("resize", () => {
    if (state.pdf) {
      clearTimeout(window.__labelerResize);
      window.__labelerResize = setTimeout(renderMain, 140);
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement || event.target instanceof HTMLSelectElement) return;
    if (!state.pdf) return;
    const key = event.key.toLowerCase();
    if (key === "r" || key === "n" || key === "u") {
      const label = key === "r" ? "relevant" : key === "n" ? "not" : "unsure";
      if (state.mode === "pages") {
        setLabel(state.pageLabels, String(state.currentPage), label);
        updatePageCard(state.currentPage);
        updateCounts();
        saveState();
      } else if (state.previewLayerId) {
        setLabel(state.layerLabels, state.previewLayerId, label);
        updateLayerRow(state.previewLayerId);
        updateCounts();
        saveState();
      }
      event.preventDefault();
    } else if (key === "arrowleft") {
      if (state.mode === "layers") moveLayer(-1);
      else setCurrentPage(state.currentPage - 1);
      event.preventDefault();
    } else if (key === "arrowright") {
      if (state.mode === "layers") moveLayer(1);
      else setCurrentPage(state.currentPage + 1);
      event.preventDefault();
    } else if (key === "arrowup") {
      if (state.mode === "layers") moveLayer(-1);
      event.preventDefault();
    } else if (key === "arrowdown") {
      if (state.mode === "layers") moveLayer(1);
      event.preventDefault();
    }
  });
}

bindEvents();
clearFile();
