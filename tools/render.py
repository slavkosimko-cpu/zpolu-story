#!/usr/bin/env python3
"""Zpolu last minute story: vpíše 3 ponuky do zelenej šablóny.
Použitie: python3 render.py template.png Oswald.ttf offers.json out.png
offers.json: {"datum":"15.10.2026","ponuky":[{"destinacia":"Egypt – Hurghada","hotel":"Hotel X","hviezdy":4,
 "cena":"499","termin":"22.10.","noci":7,"strava":"All inclusive","odlet":"Bratislava"}, ... spolu 3]}
Lyžovačka/autobus: namiesto "odlet" daj "doprava":"autobus" alebo "doprava":"vlastná".
"""
import json, sys
from PIL import Image, ImageDraw, ImageFont

tpl, fontpath, data_path, out = sys.argv[1:5]
data = json.load(open(data_path, encoding="utf-8"))
im = Image.open(tpl).convert("RGB")
d = ImageDraw.Draw(im)

GREEN = (14, 64, 40)
BOX = (8, 58, 36)
GOLD = (201, 155, 52)
CREAM_TXT = (250, 246, 232)
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TOPS = [424, 808, 1191]


def font(size, weight=700):
    f = ImageFont.truetype(fontpath, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def fit(text, maxw, size, weight=700, minsize=18):
    while size > minsize:
        f = font(size, weight)
        if d.textlength(text, font=f) <= maxw:
            return f
        size -= 1
    return font(minsize, weight)


def building(x, y):  # ľavý horný roh, 40x46
    d.rectangle((x, y, x + 40, y + 46), fill=GOLD)
    for r in range(4):
        for c in range(3):
            wx, wy = x + 6 + c * 11, y + 6 + r * 9
            d.rectangle((wx, wy, wx + 6, wy + 5), fill=CREAM_TXT)
    d.rectangle((x + 15, y + 38, x + 25, y + 46), fill=CREAM_TXT)


def calendar(x, y):  # 36x36
    d.rounded_rectangle((x, y, x + 36, y + 36), radius=5, outline=GOLD, width=4)
    d.rectangle((x, y, x + 36, y + 9), fill=GOLD)
    for r in range(2):
        for c in range(3):
            d.rectangle((x + 7 + c * 9, y + 15 + r * 8, x + 11 + c * 9, y + 19 + r * 8), fill=GOLD)


for T, p in zip(TOPS, data["ponuky"]):
    cream = im.getpixel((1000, T + 20))
    d.rectangle((432, T + 14, 1046, T + 343), fill=cream)

    # destinácia
    dest = p["destinacia"].upper()
    d.text((452, T + 78), dest, font=fit(dest, 590, 84), fill=GREEN, anchor="lm")

    # hotel + hviezdičky
    building(446, T + 150)
    fh = fit(p["hotel"], 265, 34, 500)
    d.text((500, T + 168), p["hotel"], font=fh, fill=GREEN, anchor="lm")
    n = int(p.get("hviezdy") or 0)
    if n:
        d.text((500, T + 212), "★" * n, font=ImageFont.truetype(DEJAVU, 28), fill=GOLD, anchor="lm")

    # cena
    d.rounded_rectangle((785, T + 133, 1040, T + 263), radius=24, fill=BOX, outline=GOLD, width=5)
    d.text((912, T + 162), "od", font=font(30, 500), fill=CREAM_TXT, anchor="mm")
    price = f'{p["cena"]} €'
    d.text((912, T + 214), price, font=fit(price, 225, 64), fill=CREAM_TXT, anchor="mm")

    # termín • noci • strava • ✈ odlet
    calendar(448, T + 293)
    head = "  •  ".join([p["termin"], f'{p["noci"]} nocí', p["strava"]]) + "  •  "
    # letecky: "odlet": "Bratislava"; inak (lyžovačka, autobus): "doprava": "autobus" / "vlastná"
    if p.get("odlet"):
        icon, tail = "✈", f'odlet {p["odlet"]}'
    else:
        icon, tail = "", f'doprava {p.get("doprava", "vlastná")}'
    size = 34
    while True:
        fl, pf = font(size, 500), ImageFont.truetype(DEJAVU, size)
        w = d.textlength(head, font=fl) + (d.textlength(icon + " ", font=pf) if icon else 0) + d.textlength(tail, font=fl)
        if w <= 545 or size <= 18:
            break
        size -= 1
    x, y = 498, T + 311
    d.text((x, y), head, font=fl, fill=GREEN, anchor="lm"); x += d.textlength(head, font=fl)
    if icon:
        d.text((x, y), icon, font=pf, fill=GOLD, anchor="lm"); x += d.textlength(icon + " ", font=pf)
    d.text((x, y), tail, font=fl, fill=GREEN, anchor="lm")

# spodný riadok: prekryť pôvodný text plynulým prechodom
y0, y1 = 1834, 1882
for x in range(232, 848):
    a, b = im.getpixel((x, y0)), im.getpixel((x, y1))
    for y in range(y0, y1 + 1):
        t = (y - y0) / (y1 - y0)
        im.putpixel((x, y), tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3)))
note = f'Ceny za osobu, platné k {data["datum"]}, do vypredania.'
d.text((540, 1858), note, font=font(32, 400), fill=(255, 255, 255), anchor="mm")

im.save(out, optimize=True)
print("OK", out)
