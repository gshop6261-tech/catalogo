"""
Extrae las 5 imagenes base64 embebidas en index-2.html y las guarda
como archivos JPG en images/banners/.

Se corre una sola vez (las imagenes ya extraidas quedan committeadas).
"""
import base64
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'index-2.html')
OUT_DIR = os.path.join(ROOT, 'images', 'banners')

FILENAMES = [
    '01-cockpit-redragon-vortex.jpg',
    '02-asus-rog-flow-z13.jpg',
    '03-rog-xbox-ally.jpg',
    '04-setup-gamer.jpg',
    '05-honor-magic8-lite.jpg',
]

PATTERN = re.compile(r'<img src="data:image/[^;]+;base64,([A-Za-z0-9+/=]+)"')


def main() -> int:
    if not os.path.exists(SRC):
        print(f'ERROR: no existe {SRC}', file=sys.stderr)
        return 1

    os.makedirs(OUT_DIR, exist_ok=True)

    found = 0
    with open(SRC, 'r', encoding='utf-8') as f:
        for line in f:
            m = PATTERN.search(line)
            if not m:
                continue
            if found >= len(FILENAMES):
                print(f'Aviso: encontrada imagen #{found+1} pero solo hay {len(FILENAMES)} nombres definidos', file=sys.stderr)
                break
            payload = m.group(1)
            binary = base64.b64decode(payload)
            out_path = os.path.join(OUT_DIR, FILENAMES[found])
            with open(out_path, 'wb') as out:
                out.write(binary)
            size_kb = len(binary) / 1024
            print(f'  OK  {FILENAMES[found]}  ({size_kb:.1f} KB)')
            found += 1

    if found != len(FILENAMES):
        print(f'ERROR: esperaba {len(FILENAMES)} imagenes, encontre {found}', file=sys.stderr)
        return 2

    print(f'\nListo: {found} imagenes en {OUT_DIR}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
