# Tests ORDRE-005 (petits pays touchables, recherche) au format iPhone (390×844), en mode démo — voir le compte rendu de docs/ordres/ORDRE-005.
# Usage : APP_DIR=<copie du site avec CONFIG vide> LIBS_DIR=<copies locales leaflet/maplibre/supabase-js/geojson> CHROMIUM_PATH=<chromium> python3 tests/test_ordre005_iphone.py <dossier de sortie>
import os, sys, mimetypes, urllib.parse, json
import numpy as np, cv2
from playwright.sync_api import sync_playwright
OUT = sys.argv[1]; ROOT = os.environ["APP_DIR"]; L = os.environ["LIBS_DIR"]
errs = []; results = []
MLJS = L + "/maplibre/package/dist/maplibre-gl.js"; MLCSS = L + "/maplibre/package/dist/maplibre-gl.css"
def setup(ctx, break_maplibre=False):
    def serve(route):
        path = urllib.parse.urlparse(route.request.url).path.lstrip("/") or "index.html"
        f = os.path.join(ROOT, path)
        if os.path.isfile(f): route.fulfill(path=f, content_type=mimetypes.guess_type(f)[0] or "application/octet-stream")
        else: route.fulfill(status=404, body="")
    ctx.route("http://nos-voyages.test/**", serve)
    mocks = {
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js": (L + "/leaflet-1.9.4/package/dist/leaflet.js", "application/javascript"),
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css": (L + "/leaflet-1.9.4/package/dist/leaflet.css", "text/css"),
        "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2": (L + "/supabase-supabase-js-2.117.3/package/dist/umd/supabase.js", "application/javascript"),
        "https://cdn.jsdelivr.net/npm/maplibre-gl@5.24.0/dist/maplibre-gl.css": (MLCSS, "text/css"),
    }
    for url, (f, ct) in mocks.items():
        ctx.route(url, (lambda f, ct: lambda r: r.fulfill(path=f, content_type=ct))(f, ct))
    for url in ["https://cdn.jsdelivr.net/npm/maplibre-gl@5.24.0/dist/maplibre-gl.js", "https://unpkg.com/maplibre-gl@5.24.0/dist/maplibre-gl.js"]:
        if break_maplibre: ctx.route(url, lambda r: r.fulfill(status=404, body=""))
        else: ctx.route(url, lambda r: r.fulfill(path=MLJS, content_type="application/javascript"))
    ctx.route("**/ne_50m_admin_0_countries.geojson", lambda r: r.fulfill(path=L + "/ne50.geojson", content_type="application/json", headers={"Access-Control-Allow-Origin": "*"}))
def page(b, tag, seed=None, **kw):
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers="block")
    setup(ctx, **kw); pg = ctx.new_page()
    pg.on("console", lambda m: m.type == "error" and errs.append(f"[{tag}] {m.text}"))
    pg.on("pageerror", lambda e: errs.append(f"[{tag}] {e}"))
    if seed: pg.add_init_script(f"localStorage.setItem('nos-voyages-demo', {json.dumps(json.dumps(seed))})")
    return pg
def check(name, cond): results.append(cond); print(("OK   " if cond else "ÉCHEC"), name); return cond
def shot(pg, name=None):
    buf = pg.screenshot(path=f"{OUT}/{name}.png" if name else None)
    return cv2.imdecode(np.frombuffer(buf, np.uint8), cv2.IMREAD_COLOR)
def diff(a, b, y0=0, y1=844): return float(np.abs(a[y0*2:y1*2].astype(int) - b[y0*2:y1*2].astype(int)).mean())
def px(img, x, y): return img[y*2-4:y*2+4, x*2-4:x*2+4].reshape(-1, 3).mean(0)[::-1].round()  # RGB
def centroid(img, hexc, y0=120, y1=380, tol=30):
    h = np.array([int(hexc[i:i+2], 16) for i in (5, 3, 1)])  # BGR
    zone = img[y0*2:y1*2].astype(int); m = (np.abs(zone - h).max(2) < tol)
    ys, xs = np.nonzero(m); return (xs.mean() / 2, ys.mean() / 2 + y0) if len(xs) > 200 else None
def near(c, hexc, tol=40): h = [int(hexc[i:i+2], 16) for i in (1, 3, 5)]; return all(abs(c[i] - h[i]) < tol for i in range(3))

seed = {"countries":[{"code":c,"name":c,"status":"dream","places":""} for c in ("MDV","MLT","SGP")],"memories":[],"photos":[]}
GOLD, PINK = "#f3d27a", "#ff7a8a"
def blobs(img, hexc, tol=40, y0=100, y1=760):
    h = np.array([int(hexc[i:i+2], 16) for i in (5, 3, 1)])
    m = (np.abs(img.astype(int) - h).max(2) < tol).astype(np.uint8); m[:y0*2] = 0; m[y1*2:] = 0
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    return [(cen[i][0] / 2, cen[i][1] / 2, st[i][4]) for i in range(1, n) if st[i][4] >= 6]
def h2(pg): return pg.inner_text("#sheetBody h2") if pg.locator("#sheet.open").count() else None
def search(pg, q):
    pg.click("#listBtn"); pg.wait_for_timeout(500); pg.fill("#search", q); pg.wait_for_timeout(300)
