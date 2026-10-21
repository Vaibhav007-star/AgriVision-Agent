/**
 * AgriVision Agent — Client-Side Reactive Controller (app/static/js/app.js)
 * High-performance UI engine featuring:
 * - Ambient Spores Particle Background (HTML5 Canvas)
 * - Interactive Split-Lens XAI Slider (Grad-CAM vs Original)
 * - 3D Card Mouse Tilt & Radial Glow
 * - 15L Knapsack Tank Fluid Fill Simulator & Money Saved Meter
 * - Native Web Speech Bilingual Text-to-Speech (TTS)
 * - Microclimate Weather Simulation Controls
 * - Deep Learning Pipeline Math Inspector
 * - Web Audio API Synthesizer (Zero External Assets)
 */

let currentLanguage = 'en';
let selectedFile = null;
let selectedSampleId = null;
let latestRxData = {};
let healthChart = null;
let soundEnabled = true;
let audioCtx = null;

document.addEventListener('DOMContentLoaded', () => {
  const safeRun = (name, fn) => {
    try {
      fn();
    } catch (e) {
      console.warn(`[AgriVision Init Note: ${name}]`, e);
    }
  };

  if (window.lucide) safeRun('lucide', () => window.lucide.createIcons());
  safeRun('initSporesCanvas', initSporesCanvas);
  safeRun('initSamples', initSamples);
  safeRun('initWeather', initWeather);
  safeRun('initStats', initStats);
  safeRun('initHistory', initHistory);
  safeRun('initSplitSlider', initSplitSlider);
  safeRun('init3DTilt', init3DTilt);
  safeRun('setupEventListeners', setupEventListeners);
  safeRun('populatePrintableReport', populatePrintableReport);
  safeRun('initPWA', initPWA);
  safeRun('initHaryanaBlockAdvisor', initHaryanaBlockAdvisor);
  safeRun('initMandiForecast', initMandiForecast);
  safeRun('initHaryanaGisMap', initHaryanaGisMap);
  safeRun('initVoiceAdvisor', initVoiceAdvisor);
  safeRun('initDroneBatchSurvey', initDroneBatchSurvey);
  safeRun('runNpkCalculation', runNpkCalculation);
});

// ============================================================================
// 1. Web Audio API Synthesizer
// ============================================================================
function playChime(type = 'success') {
  if (!soundEnabled) return;
  try {
    if (!audioCtx) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (AudioContextClass) audioCtx = new AudioContextClass();
    }
    if (!audioCtx) return;

    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }

    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);

    const now = audioCtx.currentTime;
    if (type === 'success') {
      osc.frequency.setValueAtTime(523.25, now); // C5
      osc.frequency.exponentialRampToValueAtTime(659.25, now + 0.12); // E5
      osc.frequency.exponentialRampToValueAtTime(783.99, now + 0.25); // G5
      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.45);
      osc.start(now);
      osc.stop(now + 0.45);
    } else if (type === 'click') {
      osc.frequency.setValueAtTime(440, now);
      gain.gain.setValueAtTime(0.06, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
      osc.start(now);
      osc.stop(now + 0.08);
    }
  } catch (e) {
    // Audio context fallback
  }
}

// ============================================================================
// 2. Ambient Spores Particle Background (Disabled - Zero Motion Mode)
// ============================================================================
function initSporesCanvas() {
  const canvas = document.getElementById('spores-canvas');
  if (canvas) {
    canvas.style.display = 'none';
  }
}

// ============================================================================
// 3. Interactive Split-Lens Slider Controller
// ============================================================================
function initSplitSlider() {
  const container = document.getElementById('split-view-container');
  const overlay = document.getElementById('split-overlay');
  const handle = document.getElementById('split-handle');
  if (!container || !overlay || !handle) return;

  let isDragging = false;

  function moveSlider(clientX) {
    const rect = container.getBoundingClientRect();
    let pos = (clientX - rect.left) / rect.width;
    pos = Math.max(0.05, Math.min(0.95, pos));
    overlay.style.width = `${pos * 100}%`;
    handle.style.left = `${pos * 100}%`;
  }

  container.addEventListener('mousedown', (e) => {
    isDragging = true;
    moveSlider(e.clientX);
  });
  window.addEventListener('mouseup', () => (isDragging = false));
  window.addEventListener('mousemove', (e) => {
    if (isDragging) moveSlider(e.clientX);
  });

  // Touch Support
  container.addEventListener('touchstart', (e) => {
    isDragging = true;
    if (e.touches.length) moveSlider(e.touches[0].clientX);
  });
  window.addEventListener('touchend', () => (isDragging = false));
  window.addEventListener('touchmove', (e) => {
    if (isDragging && e.touches.length) moveSlider(e.touches[0].clientX);
  });
}

function switchVisualMode(mode) {
  playChime('click');
  const gridContainer = document.getElementById('grid-view-container');
  const splitContainer = document.getElementById('split-view-container');
  const btnGrid = document.getElementById('view-mode-grid');
  const btnSplit = document.getElementById('view-mode-split');

  if (!gridContainer || !splitContainer || !btnGrid || !btnSplit) return;

  if (mode === 'grid') {
    gridContainer.classList.remove('hidden');
    splitContainer.classList.add('hidden');
    btnGrid.className = 'px-2.5 py-1 rounded-md bg-lime-500/20 text-lime-400 font-bold';
    btnSplit.className = 'px-2.5 py-1 rounded-md text-slate-400 hover:text-white';
  } else {
    gridContainer.classList.add('hidden');
    splitContainer.classList.remove('hidden');
    btnSplit.className = 'px-2.5 py-1 rounded-md bg-lime-500/20 text-lime-400 font-bold';
    btnGrid.className = 'px-2.5 py-1 rounded-md text-slate-400 hover:text-white';
  }
}

// ============================================================================
// 4. 3D Mouse Tilt Effect (Disabled - Zero Motion Mode)
// ============================================================================
function init3DTilt() {
  // Motion disabled per user preference
}

// ============================================================================
// 5. Setup Event Listeners
// ============================================================================
function setupEventListeners() {
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('leaf-file-input');
  const acresSlider = document.getElementById('acres-slider');
  const acresDisplay = document.getElementById('acres-display');
  const runBtn = document.getElementById('run-diagnosis-btn');
  const langToggleBtn = document.getElementById('lang-toggle-btn');
  const soundToggleBtn = document.getElementById('sound-toggle-btn');

  // Sound Toggle
  if (soundToggleBtn) {
    soundToggleBtn.addEventListener('click', () => {
      soundEnabled = !soundEnabled;
      soundToggleBtn.innerHTML = soundEnabled
        ? `<i data-lucide="volume-2" class="w-4 h-4 text-lime-400"></i>`
        : `<i data-lucide="volume-x" class="w-4 h-4 text-slate-500"></i>`;
      if (window.lucide) window.lucide.createIcons();
    });
  }

  // Drag & Drop
  if (dropZone && fileInput) {
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('border-lime-500');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('border-lime-500'));
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('border-lime-500');
      if (e.dataTransfer.files.length) {
        handleFileSelected(e.dataTransfer.files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length) {
        handleFileSelected(e.target.files[0]);
      }
    });
  }

  // Acreage Slider
  if (acresSlider && acresDisplay) {
    acresSlider.addEventListener('input', (e) => {
      acresDisplay.innerText = `${e.target.value} Acres`;
      updateDosageMath(parseFloat(e.target.value));
    });
  }

  // Diagnostic Run Button
  if (runBtn) {
    runBtn.addEventListener('click', executeDiagnosis);
  }

  // Language Toggle
  if (langToggleBtn) {
    langToggleBtn.addEventListener('click', toggleLanguage);
  }
}

