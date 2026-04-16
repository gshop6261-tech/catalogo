import json

file_path = 'g:/Mi unidad/Globalshop/Catalogo - Comrpa directa/calculadora.html'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Weight input below USD input
USD_INPUT_BLOCK = '''      <!-- USD cost input -->
      <div class="calc-section-title">3 · Costo en dólares</div>
      <div class="usd-input-wrap">
        <span class="usd-prefix">$</span>
        <input
          type="number"
          class="usd-input"
          id="usdInput"
          placeholder="0"
          min="1"
          step="1"
          oninput="onUsdInput()"
          autocomplete="off"
          inputmode="decimal"
        >
        <span class="usd-suffix">USD</span>
      </div>'''

USD_AND_WEIGHT_BLOCK = '''      <!-- USD cost input -->
      <div class="calc-section-title">3 · Costo en dólares</div>
      <div class="usd-input-wrap" style="margin-bottom: 12px;">
        <span class="usd-prefix">$</span>
        <input
          type="number"
          class="usd-input"
          id="usdInput"
          placeholder="0"
          min="1"
          step="1"
          oninput="onUsdInput()"
          autocomplete="off"
          inputmode="decimal"
        >
        <span class="usd-suffix">USD</span>
      </div>
      
      <!-- Weight input -->
      <div class="calc-section-title">3.1 · Peso (opcional)</div>
      <div class="usd-input-wrap">
        <input
          type="number"
          class="usd-input"
          id="weightInput"
          placeholder="Ej: 1.5"
          min="0"
          step="0.01"
          oninput="onUsdInput()"
          autocomplete="off"
          inputmode="decimal"
        >
        <span class="usd-suffix" style="right: 14px;">kg</span>
      </div>'''

text = text.replace(USD_INPUT_BLOCK, USD_AND_WEIGHT_BLOCK)

# 2. Add empty blocks for dynamic DOM injection
CAT_TABS_OLD = '''      <div class="cat-tabs" id="catTabs">
        <button class="cat-tab active" data-cat="celular" onclick="selectCat('celular', this)">
          <span class="ct-icon">📱</span>Celulares
        </button>
        <button class="cat-tab" data-cat="electronica" onclick="selectCat('electronica', this)">
          <span class="ct-icon">🎧</span>Electrónica
        </button>
        <button class="cat-tab" data-cat="hogar" onclick="selectCat('hogar', this)">
          <span class="ct-icon">🏠</span>Hogar
        </button>
      </div>'''

CAT_TABS_NEW = '''      <div class="cat-tabs" id="catTabs">
        <!-- JS rendered -->
      </div>'''
text = text.replace(CAT_TABS_OLD, CAT_TABS_NEW)

FORMULA_BODY_REPLACE_START = '''      <div class="formula-body" id="formulaBody">'''
FORMULA_BODY_REPLACE_END = '''        <div class="formula-group">
          <div class="fg-title">🏠 Hogar</div>
          <div class="fg-row">
            <span class="fg-type">Todos los productos</span>
            <span class="fg-formula">costo × dólar × 1.25</span>
            <span class="fg-margin">+25%</span>
          </div>
        </div>

      </div>'''

import re
text = re.sub(r'<div class="formula-body" id="formulaBody">.*?</style>.*?</head>', '', text, flags=re.DOTALL) # wait regex is dangerous, I will do string match logic

START_ID = '<div class="formula-body" id="formulaBody">'
END_ID = '      </div>\n    </div>\n\n  </div>\n</div>\n\n<!-- ══════════════════════════════════════\n     SCRIPTS\n══════════════════════════════════════ -->'
if START_ID in text and END_ID in text:
    p1 = text.split(START_ID)[0]
    p2 = text.split(END_ID)[1]
    text = p1 + START_ID + '\n        <!-- JS Rendered -->\n' + END_ID + p2

# Replace Javascript logic:
# Inject settings handling and dynamic init

JS_INIT_OLD = '''document.addEventListener('DOMContentLoaded', () => {
  // Check login
  if (!sessionStorage.getItem('calc_logged_in')) {
    document.getElementById('loginScreen').style.display = 'flex';
  }

  fetchDollar();
  setInterval(() => fetchDollar(), 5 * 60 * 1000); // refresh every 5 min
  renderHistory();
});'''

