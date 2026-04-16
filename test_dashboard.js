const fs = require('fs');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;

const html = fs.readFileSync('g:/Mi unidad/Globalshop/Catalogo - Comrpa directa/admin.html', 'utf8');

const dom = new JSDOM(html, {
  url: "https://example.org/",
  referrer: "https://example.com/",
  contentType: "text/html",
  includeNodeLocations: true,
  storageQuota: 10000000
});

const window = dom.window;
global.window = window;
global.document = window.document;
global.localStorage = {
  getItem: () => null,
  setItem: () => {}
};
global.sessionStorage = {
  getItem: () => 'true'
};
global.fetch = () => Promise.resolve({ json: () => Promise.resolve({ blue: { value_sell: 1000 } }) });

// extract scripts
const scripts = Array.from(window.document.querySelectorAll('script')).map(s => s.textContent);

try {
  for (let s of scripts) {
     if (s) {
       window.eval(s);
     }
  }
} catch (e) {
  console.log("Error evaluating script:", e);
}

try {
  window.initApp();
  console.log("initApp executed successfully");
} catch (e) {
  console.log("Error during initApp:", e);
}