function handleFileSelected(file) {
  playChime('click');
  selectedFile = file;
  selectedSampleId = null;

  const fname = file.name.toLowerCase();
  const cropSelect = document.getElementById('target-crop-select');
  if (cropSelect) {
    if (fname.includes('wheat') || fname.includes('rust') || fname.includes('gehun')) {
      cropSelect.value = 'Wheat';
    } else if (fname.includes('rice') || fname.includes('paddy') || fname.includes('dhaan')) {
      cropSelect.value = 'Rice';
    } else if (fname.includes('cotton') || fname.includes('kapas')) {
      cropSelect.value = 'Cotton';
    } else if (fname.includes('sugarcane') || fname.includes('ganna')) {
      cropSelect.value = 'Sugarcane';
    } else if (fname.includes('corn') || fname.includes('makka')) {
      cropSelect.value = 'Corn';
    }
  }

  const diagCrop = document.getElementById('diag-crop');
  const diagCond = document.getElementById('diag-condition');
  const diagAdvice = document.getElementById('diag-advice');
  const diagConf = document.getElementById('diag-conf-pct');
  const diagBadge = document.getElementById('diag-conf-badge');
  const banner = document.getElementById('diagnosis-banner');

  if (banner) banner.className = 'p-5 rounded-2xl bg-gradient-to-r from-emerald-950/70 to-zenze-card border border-lime-500/30';
  if (diagCrop) diagCrop.innerText = 'Ready for Scan';
  if (diagCond) diagCond.innerText = `Uploaded: ${file.name}`;
  if (diagAdvice) diagAdvice.innerText = 'Click "Execute Diagnostic Engine" to analyze foliar pathology.';
  if (diagConf) diagConf.innerText = '--%';
  if (diagBadge) {
    diagBadge.className = 'text-xs px-2.5 py-1 rounded-full font-bold bg-lime-500/20 text-lime-300 border border-lime-500/40';
    diagBadge.innerText = 'Queued';
  }

  const reader = new FileReader();
  reader.onload = (e) => {
    const orig = document.getElementById('preview-original');
    const clahe = document.getElementById('preview-clahe');
    const under = document.getElementById('split-img-under');
    if (orig) orig.src = e.target.result;
    if (clahe) clahe.src = e.target.result;
    if (under) under.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

async function initSamples() {
  const container = document.getElementById('samples-container');
  if (!container) return;
  try {
    const res = await fetch('/api/samples');
    const data = await res.json();
    container.innerHTML = '';

    if (!data.samples || !data.samples.length) return;

    data.samples.forEach((sample, idx) => {
      const btn = document.createElement('button');
      btn.className = `p-2 rounded-xl border text-left flex items-center gap-2 transition-all ${
        idx === 0 ? 'bg-lime-500/10 border-lime-500/40 text-lime-400' : 'bg-white/5 border-white/10 hover:border-lime-500/30 text-slate-300'
      }`;
      btn.innerHTML = `
        <img src="${sample.thumbnail}" class="w-8 h-8 rounded-lg object-cover">
        <div class="truncate">
          <div class="font-bold text-[11px] truncate">${sample.condition}</div>
          <div class="text-[9px] text-slate-400 truncate">${sample.crop}</div>
        </div>
      `;
      btn.onclick = () => selectSample(sample.id, sample.thumbnail, btn);
      container.appendChild(btn);

      if (idx === 0) {
        selectedSampleId = sample.id;
        const orig = document.getElementById('preview-original');
        const clahe = document.getElementById('preview-clahe');
        const under = document.getElementById('split-img-under');
        if (orig) orig.src = sample.thumbnail;
        if (clahe) clahe.src = sample.thumbnail;
        if (under) under.src = sample.thumbnail;
      }
    });
  } catch (err) {
    console.error('Failed to load samples:', err);
  }
}

function selectSample(id, thumbUrl, activeBtn) {
  playChime('click');
  selectedSampleId = id;
  selectedFile = null;
  const orig = document.getElementById('preview-original');
  const clahe = document.getElementById('preview-clahe');
  const under = document.getElementById('split-img-under');
  if (orig) orig.src = thumbUrl;
  if (clahe) clahe.src = thumbUrl;
  if (under) under.src = thumbUrl;

  document.querySelectorAll('#samples-container button').forEach((b) => {
    b.className = 'p-2 rounded-xl border text-left flex items-center gap-2 transition-all bg-white/5 border-white/10 hover:border-lime-500/30 text-slate-300';
  });
  if (activeBtn) {
    activeBtn.className = 'p-2 rounded-xl border text-left flex items-center gap-2 transition-all bg-lime-500/10 border-lime-500/40 text-lime-400';
  }
}

async function initWeather() {
  try {
    const res = await fetch('/api/weather?location=Karnal,%20Haryana');
    const data = await res.json();
    const tempSpan = document.getElementById('hero-temp-val');
    const sporeSpan = document.getElementById('hero-spore-val');
    const statRisk = document.getElementById('stat-spore-risk');

    if (tempSpan) tempSpan.innerText = `${data.temperature_c}°C`;
    if (sporeSpan) sporeSpan.innerText = `${data.spore_germination_risk} Risk`;
    if (statRisk) statRisk.innerText = data.spore_germination_risk;
  } catch (err) {
    console.error('Weather load error:', err);
  }
}

function simulateWeather(mode) {
  playChime('click');
  const tempSpan = document.getElementById('hero-temp-val');
  const sporeSpan = document.getElementById('hero-spore-val');
  const statRisk = document.getElementById('stat-spore-risk');

  if (mode === 'monsoon') {
    if (tempSpan) tempSpan.innerText = '26.4°C';
    if (sporeSpan) {
      sporeSpan.innerText = 'CRITICAL HIGH Risk';
      sporeSpan.className = 'font-bold text-red-400';
    }
    if (statRisk) {
      statRisk.innerText = 'Critical High';
      statRisk.className = 'text-xl font-bold text-red-400 mt-1';
    }
  } else if (mode === 'dry') {
    if (tempSpan) tempSpan.innerText = '33.8°C';
    if (sporeSpan) {
      sporeSpan.innerText = 'LOW Spore Risk';
      sporeSpan.className = 'font-bold text-emerald-400';
    }
    if (statRisk) {
      statRisk.innerText = 'Low Inoculum';
      statRisk.className = 'text-xl font-bold text-emerald-400 mt-1';
    }
  } else {
    initWeather();
    if (sporeSpan) sporeSpan.className = 'font-bold text-amber-400';
    if (statRisk) statRisk.className = 'text-xl font-bold text-amber-400 mt-1';
  }
}

async function executeDiagnosis() {
  playChime('click');
  const scanLine = document.getElementById('scan-line');
  const runBtn = document.getElementById('run-diagnosis-btn');
  const lesionTag = document.getElementById('lesion-tag');

  if (scanLine) scanLine.classList.remove('hidden');
  if (runBtn) {
    runBtn.disabled = true;
    runBtn.innerHTML = `<i data-lucide="loader-2" class="w-5 h-5 animate-spin"></i><span>Analyzing Neural Activations...</span>`;
    if (window.lucide) window.lucide.createIcons();
  }

  const formData = new FormData();
  if (selectedFile) {
    formData.append('file', selectedFile);
  } else if (selectedSampleId) {
    formData.append('sample_id', selectedSampleId);
  } else {
    formData.append('sample_id', 'tomato_early_blight');
  }

  const slider = document.getElementById('acres-slider');
  const stage = document.getElementById('stage-select');
  const loc = document.getElementById('location-input');
  const targetCropSelect = document.getElementById('target-crop-select');

  formData.append('field_acres', slider ? slider.value : '1.5');
  formData.append('crop_stage', stage ? stage.value : 'Vegetative Growth');
  formData.append('location', loc ? loc.value : 'Karnal, Haryana');
  formData.append('language', currentLanguage);
  formData.append('target_crop', targetCropSelect ? targetCropSelect.value : 'auto');

  try {
    const res = await fetch('/api/diagnose', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();

    if (!data.success) {
      alert('Diagnostic engine error: ' + (data.detail || 'Failed to analyze'));
      return;
    }

    playChime('success');

    // Populate images
    const orig = document.getElementById('preview-original');
    const clahe = document.getElementById('preview-clahe');
    const gradcam = document.getElementById('preview-gradcam');
    const under = document.getElementById('split-img-under');
    const over = document.getElementById('split-img-over');

    if (data.images.original) {
      if (orig) orig.src = data.images.original;
      if (under) under.src = data.images.original;
    }
    if (data.images.clahe && clahe) {
      clahe.src = data.images.clahe;
    }
    const diagBanner = document.getElementById('diagnosis-banner');
    const diagCrop = document.getElementById('diag-crop');
    const diagCond = document.getElementById('diag-condition');
    const diagAdvice = document.getElementById('diag-advice');
    const diagConf = document.getElementById('diag-conf-pct');
    const diagBadge = document.getElementById('diag-conf-badge');
    const isRejected = (data.is_leaf === false) || (data.confidence_level === 'Rejected');

    if (data.images && data.images.gradcam) {
      if (gradcam) gradcam.src = data.images.gradcam;
      if (over) over.src = data.images.gradcam;
    } else if (isRejected) {
      const oodSvg = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400"><rect width="400" height="400" fill="%230b130e"/><circle cx="200" cy="170" r="60" fill="%23450a0a" stroke="%23ef4444" stroke-width="4"/><line x1="160" y1="130" x2="240" y2="210" stroke="%23ef4444" stroke-width="6"/><text x="200" y="275" font-family="sans-serif" font-size="16" font-weight="bold" fill="%23fca5a5" text-anchor="middle">Non-Plant / OOD Subject</text><text x="200" y="305" font-family="sans-serif" font-size="12" fill="%2394a3b8" text-anchor="middle">No Plant Foliage Detected</text></svg>';
      if (gradcam) gradcam.src = oodSvg;
      if (over) over.src = oodSvg;
    }

    if (isRejected) {
      if (diagBanner) diagBanner.className = 'p-5 rounded-2xl bg-gradient-to-r from-rose-950/70 via-black/80 to-red-950/70 border border-rose-500/50 space-y-2';
      if (diagCrop) diagCrop.innerText = `Subject: ${data.crop || 'Non-Plant / Human Subject'}`;
      if (diagCond) diagCond.innerText = `🚫 ${data.disease || 'No Supported Crop Leaf Detected'}`;
      if (diagAdvice) diagAdvice.innerText = data.advisory_message;
      if (diagConf) diagConf.innerText = '0.0%';
      if (diagBadge) {
        diagBadge.className = 'text-xs px-2.5 py-1 rounded-full font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40';
        diagBadge.innerText = 'Rejected (Non-Crop / OOD)';
      }
      // Strictly hide lesion hotspots on non-leaf images (never show hotspots on human faces!)
      document.querySelectorAll('.lesion-hotspot').forEach(el => el.classList.add('hidden'));
      const hotspotLabel = document.querySelector('.scanner-overlay span.text-lime-400, .scanner-overlay span.text-rose-400');
      if (hotspotLabel) {
        hotspotLabel.innerText = '● 0 Hotspots';
        hotspotLabel.className = 'text-[10px] text-rose-400';
      }
      if (lesionTag) lesionTag.innerText = 'Necrotic Foliage: 0.0% (Non-Leaf)';
    } else {
      if (diagBanner) diagBanner.className = 'p-5 rounded-2xl bg-gradient-to-r from-emerald-950/70 to-zenze-card border border-lime-500/30';
      if (diagCrop) diagCrop.innerText = `Crop: ${data.crop}`;
      if (diagCond) diagCond.innerText = `${data.crop} — ${data.disease}`;
      if (diagAdvice) diagAdvice.innerText = data.advisory_message;
      if (diagConf) diagConf.innerText = `${data.confidence_percentage}%`;
      if (diagBadge) {
        diagBadge.className = 'text-xs px-2.5 py-1 rounded-full font-bold bg-lime-500/20 text-lime-300 border border-lime-500/40';
        diagBadge.innerText = `${data.confidence_level} Certainty`;
      }
      // Show lesion hotspots for valid leaves
      document.querySelectorAll('.lesion-hotspot').forEach(el => el.classList.remove('hidden'));
      const hotspotLabel = document.querySelector('.scanner-overlay span.text-rose-400, .scanner-overlay span.text-lime-400');
      if (hotspotLabel) {
        hotspotLabel.innerText = '● 2 Hotspots';
        hotspotLabel.className = 'text-[10px] text-lime-400';
      }
      if (lesionTag) lesionTag.innerText = `Necrotic Foliage: ${data.lesion_percentage}%`;
    }

    // Top-3 Distribution
    const top3Container = document.getElementById('top3-container');
    if (top3Container) {
      if (isRejected) {
        top3Container.innerHTML = `
          <div class="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs space-y-1">
            <div class="font-bold flex items-center gap-1.5"><i data-lucide="shield-alert" class="w-4 h-4"></i> Guardrail Triggered: Supported Crops Only</div>
            <p class="text-slate-300">${data.advisory_message || 'This image does not contain a close-up leaf of authorized project crops (Wheat, Rice, Cotton, Sugarcane, Mustard, Corn, Tomato, Potato, Pepper Bell, Apple). Disease diagnosis and chemical spray plans are halted to prevent misapplication.'}</p>
          </div>
        `;
        if (window.lucide) window.lucide.createIcons();
      } else if (data.top_predictions) {
        top3Container.innerHTML = '<div class="text-[11px] font-semibold text-slate-400 mb-1">Top-3 Predicted Conditions:</div>';
        data.top_predictions.forEach((p) => {
          top3Container.innerHTML += `
            <div class="space-y-1">
              <div class="flex justify-between text-[11px] text-slate-300">
                <span>${p.disease} (${p.crop})</span>
                <span class="font-bold text-white">${p.confidence_pct}</span>
              </div>
              <div class="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div class="h-full bg-lime-400 rounded-full" style="width: ${p.confidence * 100}%;"></div>
              </div>
            </div>
          `;
        });
      }
    }

    // Populate Dosage & Report
    latestRxData = data.prescription || {};
    latestDiagnosticData = data;
    populatePrintableReport(data);

    const chemReq = document.getElementById('chem-req-val');
    const orgReq = document.getElementById('organic-req-val');
    if (data.is_leaf === false) {
      if (chemReq) chemReq.innerText = '0 g (Disabled)';
      if (orgReq) orgReq.innerText = '0 ml (Disabled)';
    } else if (data.dosage_plan) {
      if (chemReq) chemReq.innerText = data.dosage_plan.chemical_required || 'N/A';
      if (orgReq) orgReq.innerText = data.dosage_plan.organic_required || 'N/A';
      updateDosageMath(parseFloat(slider ? slider.value : 1.5));
    }

    // Populate Digital IRRI Leaf Color Chart (LCC) Card
    const lccBadge = document.getElementById('lcc-panel-badge');
    const lccStatus = document.getElementById('lcc-status-val');
    const lccShade = document.getElementById('lcc-shade-val');
    const lccUrea = document.getElementById('lcc-urea-val');
    const lccAction = document.getElementById('lcc-action-val');
    const lccAdv = document.getElementById('lcc-advisory-text');

    if (data.is_leaf === false || !data.lcc) {
      if (lccBadge) {
        lccBadge.className = 'text-xs px-2.5 py-0.5 rounded-full bg-rose-500/20 text-rose-300 font-bold border border-rose-500/30';
        lccBadge.innerText = 'LCC Disabled (Non-Leaf)';
      }
      if (lccStatus) lccStatus.innerText = 'Non-Plant Subject';
      if (lccShade) lccShade.innerText = 'No chlorophyll detected';
      if (lccUrea) lccUrea.innerText = '0 kg / Acre (Disabled)';
      if (lccAction) lccAction.innerText = 'No fertilizer application';
      if (lccAdv) lccAdv.innerText = 'Digital LCC matching is strictly calibrated for genuine agricultural crop foliage.';
      for (let p = 1; p <= 5; p++) {
        const bar = document.getElementById(`lcc-bar-${p}`);
        if (bar) bar.className = 'h-9 rounded-lg flex items-center justify-center text-xs font-black text-white/50 transition-all opacity-40';
      }
    } else {
      const l = data.lcc;
      const isHi = (typeof currentLang !== 'undefined' && currentLang === 'hi');
      if (lccBadge) {
        lccBadge.className = 'text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30';
        lccBadge.innerText = `Panel ${l.panel}: ${isHi ? l.shade_name_hi : l.shade_name}`;
      }
      if (lccStatus) lccStatus.innerText = isHi ? l.nitrogen_status_hi : l.nitrogen_status;
      if (lccShade) lccShade.innerText = `${isHi ? l.shade_name_hi : l.shade_name} (${l.hex_color})`;
      if (lccUrea) {
        lccUrea.innerText = `${l.urea_recommendation_kg} kg / Acre`;
        lccUrea.className = l.urea_recommendation_kg > 0 
          ? 'text-lg font-black text-amber-400 mt-0.5' 
          : 'text-lg font-black text-lime-400 mt-0.5';
      }
      if (lccAction) lccAction.innerText = isHi ? l.action_hi : l.action;
      if (lccAdv) lccAdv.innerText = isHi ? l.advisory_hi : l.advisory;

      // Highlight active LCC Panel Bar
      for (let p = 1; p <= 5; p++) {
        const bar = document.getElementById(`lcc-bar-${p}`);
        if (bar) {
          if (p === l.panel) {
            bar.className = 'h-9 rounded-lg flex items-center justify-center text-xs font-black text-white transition-all ring-4 ring-white shadow-lg shadow-emerald-500/50 scale-105';
          } else {
            bar.className = 'h-9 rounded-lg flex items-center justify-center text-xs font-bold text-white/80 transition-all opacity-70';
          }
        }
      }
    }

    // Populate Climate Spray Card & Predictive Pathology (Pillar 1 & 2)
    const sprayBadge = document.getElementById('spray-verdict-badge');
    const sprayVerdictText = document.getElementById('spray-verdict-text');
    const sprayWindowTime = document.getElementById('spray-window-time');
    const outbreakRiskText = document.getElementById('outbreak-risk-text');
    const outbreakRiskBar = document.getElementById('outbreak-risk-bar');
    const rainGuardStatus = document.getElementById('rain-guard-status');
    const windDriftStatus = document.getElementById('wind-drift-status');
    const prevActionText = document.getElementById('preventive-action-text');

    if (data.is_leaf && data.spray_window && data.predictive_pathology) {
      const sw = data.spray_window;
      const pp = data.predictive_pathology;
      const isHi = (typeof currentLang !== 'undefined' && currentLang === 'hi');

      if (sprayBadge) {
        sprayBadge.innerText = isHi ? sw.verdict_hi : sw.verdict;
        sprayBadge.style.borderColor = sw.verdict_color;
        sprayBadge.style.color = sw.verdict_color;
      }
      if (sprayVerdictText) {
        sprayVerdictText.innerText = isHi ? sw.verdict_hi : sw.verdict;
        sprayVerdictText.style.color = sw.verdict_color;
      }
      if (sprayWindowTime) sprayWindowTime.innerText = isHi ? sw.recommended_window_hi : sw.recommended_window;

      if (outbreakRiskText) {
        outbreakRiskText.innerText = `${isHi ? pp.risk_tier_hi : pp.risk_tier} (${pp.outbreak_risk_pct}%)`;
        outbreakRiskText.style.color = pp.indicator_color;
      }
      if (outbreakRiskBar) {
        outbreakRiskBar.style.width = `${pp.outbreak_risk_pct}%`;
        outbreakRiskBar.style.backgroundColor = pp.indicator_color;
      }

      if (rainGuardStatus) {
        if (sw.rain_probability_pct >= 65) {
          rainGuardStatus.innerText = `⛔ Rain in ~${sw.hours_to_rain_estimate}h`;
          rainGuardStatus.className = 'font-bold text-rose-400';
        } else {
          rainGuardStatus.innerText = `Safe (${sw.rain_probability_pct}%)`;
          rainGuardStatus.className = 'font-bold text-emerald-400';
        }
      }

      if (windDriftStatus) {
        if (sw.wind_speed_kmh > 15.0) {
          windDriftStatus.innerText = `⚠️ ${sw.wind_speed_kmh} km/h (Drift Risk)`;
          windDriftStatus.className = 'font-bold text-amber-400';
        } else {
          windDriftStatus.innerText = `${sw.wind_speed_kmh} km/h (Safe)`;
          windDriftStatus.className = 'font-bold text-emerald-400';
        }
      }

      if (prevActionText) prevActionText.innerText = isHi ? pp.preventive_action_hi : pp.preventive_action;
    }

    // Populate Mandi (APMC) Market Intelligence & Farm Economics (Pillar 6)
    const mandiBadge = document.getElementById('mandi-trend-badge');
    const mandiLocalRate = document.getElementById('mandi-local-rate');
    const mandiLocalName = document.getElementById('mandi-local-name');
    const mandiBestRate = document.getElementById('mandi-best-rate');
    const mandiBestName = document.getElementById('mandi-best-name');
    const mandiNetProfit = document.getElementById('mandi-net-profit');
    const mandiRoi = document.getElementById('mandi-roi');
    const mandiTimingText = document.getElementById('mandi-timing-text');

    if (data.is_leaf && data.mandi_market) {
      const mm = data.mandi_market;
      const isHi = (typeof currentLang !== 'undefined' && currentLang === 'hi');

      if (mandiLocalRate) mandiLocalRate.innerText = `₹${mm.local_price_qtl.toLocaleString('en-IN')} / Qtl`;
      if (mandiLocalName) mandiLocalName.innerText = `${mm.local_mandi} • ₹${mm.local_price_kg}/kg`;
      if (mandiBestRate) mandiBestRate.innerText = `₹${mm.best_price_qtl.toLocaleString('en-IN')} / Qtl`;
      if (mandiBestName) mandiBestName.innerText = isHi ? mm.arbitrage_advice_hi : mm.arbitrage_advice;

      if (mandiNetProfit) mandiNetProfit.innerText = `₹${mm.economics.projected_net_profit_inr.toLocaleString('en-IN')}`;
      if (mandiRoi) mandiRoi.innerText = `${mm.acreage} Acres • ${mm.economics.roi_percentage}% Est. ROI`;
      if (mandiTimingText) mandiTimingText.innerText = isHi ? mm.market_timing_hi : mm.market_timing;
    }

    // Default Tab
    switchRxTab('bio');

    // Refresh history & stats
    initHistory();
    initStats();

  } catch (err) {
    console.error('Diagnosis request failed:', err);
  } finally {
    if (scanLine) scanLine.classList.add('hidden');
    if (runBtn) {
      runBtn.disabled = false;
      runBtn.innerHTML = `<i data-lucide="scan" class="w-5 h-5"></i><span>Execute Diagnostic Engine</span>`;
      if (window.lucide) window.lucide.createIcons();
    }
  }
}

function updateDosageMath(acres) {
  const waterLiters = (acres * 200.0).toFixed(1);
  const tanks = (waterLiters / 15.0).toFixed(1);
  const savings = Math.round(acres * 2260);

  const badge = document.getElementById('dosage-acres-badge');
  const vol = document.getElementById('water-volume-val');
  const count = document.getElementById('tanks-count-val');
  const sav = document.getElementById('savings-val');
  const fluid = document.getElementById('tank-fluid-level');
  const fillPct = document.getElementById('tank-fill-pct');

  if (badge) badge.innerText = `${acres} Acres`;
  if (vol) vol.innerText = `${waterLiters} L`;
  if (count) count.innerText = `${tanks} Tanks`;
  if (sav) sav.innerText = `₹${savings.toLocaleString()} Saved`;

  const pct = Math.min(95, Math.max(25, Math.round((acres / 5.0) * 80 + 15)));
  if (fluid) fluid.style.height = `${pct}%`;
  if (fillPct) fillPct.innerText = `${pct}% Capacity`;
}

function switchRxTab(tab) {
  playChime('click');
  const tabs = document.querySelectorAll('.rx-tab');
  tabs.forEach((t) => {
    t.className = 'rx-tab text-slate-400 hover:text-white pb-2';
  });

  const content = document.getElementById('rx-content');
  if (!content) return;
  content.innerHTML = '';

  if (latestDiagnosticData && latestDiagnosticData.is_leaf === false) {
    if (tab === 'bio') {
      if (tabs[0]) tabs[0].className = 'rx-tab text-amber-400 border-b-2 border-amber-400 pb-2';
      content.innerHTML = '<p class="text-amber-300 font-medium">⚠️ Biological controls are not applicable for non-plant or human subjects. Please upload an agricultural crop leaf photo.</p>';
    } else if (tab === 'chem') {
      if (tabs[1]) tabs[1].className = 'rx-tab text-rose-400 border-b-2 border-rose-400 pb-2';
      content.innerHTML = '<div class="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 space-y-1"><p class="font-bold">🛑 Chemical Treatments Strictly Disabled</p><p class="text-xs text-slate-300">Never spray agricultural fungicides or pesticides on humans, animals, or non-plant objects. Treatment formulations are strictly locked until a valid crop leaf is scanned.</p></div>';
    } else if (tab === 'prev') {
      if (tabs[2]) tabs[2].className = 'rx-tab text-lime-400 border-b-2 border-lime-400 pb-2';
      content.innerHTML = '<div class="text-slate-300 space-y-1.5 text-xs"><p>&bull; <strong>Photograph Affected Leaves:</strong> Capture close-up, sharp photos under natural daylight.</p><p>&bull; <strong>Proper Framing:</strong> Ensure the plant leaf occupies at least 25% of the camera frame.</p><p>&bull; <strong>Supported Crops:</strong> Tomato, Potato, Bell Pepper, Apple, Corn.</p></div>';
    } else if (tab === 'hindi') {
      if (tabs[3]) tabs[3].className = 'rx-tab text-rose-400 border-b-2 border-rose-400 pb-2';
      content.innerHTML = '<p class="text-rose-300 font-medium">🛑 गैर-पौधा चेतावनी: छवि में पौधे की पत्ती नहीं पाई गई (मानव या गैर-पौधा वस्तु)। किसी भी गैर-पौधे पर रासायनिक कीटनाशकों का छिड़काव न करें। कृपया फसल की पत्ती की स्पष्ट तस्वीर अपलोड करें।</p>';
    }
    return;
  }

  const currCrop = (latestDiagnosticData && latestDiagnosticData.crop) ? latestDiagnosticData.crop.toLowerCase() : 'crop';
  const isHealthy = (latestDiagnosticData && (latestDiagnosticData.is_healthy || (latestDiagnosticData.disease && latestDiagnosticData.disease.toLowerCase().includes('healthy'))));

  if (tab === 'bio') {
    if (tabs[0]) tabs[0].className = 'rx-tab text-lime-400 border-b-2 border-lime-400 pb-2';
    let defaultBio = [
      'Prune lower chlorotic foliage to prevent upward spore splash.',
      'Apply cold-pressed organic Neem oil solution (5 ml/L) mixed with mild surfactant.'
    ];
    if (currCrop.includes('wheat')) {
      defaultBio = [
        'Bio-agent formulation: Spray Trichoderma harzianum or Pseudomonas fluorescens @ 5 g/L at vegetative onset.',
        'Avoid excessive nitrogen fertilization to decrease foliar susceptibility to stripe rust.'
      ];
    } else if (currCrop.includes('rice')) {
      defaultBio = [
        'Apply Pseudomonas fluorescens (biocontrol agent) @ 10 g/kg seed and foliar spray at tillering.',
        'Regulate field water drainage to inhibit bacterial spread.'
      ];
    } else if (currCrop.includes('cotton')) {
      defaultBio = [
        'Conserve predatory beneficial insects (ladybird beetles, chrysoperla) for whitefly control.',
        'Spray 5% NSKE (Neem Seed Kernel Extract) at 15-day intervals.'
      ];
    }
    const items = (latestRxData.biological_controls && latestRxData.biological_controls.length) ? latestRxData.biological_controls : defaultBio;
    items.forEach((item) => (content.innerHTML += `<p>&bull; ${item}</p>`));
  } else if (tab === 'chem') {
    if (tabs[1]) tabs[1].className = 'rx-tab text-lime-400 border-b-2 border-lime-400 pb-2';
    let defaultChem = [
      'Spray Mancozeb 75% WP @ 2.5 g/L of water at initial symptom manifestation.',
      'Rotate with Azoxystrobin 23% SC (1 ml/L) to manage FRAC fungicide resistance.'
    ];
    if (isHealthy) {
      defaultChem = [
        '✅ No synthetic fungicide spray required (Crop foliage is healthy).',
        'Maintain balanced NPK fertilization and periodic field scouting.'
      ];
    } else if (currCrop.includes('wheat')) {
      defaultChem = [
        'First Line Defense (CCS HAU & ICAR): Propiconazole 25% EC (Tilt / Bumper) @ 200 ml per acre in 200 Liters of water (1.0 ml/L).',
        'Alternative Triazole: Tebuconazole 250 EC (Folicur) @ 200 ml/acre in 200 L water.',
        'Repeat spray after 15 days if cloudy/foggy weather persists and yellow pustules expand.'
      ];
    } else if (currCrop.includes('rice')) {
      defaultChem = [
        'Spray Streptocycline 90% (15-20 g) + Copper Oxychloride 50% WP (500 g) in 200 L water per acre.',
        'Avoid urea top-dressing during active leaf blight lesions.'
      ];
    } else if (currCrop.includes('cotton')) {
      defaultChem = [
        'Spray Copper Oxychloride 50% WP (500 g) + Streptocycline (15 g) in 200 L water per acre for bacterial leaf spots.',
        'For sucking pests: Flonicamid 50 WG @ 60 g/acre or Dinotefuran 20% SG @ 60 g/acre.'
      ];
    }
    const items = (latestRxData.chemical_controls && latestRxData.chemical_controls.length) ? latestRxData.chemical_controls : defaultChem;
    items.forEach((item) => (content.innerHTML += `<p>&bull; ${item}</p>`));
  } else if (tab === 'prev') {
    if (tabs[2]) tabs[2].className = 'rx-tab text-lime-400 border-b-2 border-lime-400 pb-2';
    let defaultPrev = [
      'Enforce crop rotation with non-host botanical families.',
      'Disinfect field tools and pruning shears with 10% sodium hypochlorite solution.'
    ];
    if (currCrop.includes('wheat')) {
      defaultPrev = [
        'Sow stripe-rust resistant wheat varieties recommended for Haryana: HD-3086 (Pusa Gautami), HD-3226, WH-1105, DBW-187.',
        'Avoid excessive nitrogen fertilization (keep Urea within 110-120 kg/acre split into 3 doses).',
        'Complete timely Rabi sowing between 25th October and 15th November.'
      ];
    } else if (currCrop.includes('rice')) {
      defaultPrev = [
        'Cultivate BLB-resistant varieties: Pusa Basmati 1718, PB 1885, PB 1886.',
        'Avoid deep standing water (keep 2-3 cm intermittent wetting and drying).'
      ];
    }
    const items = (latestRxData.cultural_prevention && latestRxData.cultural_prevention.length) ? latestRxData.cultural_prevention : defaultPrev;
    items.forEach((item) => (content.innerHTML += `<p>&bull; ${item}</p>`));
  } else if (tab === 'hindi') {
    if (tabs[3]) tabs[3].className = 'rx-tab text-lime-400 border-b-2 border-lime-400 pb-2';
    let defaultHi = latestRxData.hindi_summary;
    if (!defaultHi) {
      if (currCrop.includes('wheat')) {
        defaultHi = 'गेहूं परामर्श (CCS HAU हिसार): पीले रतुआ की रोकथाम के लिए प्रोपिकोनाजोल 25% ईसी (टिल्ट) @ 200 मिली को 200 लीटर पानी में मिलाकर प्रति एकड़ छिड़कें। 15 दिन बाद आवश्यकता पड़ने पर दोहराएं।';
      } else if (currCrop.includes('rice')) {
        defaultHi = 'धान परामर्श (HAU हिसार): पत्ती झुलसा रोग हेतु 500 ग्राम कॉपर ऑक्सीक्लोराइड + 15 ग्राम स्ट्रेप्टोसाइक्लिन को 200 लीटर पानी में घोलकर प्रति एकड़ छिड़काव करें।';
      } else {
        defaultHi = 'कृषि परामर्श तैयार है। अनुशंसित मात्रा में जैविक व रासायनिक छिड़काव करें तथा मौसम के अनुसार स्प्रे का समय चुनें।';
      }
    }
    content.innerHTML = `<p class="text-lime-300 font-medium">${defaultHi.replace(/\n/g, '<br>')}</p>`;
  }
}

// ============================================================================
// 6. Text-To-Speech (Native Web Speech Synthesis)
// ============================================================================
function readAloudPrescription() {
  if (!('speechSynthesis' in window)) {
    alert('Voice readout is not supported in this browser.');
    return;
  }
  window.speechSynthesis.cancel();

  const cond = document.getElementById('diag-condition');
  const advice = document.getElementById('diag-advice');
  let text = `${cond ? cond.innerText : 'Crop diagnosis'}. ${advice ? advice.innerText : 'Consult recommendation.'}`;

  if (latestDiagnosticData && latestDiagnosticData.is_leaf === false) {
    text = (currentLanguage === 'hi') 
      ? 'सावधान: पहचानी गई तस्वीर पौधे की पत्ती की नहीं है। किसी इंसान या गैर-पौधे पर कोई कृषि कीटनाशक या रासायनिक छिड़काव न करें।'
      : 'Alert: Input image is rejected as a non-plant subject or human. Chemical and biological pesticide application is strictly halted.';
  } else if (currentLanguage === 'hi' && latestRxData.hindi_summary) {
    text = latestRxData.hindi_summary;
  }

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = currentLanguage === 'hi' ? 'hi-IN' : 'en-US';
  utterance.rate = 0.95;

  const btnLabel = document.getElementById('tts-btn-label');
  if (btnLabel) btnLabel.innerText = 'Speaking... 🔊';
  utterance.onend = () => {
    if (btnLabel) btnLabel.innerText = 'Listen to Prescription / परामर्श सुनें 🔊';
  };
  window.speechSynthesis.speak(utterance);
}

// ============================================================================
// 7. Interactive Hotspot & Mathematical Layer Popovers
// ============================================================================
function showHotspotInfo(title, desc) {
  playChime('click');
  const popup = document.getElementById('hotspot-popup');
  const hTitle = document.getElementById('hotspot-title');
  const hDesc = document.getElementById('hotspot-desc');
  if (hTitle) hTitle.innerText = title;
  if (hDesc) hDesc.innerText = desc;
  if (popup) popup.classList.remove('hidden');
}

function showLayerMath(title, math) {
  playChime('click');
  const box = document.getElementById('layer-math-box');
  const mTitle = document.getElementById('layer-math-title');
  const mContent = document.getElementById('layer-math-content');
  if (mTitle) mTitle.innerText = title;
  if (mContent) mContent.innerText = math;
  if (box) box.classList.remove('hidden');
}

// ============================================================================
// 8. Stats & History
// ============================================================================
async function initStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();

    const totalEl = document.getElementById('stat-total-scans');
    const rateEl = document.getElementById('stat-health-rate');

    if (totalEl) totalEl.innerText = data.total_scans || '28';
    const total = data.total_scans || 28;
    const healthy = data.healthy_count || 18;
    const rate = Math.round((healthy / total) * 100);
    if (rateEl) rateEl.innerText = `${rate}%`;

    // Render Chart.js
    const canvas = document.getElementById('health-chart');
    if (!canvas || !window.Chart) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    if (healthChart) healthChart.destroy();

    healthChart = new window.Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Healthy Leaves', 'Early Blight', 'Late Blight', 'Other Pathogens'],
        datasets: [{
          label: 'Scan Incidents',
          data: [healthy, 6, 4, Math.max(0, total - healthy - 10)],
          backgroundColor: ['#84cc16', '#f59e0b', '#ef4444', '#8b5cf6'],
          borderRadius: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { display: false } },
          y: { ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.05)' } }
        }
      }
    });

  } catch (err) {
    console.error('Stats load error:', err);
  }
}

