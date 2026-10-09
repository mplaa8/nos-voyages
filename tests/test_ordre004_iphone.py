# Tests ORDRE-004 (outre-mer, apostrophes) au format iPhone (390×844), en mode démo — voir le compte rendu de docs/ordres/ORDRE-004.
# Usage : APP_DIR=<copie du site avec CONFIG vide> LIBS_DIR=<copies locales leaflet/maplibre/supabase-js/geojson> CHROMIUM_PATH=<chromium> python3 tests/test_ordre004_iphone.py <dossier de sortie>
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
demo = {"countries":[{"code":"FRA","name":"France","status":"visited","places":""},{"code":"ITA","name":"Italie","status":"visited","places":""},{"code":"JPN","name":"Japon","status":"visited","places":""},{"code":"USA","name":"États-Unis","status":"dream","places":""}],"memories":[],"photos":[]}
outre = {"countries":[{"code":"FRA","name":"France","status":"visited","places":""},{"code":"GUF","name":"Guyane","status":"visited","places":""},{"code":"REU","name":"La Réunion","status":"dream","places":""}],"memories":[],"photos":[]}
def pink_count(img, x0, x1, y0, y1):
    zone = img[y0*2:y1*2, x0*2:x1*2].astype(int); return int((np.abs(zone - np.array([138, 122, 255])).max(2) < 30).sum())
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=os.environ["CHROMIUM_PATH"], proxy={"server": os.environ["HTTPS_PROXY"]},
                          args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    # 6. Lettre + 1. globe : seule la métropole est rose
    pg = page(b, "globe", demo)
    pg.goto("http://nos-voyages.test/"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(2000)
    pg.click("#openGift"); pg.wait_for_timeout(3600)
    t = pg.inner_text("#letterText"); shot(pg, "ordre004-1-lettre-apostrophes")
    check("lettre : apostrophes typographiques (t’offrir, jusqu’à), aucune droite", "t’offrir" in t and "jusqu’à" in t and "'" not in t)
    pg.click("#letterBtn"); pg.wait_for_timeout(1600)
    g = shot(pg, "ordre004-2-globe-metropole")
    check(f"globe : rien de rose côté Antilles/Guyane ({pink_count(g, 0, 150, 380, 600)} px)", pink_count(g, 0, 150, 380, 600) == 0)
    check(f"globe : la métropole est rose ({pink_count(g, 150, 330, 300, 460)} px)", pink_count(g, 150, 330, 300, 460) > 50)
    # 4. Vol vers la France : cadrage sur la métropole
    pg.click("#listBtn"); pg.wait_for_timeout(600); pg.click(".list-item:has-text('France')"); pg.wait_for_timeout(2200)
    pg.click("#closeSheet"); pg.wait_for_timeout(900); fr = shot(pg, "ordre004-3-vol-france")
    c = centroid(fr, "#ff7a8a", 100, 422)
    check(f"vol vers la France cadré sur la métropole (centre du rose {c})", c and 120 < c[0] < 300 and 150 < c[1] < 400)
    pg.context.close()
    for mode, url in (("globe", "http://nos-voyages.test/#admin"), ("plate", "http://nos-voyages.test/?carte=plate#admin")):
        pa = page(b, mode, outre)
        pa.goto(url); pa.wait_for_load_state("networkidle"); pa.wait_for_timeout(2500)
        check(f"[{mode}] bonne carte", pa.locator(".maplibregl-canvas" if mode == "globe" else ".leaflet-container").count() == 1)
        pa.click("#loginForm button[type=submit]"); pa.wait_for_timeout(500)
        pa.click("#listBtn"); pa.wait_for_timeout(600)
        st = pa.inner_text(".list-stats"); check(f"[{mode}] stats France + Guyane : « {st} »", st == "2 pays · 2 continents découverts ensemble")
        # 2. Guyane : fiche indépendante
        pa.click(".list-item:has-text('Guyane')"); pa.wait_for_timeout(2200)
        check(f"[{mode}] fiche « Guyane » ({pa.inner_text('#sheetBody h2')})", pa.inner_text("#sheetBody h2") == "Guyane")
        pa.click("#closeSheet"); pa.wait_for_timeout(900); shot(pa, f"ordre004-4-guyane-{mode}")
        pa.mouse.click(195, 261); pa.wait_for_timeout(900)
        check(f"[{mode}] toucher la Guyane ouvre sa fiche ({pa.inner_text('#sheetBody h2') if pa.locator('#sheet.open').count() else 'rien'})", pa.locator("#sheet.open").count() == 1 and pa.inner_text("#sheetBody h2") == "Guyane")
        pa.click("#closeSheet"); pa.wait_for_timeout(500)
        pa.click("#listBtn"); pa.wait_for_timeout(600); pa.click(".list-item:has-text('France')"); pa.wait_for_timeout(2200)
        check(f"[{mode}] la France garde sa propre fiche", pa.inner_text("#sheetBody h2") == "France")
        pa.click("#closeSheet"); pa.wait_for_timeout(500)
        # 3. La Réunion : rêve -> visitée
        pa.click("#listBtn"); pa.wait_for_timeout(600); pa.click(".list-item:has-text('La Réunion')"); pa.wait_for_timeout(2200)
        pa.click("text=❤️ Visité"); pa.wait_for_timeout(700); pa.click("#closeSheet"); pa.wait_for_timeout(900)
        r = shot(pa, f"ordre004-5-reunion-{mode}")
        check(f"[{mode}] La Réunion devient rose ({pink_count(r, 150, 240, 220, 300)} px)", pink_count(r, 150, 240, 220, 300) > 20)
        pa.click("#listBtn"); pa.wait_for_timeout(600)
        st = pa.inner_text(".list-stats"); shot(pa, f"ordre004-6-stats-{mode}")
        check(f"[{mode}] stats : « {st} »", st == "3 pays · 3 continents découverts ensemble")
        pa.context.close()
    b.close()
print("Erreurs console :", *(errs or ["aucune"]), sep="\n  ")
print(f"{sum(results)}/{len(results)} vérifications réussies")
