"""Read a tabletop model's GLB and report what is in it: meshes, triangles, its size on the table, the tallest point,
and the credit and licence it carries. Standard library only.

    python3 method/check_model.py model/warm.glb

The model is in metres on the table, y up (glTF). Divide by the scale (1:6670 here) for real-world metres, and by the
height exaggeration (1.5) as well for real heights."""
import json, struct, sys


def read_glb(path):
    b = open(path, 'rb').read()
    magic, version, length = struct.unpack_from('<4sII', b, 0)
    if magic != b'glTF' or version != 2: raise SystemExit(f'{path}: not a glTF 2.0 binary')
    jlen, jtype = struct.unpack_from('<I4s', b, 12)
    gltf = json.loads(b[20:20 + jlen])
    return gltf, length


def main(path):
    g, size = read_glb(path)
    acc = g['accessors']
    tris, lo, hi = 0, [1e9] * 3, [-1e9] * 3
    for m in g['meshes']:
        for p in m['primitives']:
            n = acc[p['indices']]['count'] if 'indices' in p else acc[p['attributes']['POSITION']]['count']
            tris += n // 3
            a = acc[p['attributes']['POSITION']]
            lo = [min(x, y) for x, y in zip(lo, a['min'])]; hi = [max(x, y) for x, y in zip(hi, a['max'])]
    across = max(hi[0] - lo[0], hi[2] - lo[2])
    print(f'{path}: {size / 1e6:.1f} MB, {len(g["meshes"])} meshes, {len(g.get("materials", []))} materials, {tris:,} triangles')
    print(f'on the table: {across * 100:.1f} cm across, {(hi[1] - lo[1]) * 100:.1f} cm from the underside of the slab to the top')
    asset = g.get('asset', {})
    print('copyright:', asset.get('copyright', '(none)'))
    lic = (asset.get('extras') or {}).get('licence') or (g.get('extras') or {}).get('licence')
    if lic: print('licence:', lic)


if __name__ == '__main__':
    if len(sys.argv) < 2: raise SystemExit(__doc__)
    for f in sys.argv[1:]: main(f)