async function initHistory() {
  try {
    const res = await fetch('/api/history?limit=10');
    const data = await res.json();
    const tbody = document.getElementById('history-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (!data.history || !data.history.length) {
      tbody.innerHTML = '<tr><td colspan="7" class="p-4 text-center text-slate-500">No previous scan records found in SQLite database.</td></tr>';
      return;
    }

    data.history.forEach((row) => {
      const confPct = (parseFloat(row.confidence) * 100).toFixed(1);
      const isHealthy = row.disease && row.disease.toLowerCase().includes('healthy');
      tbody.innerHTML += `
        <tr class="hover:bg-white/[0.02] transition-colors">
          <td class="p-3 font-mono font-bold text-lime-400">#${row.prediction_id}</td>
          <td class="p-3 text-slate-400">${row.timestamp || 'Recent'}</td>
          <td class="p-3 font-semibold text-white">${row.crop}</td>
          <td class="p-3">
            <span class="px-2 py-0.5 rounded text-[10px] font-bold ${isHealthy ? 'bg-emerald-500/20 text-emerald-300' : 'bg-red-500/20 text-red-300'}">
              ${row.disease}
            </span>
          </td>
          <td class="p-3 font-bold text-lime-400">${confPct}%</td>
          <td class="p-3 text-slate-400">${row.crop_stage || 'Vegetative'}</td>
          <td class="p-3 text-slate-300 truncate max-w-xs">${row.recommendation || 'Grounded advisory ready.'}</td>
        </tr>
      `;
    });

  } catch (err) {
    console.error('History load error:', err);
  }
}

function loadHistory() {
  initHistory();
}

// ============================================================================
// 9. Floating Farmer Advisory Chatbot
// ============================================================================
function toggleChatDrawer() {
  playChime('click');
  const drawer = document.getElementById('chat-drawer');
  if (drawer) drawer.classList.toggle('hidden');
}

