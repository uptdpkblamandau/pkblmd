"""Membuat galeri.json dari isi folder gambar/galeri, dan mengecilkan foto yang terlalu besar.

Susunan folder:
  gambar/galeri/gedung-dan-ruangan/            -> foto gedung dan ruangan
  gambar/galeri/alat-uji/                      -> foto alat uji
  gambar/galeri/kegiatan/<nama-kegiatan>/      -> satu folder = satu sub kegiatan
Nama folder / nama file jadi judul / keterangan (tanda - dan _ jadi spasi).
Awalan angka 1-2 digit (01-, 02-) dipakai untuk mengatur urutan dan tidak ditampilkan.
"""
import json, os, re, sys
from urllib.parse import quote
from PIL import Image, ImageOps

ROOT = 'gambar/galeri'
MAKS = 1280                      # sisi terpanjang foto (piksel)
EXT = ('.jpg', '.jpeg', '.png', '.webp')


def natural(t):
    return [int(x) if x.isdigit() else x.casefold() for x in re.split(r'(\d+)', t)]


def bersih(nama):
    nama = os.path.splitext(nama)[0]
    nama = re.sub(r'^\d{1,2}[-_ ]+', '', nama)
    nama = re.sub(r'[-_]+', ' ', nama).strip()
    return ' '.join(w[:1].upper() + w[1:] for w in nama.split())


def judul_foto(nama):
    b = bersih(nama)
    if re.fullmatch(r'(?i)(img|dsc|dscn|pxl|wa|photo|image|foto|screenshot)?[\s\d_().-]*', b):
        return ''                # nama bawaan kamera/WA: tidak dijadikan keterangan
    return b


def kecilkan(path):
    try:
        im = Image.open(path)
        besar = max(im.size) > MAKS
        ada_exif = bool(im.getexif())
        if not (besar or ada_exif):
            return
        fmt = (im.format or 'JPEG').upper()
        im = ImageOps.exif_transpose(im)
        if besar:
            im.thumbnail((MAKS, MAKS), Image.LANCZOS)
        if fmt == 'PNG':
            im.save(path, 'PNG', optimize=True)
        elif fmt == 'WEBP':
            im.save(path, 'WEBP', quality=80)
        else:
            im.convert('RGB').save(path, 'JPEG', quality=80, optimize=True)   # tanpa EXIF/lokasi
        print('dikecilkan:', path)
    except Exception as e:
        print('GAGAL:', path, e)


def foto_di(folder):
    hasil = []
    if not os.path.isdir(folder):
        return hasil
    for n in sorted(os.listdir(folder), key=natural):
        p = os.path.join(folder, n)
        if os.path.isfile(p) and n.lower().endswith(EXT):
            kecilkan(p)
            src = '/'.join(quote(x) for x in p.split(os.sep))
            hasil.append({'src': src, 'cap': judul_foto(n)})
    return hasil


data = {
    'gedung': foto_di(os.path.join(ROOT, 'gedung-dan-ruangan')),
    'alat': foto_di(os.path.join(ROOT, 'alat-uji')),
    'kegiatan': [],
}
kg = os.path.join(ROOT, 'kegiatan')
if os.path.isdir(kg):
    for n in sorted(os.listdir(kg), key=natural):
        if os.path.isdir(os.path.join(kg, n)):
            f = foto_di(os.path.join(kg, n))
            if f:
                data['kegiatan'].append({'judul': bersih(n), 'foto': f})

with open('galeri.json', 'w', encoding='utf-8') as fh:
    json.dump(data, fh, ensure_ascii=False, indent=1)
print('galeri.json:', len(data['gedung']), 'gedung,', len(data['alat']), 'alat,', len(data['kegiatan']), 'kegiatan')
