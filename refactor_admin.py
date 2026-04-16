import json

file_path = 'g:/Mi unidad/Globalshop/Catalogo - Comrpa directa/admin.html'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace menu item
text = text.replace(
'''      <div class="nav-item" data-page="formulas" onclick="navTo('formulas')">
        <span class="ni">🧮</span> Calc. de Precios
      </div>''',
'''      <div class="nav-item" data-page="categories" onclick="navTo('categories')">
        <span class="ni">🧮</span> Categorías y Reglas
      </div>''')

formulas_page_old = '''    <!-- ─────── FORMULAS (Calc. de Precios) ─────── -->
    <section id="page-formulas" class="page">
      <div class="page-header">
        <div>
          <div class="page-title">Calculadora de Precios</div>
          <div class="page-sub">Definí los márgenes y gastos logísticos por categoría. Se aplicarán a todos los cálculos.</div>
        </div>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Categoría / Tipo de artículo</th>
              <th width="150">Ganancia (%)</th>
              <th width="150">Ajuste Fijo (U$D)</th>
            </tr>
          </thead>
          <tbody id="formulasTableBody">
            <!-- Rendered by JS -->
          </tbody>
        </table>
      </div>
      <div style="margin-top:14px;display:flex;gap:10px;justify-content:flex-end">
        <button class="btn btn-green" onclick="saveFormulas()">💾 Guardar configuración</button>
      </div>
      
      <div style="background:var(--surface);border-radius:var(--r-md);padding:14px;border:1px solid var(--border);margin-top:20px;">
        <h4 style="font-size:12px;margin-bottom:6px">¿Cómo funciona el cálculo automático?</h4>
        <p style="font-size:11px;color:var(--text-3);line-height:1.5;">La fórmula de precio es: <strong>((Costo U$D + % Ganancia) + Ajuste U$D) × Dólar vigente</strong>.<br>
        1. Se toma el Costo USD.<br>
        2. Se le suma el % de ganancia.<br>
        3. Se suma el Ajuste Fijo en dólares.<br>
        4. Luego se multiplica por la cotización del dólar.</p>
      </div>
    </section>'''

categories_page_new = '''    <!-- ─────── CATEGORIAS Y REGLAS ─────── -->
    <section id="page-categories" class="page">
      <div class="page-header">
        <div>
          <div class="page-title">Categorías y Reglas de Precio</div>
          <div class="page-sub">Gestioná las categorías de tu catálogo y sus reglas matemáticas asociadas.</div>
        </div>
        <button class="btn btn-green" onclick="openCategoryModal()">＋ Agregar categoría</button>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Categoría</th>
              <th>Subtipos</th>
              <th>Reglas matemáticas configuradas</th>
              <th>Acción</th>
            </tr>
          </thead>
          <tbody id="categoriesTableBody">
            <!-- Rendered by JS -->
          </tbody>
        </table>
      </div>
      
      <div style="background:var(--surface);border-radius:var(--r-md);padding:14px;border:1px solid var(--border);margin-top:20px;">
        <h4 style="font-size:12px;margin-bottom:6px">¿Cómo funcionan las reglas de precio?</h4>
        <p style="font-size:11px;color:var(--text-3);line-height:1.5;">La fórmula base es siempre: <strong>((Costo U$D + % Ganancia) + Ajuste U$D) × Dólar vigente</strong>.<br>
        Podés crear múltiples reglas dentro de una misma categoría que se activan según el <strong>Subtipo</strong>, el <strong>Precio USD</strong> o el <strong>Peso (kg)</strong> del producto.</p>
      </div>
    </section>

    <!-- Modal de Categoría -->
    <div class="modal-backdrop" id="categoryModal" role="dialog">
      <div class="modal" style="max-width: 600px;">
        <div class="modal-header">
          <div class="modal-title" id="catModalTitle">Nueva categoría</div>
          <button class="modal-close" onclick="closeCategoryModal()">✕</button>
        </div>
        <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">
          <input type="hidden" id="cmId">
          <div class="form-grid">
            <div class="form-group form-full">
              <label class="form-label">Nombre de Categoría <span class="req">*</span></label>
              <input type="text" class="form-input" id="cmName" placeholder="Ej: Celulares">
            </div>
            <div class="form-group form-full">
              <label class="form-label">Ícono (Emoji)</label>
              <input type="text" class="form-input" id="cmIcon" placeholder="📱" maxlength="4">
            </div>
            
            <div class="form-section form-full">📦 Subtipos (opcional)</div>
            <div class="form-group form-full" style="padding-bottom:10px;">
               <div id="cmSubtypesList" style="display:flex; flex-direction:column; gap:8px;"></div>
               <button class="btn btn-ghost btn-sm" style="margin-top:10px" onclick="addCategorySubtype()">+ Agregar Subtipo</button>
            </div>

            <div class="form-section form-full">📐 Reglas de cálculo</div>
            <div class="form-group form-full">
               <div id="cmRulesList" style="display:flex; flex-direction:column; gap:12px;"></div>
               <button class="btn btn-ghost btn-sm" style="margin-top:10px" onclick="addCategoryRule()">+ Agregar Regla</button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" onclick="closeCategoryModal()">Cancelar</button>
          <button class="btn btn-green" onclick="saveCategory()">💾 Guardar categoría</button>
        </div>
      </div>
    </div>
'''