async function submitChat(e) {
  if (e) e.preventDefault();
  const input = document.getElementById('chat-input');
  if (!input) return;
  const msg = input.value.trim();
  if (!msg) return;

  playChime('click');
  appendChatMessage('user', msg);
  input.value = '';

  try {
    const formData = new FormData();
    formData.append('message', msg);
    formData.append('language', currentLanguage);

    const res = await fetch('/api/chat', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    playChime('success');
    appendChatMessage('assistant', data.content);
  } catch (err) {
    appendChatMessage('assistant', 'Error communicating with agricultural knowledge base.');
  }
}

function sendQuickChat(query) {
  const drawer = document.getElementById('chat-drawer');
  if (drawer && drawer.classList.contains('hidden')) {
    drawer.classList.remove('hidden');
  }
  const input = document.getElementById('chat-input');
  if (input) input.value = query;
  submitChat();
}

function appendChatMessage(role, text) {
  const stream = document.getElementById('chat-messages');
  if (!stream) return;
  const isUser = role === 'user';
  const bubble = document.createElement('div');
  bubble.className = `p-3 rounded-xl ${isUser ? 'bg-lime-500/20 text-lime-200 border border-lime-500/30 ml-8' : 'bg-white/5 text-slate-200 border border-white/10 mr-8'} leading-relaxed`;
  bubble.innerHTML = text.replace(/\n/g, '<br>');
  stream.appendChild(bubble);
  stream.scrollTop = stream.scrollHeight;
}

function toggleLanguage() {
  playChime('click');
  currentLanguage = currentLanguage === 'en' ? 'hi' : 'en';
  const label = document.getElementById('lang-label');
  if (label) {
    label.innerText = currentLanguage === 'en' ? 'English / हिंदी' : 'हिंदी (Hindi Active)';
  }
}

// ============================================================================
// 12. Executive Clinical Lab Report & PDF Print System
// ============================================================================
function populatePrintableReport(data = null) {
  const d = data || latestDiagnosticData;
  const now = new Date();
  const dateStr = now.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }) + ' • ' + now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) + ' IST';
  
  const repDate = document.getElementById('rep-date');
  if (repDate) repDate.innerText = dateStr;

  const repId = document.getElementById('rep-id');
  if (repId) {
    const idVal = d && d.prediction_id ? `AGV-LAB-2026-${String(d.prediction_id).padStart(4, '0')}` : `AGV-LAB-2026-${Math.floor(1000 + Math.random() * 9000)}`;
    repId.innerText = idVal;
  }

  const slider = document.getElementById('acres-slider');
  const stage = document.getElementById('stage-select');
  const loc = document.getElementById('location-input');

  const acresVal = slider ? `${slider.value} Acres` : '1.5 Acres';
  const stageVal = stage ? stage.value : 'Vegetative Growth';
  const locVal = loc && loc.value ? loc.value : 'Karnal, Haryana';

  const repCrop = document.getElementById('rep-crop');
  const repLocation = document.getElementById('rep-location');
  const repAcres = document.getElementById('rep-acres');
  const repStage = document.getElementById('rep-stage');

  const cropBotanicalMap = {
    'Wheat': 'Triticum aestivum',
    'Rice': 'Oryza sativa',
    'Cotton': 'Gossypium hirsutum',
    'Sugarcane': 'Saccharum officinarum',
    'Corn': 'Zea mays',
    'Tomato': 'Solanum lycopersicum',
    'Potato': 'Solanum tuberosum',
    'Pepper Bell': 'Capsicum annuum',
    'Apple': 'Malus domestica',
    'Mustard': 'Brassica juncea'
  };
  const sciName = (d && d.crop && cropBotanicalMap[d.crop]) ? cropBotanicalMap[d.crop] : 'Agronomic Cultivar';
  if (repCrop) repCrop.innerText = d && d.crop ? `${d.crop} (${sciName})` : 'Tomato (Solanum lycopersicum)';
  if (repLocation) repLocation.innerText = locVal;
  if (repAcres) repAcres.innerText = acresVal;
  if (repStage) repStage.innerText = stageVal;

  // Images
  const orig = document.getElementById('preview-original');
  const clahe = document.getElementById('preview-clahe');
  const gradcam = document.getElementById('preview-gradcam');

  const repImgOrig = document.getElementById('rep-img-original');
  const repImgClahe = document.getElementById('rep-img-clahe');
  const repImgGrad = document.getElementById('rep-img-gradcam');

  if (repImgOrig && orig && orig.src) repImgOrig.src = orig.src;
  if (repImgClahe && clahe && clahe.src) repImgClahe.src = clahe.src;
  if (repImgGrad && gradcam && gradcam.src) repImgGrad.src = gradcam.src;

  const lesionTag = document.getElementById('lesion-tag');
  const repLesion = document.getElementById('rep-lesion-badge');
  if (repLesion && lesionTag) repLesion.innerText = lesionTag.innerText;

  // Diagnosis
  const repCond = document.getElementById('rep-condition');
  const repPathogen = document.getElementById('rep-pathogen-info');
  const repDesc = document.getElementById('rep-summary-text');
  const repConf = document.getElementById('rep-conf-val');
  const repCert = document.getElementById('rep-certainty-badge');

  if (d && d.crop && d.disease) {
    if (repCond) repCond.innerText = `${d.crop} — ${d.disease}`;
    if (repDesc) repDesc.innerText = d.advisory_message || 'Pathological verification confirmed via deep neural network feature activations.';
    if (repConf) repConf.innerText = `${d.confidence_percentage}%`;
    if (repCert) repCert.innerText = `${(d.confidence_level || 'HIGH').toUpperCase()} CERTAINTY`;

    // Pathogen details
    let pathName = 'Pathogen: Foliar Plant Pathogen';
    if (d.disease.includes('Stripe Rust') || d.disease.includes('Yellow Rust')) pathName = 'Pathogen: Puccinia striiformis f. sp. tritici (Fungus) • Severity: High';
    else if (d.disease.includes('Leaf Rust') || d.disease.includes('Brown Rust')) pathName = 'Pathogen: Puccinia triticina (Fungus) • Severity: Moderate to High';
    else if (d.disease.includes('Stem Rust') || d.disease.includes('Black Rust')) pathName = 'Pathogen: Puccinia graminis f. sp. tritici (Fungus) • Severity: Critical';
    else if (d.crop === 'Rice' && d.disease.includes('Bacterial')) pathName = 'Pathogen: Xanthomonas oryzae pv. oryzae (Bacterium) • Severity: High';
    else if (d.crop === 'Rice' && d.disease.includes('Brown Spot')) pathName = 'Pathogen: Bipolaris oryzae (Fungus) • Severity: Moderate';
    else if (d.crop === 'Rice' && d.disease.includes('Smut')) pathName = 'Pathogen: Entyloma oryzae (Fungus) • Severity: Moderate';
    else if (d.crop === 'Cotton' && d.disease.includes('Diseased')) pathName = 'Pathogen: Xanthomonas citri pv. malvacearum / Foliar Complex • Severity: High';
    else if (d.crop === 'Sugarcane' && d.disease.includes('Red Rot')) pathName = 'Pathogen: Colletotrichum falcatum (Fungus) • Severity: Critical';
    else if (d.crop === 'Sugarcane' && d.disease.includes('Rust')) pathName = 'Pathogen: Puccinia melanocephala (Fungus) • Severity: Moderate';
    else if (d.crop === 'Sugarcane' && d.disease.includes('Yellow')) pathName = 'Pathogen: Sugarcane Yellow Leaf Luteovirus • Severity: High';
    else if (d.disease.includes('Late Blight')) pathName = 'Pathogen: Phytophthora infestans (Oomycete Water Mold) • Severity: Critical';
    else if (d.disease.includes('Early Blight')) pathName = 'Pathogen: Alternaria solani (Fungus) • Severity: Moderate to High';
    else if (d.disease.includes('Bacterial')) pathName = 'Pathogen: Xanthomonas campestris (Bacterium) • Severity: Severe';
    else if (d.disease.includes('Septoria')) pathName = 'Pathogen: Septoria lycopersici (Fungus) • Severity: Moderate';
    else if (d.disease.includes('Leaf Mold')) pathName = 'Pathogen: Passalora fulva (Fungus) • Severity: Moderate';
    else if (d.disease.includes('Spider')) pathName = 'Pathogen: Tetranychus urticae (Acarina / Pest) • Severity: Moderate';
    else if (d.disease.includes('Yellow Leaf Curl')) pathName = 'Pathogen: Tomato Yellow Leaf Curl Begomovirus • Severity: High';
    else if (d.disease.includes('Healthy')) pathName = 'Specimen Condition: Healthy Foliage • No Pathogen Detected';
    if (repPathogen) repPathogen.innerText = pathName;
  }

  // Top 3
  const repTop3 = document.getElementById('rep-top3-list');
  if (repTop3 && d && d.top_predictions) {
    repTop3.innerHTML = '';
    d.top_predictions.forEach((p, idx) => {
      repTop3.innerHTML += `
        <div class="diff-item">
          <span class="diff-name">${idx + 1}. ${p.disease} (${p.crop})</span>
          <div class="diff-bar-wrap"><div class="diff-bar" style="width: ${p.confidence * 100}%;"></div></div>
          <span class="diff-score">${p.confidence_pct}</span>
        </div>
      `;
    });
  }

  // Weather
  const repTemp = document.getElementById('rep-temp');
  const repRh = document.getElementById('rep-rh');
  const repRain = document.getElementById('rep-rain');
  const repSpore = document.getElementById('rep-spore-risk');
  const repWeatherAdvice = document.getElementById('rep-weather-advice');

  if (d && d.weather) {
    if (repTemp) repTemp.innerText = `${d.weather.temperature_c}°C`;
    if (repRh) repRh.innerText = `${d.weather.humidity_pct}%`;
    if (repRain) repRain.innerText = `${d.weather.rain_probability_pct}%`;
    if (repSpore) repSpore.innerText = `${d.weather.spore_germination_risk} Risk`;
    if (repWeatherAdvice) repWeatherAdvice.innerText = `${d.weather.agronomic_advice} ${d.weather.spray_recommendation}`;
  }

  // Dosage table
  const acresNum = slider ? parseFloat(slider.value) : 1.5;
  const waterL = (acresNum * 200.0).toFixed(1);
  const tanksNum = (waterL / 15.0).toFixed(1);
  const savingsNum = Math.round(acresNum * 2260);

  const repDoseAcres = document.getElementById('rep-dose-acres');
  const repDoseWater = document.getElementById('rep-dose-water');
  const repDoseTanks = document.getElementById('rep-dose-tanks');
  const repDoseChem = document.getElementById('rep-dose-chem');
  const repDoseOrg = document.getElementById('rep-dose-org');
  const repDoseSavings = document.getElementById('rep-dose-savings');

  if (repDoseAcres) repDoseAcres.innerText = `${acresNum} Acres`;
  if (repDoseWater) repDoseWater.innerText = `${waterL} Liters`;
  if (repDoseTanks) repDoseTanks.innerText = `${tanksNum} Tanks`;
  if (repDoseChem) repDoseChem.innerText = (d && d.dosage_plan && d.dosage_plan.chemical_required) || `${Math.round(acresNum * 500)} g Mancozeb 75% WP`;
  if (repDoseOrg) repDoseOrg.innerText = (d && d.dosage_plan && d.dosage_plan.organic_required) || `${(acresNum * 1.0).toFixed(1)} L Neem Oil 10,000 ppm`;
  if (repDoseSavings) repDoseSavings.innerText = `₹${savingsNum.toLocaleString()} Saved`;

  // Prescriptions
  const rx = (d && d.prescription) || latestRxData;
  const repBio = document.getElementById('rep-rx-bio');
  const repChem = document.getElementById('rep-rx-chem');
  const repCult = document.getElementById('rep-rx-cult');
  const repHindi = document.getElementById('rep-hindi-text');

  if (rx) {
    if (repBio && rx.biological_controls && rx.biological_controls.length > 0) {
      repBio.innerHTML = rx.biological_controls.map(b => `<li>${b}</li>`).join('');
    }
    if (repChem && rx.chemical_controls && rx.chemical_controls.length > 0) {
      repChem.innerHTML = rx.chemical_controls.map(c => `<li>${c}</li>`).join('');
    }
    if (repCult && rx.cultural_prevention && rx.cultural_prevention.length > 0) {
      repCult.innerHTML = rx.cultural_prevention.map(cp => `<li>${cp}</li>`).join('');
    }
    if (repHindi && rx.hindi_summary) {
      repHindi.innerText = rx.hindi_summary;
    }
  }

  // Unique Hash
  const repHash = document.getElementById('rep-hash');
  if (repHash) {
    repHash.innerText = (Math.random().toString(36).substring(2, 10) + Math.random().toString(36).substring(2, 8)).toUpperCase();
  }
}

function printLabReport() {
  playChime('click');
  populatePrintableReport();
  window.print();
}

function openReportModal() {
  playChime('click');
  populatePrintableReport();
  const reportElement = document.getElementById('printable-lab-report');
  const modalBody = document.getElementById('report-modal-body');
  const backdrop = document.getElementById('report-modal-backdrop');

  if (reportElement && modalBody && backdrop) {
    modalBody.innerHTML = reportElement.innerHTML;
    backdrop.classList.remove('hidden');
    backdrop.classList.add('flex');
    if (window.lucide) window.lucide.createIcons();
  }
}

function closeReportModal() {
  playChime('click');
  const backdrop = document.getElementById('report-modal-backdrop');
  if (backdrop) {
    backdrop.classList.remove('flex');
    backdrop.classList.add('hidden');
  }
}

// ============================================================================
// 13. PWA (Progressive Web App) Service Worker & Installation Engine
// ============================================================================
let deferredInstallPrompt = null;

function initPWA() {
  // 1. Register Service Worker with Root Scope
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/service-worker.js', { scope: '/' })
        .then((reg) => {
          console.log('[AgriVision PWA] Service Worker registered successfully! Scope:', reg.scope);
        })
        .catch((err) => {
          console.warn('[AgriVision PWA] Service Worker registration note:', err);
        });
    });
  }

  // 2. Intercept Native Installation Prompt
  const installBtn = document.getElementById('pwa-install-btn');
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredInstallPrompt = e;
    console.log('[AgriVision PWA] App is installable. Displaying Install button.');
    if (installBtn) {
      installBtn.classList.remove('hidden');
      installBtn.classList.add('flex');
      if (window.lucide) window.lucide.createIcons();
    }
  });

  // 3. User Click Handler for Install Button
  if (installBtn) {
    // If on mobile browser where prompt event might not fire immediately, still enable install guidance
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    if (isMobile && !window.matchMedia('(display-mode: standalone)').matches) {
      installBtn.classList.remove('hidden');
      installBtn.classList.add('flex');
      if (window.lucide) window.lucide.createIcons();
    }

    installBtn.addEventListener('click', async () => {
      playChime('click');
      if (deferredInstallPrompt) {
        deferredInstallPrompt.prompt();
        const { outcome } = await deferredInstallPrompt.userChoice;
        console.log(`[AgriVision PWA] User install choice: ${outcome}`);
        deferredInstallPrompt = null;
        installBtn.classList.remove('flex');
        installBtn.classList.add('hidden');
      } else {
        // Platform specific instructions
        const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
        if (isIOS) {
          alert('📲 To install AgriVision on iOS: Tap the Safari Share button (box with arrow) at the bottom, then tap "Add to Home Screen".');
        } else {
          alert('📲 To install AgriVision on Android: Tap the 3 dots menu in Chrome, then tap "Install App" or "Add to Home screen".');
        }
      }
    });
  }

  // 4. Listen for Successful Installation
  window.addEventListener('appinstalled', () => {
    console.log('[AgriVision PWA] AgriVision Agent successfully installed as a native app!');
    if (installBtn) {
      installBtn.classList.remove('flex');
      installBtn.classList.add('hidden');
    }
  });
}

// ============================================================================
// 14. Pillar 5: Voice-First Vernacular Indian Speech Recognition Engine
// ============================================================================
let speechRecognitionInstance = null;
let isRecognizingSpeech = false;

function toggleSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const micBtn = document.getElementById('voice-input-btn');
  const chatInput = document.getElementById('chat-input');

  if (!SpeechRecognition) {
    alert('🎙️ Browser Notice: Web Speech Recognition is supported on Google Chrome, Microsoft Edge, and modern Android browsers. Please type your query in Hindi or English.');
    return;
  }

  if (isRecognizingSpeech && speechRecognitionInstance) {
    speechRecognitionInstance.stop();
    return;
  }

  try {
    speechRecognitionInstance = new SpeechRecognition();
    speechRecognitionInstance.continuous = false;
    speechRecognitionInstance.interimResults = true;
    speechRecognitionInstance.lang = (typeof currentLang !== 'undefined' && currentLang === 'hi') ? 'hi-IN' : 'en-IN';

    speechRecognitionInstance.onstart = () => {
      isRecognizingSpeech = true;
      if (micBtn) {
        micBtn.className = 'w-9 h-9 rounded-xl bg-rose-500/30 text-rose-300 border border-rose-500/50 flex items-center justify-center shrink-0 ring-2 ring-rose-400';
      }
      if (chatInput) {
        chatInput.placeholder = (typeof currentLang !== 'undefined' && currentLang === 'hi') ? 'सुन रहा हूँ... बोलिए...' : 'Listening... Speak your question...';
      }
    };

    speechRecognitionInstance.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        transcript += event.results[i][0].transcript;
      }
      if (chatInput) {
        chatInput.value = transcript;
      }
    };

    speechRecognitionInstance.onerror = (event) => {
      console.warn('[AgriVision Voice] Speech recognition event:', event.error);
    };

    speechRecognitionInstance.onend = () => {
      isRecognizingSpeech = false;
      if (micBtn) {
        micBtn.className = 'w-9 h-9 rounded-xl bg-white/10 hover:bg-lime-500/20 text-lime-400 border border-white/10 flex items-center justify-center shrink-0 transition-all';
      }
      if (chatInput) {
        chatInput.placeholder = (typeof currentLang !== 'undefined' && currentLang === 'hi') ? 'सवाल लिखें या बोलें (हिंदी / English)...' : 'Type question (English or हिंदी)...';
      }
    };

    speechRecognitionInstance.start();
  } catch (err) {
    console.error('Failed to start speech recognition:', err);
    isRecognizingSpeech = false;
  }
}

