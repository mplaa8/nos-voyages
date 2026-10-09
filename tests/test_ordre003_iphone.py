# Tests ORDRE-003 (globe) au format iPhone (390×844), en mode démo — voir le compte rendu de docs/ordres/ORDRE-003.
# Usage : APP_DIR=<copie du site avec CONFIG vide> LIBS_DIR=<copies locales leaflet/maplibre/supabase-js/geojson> CHROMIUM_PATH=<chromium> python3 tests/test_ordre003_iphone.py <dossier de sortie>
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
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=os.environ["CHROMIUM_PATH"], proxy={"server": os.environ["HTTPS_PROXY"]},
                          args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    # 1. Accueil -> lettre -> globe qui tourne
    pg = page(b, "globe", demo)
    pg.goto("http://nos-voyages.test/"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(2000)
    pg.click("#openGift"); pg.wait_for_timeout(3600); pg.click("#letterBtn"); pg.wait_for_timeout(1500)
    check("globe MapLibre actif (pas de Leaflet)", pg.locator(".maplibregl-canvas").count() == 1 and pg.locator(".leaflet-container").count() == 0)
    a = shot(pg, "ordre003-1-globe"); pg.wait_for_timeout(3000); bb = shot(pg)
    check(f"le globe tourne (écart d'image {diff(a, bb, 120, 760):.2f})", diff(a, bb, 120, 760) > .3)
    pg.wait_for_timeout(9000); shot(pg, "ordre003-2-globe-japon-usa")
    # 4 + 2. Vol vers la France depuis la liste
    pg.click("#listBtn"); pg.wait_for_timeout(700)
    pg.click(".list-item:has-text('France')"); pg.wait_for_timeout(2200)
    check("fiche France ouverte après le vol", pg.inner_text("#sheetBody h2") == "France")
    img = shot(pg, "ordre003-3-vol-france")
    c = px(img, 195, 261); check(f"France en rose (sous le voile de la fiche) au centre de la zone visible {c}", near(c, "#914858"))
    # 3. Fermer la fiche : pas de saut, pas de reprise de rotation
    before = shot(pg); pg.click("#closeSheet"); pg.wait_for_timeout(1200); after = shot(pg, "ordre003-4-europe")
    c0, c1 = centroid(before, "#914858"), centroid(after, "#ff7a8a")
    check(f"fermer la fiche ne déplace pas la vue (France avant {c0}, après {c1})", c0 and c1 and abs(c0[0]-c1[0]) < 4 and abs(c0[1]-c1[1]) < 4)
    pg.wait_for_timeout(2000); after2 = shot(pg)
    check(f"pas de rotation à ce zoom (écart {diff(after, after2):.2f})", diff(after, after2) < .2)
    # 3. Toucher un pays sur le globe ouvre sa fiche
    pg.mouse.click(195, 261); pg.wait_for_timeout(900)
    check(f"toucher un pays ouvre sa fiche ({pg.inner_text('#sheetBody h2')})", pg.locator("#sheet.open").count() == 1)
    pg.click("#closeSheet"); pg.wait_for_timeout(600)
    # 5. Bouton monde
    pg.click("#worldBtn"); pg.wait_for_timeout(1800); w1 = shot(pg, "ordre003-5-retour-monde"); pg.wait_for_timeout(2500); w2 = shot(pg)
    check(f"🌍 : retour au globe entier et reprise de la rotation (écart {diff(w1, w2, 120, 760):.2f})", diff(w1, w2, 120, 760) > .3)
    pg.click("#listBtn"); pg.wait_for_timeout(600); pg.click(".list-item:has-text('Japon')"); pg.wait_for_timeout(2200)
    pg.click("#closeSheet"); pg.wait_for_timeout(900); j = shot(pg, "ordre003-8-japon")
    check("Japon (Asie) affiché en rose", centroid(j, "#ff7a8a", 100, 422) is not None)
    # 7. #admin : changement de statut -> couleur immédiate
    pa = page(b, "admin", demo)
    pa.goto("http://nos-voyages.test/#admin"); pa.wait_for_load_state("networkidle"); pa.wait_for_timeout(2500)
    check("#admin : pas d'accueil ni de lettre", pa.locator("#welcome").count() == 0 and not pa.locator("#letter").is_visible())
    pa.click("#loginForm button[type=submit]"); pa.wait_for_timeout(500)
    check("mode édition actif", pa.locator("body.admin").count() == 1)
    pa.click("#listBtn"); pa.wait_for_timeout(600); pa.click(".list-item:has-text('France')"); pa.wait_for_timeout(2300)
    pa.click("text=✨ Un jour"); pa.wait_for_timeout(700); pa.click("#closeSheet"); pa.wait_for_timeout(900)
    c2 = px(shot(pa, "ordre003-6-admin-statut"), 195, 261)
    check(f"statut « Un jour » : France dorée {c2}", near(c2, "#f3d27a"))
    pa.mouse.click(195, 261); pa.wait_for_timeout(900); pa.click("text=❤️ Visité"); pa.wait_for_timeout(700); pa.click("#closeSheet"); pa.wait_for_timeout(900)
    c3 = px(shot(pa), 195, 261)
    check(f"retour à « Visité » : France rose {c3}", near(c3, "#ff7a8a"))
    # 6a. ?carte=plate
    pf = page(b, "plate", demo)
    pf.goto("http://nos-voyages.test/?carte=plate#admin"); pf.wait_for_load_state("networkidle"); pf.wait_for_timeout(2000)
    check("?carte=plate : carte Leaflet, pas de MapLibre", pf.locator(".leaflet-container").count() == 1 and pf.locator(".maplibregl-canvas").count() == 0)
    check("?carte=plate conservé après #admin", "carte=plate" in pf.url)
    pf.click("#loginCancel"); pf.click("#listBtn"); pf.wait_for_timeout(500); pf.click(".list-item:has-text('Japon')"); pf.wait_for_timeout(1500)
    check("carte plate : vol vers le Japon et fiche", pf.inner_text("#sheetBody h2") == "Japon")
    shot(pf, "ordre003-7-carte-plate")
    # 6b. MapLibre indisponible -> bascule automatique
    pk = page(b, "secours", demo, break_maplibre=True)
    pk.goto("http://nos-voyages.test/#admin"); pk.wait_for_load_state("networkidle"); pk.wait_for_timeout(2500)
    check("MapLibre en échec : bascule automatique sur la carte plate", pk.locator(".leaflet-container").count() == 1 and pk.locator("#mapLoading").count() == 0)
    # 2. Stats et lettre toujours là
    pk.click("#loginCancel"); pk.click("#listBtn"); pk.wait_for_timeout(500)
    check("statistiques intactes", pk.inner_text(".list-stats") == "3 pays · 2 continents découverts ensemble")
    b.close()
print("Erreurs console :", *(errs or ["aucune"]), sep="\n  ")
print(f"{sum(results)}/{len(results)} vérifications réussies")