text = text.replace(formulas_page_old, categories_page_new)

text = text.replace(
'''        <div class="form-group">
          <label class="form-label">Emoji (ícono)</label>''',
'''        <div class="form-group">
          <label class="form-label">Peso (kg)</label>
          <input type="number" class="form-input" id="pmWeight" placeholder="Ej: 1.5" min="0" step="0.01" oninput="autoCalcArs(); updatePreview()">
          <span class="form-hint">Opcional.</span>
        </div>
        <div class="form-group">
          <label class="form-label">Emoji (ícono)</label>''')

CATS_BLOCK_OLD = '''const CATS = ['Celulares', 'Smart TV', 'Audio', 'Computación', 'Accesorios', 'Hogar'];

const SUBTYPES = {
  'Celulares': [
    { id: 'slim', label: 'Caja slim (sin cargador)' },
    { id: 'gruesa', label: 'Caja gruesa (con cargador)' }
  ],
  'Electrónica': [
    { id: 'chico', label: 'Chico (Caja zapatilla / Accesorios)' },
    { id: 'grande', label: 'Grande (Aspiradoras / TV / Pesados)' }
  ]
};'''

CATS_BLOCK_NEW = '''const CATS = () => (settings.categories || []).map(c => c.name);

const SUBTYPES = (catName) => {
  const cat = (settings.categories || []).find(c => c.name === catName);
  return cat && cat.subtypes && cat.subtypes.length > 0 ? cat.subtypes : [{ id: 'unico', label: 'Único' }];
};'''

text = text.replace(CATS_BLOCK_OLD, CATS_BLOCK_NEW)

DEFAULT_SETTINGS_OLD = '''const DEFAULT_SETTINGS = {
  whatsapp: '5491154125271',
  dollarManual: null,
  dollarAuto: null,
  dollarUpdated: null,
  formulas: {
    "celular_slim":         { margin: 8,  add: 6, label:"Celulares (≤ $300) - Slim" },
    "celular_gruesa":       { margin: 10, add: 4, label:"Celulares (≤ $300) - Gruesa" },
    "celular_slim_high":    { margin: 8,  add: 0, label:"Celulares (> $300) - Slim" },
    "celular_gruesa_high":  { margin: 10, add: 0, label:"Celulares (> $300) - Gruesa" },
    "electronica_chico":    { margin: 20, add: 0, label:"Electrónica/Otros - Chico" },
    "electronica_grande":   { margin: 25, add: 0, label:"Electrónica/Otros - Grande" },
    "hogar_unico":          { margin: 25, add: 0, label:"Hogar (General)" }
  }
};'''