// ============================================================================
// 12. Haryana Regional Agronomy & Offline Block Advisor
// ============================================================================
let haryanaBlocksData = (typeof window !== 'undefined' && window.DEFAULT_HARYANA_BLOCKS) ? window.DEFAULT_HARYANA_BLOCKS : [];

async function initHaryanaBlockAdvisor() {
  const districtSelect = document.getElementById('haryana-district-select');
  const blockSelect = document.getElementById('haryana-block-select');
  if (!districtSelect || !blockSelect) return;

  if (!haryanaBlocksData || haryanaBlocksData.length === 0) {
    if (window.DEFAULT_HARYANA_BLOCKS && window.DEFAULT_HARYANA_BLOCKS.length > 0) {
      haryanaBlocksData = window.DEFAULT_HARYANA_BLOCKS;
    }
  }

  function populateDistrictsDropdown() {
    if (!haryanaBlocksData || haryanaBlocksData.length === 0) return;
    const districts = [...new Set(haryanaBlocksData.map(b => b.district))].sort();
    if (districts.length === 0) return;

    if (districtSelect.options.length < 22) {
      const currentVal = districtSelect.value || 'Karnal';
      districtSelect.innerHTML = '';
      districts.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d;
        opt.textContent = d;
        opt.style.backgroundColor = '#111e16';
        opt.style.color = '#ffffff';
        if (d.toLowerCase() === currentVal.toLowerCase()) opt.selected = true;
        districtSelect.appendChild(opt);
      });
    }
  }

  function updateBlocksForDistrict(districtName) {
    if (!haryanaBlocksData || haryanaBlocksData.length === 0) return;
    const filteredBlocks = haryanaBlocksData.filter(b => b.district.toLowerCase() === districtName.toLowerCase());
    blockSelect.innerHTML = '';
    filteredBlocks.forEach((b, idx) => {
      const opt = document.createElement('option');
      opt.value = b.block_name;
      opt.textContent = b.block_name;
      opt.style.backgroundColor = '#111e16';
      opt.style.color = '#ffffff';
      if (idx === 0) opt.selected = true;
      blockSelect.appendChild(opt);
    });
    if (filteredBlocks.length > 0) {
      renderBlockDetails(filteredBlocks[0]);
    }
  }

  function renderBlockDetails(block) {
    if (!block) return;

    // 1. Dialect
    const dialectText = document.getElementById('haryana-dialect-text');
    if (dialectText) {
      dialectText.textContent = block.primary_dialect || 'Bangru / Khadar Haryanvi';
    }

    // 2. Primary Crops
    const cropsContainer = document.getElementById('haryana-crops-container');
    if (cropsContainer) {
      cropsContainer.innerHTML = '';
      (block.primary_crops || []).forEach(crop => {
        const pill = document.createElement('span');
        pill.className = 'px-2.5 py-1 rounded-lg bg-lime-500/15 border border-lime-500/30 text-lime-300 text-xs font-semibold flex items-center gap-1';
        pill.innerHTML = `<span>🌾</span> <span>${crop}</span>`;
        cropsContainer.appendChild(pill);
      });
    }

    // 3. Top Diseases
    const diseasesContainer = document.getElementById('haryana-diseases-container');
    if (diseasesContainer) {
      diseasesContainer.innerHTML = '';
      (block.top_3_diseases || []).forEach(dis => {
        const card = document.createElement('div');
        card.className = 'p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-200 text-xs flex items-center gap-2';
        card.innerHTML = `<span class="text-amber-400">⚠️</span> <span>${dis}</span>`;
        diseasesContainer.appendChild(card);
      });
    }

    // 4. Symptom Checklist Tabs
    const triageTabs = document.getElementById('haryana-triage-tabs');
    const symptomChain = document.getElementById('haryana-symptom-chain');
    const hauSolution = document.getElementById('haryana-hau-solution');

    const checklist = block.symptom_checklist || {};
    const solutions = block.approved_pesticide_solution || {};
    const keys = Object.keys(checklist);

    if (triageTabs && keys.length > 0) {
      triageTabs.innerHTML = '';
      keys.forEach((k, idx) => {
        const tabBtn = document.createElement('button');
        const isSelected = idx === 0;
        tabBtn.className = `px-3 py-1 rounded-lg text-xs font-bold transition-all ${
          isSelected
            ? 'bg-lime-500/30 text-lime-300 border border-lime-500/50'
            : 'bg-white/5 text-slate-400 border border-white/10 hover:bg-white/10'
        }`;
        tabBtn.textContent = k.replace(/_/g, ' ');

        tabBtn.addEventListener('click', () => {
          Array.from(triageTabs.children).forEach(c => {
            c.className = 'px-3 py-1 rounded-lg text-xs font-bold transition-all bg-white/5 text-slate-400 border border-white/10 hover:bg-white/10';
          });
          tabBtn.className = 'px-3 py-1 rounded-lg text-xs font-bold transition-all bg-lime-500/30 text-lime-300 border border-lime-500/50';
          if (symptomChain) symptomChain.textContent = checklist[k] || 'Diagnostic chain not available.';
          if (hauSolution) hauSolution.textContent = solutions[k] || 'Solution recommendation pending HAU review.';
        });

        triageTabs.appendChild(tabBtn);
      });

      // Set initial tab values
      if (symptomChain) symptomChain.textContent = checklist[keys[0]] || '';
      if (hauSolution) hauSolution.textContent = solutions[keys[0]] || '';
    }

    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  // Synchronous initialization from embedded dataset
  populateDistrictsDropdown();
  updateBlocksForDistrict(districtSelect.value || 'Karnal');

  // Event Listeners
  districtSelect.addEventListener('change', (e) => {
    updateBlocksForDistrict(e.target.value);
  });

  blockSelect.addEventListener('change', (e) => {
    if (!haryanaBlocksData) return;
    const selectedB = haryanaBlocksData.find(
      b => b.district.toLowerCase() === districtSelect.value.toLowerCase() && b.block_name === e.target.value
    );
    if (selectedB) renderBlockDetails(selectedB);
  });

  // Background fetch to refresh data if server has updates
  try {
    const res = await fetch('/api/haryana/offline-blocks');
    if (res.ok) {
      const data = await res.json();
      if (data.blocks && data.blocks.length > 0) {
        haryanaBlocksData = data.blocks;
        populateDistrictsDropdown();
      }
    }
  } catch (err) {
    console.log('[AgriVision Haryana] Operating in offline mode.');
  }
}

// ============================================================================
// PILLAR 7: Haryana APMC Mandi 14-Day Price Forecaster
// ============================================================================
let mandiChartInstance = null;

async function initMandiForecast() {
  await fetchMandiForecast();
}

async function fetchMandiForecast() {
  const cropSelect = document.getElementById('forecast-crop-select');
  const crop = cropSelect ? cropSelect.value : 'wheat';
  const district = (document.getElementById('haryana-district-select') && document.getElementById('haryana-district-select').value) || 'Karnal';

  try {
    const res = await fetch(`/api/mandi/forecast/${crop}?district=${encodeURIComponent(district)}`);
    if (!res.ok) return;
    const data = await res.json();

    // 1. Update Action Badge
    const badge = document.getElementById('forecast-action-badge');
    if (badge) {
      const isHold = data.recommendation === 'STRONG_HOLD' || data.recommendation === 'HOLD';
      const isSell = data.recommendation === 'SELL_NOW';
      badge.textContent = `${isHold ? '🎯' : isSell ? '⚡' : '⚖️'} ${data.recommendation.replace('_', ' ')} (${data.price_change_pct >= 0 ? '+' : ''}${data.price_change_pct}%)`;
      badge.className = `text-xs px-2.5 py-0.5 rounded-full font-bold border ${isHold ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' : isSell ? 'bg-rose-500/20 text-rose-300 border-rose-500/30' : 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30'}`;
    }

    // 2. Update Mandi Tag
    const tag = document.getElementById('forecast-mandi-tag');
    if (tag) {
      tag.innerHTML = `Target APMC: <span class="text-emerald-400 font-bold">${data.primary_mandi}</span> (MSP: ₹${data.msp_per_qtl}/Qtl)`;
    }

    // 3. Update Advisory Box
    const title = document.getElementById('forecast-advisory-title');
    const desc = document.getElementById('forecast-advisory-desc');
    if (title && data.advisory_en) {
      title.innerHTML = `<i data-lucide="check-circle-2" class="w-3.5 h-3.5"></i><span>${data.advisory_en.title}</span>`;
    }
    if (desc && data.advisory_en) {
      desc.textContent = data.advisory_en.details;
    }

    // 4. Render Chart.js
    const ctx = document.getElementById('mandiForecastChart');
    if (ctx) {
      const histDates = data.historical_series.map(d => d.date.slice(5));
      const histPrices = data.historical_series.map(d => d.price);

      const fcastDates = data.forecast_series.map(d => d.date.slice(5));
      const fcastPrices = data.forecast_series.map(d => d.projected_price);
      const upperBounds = data.forecast_series.map(d => d.upper_bound);
      const lowerBounds = data.forecast_series.map(d => d.lower_bound);

      const allLabels = [...histDates, ...fcastDates];
      const histDataPadded = [...histPrices, ...Array(fcastDates.length).fill(null)];
      const fcastDataPadded = [...Array(histDates.length - 1).fill(null), histPrices[histPrices.length - 1], ...fcastPrices];
      const upperPadded = [...Array(histDates.length - 1).fill(null), histPrices[histPrices.length - 1], ...upperBounds];
      const lowerPadded = [...Array(histDates.length - 1).fill(null), histPrices[histPrices.length - 1], ...lowerBounds];

      if (mandiChartInstance) {
        mandiChartInstance.destroy();
      }

      mandiChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: allLabels,
          datasets: [
            {
              label: 'Historical Mandi Price',
              data: histDataPadded,
              borderColor: '#06b6d4',
              backgroundColor: 'rgba(6, 182, 212, 0.1)',
              borderWidth: 2,
              pointRadius: 2,
              tension: 0.3
            },
            {
              label: '14-Day Forward Forecast',
              data: fcastDataPadded,
              borderColor: '#10b981',
              borderDash: [5, 5],
              borderWidth: 2,
              pointRadius: 2,
              tension: 0.3
            },
            {
              label: 'Confidence Band (Upper)',
              data: upperPadded,
              borderColor: 'transparent',
              backgroundColor: 'rgba(16, 185, 129, 0.08)',
              fill: '+1',
              pointRadius: 0
            },
            {
              label: 'Confidence Band (Lower)',
              data: lowerPadded,
              borderColor: 'transparent',
              backgroundColor: 'transparent',
              pointRadius: 0
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              grid: { color: 'rgba(255,255,255,0.05)' },
              ticks: { color: '#94a3b8', font: { size: 9 }, maxTicksLimit: 10 }
            },
            y: {
              grid: { color: 'rgba(255,255,255,0.05)' },
              ticks: { color: '#94a3b8', font: { size: 9 } }
            }
          }
        }
      });
    }

    if (window.lucide) {
      window.lucide.createIcons();
    }
  } catch (err) {
    console.warn('[Mandi Forecast] Error fetching forecast:', err);
  }
}

// ============================================================================
// PILLAR 8: Haryana Agricultural GIS Outbreak Map
// ============================================================================
let haryanaGisMapInstance = null;
let haryanaGisMarkers = {};

async function initHaryanaGisMap() {
  const mapContainer = document.getElementById('haryana-gis-map');
  if (!mapContainer) return;

  // 1. Telemetry Data (Immediate offline data with live network enhancement)
  let data = (typeof window !== 'undefined' && window.DEFAULT_HARYANA_GIS_DATA) ? window.DEFAULT_HARYANA_GIS_DATA : {
    map_center: [29.25, 76.5],
    default_zoom: 8,
    high_risk_districts: 3,
    total_active_pathology_cases: 184,
    districts: []
  };

  const updateTelemetryUi = (d) => {
    const highRiskBadge = document.getElementById('gis-high-risk-badge');
    if (highRiskBadge) {
      highRiskBadge.textContent = `${d.high_risk_districts || 3} High Risk Districts`;
    }
    const totalCases = document.getElementById('gis-total-cases');
    if (totalCases) {
      totalCases.textContent = `${d.total_active_pathology_cases || 184} Active Clusters`;
    }
    renderGisDistrictTicker(d.districts || []);
  };

  updateTelemetryUi(data);

  // 2. Render Map (Leaflet or Vector SVG fallback)
  if (window.L && typeof L.map === 'function') {
    renderLeafletGisMap(mapContainer, data);
  } else {
    renderSvgGisMap(mapContainer, data);
  }

  // 3. Background Network Fetch
  try {
    const res = await fetch('/api/haryana/outbreak-map');
    if (res.ok) {
      const liveData = await res.json();
      if (liveData && liveData.districts && liveData.districts.length > 0) {
        updateTelemetryUi(liveData);
        if (window.L && typeof L.map === 'function') {
          renderLeafletGisMap(mapContainer, liveData);
        } else {
          renderSvgGisMap(mapContainer, liveData);
        }
      }
    }
  } catch (err) {
    console.log('[Haryana GIS Map] Operating in offline GIS mode.');
  }
}

function renderGisDistrictTicker(districts) {
  const ticker = document.getElementById('gis-district-list');
  if (!ticker || !districts || districts.length === 0) return;
  ticker.innerHTML = '';

  districts.forEach(d => {
    const item = document.createElement('div');
    item.className = 'flex items-center justify-between p-2 rounded-lg bg-black/40 border border-white/5 hover:border-white/20 transition cursor-pointer';
    item.onclick = () => window.focusGisDistrict(d.district, d.lat, d.lon);
    item.innerHTML = `
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full" style="background-color: ${d.pin_color}"></span>
        <span class="font-bold text-white">${d.district}</span>
        <span class="text-[10px] text-slate-400">(${d.primary_crop})</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-[10px] text-slate-300 truncate max-w-[140px]">${d.dominant_disease}</span>
        <span class="text-[10px] px-1.5 py-0.5 rounded font-bold ${d.badge_class}">${d.risk_level}</span>
      </div>
    `;
    ticker.appendChild(item);
  });
}