def goto(pg, q, name):
    search(pg, q); pg.click(f"#listBody .list-item:has-text('{name}')"); pg.wait_for_timeout(2300)
def close(pg):
    if pg.locator("#sheet.open").count(): pg.click("#closeSheet"); pg.wait_for_timeout(900)
def zoom_out(pg, x=195, y=261, steps=8):
    # vue d'ensemble : bouton 🌍, puis une touche dans l'espace (hors du globe) arrête la rotation
    pg.click("#worldBtn"); pg.wait_for_timeout(1400); pg.mouse.click(12, 720); pg.wait_for_timeout(600)
def tap_blob(pg, img, hexc, label, near_xy=None):
    bl = blobs(img, hexc)
    if near_xy: bl.sort(key=lambda b: (b[0]-near_xy[0])**2 + (b[1]-near_xy[1])**2)
    if not bl: return None
    x, y, _ = bl[0]; pg.mouse.click(x, y); pg.wait_for_timeout(900); r = h2(pg); close(pg); return r

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=os.environ["CHROMIUM_PATH"], proxy={"server": os.environ["HTTPS_PROXY"]},
                          args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    for mode, base in (("globe", "http://nos-voyages.test/"), ("plate", "http://nos-voyages.test/?carte=plate")):
        pg = page(b, mode, seed)
        pg.goto(base + "#admin"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(2500)
        pg.click("#loginForm button[type=submit]"); pg.wait_for_timeout(500)
        # 6. Recherche
        search(pg, "maldives"); r = pg.inner_text("#listBody")
        check(f"[{mode}] recherche « maldives » → Maldives", r.split("\n")[0].strip() == "Maldives" or "Maldives" in r.split("\n")[1:3])
        pg.fill("#search", "reunion"); pg.wait_for_timeout(300)
        check(f"[{mode}] recherche « reunion » → La Réunion", "La Réunion" in pg.inner_text("#listBody"))
        pg.fill("#search", "Côte"); pg.wait_for_timeout(300); r = pg.inner_text("#listBody")
        check(f"[{mode}] recherche « Côte » → Côte d'Ivoire", "Côte d" in r and "Ivoire" in r)
        pg.fill("#search", "zzz"); pg.wait_for_timeout(300)
        check(f"[{mode}] recherche sans résultat : message", "Aucun pays ne correspond" in pg.inner_text("#listBody"))
        pg.fill("#search", ""); pg.wait_for_timeout(300)
        check(f"[{mode}] champ vidé : liste habituelle", "Relire ta lettre" in pg.inner_text("#listBody"))
        fs = pg.eval_on_selector("#search", "e => [getComputedStyle(e).fontSize, e.getBoundingClientRect().height]")
        check(f"[{mode}] champ en 16 px, hauteur ≥ 44 ({fs})", fs[0] == "16px" and fs[1] >= 44)
        pg.fill("#search", "maldives"); pg.wait_for_timeout(300); shot(pg, f"ordre005-1-recherche-{mode}")
        pg.click("#listBody .list-item:has-text('Maldives')"); pg.wait_for_timeout(2300)
        check(f"[{mode}] toucher le résultat ouvre la fiche Maldives", h2(pg) == "Maldives")
        close(pg); arch = shot(pg, f"ordre005-2-archipel-{mode}")
        # 1. Globe / carte entière : toucher le point des Maldives (gold = rêve)
        if mode == "globe": zoom_out(pg)
        else: pg.click("#worldBtn"); pg.wait_for_timeout(800)
        w = shot(pg, f"ordre005-3-monde-{mode}")
        names = set()
        for (x, y, _) in blobs(w, GOLD):
            pg.mouse.click(x, y); pg.wait_for_timeout(800); names.add(h2(pg)); close(pg)
        check(f"[{mode}] vue d'ensemble : toucher les points dorés ouvre {sorted(n for n in names if n)}", "Maldives" in names)
        # 2 + 8. Marquer les Maldives visitées (mode édition) → point rose visible vue d'ensemble
        goto(pg, "maldives", "Maldives"); pg.click("text=❤️ Visité"); pg.wait_for_timeout(700); close(pg); pg.wait_for_timeout(2500)  # le message « Ajouté… » disparaît
        at = shot(pg, f"ordre005-4-atolls-roses-{mode}")
        check(f"[{mode}] atolls roses au zoom ({len(blobs(at, PINK))} taches)", len(blobs(at, PINK)) >= 1)
        # 3. toucher à côté d'un atoll éloigné du centre (≤ 16 px) → Maldives
        far = sorted(blobs(at, PINK), key=lambda b: -((b[0]-195)**2 + (b[1]-261)**2))
        if far:
            x, y, _ = far[0]; tx = x + 12 if x < 300 else x - 12
            pg.mouse.click(tx, y); pg.wait_for_timeout(900)
            check(f"[{mode}] toucher à 12 px d'un atoll ({x:.0f},{y:.0f}) ouvre les Maldives", h2(pg) == "Maldives"); close(pg)
        if mode == "globe": zoom_out(pg)
        else: pg.click("#worldBtn"); pg.wait_for_timeout(800)
        w2 = shot(pg, f"ordre005-5-maldives-visitees-{mode}")
        pk = blobs(w2, PINK)
        check(f"[{mode}] vue d'ensemble : Maldives visitées = point rose visible ({len(pk)})", len(pk) >= 1)
        if pk:
            pk.sort(key=lambda b: -b[2]); pg.mouse.click(pk[0][0], pk[0][1]); pg.wait_for_timeout(800)
            check(f"[{mode}] toucher le point rose ouvre les Maldives ({h2(pg)})", h2(pg) == "Maldives"); close(pg)
        # 4. Malte et Singapour : zoom sur le pays, toucher le point
        for q, name in (("malte", "Malte"), ("singapour", "Singapour")):
            goto(pg, q, name); close(pg)
            pg.mouse.click(195, 261); pg.wait_for_timeout(900)
            check(f"[{mode}] {name} : toucher au centre du cadrage ouvre la fiche ({h2(pg)})", h2(pg) == name); close(pg)
            pg.mouse.click(195 + 14, 261 - 10); pg.wait_for_timeout(900)
            check(f"[{mode}] {name} : toucher à ~17 px du point ouvre aussi la fiche ({h2(pg)})", h2(pg) == name); close(pg)
        if mode == "globe":
            # Malte vue d'ensemble (point doré à côté de la Sicile)
            goto(pg, "italie", "Italie"); close(pg); zoom_out(pg, steps=6); it = shot(pg, "ordre005-6-malte-monde")
            mt = blobs(it, GOLD)
            if mt:
                mt.sort(key=lambda b: -b[2]); pg.mouse.click(mt[0][0], mt[0][1]); pg.wait_for_timeout(800)
                check(f"[globe] vue d'ensemble : toucher le point de Malte ({h2(pg)})", h2(pg) == "Malte"); close(pg)
            # 5. Non-régression : grands pays, océan, glissement
            for q, name in (("france", "France"), ("italie", "Italie"), ("belgique", "Belgique")):
                goto(pg, q, name); close(pg); pg.mouse.click(195, 261); pg.wait_for_timeout(900)
                check(f"[globe] toucher le centre de {name} ouvre {name} ({h2(pg)})", h2(pg) == name); close(pg)
            # vue d'ensemble : chaque grand pays, marqué visité, est repéré en rose puis touché en son centre
            for q, name, xy in (("france", "France", (172, 366)), ("italie", "Italie", (196, 380)), ("belgique", "Belgique", (181, 346))):
                goto(pg, q, name); pg.click("text=❤️ Visité"); pg.wait_for_timeout(600); close(pg); pg.wait_for_timeout(2500)
                zoom_out(pg); v = shot(pg, f"ordre005-7-monde-{q}")
                bl = sorted(blobs(v, PINK), key=lambda b: (b[0]-xy[0])**2 + (b[1]-xy[1])**2)
                got = None
                if bl: pg.mouse.click(bl[0][0], bl[0][1]); pg.wait_for_timeout(900); got = h2(pg); close(pg)
                check(f"[globe] vue d'ensemble : toucher le centre de {name} ouvre {name} ({got})", got == name)
                goto(pg, q, name); pg.click("text=Pas encore"); pg.wait_for_timeout(600); close(pg)
            o = shot(pg)
            ocean = np.array([0x33, 0x1b, 0x16])
            spot = None
            for y in range(200, 740, 8):
                for x in range(40, 350, 8):
                    zone = o[(y-20)*2:(y+20)*2, (x-20)*2:(x+20)*2].astype(int)
                    if zone.size and (np.abs(zone - ocean).max(2) < 6).all(): spot = (x, y); break
                if spot: break
            # le point doit être sur le globe : l'espace autour a des étoiles / dégradé, l'océan est uni #161b33
            if spot:
                pg.mouse.click(*spot); pg.wait_for_timeout(900)
                check(f"[globe] toucher en plein océan {spot} n'ouvre rien", pg.locator("#sheet.open").count() == 0); close(pg)
            pg.mouse.move(120, 400); pg.mouse.down(); pg.mouse.move(200, 420, steps=8); pg.mouse.move(280, 430, steps=8); pg.mouse.up(); pg.wait_for_timeout(900)
            check("[globe] faire tourner le globe d'un glissement n'ouvre rien", pg.locator("#sheet.open").count() == 0)
        pg.context.close()
    b.close()
print("Erreurs console :", *(errs or ["aucune"]), sep="\n  ")
print(f"{sum(results)}/{len(results)} vérifications réussies")