DEFAULT_SETTINGS_NEW = """const DEFAULT_CATEGORIES = [
  {
    id: "celulares",
    name: "Celulares",
    icon: "📱",
    subtypes: [
      { id: "slim", label: "Caja slim (sin cargador)" },
      { id: "gruesa", label: "Caja gruesa (con cargador)" }
    ],
    rules: [
      { subtype: "slim", type: "price", op: "<=", val: 300, margin: 8, add: 6 },
      { subtype: "slim", type: "price", op: ">", val: 300, margin: 8, add: 0 },
      { subtype: "gruesa", type: "price", op: "<=", val: 300, margin: 10, add: 4 },
      { subtype: "gruesa", type: "price", op: ">", val: 300, margin: 10, add: 0 }
    ]
  },
  {
    id: "smart-tv",
    name: "Smart TV",
    icon: "📺",
    subtypes: [
      { id: "chico", label: "Chico" },
      { id: "grande", label: "Grande" }
    ],
    rules: [
      { subtype: "chico", type: "none", val: 0, margin: 20, add: 0 },
      { subtype: "grande", type: "none", val: 0, margin: 25, add: 0 }
    ]
  },
  {
    id: "audio",
    name: "Audio",
    icon: "🎧",
    subtypes: [{ id: "unico", label: "Único" }],
    rules: [{ subtype: "unico", type: "none", val: 0, margin: 20, add: 0 }]
  },
  {
    id: "computacion",
    name: "Computación",
    icon: "💻",
    subtypes: [{ id: "unico", label: "Único" }],
    rules: [{ subtype: "unico", type: "none", val: 0, margin: 20, add: 0 }]
  },
  {
    id: "accesorios",
    name: "Accesorios",
    icon: "🎒",
    subtypes: [{ id: "unico", label: "Único" }],
    rules: [{ subtype: "unico", type: "none", val: 0, margin: 20, add: 0 }]
  },
  {
    id: "hogar",
    name: "Hogar",
    icon: "🏠",
    subtypes: [{ id: "unico", label: "Único" }],
    rules: [{ subtype: "unico", type: "none", val: 0, margin: 25, add: 0 }]
  }
];

const DEFAULT_SETTINGS = {
  whatsapp: '5491154125271',
  dollarManual: null,
  dollarAuto: null,
  dollarUpdated: null,
  categories: JSON.parse(JSON.stringify(DEFAULT_CATEGORIES))
};"""

text = text.replace(DEFAULT_SETTINGS_OLD, DEFAULT_SETTINGS_NEW)

text = text.replace(
'''      // NOTE: usd and priceHistory intentionally excluded from catalog sync
    })),
    banners: banners.filter(b => b.activo),''',
'''      // NOTE: usd and priceHistory intentionally excluded from catalog sync
    })),
    banners: banners.filter(b => b.activo),
    categories: settings.categories || [],''')

INIT_APP_OLD = '''  settings = load(LS_SETTINGS, DEFAULT_SETTINGS);

  // Populate cat dropdowns
  populateCatDropdowns();'''
INIT_APP_NEW = '''  settings = load(LS_SETTINGS, DEFAULT_SETTINGS);
  if (settings.formulas && !settings.categories) {
    settings.categories = JSON.parse(JSON.stringify(DEFAULT_CATEGORIES));
    saveSettings();
  }

  // Populate cat dropdowns
  populateCatDropdowns();'''

text = text.replace(INIT_APP_OLD, INIT_APP_NEW)

text = text.replace(
'''  // Ensure formulas exist for backwards comp if previous settings existed
  if (!settings.formulas) settings.formulas = JSON.parse(JSON.stringify(DEFAULT_SETTINGS.formulas));

  renderFormulasTable();''',
'''  if (!settings.categories) settings.categories = JSON.parse(JSON.stringify(DEFAULT_CATEGORIES));

  renderCategoriesTable();''')

text = text.replace('CATS.forEach(c => {', 'CATS().forEach(c => {')
text = text.replace("case 'formulas':  renderFormulasTable(); break;", "case 'categories':  renderCategoriesTable(); break;")