function renderLeafletGisMap(mapContainer, data) {
  try {
    const placeholder = document.getElementById('gis-map-placeholder');
    if (placeholder) placeholder.remove();

    if (!haryanaGisMapInstance) {
      haryanaGisMapInstance = L.map('haryana-gis-map', {
        center: data.map_center || [29.25, 76.5],
        zoom: data.default_zoom || 8,
        zoomControl: true,
        attributionControl: false
      });

      // Standard OSM Tile Layer with fast response
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        subdomains: 'abc',
        attribution: '&copy; OpenStreetMap'
      }).addTo(haryanaGisMapInstance);
    }

    setTimeout(() => { if (haryanaGisMapInstance) haryanaGisMapInstance.invalidateSize(); }, 250);
    setTimeout(() => { if (haryanaGisMapInstance) haryanaGisMapInstance.invalidateSize(); }, 800);
    window.addEventListener('resize', () => { if (haryanaGisMapInstance) haryanaGisMapInstance.invalidateSize(); });

    Object.values(haryanaGisMarkers).forEach(m => m.remove());
    haryanaGisMarkers = {};

    data.districts.forEach(d => {
      const radius = d.risk_level === 'HIGH' ? 14 : d.risk_level === 'MODERATE' ? 10 : 7;
      const marker = L.circleMarker([d.lat, d.lon], {
        radius: radius,
        fillColor: d.pin_color,
        color: '#ffffff',
        weight: 1.5,
        opacity: 0.9,
        fillOpacity: 0.8
      }).addTo(haryanaGisMapInstance);

      haryanaGisMarkers[d.district] = marker;

      const popupHtml = `
        <div style="font-family: 'Inter', sans-serif; font-size: 11px; color: #f0fdf4; min-width: 180px; line-height: 1.4;">
          <div style="font-weight: 800; font-size: 13px; color: #84cc16; border-bottom: 1px solid rgba(255,255,255,0.15); padding-bottom: 3px; margin-bottom: 5px;">
            ${d.district} District (हरियाणा)
          </div>
          <div><b>Zone:</b> ${d.zone}</div>
          <div><b>Crop:</b> ${d.primary_crop}</div>
          <div><b>Pathogen:</b> <span style="color: ${d.pin_color}; font-weight: bold;">${d.dominant_disease}</span></div>
          <div><b>Active Clusters:</b> ${d.active_cases}</div>
          <div style="margin-top: 5px; font-size: 10px; color: #cbd5e1; background: rgba(0,0,0,0.5); padding: 5px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.1);">
            ${d.kvk_alert_en}
          </div>
        </div>
      `;
      marker.bindPopup(popupHtml);

      marker.on('click', () => {
        const select = document.getElementById('haryana-district-select');
        if (select && select.value !== d.district) {
          select.value = d.district;
          select.dispatchEvent(new Event('change'));
        }
      });
    });
  } catch (err) {
    console.warn('[Leaflet Render Exception, falling back to SVG]:', err);
    renderSvgGisMap(mapContainer, data);
  }
}

function renderSvgGisMap(container, data) {
  if (!container || !data || !data.districts) return;
  const w = container.clientWidth || 600;
  const h = container.clientHeight || 340;

  const minLat = 27.65, maxLat = 30.90;
  const minLon = 74.45, maxLon = 77.60;

  let svgHtml = `
    <svg viewBox="0 0 ${w} ${h}" class="w-full h-full bg-[#08100b]" style="user-select: none;">
      <defs>
        <radialGradient id="haryanaGisGrid" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#16291d" stop-opacity="0.8"/>
          <stop offset="100%" stop-color="#08100b" stop-opacity="1"/>
        </radialGradient>
      </defs>
      <rect width="${w}" height="${h}" fill="url(#haryanaGisGrid)"/>
      <path d="M 30 30 L ${w-30} 30 L ${w-30} ${h-30} L 30 ${h-30} Z" fill="none" stroke="rgba(74,222,128,0.1)" stroke-width="1" stroke-dasharray="4,4"/>
  `;

  data.districts.forEach(d => {
    const x = Math.round(((d.lon - minLon) / (maxLon - minLon)) * (w - 100) + 50);
    const y = Math.round(((maxLat - d.lat) / (maxLat - minLat)) * (h - 70) + 35);
    const r = d.risk_level === 'HIGH' ? 8 : d.risk_level === 'MODERATE' ? 6 : 4.5;

    svgHtml += `
      <g class="cursor-pointer" onclick="window.focusGisDistrict('${d.district}', ${d.lat}, ${d.lon})">
        <circle cx="${x}" cy="${y}" r="${r + 4}" fill="${d.pin_color}" opacity="0.25"/>
        <circle cx="${x}" cy="${y}" r="${r}" fill="${d.pin_color}" stroke="#ffffff" stroke-width="1.5"/>
        <text x="${x}" y="${y - r - 3}" fill="#e2e8f0" font-size="9" font-weight="bold" text-anchor="middle" font-family="Inter, sans-serif">${d.district}</text>
      </g>
    `;
  });

  svgHtml += `</svg>`;
  container.innerHTML = svgHtml;
}

window.focusGisDistrict = function(districtName, lat, lon) {
  if (haryanaGisMapInstance && haryanaGisMarkers[districtName]) {
    haryanaGisMapInstance.setView([lat, lon], 10);
    haryanaGisMarkers[districtName].openPopup();
  }

  const select = document.getElementById('haryana-district-select');
  if (select && select.value !== districtName) {
    select.value = districtName;
    select.dispatchEvent(new Event('change'));
  }
};

// ============================================================================
// PILLAR 1: Vernacular Voice AI (Haryanvi & Hindi Speech-to-Diagnosis & TTS)
// ============================================================================
let voiceRecognition = null;
let isVoiceRecording = false;
let currentVoiceDialect = 'haryanvi';
let latestVoiceResponse = null;

function initVoiceAdvisor() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    try {
      voiceRecognition = new SpeechRecognition();
      voiceRecognition.continuous = false;
      voiceRecognition.interimResults = false;
      voiceRecognition.lang = 'hi-IN';

      voiceRecognition.onstart = () => {
        isVoiceRecording = true;
        const statusEl = document.getElementById('voice-listening-status');
        const micIcon = document.getElementById('voice-mic-icon');
        const micText = document.getElementById('voice-mic-text');
        if (statusEl) statusEl.classList.remove('hidden');
        if (micIcon) micIcon.classList.add('text-red-500');
        if (micText) micText.innerText = 'रुकें (Stop)';
      };

      voiceRecognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const input = document.getElementById('voice-query-input');
        if (input) {
          input.value = transcript;
          submitVoiceQuery(transcript);
        }
      };

      voiceRecognition.onerror = (event) => {
        console.warn('[AgriVision Voice] Recognition error:', event.error);
        stopVoiceRecording();
      };

      voiceRecognition.onend = () => {
        stopVoiceRecording();
      };
    } catch (e) {
      console.warn('[AgriVision Voice] Speech Recognition init notice:', e);
    }
  }

  const queryInput = document.getElementById('voice-query-input');
  if (queryInput) {
    queryInput.addEventListener('input', () => {
      const clearBtn = document.getElementById('voice-clear-btn');
      if (clearBtn) {
        if (queryInput.value && queryInput.value.trim().length > 0) {
          clearBtn.classList.remove('hidden');
        } else {
          clearBtn.classList.add('hidden');
        }
      }
    });

    queryInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        submitVoiceQuery(queryInput.value);
      }
    });
  }
}

function toggleVoiceRecording() {
  if (!voiceRecognition) {
    alert('Browser voice recognition is not supported in this browser. Please type your query or use Chrome / Edge.');
    return;
  }
  if (isVoiceRecording) {
    voiceRecognition.stop();
    stopVoiceRecording();
  } else {
    try {
      voiceRecognition.lang = currentVoiceDialect === 'english' ? 'en-IN' : 'hi-IN';
      voiceRecognition.start();
    } catch (e) {
      console.warn('[AgriVision Voice] Error starting speech recognition:', e);
    }
  }
}

function stopVoiceRecording() {
  isVoiceRecording = false;
  const statusEl = document.getElementById('voice-listening-status');
  const micIcon = document.getElementById('voice-mic-icon');
  const micText = document.getElementById('voice-mic-text');
  if (statusEl) statusEl.classList.add('hidden');
  if (micIcon) micIcon.classList.remove('text-red-500');
  if (micText) micText.innerText = 'बोलें (Speak)';
}

function switchVoiceDialect(dialect) {
  currentVoiceDialect = dialect;
  const btnHaryanvi = document.getElementById('voice-dialect-haryanvi');
  const btnHindi = document.getElementById('voice-dialect-hindi');
  const btnEnglish = document.getElementById('voice-dialect-english');

  const inactiveClass = 'px-2.5 py-1 rounded-lg font-bold text-slate-400 hover:text-white transition cursor-pointer';
  const activeClass = 'px-2.5 py-1 rounded-lg font-bold bg-lime-500/20 text-lime-300 border border-lime-500/30 transition cursor-pointer';

  if (btnHaryanvi) btnHaryanvi.className = dialect === 'haryanvi' ? activeClass : inactiveClass;
  if (btnHindi) btnHindi.className = dialect === 'hindi' ? activeClass : inactiveClass;
  if (btnEnglish) btnEnglish.className = dialect === 'english' ? activeClass : inactiveClass;

  if (latestVoiceResponse) {
    updateVoiceResponseDisplay(latestVoiceResponse);
  }
}

function setVoicePrompt(text) {
  const input = document.getElementById('voice-query-input');
  const clearBtn = document.getElementById('voice-clear-btn');
  if (input) {
    input.value = text;
    if (clearBtn) clearBtn.classList.remove('hidden');
    submitVoiceQuery(text);
  }
}

function clearVoiceInput() {
  const input = document.getElementById('voice-query-input');
  const clearBtn = document.getElementById('voice-clear-btn');
  if (input) {
    input.value = '';
    input.focus();
  }
  if (clearBtn) clearBtn.classList.add('hidden');
}

// Built-in Offline Fallback KB for Zero-Latency Field Diagnostics (Supports Hindi, Haryanvi, Hinglish & English)
const OFFLINE_VOICE_KB = [
  {
    keywords: [
      'टमाटर', 'tamatar', 'tomater', 'tamater', 'tomato', 'tamato',
      'अगेती', 'ageti', 'aageti', 'agethi', 'aagethi', 'aage thi', 'aage', 'aageti jhulsa',
      'झुलसा', 'jhulsa', 'jhilsa', 'jhilasa', 'blight', 'early', 'काले', 'छल्लेदार', 'dhabbe'
    ],
    crop: 'Tomato',
    hindi_crop_name: 'टमाटर (Tomato)',
    disease_detected: 'Early Blight (अगेती झुलसा - Alternaria solani)',
    severity: 'MODERATE',
    spoken_haryanvi: 'राम राम किसान भाई! टमाटर की निचली पत्तियां पै अगेती झुलसा आ गया सै। 600 ग्राम मैंकोजेब (M-45) 200 लीटर पाणी म मिलाकै बढ़िया छिड़काव करो।',
    spoken_hi: 'किसान भाई, आपकी टमाटर में Early Blight (अगेती झुलसा) के लक्षण हैं। समाधान: मैंकोजेब 75% WP @ 600-800 ग्राम प्रति 200 लीटर पानी में मिलाकर 10-12 दिन के अंतराल पर छिड़कें।',
    spoken_en: 'Farmer alert: Early Blight detected in Tomato. Recommendation: Spray Mancozeb 75% WP (Dithane M-45) @ 600-800 g in 200 L water per acre.',
    prescription: 'मैंकोजेब 75% WP (डाइथेन एम-45) @ 600-800 ग्राम प्रति 200 लीटर पानी में मिलाकर 10-12 दिन के अंतराल पर छिड़कें।'
  },
  {
    keywords: [
      'कनक', 'गेहूं', 'गेहूँ', 'kanak', 'gehu', 'gehun', 'wheat', 'gahu',
      'पीला', 'peela', 'pila', 'रतुआ', 'ratua', 'ratawa', 'rust', 'yellow rust', 'yellow'
    ],
    crop: 'Wheat',
    hindi_crop_name: 'कनक / गेहूं (Wheat)',
    disease_detected: 'Yellow Rust (पीला रतुआ - Puccinia striiformis)',
    severity: 'HIGH',
    spoken_haryanvi: 'राम राम किसान भाई! म्हारी कनक म पीला रतुआ का अटैक सै। 200 मिली प्रोपिकोनाजोल (टिल्ट) 200 लीटर पाणी म मिलाकै धूप खिलदे ई छिड़क देओ।',
    spoken_hi: 'किसान भाई, कनक में पीला रतुआ (Yellow Rust) के लक्षण हैं। समाधान: प्रोपिकोनाजोल 25% EC @ 200 मिली प्रति 200 लीटर पानी में मिलाकर प्रति एकड़ छिड़काव करें।',
    spoken_en: 'Farmer advisory: Yellow Rust detected in Wheat crop. Spray Propiconazole 25% EC (Tilt) @ 200 ml in 200 L water per acre.',
    prescription: '200 मिली प्रोपिकोनाजोल 25% EC (टिल्ट) को 200 लीटर पानी में मिलाकर प्रति एकड़ छिड़कें (CCS HAU हिसार सिफारिश)।'
  },
  {
    keywords: [
      'धान', 'बासमती', 'चावल', 'झीरी', 'dhan', 'dhaan', 'basmati', 'rice', 'paddy',
      'पत्ती', 'patti', 'झुलसा', 'jhulsa', 'jhilsa', 'blast', 'शीथ', 'blight'
    ],
    crop: 'Rice',
    hindi_crop_name: 'धान / बासमती (Paddy)',
    disease_detected: 'Bacterial Leaf Blight / Blast (पत्ती झुलसा)',
    severity: 'HIGH',
    spoken_haryanvi: 'राम राम भाई! धान की पत्तियां पै झुलसा रोग आग्या। तुरंत 300 ग्राम ट्राइसाइक्लाजोल (बाण) 200 लीटर पाणी म मिलाकै खेत म मार देओ।',
    spoken_hi: 'किसान भाई, धान की फसल में पत्ती झुलसा या ब्लास्ट का प्रकोप है। 300 ग्राम ट्राइसाइक्लाजोल 75% WP को 200 लीटर पानी में मिलाकर प्रति एकड़ छिड़काव करें।',
    spoken_en: 'Paddy alert: Leaf Blast / Blight symptoms identified. Spray Tricyclazole 75% WP @ 300 g in 200 L water per acre.',
    prescription: '300 ग्राम ट्राइसाइक्लाजोल 75% WP (Beam / Baan) को 200 लीटर पानी में प्रति एकड़ छिड़कें।'
  },
  {
    keywords: [
      'नरमा', 'कपास', 'narma', 'kapas', 'cotton', 'kapaas',
      'गुलाबी', 'gulabi', 'सूंढी', 'सुंडी', 'sundi', 'sundhi', 'bollworm', 'pink bollworm'
    ],
    crop: 'Cotton',
    hindi_crop_name: 'नरमा / कपास (Cotton)',
    disease_detected: 'Pink Bollworm (गुलाबी सूंढी - Pectinophora gossypiella)',
    severity: 'CRITICAL',
    spoken_haryanvi: 'राम राम किसान भाई! नरमा म गुलाबी सूंढी का खतरा बढ़ग्या। 100 मिली इमामेक्टिन बेंजोएट (प्रोक्लेम) 200 लीटर पाणी म मिलाकै शामती टैम छिड़काव करो।',
    spoken_hi: 'किसान भाई, कपास में गुलाबी सूंढी का प्रकोप है। इमामेक्टिन बेंजोएट 5% SG @ 100 ग्राम प्रति 200 लीटर पानी में मिलाकर सायंकाल छिड़काव करें।',
    spoken_en: 'Cotton alert: Pink Bollworm infestation detected. Spray Emamectin Benzoate 5% SG @ 100 g in 200 L water per acre.',
    prescription: '100 ग्राम इमामेक्टिन बेंजोएट 5% SG या 200 मिली प्रोफेनोफॉस 50% EC प्रति एकड़ 200 लीटर पानी में मिलाकर स्प्रे करें।'
  },
  {
    keywords: [
      'सरसों', 'राया', 'राई', 'sarson', 'sarso', 'mustard', 'raya',
      'सफेद', 'safed', 'रतुआ', 'ratua', 'चेपा', 'chepa', 'aphid', 'white rust'
    ],
    crop: 'Mustard',
    hindi_crop_name: 'सरसों / राया (Mustard)',
    disease_detected: 'White Rust & Aphids (सफेद रतुआ व मोयला/चेपा)',
    severity: 'MODERATE',
    spoken_haryanvi: 'राम राम किसान भाई! सरसों म सफेद रतुआ और चेपा दिख रह्या सै। 600 ग्राम मैंकोजेब गैल 50 मिली इमिडाक्लोप्रिड 200 लीटर पाणी म मिलाकै छिड़क दो।',
    spoken_hi: 'किसान भाई, सरसों में सफेद रतुआ और चेपा/माहू का प्रकोप है। 600 ग्राम रिडोमिल एमजेड या मैंकोजेब के साथ 50-60 मिली इमिडाक्लोप्रिड 17.8% SL मिलाकर छिड़कें।',
    spoken_en: 'Mustard alert: White Rust and Aphid pest complex. Spray Mancozeb 75% WP (600 g) along with Imidacloprid 17.8% SL (50 ml) per acre.',
    prescription: '600 ग्राम मैंकोजेब + 50 मिली इमिडाक्लोप्रिड 17.8% SL को 200 लीटर पानी में मिलाकर प्रति एकड़ छिड़कें।'
  },
  {
    keywords: [
      'आलू', 'aloo', 'aalu', 'potato',
      'पछेती', 'pacheti', 'झुलसा', 'jhulsa', 'jhilsa', 'late blight', 'blight'
    ],
    crop: 'Potato',
    hindi_crop_name: 'आलू (Potato)',
    disease_detected: 'Late Blight (पछेती झुलसा - Phytophthora infestans)',
    severity: 'CRITICAL',
    spoken_haryanvi: 'राम राम किसान भाई! आलू म पछेती झुलसा का भारी खतरा सै। 600 ग्राम साइमोक्सानिल + मैंकोजेब (कर्जेट) 200 लीटर पाणी म तुरंत छिड़को।',
    spoken_hi: 'किसान भाई, आलू की फसल में पछेती झुलसा के लक्षण हैं। साइमोक्सानिल 8% + मैंकोजेब 64% WP (कर्जेट) @ 600 ग्राम प्रति 200 लीटर पानी में मिलाकर तुरंत छिड़काव करें।',
    spoken_en: 'Potato alert: Late Blight (Phytophthora) detected. Spray Cymoxanil + Mancozeb (Curzate) @ 600 g in 200 L water per acre immediately.',
    prescription: 'साइमोक्सानिल 8% + मैंकोजेब 64% WP @ 600 ग्राम प्रति 200 लीटर पानी में तुरंत स्प्रे करें।'
  }
];