JS_INIT_NEW = '''document.addEventListener('DOMContentLoaded', () => {
  // Check login
  if (!sessionStorage.getItem('calc_logged_in')) {
    document.getElementById('loginScreen').style.display = 'flex';
  }
  
  initCategories();
  fetchDollar();
  setInterval(() => fetchDollar(), 5 * 60 * 1000); // refresh every 5 min
  renderHistory();
  renderFormulaRef();
});

let settings = JSON.parse(localStorage.getItem('cd_settings') || '{}');
let cats = settings.categories || [];

function initCategories() {
  const tabs = document.getElementById('catTabs');
  if(!cats.length) {
    tabs.innerHTML = '<div style="color:var(--text3);font-size:12px;padding:10px;">No hay categorías configuradas. Usá el Panel Admin.</div>';
    return;
  }
  
  tabs.innerHTML = cats.map((c, i) => `
    <button class="cat-tab ${i===0?'active':''}" data-cat="${c.name}" onclick="selectCat('${c.name}', this)">
      <span class="ct-icon">${c.icon}</span>${c.name}
    </button>
  `).join('');
  
  selectedCat = cats[0].name;
  renderSubtypes(selectedCat);
}

function renderFormulaRef() {
  const fb = document.getElementById('formulaBody');
  if(!cats.length) { fb.innerHTML = '<div style="font-size:12px;color:var(--text3);padding:10px;">Sin reglas.</div>'; return; }
  
  fb.innerHTML = cats.map(c => {
    if(!c.rules || c.rules.length===0) return '';
    const st = c.name;
    const rulesHtml = c.rules.map(r => {
      let condText = r.type === 'none' ? 'Siempre' : (r.type==='price' ? `Precio ${r.op} ${r.val}` : `Peso ${r.op} ${r.val}`);
      return `
        <div class="fg-row">
          <span class="fg-type">${r.subtype} <span style="font-size:9px;color:var(--text3)">(${condText})</span></span>
          <span class="fg-margin" style="background:var(--green);color:#fff;border:none;">+${r.margin}% +$${r.add}</span>
        </div>
      `;
    }).join('');
    
    return `
      <div class="formula-group">
        <div class="fg-title">${c.icon} ${c.name}</div>
        ${rulesHtml}
      </div>
    `;
  }).join('');
}
'''
text = text.replace(JS_INIT_OLD, JS_INIT_NEW)

# Change getFormula logic
GET_FORMULA_OLD = '''function getFormula(cat, sub, usd) {
  const cdSettings = JSON.parse(localStorage.getItem('cd_settings') || '{}');
  const formulas = cdSettings.formulas || {
    "celular_slim":         { margin: 8,  add: 6, label:"Celulares (≤ $300) - Slim" },
    "celular_gruesa":       { margin: 10, add: 4, label:"Celulares (≤ $300) - Gruesa" },
    "celular_slim_high":    { margin: 8,  add: 0, label:"Celulares (> $300) - Slim" },
    "celular_gruesa_high":  { margin: 10, add: 0, label:"Celulares (> $300) - Gruesa" },
    "electronica_chico":    { margin: 20, add: 0, label:"Electrónica/Otros - Chico" },
    "electronica_grande":   { margin: 25, add: 0, label:"Electrónica/Otros - Grande" },
    "hogar_unico":          { margin: 25, add: 0, label:"Hogar (General)" }
  };

  let key = 'hogar_unico';
  if (cat === 'celular') {
    if (usd > 300) {
      key = 'celular_' + (sub || 'slim') + '_high';
    } else {
      key = 'celular_' + (sub || 'slim');
    }
  } else if (cat === 'electronica') {
    key = 'electronica_' + (sub || 'chico');
  } else if (cat === 'hogar') {
    key = 'hogar_unico';
  }

  const rule = formulas[key];
  const pct = 1 + (rule.margin / 100);
  const baseUsd = (usd * pct) + rule.add;
  const rawArs = baseUsd * dollar;
  const ars = Math.ceil(rawArs / 100) * 100;

  return {
    ars,
    margin: pct,
    label: rule.label,
    formulaStr: `((${usd} + ${rule.margin}%) + ${rule.add}) × ${Number(dollar).toLocaleString('es-AR')}`,
    steps: [
      { k: 'Costo USD',     v: `U$D ${usd}` },
      { k: `Margen (+${rule.margin}%)`,      v: `+ U$D ${(usd * (rule.margin/100)).toFixed(2)}` },
      { k: `Ajuste fijo (+U$D ${rule.add})`, v: `+ U$D ${rule.add}` },
      { k: 'Base ajustada', v: `U$D ${baseUsd.toFixed(2)}` },
      { k: 'Cotización',    v: `$ ${Number(dollar).toLocaleString('es-AR')}` },
      { k: 'Subtotal ARS',  v: `$ ${Math.round(rawArs).toLocaleString('es-AR')}` },
      { k: 'Redondeo ↑100', v: `$ ${ars.toLocaleString('es-AR')}` },
    ]
  };
}'''