text = text.replace("document.getElementById('pmUsd').value       = p.usd || '';", "document.getElementById('pmUsd').value       = p.usd || '';\n    document.getElementById('pmWeight').value    = p.weight || '';")
text = text.replace("['pmId','pmName','pmSub','pmDesc','pmImg','pmArs','pmUsd','pmUsdSell','pmBadge'].forEach", "['pmId','pmName','pmSub','pmDesc','pmImg','pmArs','pmUsd','pmWeight','pmUsdSell','pmBadge'].forEach")
text = text.replace("const usd   = parseFloat(document.getElementById('pmUsd').value) || null;", "const usd   = parseFloat(document.getElementById('pmUsd').value) || null;\n  const weight= parseFloat(document.getElementById('pmWeight').value) || null;")
text = text.replace("ars, usd, usdSell, activo: true", "ars, usd, weight, usdSell, activo: true")
text = text.replace("p.ars   = ars;  p.usd   = usd;   p.usdSell = usdSell;", "p.ars   = ars;  p.usd   = usd;   p.weight = weight; p.usdSell = usdSell;")

UPDATE_SUBS_OLD = '''  let options = [];
  if (cat === 'Celulares') {
    options = SUBTYPES.Celulares;
  } else if (['Electrónica', 'Audio', 'Accesorios', 'Computación', 'Smart TV'].includes(cat)) {
    options = SUBTYPES.Electrónica;
  } else {
    options = [{ id: 'unico', label: '-' }];
  }'''
UPDATE_SUBS_NEW = '''  let options = SUBTYPES(cat);'''
text = text.replace(UPDATE_SUBS_OLD, UPDATE_SUBS_NEW)

GET_CALC_OLD = '''function getCalculationResult(cat, sub, usdCost) {
  if (!settings.formulas) return null;
  const u = parseFloat(usdCost);
  if (!u || u <= 0 || !dollar) return null;
  
  let key = 'hogar_unico'; 
  
  if (cat === 'Celulares') {
    if (u > 300) {
      key = 'celular_' + (sub || 'slim') + '_high';
    } else {
      key = 'celular_' + (sub || 'slim');
    }
  } else if (cat === 'Electrónica' || ['Audio', 'Accesorios', 'Computación', 'Smart TV'].includes(cat)) {
    key = 'electronica_' + (sub || 'chico');
  }

  const rule = settings.formulas[key];
  if (!rule) return null;
  
  const pct = 1 + (rule.margin / 100);
  const baseUsd = (u * pct) + rule.add;
  const rawArs = baseUsd * dollar;
  const ars = Math.ceil(rawArs / 100) * 100;
  
  return { ars, baseUsd, rule, key };
}'''

GET_CALC_NEW = '''function getCalculationResult(catName, sub, usdCost, weightArg) {
  if (!settings.categories) return null;
  const u = parseFloat(usdCost);
  const w = parseFloat(weightArg) || 0;
  if (!u || u <= 0 || !dollar) return null;
  
  const c = settings.categories.find(x => x.name === catName);
  if (!c) return null;
  
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
     else return null;
  }

  const pct = 1 + (matchedRule.margin / 100);
  const baseUsd = (u * pct) + matchedRule.add;
  const rawArs = baseUsd * dollar;
  const ars = Math.ceil(rawArs / 100) * 100;
  
  return { ars, baseUsd, rule: matchedRule, key: catName + '_' + subtypeTarget };
}'''

text = text.replace(GET_CALC_OLD, GET_CALC_NEW)

text = text.replace(
'''  const usd = document.getElementById('pmUsd').value;
  const hint = document.getElementById('pmCalcHint');''',
'''  const usd = document.getElementById('pmUsd').value;
  const weight = document.getElementById('pmWeight')?.value || 0;
  const hint = document.getElementById('pmCalcHint');''')

text = text.replace("const res = getCalculationResult(cat, sub, usd);", "const res = getCalculationResult(cat, sub, usd, weight);")
text = text.replace("const res = getCalculationResult(p.cat, p.calcSub, p.usd);", "const res = getCalculationResult(p.cat, p.calcSub, p.usd, p.weight);")

FORMULAS_END_OLD = '''function saveFormulas() {
  Object.keys(settings.formulas).forEach(key => {
    const m = parseFloat(document.getElementById('f_margin_'+key).value) || 0;
    const a = parseFloat(document.getElementById('f_add_'+key).value) || 0;
    settings.formulas[key].margin = m;
    settings.formulas[key].add = a;
  });
  saveSettings();
  showToast('✅ Fórmulas actualizadas correctamente.');
}'''