function getOfflineVoiceAdvisory(query, dialect, district) {
  const qLower = (query || '').toLowerCase();
  let bestEntry = null;
  let maxMatches = 0;

  for (const item of OFFLINE_VOICE_KB) {
    let count = 0;
    for (const kw of item.keywords) {
      if (qLower.includes(kw.toLowerCase())) {
        count++;
      }
    }
    if (count > maxMatches) {
      maxMatches = count;
      bestEntry = item;
    }
  }

  if (bestEntry && maxMatches > 0) {
    return {
      status: 'DIAGNOSIS_MATCHED',
      query: query,
      district: district || 'Karnal',
      crop: bestEntry.crop,
      hindi_crop_name: bestEntry.hindi_crop_name,
      disease_detected: bestEntry.disease_detected,
      severity: bestEntry.severity,
      spoken_haryanvi: bestEntry.spoken_haryanvi,
      spoken_hi: bestEntry.spoken_hi,
      spoken_en: bestEntry.spoken_en,
      prescription: bestEntry.prescription,
      recommendation: bestEntry.prescription,
      requested_dialect: dialect || 'haryanvi'
    };
  }

  return {
    status: 'GENERAL_ADVICE',
    query: query,
    district: district || 'Karnal',
    crop: 'General Crop Advisory',
    hindi_crop_name: 'सामान्य फसल सुरक्षा (Crop Care)',
    disease_detected: 'कृषि परामर्श व नियमित रोग प्रबंधन',
    severity: 'NORMAL',
    spoken_haryanvi: `राम राम किसान भाई! ${district || 'हरियाणा'} म फसल की नियमित जांच करो। पत्तियां पै धब्बे या कीट दिखण पै तुरंत नजदीकी केवीके या कृषि केंद्र म दिखाओ।`,
    spoken_hi: `किसान भाई, ${district || 'हरियाणा'} क्षेत्र में रोग-कीट के शुरुआती लक्षण दिखते ही संतुलित नीम तेल या फफूंदनाशक का स्प्रे करें और कृषि विज्ञान केंद्र (KVK) से संपर्क करें।`,
    spoken_en: `Farmer Advisory for ${district || 'Haryana'}: Monitor fields daily for symptoms. Use balanced bio-pesticides or consult your local Krishi Vigyan Kendra (KVK).`,
    prescription: 'जैविक नियंत्रण के लिए नीम तेल 10,000 ppm @ 2-3 मिली प्रति लीटर पानी का छिड़काव करें व नजदीकी KVK से सलाह लें।',
    recommendation: 'जैविक नियंत्रण के लिए नीम तेल 10,000 ppm @ 2-3 मिली प्रति लीटर पानी का छिड़काव करें।',
    requested_dialect: dialect || 'haryanvi'
  };
}

async function submitVoiceQuery(overrideQuery = null) {
  const input = document.getElementById('voice-query-input');
  const submitBtn = document.getElementById('voice-submit-btn');
  const query = (overrideQuery || (input ? input.value : '')).trim();
  if (!query) return;

  const districtSelect = document.getElementById('haryana-district-select');
  const district = (districtSelect && districtSelect.value) || 'Karnal';

  // Visual loading feedback on submit button
  const origBtnContent = submitBtn ? submitBtn.innerHTML : 'पूछें';
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="inline-block animate-spin mr-1">⏳</span> जांच जारी...';
    submitBtn.classList.add('opacity-80');
  }

  let matchedData = null;

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 6000);
    const res = await fetch(`/api/voice/query?query=${encodeURIComponent(query)}&district=${encodeURIComponent(district)}&dialect=${encodeURIComponent(currentVoiceDialect)}`, {
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (res.ok) {
      matchedData = await res.json();
    }
  } catch (err) {
    console.warn('[AgriVision Voice] API query failed, checking offline fallback:', err);
  }

  // If server was offline or returned no match, resolve from built-in offline KB
  if (!matchedData || !matchedData.disease_detected || matchedData.status === 'ERROR') {
    matchedData = getOfflineVoiceAdvisory(query, currentVoiceDialect, district);
  }

  if (matchedData) {
    latestVoiceResponse = matchedData;
    updateVoiceResponseDisplay(matchedData);

    if (matchedData.district && districtSelect && districtSelect.value !== matchedData.district) {
      districtSelect.value = matchedData.district;
      districtSelect.dispatchEvent(new Event('change'));
    }
  }

  // Restore button state
  if (submitBtn) {
    submitBtn.disabled = false;
    submitBtn.innerHTML = origBtnContent;
    submitBtn.classList.remove('opacity-80');
    if (window.lucide) window.lucide.createIcons();
  }
}

function updateVoiceResponseDisplay(data) {
  const panel = document.getElementById('voice-response-panel');
  if (!panel) return;
  panel.classList.remove('hidden');

  const cropBadge = document.getElementById('voice-res-crop-badge');
  const diseaseBadge = document.getElementById('voice-res-disease-badge');
  const severityBadge = document.getElementById('voice-res-severity-badge');
  const dialectLabel = document.getElementById('voice-res-dialect-label');
  const scriptEl = document.getElementById('voice-res-script');
  const treatmentEl = document.getElementById('voice-res-treatment');

  if (cropBadge) cropBadge.innerText = data.hindi_crop_name || data.crop || 'Crop';
  if (diseaseBadge) diseaseBadge.innerText = data.disease_detected || 'General Cultivation Guidance';
  
  if (severityBadge) {
    severityBadge.innerText = `${data.severity || 'NORMAL'} SEVERITY`;
    severityBadge.className = data.severity === 'CRITICAL'
      ? 'text-[10px] px-2 py-0.5 rounded-full font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30'
      : data.severity === 'HIGH'
      ? 'text-[10px] px-2 py-0.5 rounded-full font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30'
      : 'text-[10px] px-2 py-0.5 rounded-full font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
  }

  let scriptText = data.spoken_haryanvi;
  let labelText = 'हरियाणवी बोली परामर्श (Haryanvi Spoken Audio Script):';

  if (currentVoiceDialect === 'hindi') {
    scriptText = data.spoken_hi;
    labelText = 'हिंदी कृषक परामर्श (Hindi Spoken Audio Script):';
  } else if (currentVoiceDialect === 'english') {
    scriptText = data.spoken_en;
    labelText = 'English Agronomic Voice Script:';
  }

  if (dialectLabel) dialectLabel.innerText = labelText;
  if (scriptEl) scriptEl.innerText = scriptText || data.spoken_hi;
  if (treatmentEl) treatmentEl.innerText = data.prescription || data.recommendation;

  if (window.lucide) window.lucide.createIcons();

  try {
    if (panel) panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  } catch (e) {}
}

let isVoiceAdvisorySpeaking = false;

function playCurrentVoiceAdvisory() {
  if (!('speechSynthesis' in window)) {
    alert('Text-to-Speech audio playback is not supported on this browser.');
    return;
  }

  // If already speaking, pressing again stops / silences the audio!
  if (window.speechSynthesis.speaking || isVoiceAdvisorySpeaking) {
    stopCurrentVoiceAdvisory();
    return;
  }

  const scriptEl = document.getElementById('voice-res-script');
  const textToSpeak = scriptEl ? scriptEl.innerText : '';
  if (!textToSpeak) return;

  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(textToSpeak);
  utterance.rate = 0.95;
  utterance.pitch = 1.0;
  utterance.lang = currentVoiceDialect === 'english' ? 'en-IN' : 'hi-IN';

  const btnText = document.getElementById('voice-tts-btn-text');
  const playBtn = document.getElementById('voice-play-tts-btn');
  const stopBtn = document.getElementById('voice-stop-tts-btn');

  utterance.onstart = () => {
    isVoiceAdvisorySpeaking = true;
    if (btnText) btnText.innerText = '🔊 बोल रहा हूँ... (रोकने के लिए दबाएं)';
    if (playBtn) playBtn.className = 'px-3 py-1 rounded-lg bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs flex items-center gap-1.5 shadow transition cursor-pointer';
    if (stopBtn) {
      stopBtn.classList.remove('hidden');
      stopBtn.classList.add('flex');
    }
  };

  const onCompleteOrHalt = () => {
    isVoiceAdvisorySpeaking = false;
    if (btnText) btnText.innerText = '🔊 पुनः सुनें (Replay)';
    if (playBtn) playBtn.className = 'px-3 py-1 rounded-lg bg-lime-500 hover:bg-lime-400 text-black font-bold text-xs flex items-center gap-1.5 shadow transition cursor-pointer';
    if (stopBtn) {
      stopBtn.classList.add('hidden');
      stopBtn.classList.remove('flex');
    }
  };

  utterance.onend = onCompleteOrHalt;
  utterance.onerror = onCompleteOrHalt;

  window.speechSynthesis.speak(utterance);
}

function stopCurrentVoiceAdvisory() {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
  isVoiceAdvisorySpeaking = false;
  const btnText = document.getElementById('voice-tts-btn-text');
  const playBtn = document.getElementById('voice-play-tts-btn');
  const stopBtn = document.getElementById('voice-stop-tts-btn');
  if (btnText) btnText.innerText = '🔊 पुनः सुनें (Replay)';
  if (playBtn) playBtn.className = 'px-3 py-1 rounded-lg bg-lime-500 hover:bg-lime-400 text-black font-bold text-xs flex items-center gap-1.5 shadow transition cursor-pointer';
  if (stopBtn) {
    stopBtn.classList.add('hidden');
    stopBtn.classList.remove('flex');
  }
}

window.toggleVoiceRecording = toggleVoiceRecording;
window.submitVoiceQuery = submitVoiceQuery;
window.switchVoiceDialect = switchVoiceDialect;
window.setVoicePrompt = setVoicePrompt;
window.clearVoiceInput = clearVoiceInput;
window.playCurrentVoiceAdvisory = playCurrentVoiceAdvisory;
window.stopCurrentVoiceAdvisory = stopCurrentVoiceAdvisory;

// ============================================================================
// PILLAR 2: Live Camera Stream & Real-Time Bounding Box Scanner
// ============================================================================
let liveCameraStream = null;
let currentCameraFacing = 'environment';
let cameraAnimFrameId = null;

function switchScannerMode(mode) {
  playChime('click');
  const panelSingle = document.getElementById('panel-single-upload');
  const panelCamera = document.getElementById('panel-live-camera');
  const panelDrone = document.getElementById('panel-drone-batch');

  const tabSingle = document.getElementById('mode-tab-single');
  const tabCamera = document.getElementById('mode-tab-camera');
  const tabDrone = document.getElementById('mode-tab-drone');

  const inactiveTab = 'py-2 px-1 rounded-lg font-bold text-slate-400 hover:text-white flex items-center justify-center gap-1.5 transition cursor-pointer';
  const activeTab = 'py-2 px-1 rounded-lg font-bold bg-lime-500/20 text-lime-400 border border-lime-500/30 flex items-center justify-center gap-1.5 transition cursor-pointer';

  if (panelSingle) panelSingle.className = mode === 'single' ? '' : 'hidden';
  if (panelCamera) panelCamera.className = mode === 'camera' ? 'space-y-3' : 'hidden';
  if (panelDrone) panelDrone.className = mode === 'drone' ? 'space-y-4' : 'hidden';

  if (tabSingle) tabSingle.className = mode === 'single' ? activeTab : inactiveTab;
  if (tabCamera) tabCamera.className = mode === 'camera' ? activeTab : inactiveTab;
  if (tabDrone) tabDrone.className = mode === 'drone' ? activeTab : inactiveTab;

  if (mode === 'camera') {
    startLiveCamera();
    // Hide benchmark hotspots
    document.querySelectorAll('.lesion-hotspot').forEach(el => el.classList.add('hidden'));
    const diagCrop = document.getElementById('diag-crop');
    const diagCond = document.getElementById('diag-condition');
    const diagAdvice = document.getElementById('diag-advice');
    const diagConf = document.getElementById('diag-conf-pct');
    const diagBadge = document.getElementById('diag-conf-badge');
    const diagBanner = document.getElementById('diagnosis-banner');
    if (diagBanner) diagBanner.className = 'p-5 rounded-2xl bg-gradient-to-r from-emerald-950/70 to-zenze-card border border-lime-500/30';
    if (diagCrop) diagCrop.innerText = 'Live Optical Scanner';
    if (diagCond) diagCond.innerText = '📷 Ready to Scan Crop Leaf';
    if (diagAdvice) diagAdvice.innerText = 'Position plant foliage inside the central viewfinder box and click "Capture & Diagnose".';
    if (diagConf) diagConf.innerText = '--';
    if (diagBadge) {
      diagBadge.className = 'text-xs px-2.5 py-1 rounded-full font-bold bg-lime-500/20 text-lime-300 border border-lime-500/30';
      diagBadge.innerText = 'CAMERA ACTIVE';
    }
  } else if (mode !== 'camera' && liveCameraStream) {
    stopLiveCamera();
  }
}

