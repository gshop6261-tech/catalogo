import json

f = 'g:/Mi unidad/Globalshop/Catalogo - Comrpa directa/admin.html'
with open(f, 'r', encoding='utf-8') as fi:
    content = fi.read()

# Fix the replacement
content = content.replace('<div class="stats-grid">\n    ${CATS().map(c => `', '</div>\n    ${CATS().map(c => `')
content = content.replace('${CATS.map(', '${CATS().map(')

with open(f, 'w', encoding='utf-8') as fo:
    fo.write(content)

print("Dashboard fixed.")