CATEGORIES_JS_NEW = '''function renderCategoriesTable() {
  const tbody = document.getElementById('categoriesTableBody');
  if(!tbody || !settings.categories) return;
  const cats = settings.categories;
  
  tbody.innerHTML = cats.map(c => {
    const rulesSummary = (c.rules || []).map(r => {
       const opText = r.type === 'none' ? 'Siempre' : `${r.type==='price'?'Precio':'Peso'} ${r.op} ${r.val}`;
       return `[${r.subtype}] ${opText} ➜ +${r.margin}% +$${r.add}`;
    }).join('<br>');
    const subsSummary = (c.subtypes || []).map(s => s.label).join(', ') || 'Único';
    
    return `
      <tr>
        <td style="font-weight:700;font-size:13px">${c.icon} ${c.name}</td>
        <td style="font-size:11px;color:var(--text-2);max-width:200px;">${subsSummary}</td>
        <td style="font-size:10px;color:var(--text-3);line-height:1.4">${rulesSummary || 'Sin reglas'}</td>
        <td>
          <button class="btn btn-ghost btn-sm btn-icon" onclick="openCategoryModal('${c.id}')" title="Editar">✏️</button>
          <button class="btn btn-ghost btn-sm btn-icon" onclick="deleteCategory('${c.id}')" title="Eliminar" style="color:var(--red)">🗑</button>
        </td>
      </tr>
    `;
  }).join('');
}

function deleteCategory(id) {
   showConfirm('🗑 Eliminar Categoría', `¿Seguro que deseas eliminarla?`, () => {
      settings.categories = settings.categories.filter(c => c.id !== id);
      saveSettings();
      renderCategoriesTable();
      populateCatDropdowns();
   });
}

function openCategoryModal(id) {
  const mo = document.getElementById('categoryModal');
  const cat = settings.categories.find(c => c.id === id);
  document.getElementById('cmId').value = id || '';
  
  window._tempSubtypes = cat ? JSON.parse(JSON.stringify(cat.subtypes || [])) : [];
  window._tempRules = cat ? JSON.parse(JSON.stringify(cat.rules || [])) : [];
  
  document.getElementById('cmName').value = cat ? cat.name : '';
  document.getElementById('cmIcon').value = cat ? (cat.icon || '📦') : '📦';
  document.getElementById('catModalTitle').textContent = cat ? 'Editar Categoría' : 'Nueva Categoría';
  
  renderCmSubtypes();
  renderCmRules();
  
  mo.classList.add('show');
}

function renderCmSubtypes() {
   const ls = document.getElementById('cmSubtypesList');
   ls.innerHTML = window._tempSubtypes.map((s, i) => `
     <div style="display:flex;gap:8px;align-items:center;background:var(--surf-2);padding:10px;border-radius:var(--r-sm);border:1px solid var(--border)">
       <input type="text" class="form-input" placeholder="ID (ej: slim)" style="width:80px" value="${s.id}" onchange="window._tempSubtypes[${i}].id=this.value; renderCmRules();">
       <input type="text" class="form-input" placeholder="Label visible" style="flex:1" value="${s.label}" onchange="window._tempSubtypes[${i}].label=this.value">
       <button class="btn btn-ghost btn-sm btn-icon text-red" onclick="window._tempSubtypes.splice(${i},1); renderCmSubtypes(); renderCmRules();">✕</button>
     </div>
   `).join('');
}

function renderCmRules() {
   const ls = document.getElementById('cmRulesList');
   const subOpts = window._tempSubtypes.length > 0 ? window._tempSubtypes : [{id:'unico', label:'Único'}];
   
   ls.innerHTML = window._tempRules.map((r, i) => {
      const typeOpts = `
         <option value="none" ${r.type==='none'?'selected':''}>Siempre</option>
         <option value="price" ${r.type==='price'?'selected':''}>Precio (U$D)</option>
         <option value="weight" ${r.type==='weight'?'selected':''}>Peso (kg)</option>
      `;
      const opOpts = `
         <option value="<=" ${r.op==='<='?'selected':''}>&le;</option>
         <option value=">=" ${r.op==='>='?'selected':''}>&ge;</option>
         <option value="<" ${r.op==='<'?'selected':''}>&lt;</option>
         <option value=">" ${r.op==='>'?'selected':''}>&gt;</option>
      `;
      const sOpts = subOpts.map(so => `<option value="${so.id}" ${r.subtype===so.id?'selected':''}>${so.id}</option>`).join('');
      
      return `
      <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;background:var(--surf-2);padding:10px;border-radius:var(--r-sm);border:1px solid var(--border)">
         <div>
            <div style="font-size:10px;color:var(--text-3);margin-bottom:2px">Aplica a:</div>
            <select class="form-select" style="padding:6px;font-size:12px;height:auto" onchange="window._tempRules[${i}].subtype=this.value">${sOpts}</select>
         </div>
         <div>
            <div style="font-size:10px;color:var(--text-3);margin-bottom:2px">Condición:</div>
            <div style="display:flex;gap:4px">
               <select class="form-select" style="padding:6px;font-size:12px;height:auto;width:95px" onchange="window._tempRules[${i}].type=this.value; renderCmRules()">${typeOpts}</select>
               ${r.type !== 'none' ? `
               <select class="form-select" style="padding:6px;font-size:12px;height:auto;width:50px" onchange="window._tempRules[${i}].op=this.value">${opOpts}</select>
               <input type="number" class="form-input" style="padding:6px;font-size:12px;height:auto;width:60px" value="${r.val||0}" onchange="window._tempRules[${i}].val=parseFloat(this.value)">
               ` : ''}
            </div>
         </div>
         <div>
            <div style="font-size:10px;color:var(--text-3);margin-bottom:2px">Margen (+%)</div>
            <input type="number" class="form-input" style="padding:6px;font-size:12px;height:auto;width:70px" value="${r.margin}" onchange="window._tempRules[${i}].margin=parseFloat(this.value)||0">
         </div>
         <div>
            <div style="font-size:10px;color:var(--text-3);margin-bottom:2px">Cargo (+USD)</div>
            <input type="number" class="form-input" style="padding:6px;font-size:12px;height:auto;width:70px" value="${r.add}" onchange="window._tempRules[${i}].add=parseFloat(this.value)||0">
         </div>
         <button class="btn btn-ghost btn-sm btn-icon text-red" style="margin-top:14px" onclick="window._tempRules.splice(${i},1); renderCmRules();">✕</button>
      </div>`
   }).join('');
}

function addCategorySubtype() {
   window._tempSubtypes.push({id:'', label:''});
   renderCmSubtypes();
}

function addCategoryRule() {
   const st = window._tempSubtypes.length ? window._tempSubtypes[0].id : 'unico';
   window._tempRules.push({subtype:st, type:'none', op:'<=', val:0, margin:0, add:0});
   renderCmRules();
}

function closeCategoryModal() {
   document.getElementById('categoryModal').classList.remove('show');
}

function saveCategory() {
   const cmId = document.getElementById('cmId').value;
   const name = document.getElementById('cmName').value.trim();
   const icon = document.getElementById('cmIcon').value.trim() || '📦';
   
   if (!name) return showToast('El nombre de categoría es obligatorio', 'error');
   
   const newId = cmId || name.toLowerCase().replace(/\\s+/g, '-').replace(/[^a-z0-9\\-]/g,'');
   
   // Clean up sub/rules empty
   const validSubs = window._tempSubtypes.filter(s => s.id && s.label);
   
   const newCat = {
      id: newId,
      name, icon,
      subtypes: validSubs,
      rules: window._tempRules
   };
   
   if (cmId) {
      const idx = settings.categories.findIndex(c => c.id === cmId);
      if (idx !== -1) settings.categories[idx] = newCat;
   } else {
      settings.categories.push(newCat);
   }
   
   saveSettings();
   closeCategoryModal();
   renderCategoriesTable();
   populateCatDropdowns();
   showToast('✅ Categoría guardada');
}
'''
text = text.replace(FORMULAS_END_OLD, CATEGORIES_JS_NEW)
text = text.replace("function renderFormulasTable() {", "function renderFormulasTable_OLD() {")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated admin.html successfully!')