GET_FORMULA_NEW = '''function getFormula(catName, sub, usd, weightArg) {
  const cdSettings = JSON.parse(localStorage.getItem('cd_settings') || '{}');
  const catArray = cdSettings.categories || [];
  const u = parseFloat(usd);
  const w = parseFloat(weightArg) || 0;
  
  const c = catArray.find(x => x.name === catName);
  if (!c) return { ars:0, steps:[] };
  
  const rules = c.rules || [];
  let matchedRule = rules.find(r => r.subtype === 'unico'); 
  const subtypeTarget = sub || 'unico';
  const typeRules = rules.filter(r => r.subtype === subtypeTarget);
  
  for (let r of typeRules) {
    if (r.type === 'none') { matchedRule = r; break; }
    if (r.type === 'price') {
       if (r.op === '<=' && u <= r.val) { matchedRule = r; break; }
       if (r.op === '>=' && u >= r.val) { matchedRule = r; break; }
       if (r.op === '<'  && u < r.val)  { matchedRule = r; break; }
       if (r.op === '>'  && u > r.val)  { matchedRule = r; break; }
    }
    if (r.type === 'weight') {
       if (r.op === '<=' && w <= r.val) { matchedRule = r; break; }
       if (r.op === '>=' && w >= r.val) { matchedRule = r; break; }
       if (r.op === '<'  && w < r.val)  { matchedRule = r; break; }
       if (r.op === '>'  && w > r.val)  { matchedRule = r; break; }
    }
  }
  
  if (!matchedRule) {
     if (typeRules.length > 0) matchedRule = typeRules[0]; 
     else matchedRule = { margin: 0, add: 0 };
  }

  const pct = 1 + (matchedRule.margin / 100);
  const baseUsd = (u * pct) + matchedRule.add;
  const rawArs = baseUsd * dollar;
  const ars = Math.ceil(rawArs / 100) * 100;

  return {
    ars,
    margin: pct,
    label: `${catName} - ${subtypeTarget}`,
    formulaStr: `((${usd} + ${matchedRule.margin}%) + ${matchedRule.add}) × ${Number(dollar).toLocaleString('es-AR')}`,
    steps: [
      { k: 'Costo USD',     v: `U$D ${usd}` },
      { k: `Margen (+${matchedRule.margin}%)`,      v: `+ U$D ${(usd * (matchedRule.margin/100)).toFixed(2)}` },
      { k: `Ajuste fijo (+U$D ${matchedRule.add})`, v: `+ U$D ${matchedRule.add}` },
      { k: 'Base ajustada', v: `U$D ${baseUsd.toFixed(2)}` },
      { k: 'Cotización',    v: `$ ${Number(dollar).toLocaleString('es-AR')}` },
      { k: 'Subtotal ARS',  v: `$ ${Math.round(rawArs).toLocaleString('es-AR')}` },
      { k: 'Redondeo ↑100', v: `$ ${ars.toLocaleString('es-AR')}` },
    ]
  };
}'''
text = text.replace(GET_FORMULA_OLD, GET_FORMULA_NEW)


# Rebuild renderSubtypes logic
RENDER_SUBTYPES_OLD = '''function renderSubtypes(cat) {
  const row   = document.getElementById('subtypeRow');
  const label = document.getElementById('subtypeLabel');
  const subs  = SUBTYPES[cat];

  if (!subs) {
    // Hogar: no subtype needed
    row.style.display = 'none';
    label.style.display = 'none';
    selectedSub = 'unico';
    return;
  }

  row.style.display = 'grid';
  label.style.display = 'block';

  row.innerHTML = subs.map((s, i) => `
    <button
      class="subtype-btn ${i === 0 ? 'active' : ''}"
      data-sub="${s.id}"
      onclick="selectSub('${s.id}', this)"
    >
      <span class="sb-icon">${s.icon}</span>
      <span>${s.label}</span>
      <span class="sb-note">${s.note}</span>
    </button>
  `).join('');

  selectedSub = subs[0].id;
}'''

RENDER_SUBTYPES_NEW = '''function renderSubtypes(catName) {
  const row   = document.getElementById('subtypeRow');
  const label = document.getElementById('subtypeLabel');
  
  const c = cats.find(x => x.name === catName);
  const subs = (c && c.subtypes && c.subtypes.length > 0) ? c.subtypes : null;

  if (!subs) {
    row.style.display = 'none';
    label.style.display = 'none';
    selectedSub = 'unico';
    return;
  }

  row.style.display = 'grid';
  label.style.display = 'block';

  row.innerHTML = subs.map((s, i) => `
    <button
      class="subtype-btn ${i === 0 ? 'active' : ''}"
      data-sub="${s.id}"
      onclick="selectSub('${s.id}', this)"
    >
      <span class="sb-icon">📦</span>
      <span>${s.label}</span>
      <span class="sb-note"></span>
    </button>
  `).join('');

  selectedSub = subs[0].id;
}'''
text = text.replace(RENDER_SUBTYPES_OLD, RENDER_SUBTYPES_NEW)

# Change calculate() logic string:
text = text.replace("const result = getFormula(selectedCat, selectedSub, usd);", "const result = getFormula(selectedCat, selectedSub, usd, parseFloat(document.getElementById('weightInput').value)||0);")

text = text.replace(
'''  // Save to history
  addToHistory({
    ars:    result.ars,
    usd,
    name:   name || catLabel(selectedCat) + ' U$D ' + usd,
    cat:    selectedCat,''',
'''  // Save to history
  addToHistory({
    ars:    result.ars,
    usd,
    name:   name || selectedCat + ' U$D ' + usd,
    cat:    selectedCat,''')

# Finally catLabel isn't used except inside history logic, so I can replace:
text = text.replace("catLabel(h.cat)", "h.cat")


with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)
print('calculadora.html updated successfully')