async function startLiveCamera() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert('WebRTC camera streaming is not supported on this device/browser.');
    return;
  }

  const video = document.getElementById('live-camera-video');
  const placeholder = document.getElementById('camera-idle-placeholder');
  const hud = document.getElementById('camera-active-hud');
  const controls = document.getElementById('camera-controls-bar');

  try {
    if (liveCameraStream) {
      liveCameraStream.getTracks().forEach(t => t.stop());
    }

    const constraints = {
      video: {
        facingMode: currentCameraFacing,
        width: { ideal: 1280 },
        height: { ideal: 720 }
      },
      audio: false
    };

    liveCameraStream = await navigator.mediaDevices.getUserMedia(constraints);
    if (video) {
      video.srcObject = liveCameraStream;
      await video.play();
    }

    if (placeholder) placeholder.classList.add('hidden');
    if (hud) hud.classList.remove('hidden');
    if (controls) controls.classList.remove('hidden');

    drawLiveBoundingBoxes();
  } catch (err) {
    console.warn('[AgriVision Camera] Error accessing camera:', err);
    alert('Unable to access camera. Please allow camera permissions in your browser settings.');
  }
}

function stopLiveCamera() {
  if (liveCameraStream) {
    liveCameraStream.getTracks().forEach(t => t.stop());
    liveCameraStream = null;
  }
  if (cameraAnimFrameId) {
    cancelAnimationFrame(cameraAnimFrameId);
    cameraAnimFrameId = null;
  }

  const placeholder = document.getElementById('camera-idle-placeholder');
  const hud = document.getElementById('camera-active-hud');
  const controls = document.getElementById('camera-controls-bar');
  const canvas = document.getElementById('live-camera-canvas');

  if (placeholder) placeholder.classList.remove('hidden');
  if (hud) hud.classList.add('hidden');
  if (controls) controls.classList.add('hidden');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
}

function flipCameraFacingMode() {
  currentCameraFacing = currentCameraFacing === 'environment' ? 'user' : 'environment';
  startLiveCamera();
}

let offscreenSampleCanvas = null;

function drawLiveBoundingBoxes() {
  const video = document.getElementById('live-camera-video');
  const canvas = document.getElementById('live-camera-canvas');
  if (!video || !canvas || video.paused || video.ended) return;

  const w = video.videoWidth || 640;
  const h = video.videoHeight || 360;

  if (canvas.width !== w || canvas.height !== h) {
    canvas.width = w;
    canvas.height = h;
  }

  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, w, h);

  // Dynamic targeting box (central 60% of viewport)
  const boxW = Math.round(w * 0.6);
  const boxH = Math.round(h * 0.65);
  const boxX = Math.round((w - boxW) / 2);
  const boxY = Math.round((h - boxH) / 2);

  // Real-time optical color sampling from viewfinder ROI
  if (!offscreenSampleCanvas) {
    offscreenSampleCanvas = document.createElement('canvas');
    offscreenSampleCanvas.width = 32;
    offscreenSampleCanvas.height = 32;
  }
  const sCtx = offscreenSampleCanvas.getContext('2d', { willReadFrequently: true });
  let isHumanDetected = false;
  let isGreenLeafDetected = false;

  try {
    sCtx.drawImage(video, boxX, boxY, boxW, boxH, 0, 0, 32, 32);
    const pix = sCtx.getImageData(0, 0, 32, 32).data;
    let skinCount = 0;
    let greenCount = 0;

    for (let i = 0; i < pix.length; i += 4) {
      const r = pix[i], g = pix[i+1], b = pix[i+2];
      if (r > 70 && g > 35 && b > 20 && r > g && r > b && (r - b) >= 15 && (r - g) >= 8) {
        skinCount++;
      }
      if (g > 40 && g > r * 1.08 && g > b * 1.15) {
        greenCount++;
      }
    }
    if (skinCount > 100) isHumanDetected = true;
    else if (greenCount > 140) isGreenLeafDetected = true;
  } catch (e) {}

  let boxColor = '#84cc16';
  let labelText = '🌿 Leaf ROI: Target Centered';

  if (isHumanDetected) {
    boxColor = '#ef4444';
    labelText = '⚠️ Human / Non-Plant in Frame';
  } else if (!isGreenLeafDetected) {
    boxColor = '#38bdf8';
    labelText = '🔍 Aim Camera at Crop Foliage';
  }

  // Draw corner brackets
  ctx.strokeStyle = boxColor;
  ctx.lineWidth = 3;
  const cornerLen = 24;

  // Top-Left
  ctx.beginPath();
  ctx.moveTo(boxX, boxY + cornerLen);
  ctx.lineTo(boxX, boxY);
  ctx.lineTo(boxX + cornerLen, boxY);
  ctx.stroke();

  // Top-Right
  ctx.beginPath();
  ctx.moveTo(boxX + boxW - cornerLen, boxY);
  ctx.lineTo(boxX + boxW, boxY);
  ctx.lineTo(boxX + boxW, boxY + cornerLen);
  ctx.stroke();

  // Bottom-Left
  ctx.beginPath();
  ctx.moveTo(boxX, boxY + boxH - cornerLen);
  ctx.lineTo(boxX, boxY + boxH);
  ctx.lineTo(boxX + cornerLen, boxY + boxH);
  ctx.stroke();

  // Bottom-Right
  ctx.beginPath();
  ctx.moveTo(boxX + boxW - cornerLen, boxY + boxH);
  ctx.lineTo(boxX + boxW, boxY + boxH);
  ctx.lineTo(boxX + boxW, boxY + boxH - cornerLen);
  ctx.stroke();

  // Crosshair center dot
  ctx.fillStyle = boxColor;
  ctx.beginPath();
  ctx.arc(w / 2, h / 2, 4, 0, Math.PI * 2);
  ctx.fill();

  // Bounding Box Label
  ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
  const labelWidth = isHumanDetected ? 200 : (isGreenLeafDetected ? 180 : 195);
  ctx.fillRect(boxX, boxY - 26, labelWidth, 22);
  ctx.fillStyle = boxColor;
  ctx.font = 'bold 11px Inter, sans-serif';
  ctx.fillText(labelText, boxX + 6, boxY - 11);

  cameraAnimFrameId = requestAnimationFrame(drawLiveBoundingBoxes);
}

function captureAndDiagnoseFrame() {
  const video = document.getElementById('live-camera-video');
  if (!video || !video.videoWidth) {
    alert('Please start the camera stream first.');
    return;
  }

  playChime('click');
  document.querySelectorAll('.lesion-hotspot').forEach(el => el.classList.add('hidden'));
  const snapCanvas = document.createElement('canvas');
  snapCanvas.width = video.videoWidth;
  snapCanvas.height = video.videoHeight;
  const ctx = snapCanvas.getContext('2d');
  ctx.drawImage(video, 0, 0, snapCanvas.width, snapCanvas.height);

  snapCanvas.toBlob((blob) => {
    if (!blob) return;
    const file = new File([blob], 'camera_live_capture.jpg', { type: 'image/jpeg' });
    selectedFile = file;
    selectedSampleId = null;

    const dataUrl = snapCanvas.toDataURL('image/jpeg');
    const orig = document.getElementById('preview-original');
    const clahe = document.getElementById('preview-clahe');
    const under = document.getElementById('split-img-under');
    if (orig) orig.src = dataUrl;
    if (clahe) clahe.src = dataUrl;
    if (under) under.src = dataUrl;

    executeDiagnosis();
  }, 'image/jpeg', 0.92);
}

// ============================================================================
// PILLAR 3: Drone & Multi-Leaf Batch Survey (Canopy Infection & ETL Alert)
// ============================================================================
let droneBatchFiles = [];

function initDroneBatchSurvey() {
  const droneDrop = document.getElementById('drone-drop-zone');
  const batchInput = document.getElementById('batch-file-input');

  if (droneDrop && batchInput) {
    droneDrop.addEventListener('click', () => batchInput.click());
    droneDrop.addEventListener('dragover', (e) => {
      e.preventDefault();
      droneDrop.classList.add('border-amber-400');
    });
    droneDrop.addEventListener('dragleave', () => droneDrop.classList.remove('border-amber-400'));
    droneDrop.addEventListener('drop', (e) => {
      e.preventDefault();
      droneDrop.classList.remove('border-amber-400');
      if (e.dataTransfer.files.length) {
        handleBatchFilesSelected(e.dataTransfer.files);
      }
    });

    batchInput.addEventListener('change', (e) => {
      if (e.target.files.length) {
        handleBatchFilesSelected(e.target.files);
      }
    });
  }
}

async function handleBatchFilesSelected(fileList) {
  const files = Array.from(fileList).slice(0, 20);
  if (files.length === 0) return;

  droneBatchFiles = files;
  playChime('click');

  const resultsPanel = document.getElementById('drone-batch-results');
  const totalCountEl = document.getElementById('batch-total-count');
  const infectedCountEl = document.getElementById('batch-infected-count');
  const rateEl = document.getElementById('batch-infection-rate');
  const etlBadge = document.getElementById('batch-etl-badge');
  const etlAdvice = document.getElementById('batch-etl-advice');
  const strip = document.getElementById('batch-thumbnails-strip');

  if (resultsPanel) resultsPanel.classList.remove('hidden');
  if (totalCountEl) totalCountEl.innerText = files.length;
  if (strip) strip.innerHTML = '<div class="text-xs text-amber-300 animate-pulse">Analyzing multi-leaf field survey...</div>';

  let infectedCount = 0;
  const analysisPromises = files.map(async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('acres', '1.5');
    formData.append('target_crop', 'auto');

    try {
      const res = await fetch('/api/diagnose', { method: 'POST', body: formData });
      if (res.ok) {
        const d = await res.json();
        const isHealthy = d.prediction && d.prediction.disease && d.prediction.disease.toLowerCase().includes('healthy');
        if (!isHealthy) infectedCount++;
        return { file, diagnosis: d, isHealthy };
      }
    } catch (e) {
      console.warn('[Batch Scan Error]:', e);
    }
    return { file, diagnosis: null, isHealthy: true };
  });

  const results = await Promise.all(analysisPromises);
  const infectionRate = Math.round((infectedCount / files.length) * 100);

  if (infectedCountEl) infectedCountEl.innerText = infectedCount;
  if (rateEl) rateEl.innerText = `${infectionRate}%`;

  if (etlBadge && etlAdvice) {
    if (infectionRate < 5) {
      etlBadge.innerText = 'ETL NORMAL (<5%)';
      etlBadge.className = 'text-[10px] px-2 py-0.5 rounded-full font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
      etlAdvice.innerHTML = '<b>🟢 Safe Level:</b> Field infection is negligible. Routine cultural monitoring advised. No chemical fungicide intervention warranted.';
    } else if (infectionRate <= 15) {
      etlBadge.innerText = 'ETL MODERATE (5-15%)';
      etlBadge.className = 'text-[10px] px-2 py-0.5 rounded-full font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30';
      etlAdvice.innerHTML = '<b>🟡 Moderate Warning:</b> Infection approaching economic injury level. Apply preventive organic bio-fungicide (Neem Azadirachtin / Trichoderma) to prevent secondary canopy spread.';
    } else {
      etlBadge.innerText = 'ETL CRITICAL BREACH (>15%)';
      etlBadge.className = 'text-[10px] px-2 py-0.5 rounded-full font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30';
      etlAdvice.innerHTML = '<b>🔴 Economic Threshold Breached:</b> Severe canopy infection detected across multiple walk points. Immediate CCS HAU recommended targeted chemical fungicide spray justified to prevent substantial yield loss.';
    }
  }

  if (strip) {
    strip.innerHTML = '';
    results.forEach((item) => {
      const card = document.createElement('div');
      card.className = 'flex-shrink-0 w-16 p-1 rounded-lg bg-black/50 border ' + (item.isHealthy ? 'border-emerald-500/40' : 'border-rose-500/50') + ' text-center text-[9px]';
      const objUrl = URL.createObjectURL(item.file);
      card.innerHTML = `
        <img src="${objUrl}" class="w-14 h-12 rounded object-cover mx-auto">
        <div class="mt-1 font-bold truncate ${item.isHealthy ? 'text-emerald-400' : 'text-rose-400'}">
          ${item.isHealthy ? 'Healthy' : 'Diseased'}
        </div>
      `;
      strip.appendChild(card);
    });
  }

  if (window.lucide) window.lucide.createIcons();

  try {
    if (resultsPanel) resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  } catch (e) {}
}

window.switchScannerMode = switchScannerMode;
window.startLiveCamera = startLiveCamera;
window.stopLiveCamera = stopLiveCamera;
window.flipCameraFacingMode = flipCameraFacingMode;
window.captureAndDiagnoseFrame = captureAndDiagnoseFrame;
window.handleBatchFilesSelected = handleBatchFilesSelected;

// ============================================================================
// PILLAR 4: N-P-K Soil Nutrition & Fertilizer Dosing Calculator
// ============================================================================
async function runNpkCalculation() {
  const cropSelect = document.getElementById('npk-crop-select');
  const stageSelect = document.getElementById('npk-stage-select');
  const soilSelect = document.getElementById('npk-soil-select');
  const defSelect = document.getElementById('npk-deficiency-select');
  const slider = document.getElementById('acres-slider');

  const crop = cropSelect ? cropSelect.value : 'wheat';
  const stage = stageSelect ? stageSelect.value : 'basal';
  const soil = soilSelect ? soilSelect.value : 'alluvial_loam';
  const def = defSelect ? defSelect.value : '';
  const acres = slider ? parseFloat(slider.value) || 1.0 : 1.0;

  try {
    const res = await fetch(`/api/soil/npk-calculator?crop=${encodeURIComponent(crop)}&acres=${acres}&soil_type=${encodeURIComponent(soil)}&growth_stage=${encodeURIComponent(stage)}${def ? '&deficiency=' + encodeURIComponent(def) : ''}`);
    if (!res.ok) return;
    const data = await res.json();

    const ureaEl = document.getElementById('npk-res-urea');
    const dapEl = document.getElementById('npk-res-dap');
    const mopEl = document.getElementById('npk-res-mop');
    const zincEl = document.getElementById('npk-res-zinc');
    const bioSummary = document.getElementById('npk-bio-summary');
    const alertBox = document.getElementById('npk-deficiency-alert');
    const alertTitle = document.getElementById('npk-deficiency-title');
    const alertDesc = document.getElementById('npk-deficiency-desc');
    const alertSpray = document.getElementById('npk-deficiency-spray');

    if (ureaEl) ureaEl.innerText = `${data.chemical_bags_needed.urea_45kg_bags} Bags`;
    if (dapEl) dapEl.innerText = `${data.chemical_bags_needed.dap_50kg_bags} Bags`;
    if (mopEl) mopEl.innerText = `${data.chemical_bags_needed.mop_potash_50kg_bags} Bags`;
    if (zincEl) zincEl.innerText = `${data.chemical_bags_needed.zinc_sulphate_kg} kg`;

    if (bioSummary && data.organic_alternatives) {
      bioSummary.innerText = `🌿 जैविक विकल्प: ${data.organic_alternatives.vermicompost_tonnes} टन वर्मीकम्पोस्ट + ${data.organic_alternatives.azotobacter_bio_fertilizer_pkts} पैकेट एजोटोबैक्टर`;
    }

    if (alertBox) {
      if (data.deficiency_triage) {
        alertBox.classList.remove('hidden');
        if (alertTitle) alertTitle.innerText = `${data.deficiency_triage.vernacular_name} (${data.deficiency_triage.element}):`;
        if (alertDesc) alertDesc.innerText = `${data.deficiency_triage.symptoms} अंतर: ${data.deficiency_triage.distinction_from_pathology}`;
        if (alertSpray) alertSpray.innerText = `⚡ आपातकालीन स्प्रे: ${data.deficiency_triage.emergency_spray}`;
      } else {
        alertBox.classList.add('hidden');
      }
    }
  } catch (err) {
    console.warn('[AgriVision NPK] Calculation error:', err);
  }
}

window.runNpkCalculation = runNpkCalculation;






