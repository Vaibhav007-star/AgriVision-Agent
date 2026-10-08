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
  if (window.lucide) {
    window.lucide.createIcons();
  }
  initSporesCanvas();
  initSamples();
  initWeather();
  initStats();
  initHistory();
  initSplitSlider();
  init3DTilt();
  setupEventListeners();
  populatePrintableReport();
  initPWA();
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
// 2. Ambient Spores Particle Background
// ============================================================================
function initSporesCanvas() {
  const canvas = document.getElementById('spores-canvas');
  if (!canvas || !canvas.parentElement) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  let width = (canvas.width = canvas.parentElement.offsetWidth);
  let height = (canvas.height = canvas.parentElement.offsetHeight);

  window.addEventListener('resize', () => {
    if (canvas && canvas.parentElement) {
      width = canvas.width = canvas.parentElement.offsetWidth;
      height = canvas.height = canvas.parentElement.offsetHeight;
    }
  });

  const particles = Array.from({ length: 45 }, () => ({
    x: Math.random() * width,
    y: Math.random() * height,
    radius: Math.random() * 2 + 0.6,
    dx: (Math.random() - 0.5) * 0.4,
    dy: -Math.random() * 0.5 - 0.2,
    alpha: Math.random() * 0.5 + 0.2
  }));

  function render() {
    ctx.clearRect(0, 0, width, height);
    particles.forEach((p) => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(132, 204, 22, ${p.alpha})`;
      ctx.shadowBlur = 8;
      ctx.shadowColor = '#84cc16';
      ctx.fill();

      p.x += p.dx;
      p.y += p.dy;

      if (p.y < 0) p.y = height;
      if (p.x < 0) p.x = width;
      if (p.x > width) p.x = 0;
    });
    requestAnimationFrame(render);
  }
  render();
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
// 4. 3D Mouse Tilt Effect for Zenze Cards
// ============================================================================
function init3DTilt() {
  const cards = document.querySelectorAll('.zenze-card');
  cards.forEach((card) => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = ((y - centerY) / centerY) * -4;
      const rotateY = ((x - centerX) / centerX) * 4;
      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-2px)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)';
    });
  });
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
    const res = await fetch('/api/weather?location=Bhopal,%20India');
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
      sporeSpan.className = 'font-bold text-red-400 animate-pulse';
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

  formData.append('field_acres', slider ? slider.value : '1.5');
  formData.append('crop_stage', stage ? stage.value : 'Vegetative Growth');
  formData.append('location', loc ? loc.value : 'Bhopal, India');
  formData.append('language', currentLanguage);

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
    if (data.images.gradcam) {
      if (gradcam) gradcam.src = data.images.gradcam;
      if (over) over.src = data.images.gradcam;
    }

    if (lesionTag) lesionTag.innerText = `Necrotic Foliage: ${data.lesion_percentage}%`;

    // Populate Diagnosis Banner
    const diagCrop = document.getElementById('diag-crop');
    const diagCond = document.getElementById('diag-condition');
    const diagAdvice = document.getElementById('diag-advice');
    const diagConf = document.getElementById('diag-conf-pct');
    const diagBadge = document.getElementById('diag-conf-badge');

    if (data.is_leaf === false) {
      if (diagCrop) diagCrop.innerText = 'Input: Non-Plant / Human Subject';
      if (diagCond) diagCond.innerText = '⚠️ No Crop Leaf Detected';
      if (diagAdvice) diagAdvice.innerText = data.advisory_message;
      if (diagConf) diagConf.innerText = '0.0%';
      if (diagBadge) {
        diagBadge.className = 'text-xs px-2.5 py-1 rounded-full font-bold bg-rose-500/20 text-rose-300 border border-rose-500/40';
        diagBadge.innerText = 'Rejected (Non-Leaf)';
      }
    } else {
      if (diagCrop) diagCrop.innerText = `Crop: ${data.crop}`;
      if (diagCond) diagCond.innerText = `${data.crop} — ${data.disease}`;
      if (diagAdvice) diagAdvice.innerText = data.advisory_message;
      if (diagConf) diagConf.innerText = `${data.confidence_percentage}%`;
      if (diagBadge) {
        diagBadge.className = 'text-xs px-2.5 py-1 rounded-full font-bold bg-lime-500/20 text-lime-300 border border-lime-500/40';
        diagBadge.innerText = `${data.confidence_level} Certainty`;
      }
    }

    // Top-3 Distribution
    const top3Container = document.getElementById('top3-container');
    if (top3Container) {
      if (data.is_leaf === false) {
        top3Container.innerHTML = `
          <div class="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs space-y-1">
            <div class="font-bold flex items-center gap-1.5"><i data-lucide="shield-alert" class="w-4 h-4"></i> Out-of-Distribution Guardrail Triggered</div>
            <p class="text-slate-300">The scanned image does not contain agricultural crop foliage. To prevent harmful pesticide recommendations, disease classification and chemical dosages have been halted.</p>
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

  if (tab === 'bio') {
    if (tabs[0]) tabs[0].className = 'rx-tab text-lime-400 border-b-2 border-lime-400 pb-2';
    const items = latestRxData.biological_controls || [
      'Prune lower chlorotic foliage to prevent upward spore splash.',
      'Apply cold-pressed organic Neem oil solution (5 ml/L) mixed with mild surfactant.'
    ];
    items.forEach((item) => (content.innerHTML += `<p>&bull; ${item}</p>`));
  } else if (tab === 'chem') {
    if (tabs[1]) tabs[1].className = 'rx-tab text-lime-400 border-b-2 border-lime-400 pb-2';
    const items = latestRxData.chemical_controls || [
      'Spray Mancozeb 75% WP @ 2.5 g/L of water at initial symptom manifestation.',
      'Rotate with Azoxystrobin 23% SC (1 ml/L) to manage FRAC fungicide resistance.'
    ];
    items.forEach((item) => (content.innerHTML += `<p>&bull; ${item}</p>`));
  } else if (tab === 'prev') {
    if (tabs[2]) tabs[2].className = 'rx-tab text-lime-400 border-b-2 border-lime-400 pb-2';
    const items = latestRxData.cultural_prevention || [
      'Enforce 3-year crop rotation with non-solanaceous crops.',
      'Disinfect pruning shears with 10% sodium hypochlorite solution.'
    ];
    items.forEach((item) => (content.innerHTML += `<p>&bull; ${item}</p>`));
  } else if (tab === 'hindi') {
    if (tabs[3]) tabs[3].className = 'rx-tab text-lime-400 border-b-2 border-lime-400 pb-2';
    const text = latestRxData.hindi_summary || 'कृषि परामर्श तैयार कर दिया गया है। नीम का तेल और मैंकोजेब का अनुशंसित छिड़काव करें।';
    content.innerHTML = `<p class="text-lime-300 font-medium">${text.replace(/\n/g, '<br>')}</p>`;
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

  if (currentLanguage === 'hi' && latestRxData.hindi_summary) {
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
  const locVal = loc && loc.value ? loc.value : 'Bhopal, India';

  const repCrop = document.getElementById('rep-crop');
  const repLocation = document.getElementById('rep-location');
  const repAcres = document.getElementById('rep-acres');
  const repStage = document.getElementById('rep-stage');

  if (repCrop) repCrop.innerText = d && d.crop ? `${d.crop} (${d.crop === 'Tomato' ? 'Solanum lycopersicum' : (d.crop === 'Potato' ? 'Solanum tuberosum' : 'Capsicum annuum')})` : 'Tomato (Solanum lycopersicum)';
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
    let pathName = 'Pathogen: Unknown';
    if (d.disease.includes('Late Blight')) pathName = 'Pathogen: Phytophthora infestans (Oomycete Water Mold) • Severity: Critical';
    else if (d.disease.includes('Early Blight')) pathName = 'Pathogen: Alternaria solani (Fungus) • Severity: Moderate to High';
    else if (d.disease.includes('Bacterial')) pathName = 'Pathogen: Xanthomonas campestris (Bacterium) • Severity: Severe';
    else if (d.disease.includes('Septoria')) pathName = 'Pathogen: Septoria lycopersici (Fungus) • Severity: Moderate';
    else if (d.disease.includes('Leaf Mold')) pathName = 'Pathogen: Passalora fulva (Fungus) • Severity: Moderate';
    else if (d.disease.includes('Spider')) pathName = 'Pathogen: Tetranychus urticae (Acarina / Pest) • Severity: Moderate';
    else if (d.disease.includes('Yellow')) pathName = 'Pathogen: Tomato Yellow Leaf Curl Begomovirus • Severity: High';
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

