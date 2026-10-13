# ORDRE-009E — photos du jeu des envies : bannière Wikivoyage + photo principale de l'article Wikipédia des lieux de lieux-envies.json ;
# page revue-photos.html. Réponses Wikidata, Commons, Wikipédia et images simulées, iPhone 390×844 (et Mac 1280 pour la revue), mode démo.
# Usage : APP_DIR=<copie du site avec CONFIG vide> LIBS_DIR=<copies locales leaflet/maplibre/supabase-js/geojson> CHROMIUM_PATH=<chromium> python3 tests/test_photos_paysages.py <dossier de sortie>
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
def page(b, tag, seed=None, init=None, **kw):
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers="block")
    setup(ctx, **kw); pg = ctx.new_page()
    pg.on("console", lambda m: m.type == "error" and errs.append(f"[{tag}] {m.text}"))
    pg.on("pageerror", lambda e: errs.append(f"[{tag}] {e}"))
    if init: pg.add_init_script(init)
    if seed: pg.add_init_script(f"if (!localStorage.getItem('nos-voyages-demo')) localStorage.setItem('nos-voyages-demo', {json.dumps(json.dumps(seed))})")
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


import re
T = "2026-10-01T10:00:00Z"
def close_match(pg):
    while pg.locator("#match.show").count(): pg.click("#matchBtn"); pg.wait_for_timeout(500)
def h2(pg): return pg.inner_text("#sheetBody h2") if pg.locator("#sheet.open").count() else None
def who(pg, w): pg.click(f"#demoWho [data-who='{w}']"); pg.wait_for_timeout(500)
def top(pg): return pg.get_attribute("#gameStack .swipe.top", "data-code") if pg.locator("#gameStack .swipe.top").count() else None
def top_name(pg): return pg.inner_text("#gameStack .swipe.top h2")
def open_list(pg):
    close_match(pg)
    if pg.locator("#sheet.open").count(): pg.click("#closeSheet"); pg.wait_for_timeout(400)
    pg.click("#listBtn"); pg.wait_for_timeout(500)
def open_game(pg, region=None):
    open_list(pg); pg.click("[data-action=play]"); pg.wait_for_timeout(500)
    if region: pg.click(f"#gameFilters [data-region='{region}']"); pg.wait_for_timeout(300)
def swipe(pg, direction):
    b = pg.locator("#gameStack .swipe.top").bounding_box(); x, y = b["x"] + b["width"] / 2, b["y"] + b["height"] / 2
    pg.mouse.move(x, y); pg.mouse.down(); pg.mouse.move(x + 90 * direction, y + 10, steps=6)
    st = pg.locator("#gameStack .swipe.top .stamp." + ("yes" if direction > 0 else "no")).evaluate("e => getComputedStyle(e).opacity")
    pg.mouse.move(x + 220 * direction, y + 20, steps=6); pg.mouse.up(); pg.wait_for_timeout(500); return float(st)
def btn(pg, ans): pg.click("#gameYes" if ans == "oui" else "#gameNo"); pg.wait_for_timeout(450)
def answer_until(pg, target, ans, seen=None, max_n=60):
    for _ in range(max_n):
        c = top(pg)
        if c is None: return False
        if seen is not None: seen.append(c)
        if c == target: btn(pg, ans); return True
        btn(pg, "non")
    return False
def counter(pg): return pg.inner_text("#gameCount")




import hashlib, urllib.parse as up
def jpeg_bytes(seed):
    h = hashlib.md5(seed.encode()).digest(); img = np.zeros((450, 800, 3), np.uint8); img[:] = (h[0], h[1], h[2])
    cv2.circle(img, (400, 225), 120, (h[3], h[4], 255), -1); return cv2.imencode(".jpg", img)[1].tobytes()
CORS = {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"}
C = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/"
def th(f, w=960, h=640, base=C): fq = up.quote(f.replace(" ", "_")); return {"source": base + fq + "/960px-" + fq + (".png" if not f.lower().endswith((".jpg", ".jpeg")) else ""), "width": w, "height": h}
# Pages Wikipédia simulées (titre final → page)
PAGES = {
    "Mercury": {"pageprops": {"disambiguation": ""}, "thumbnail": th("Mercury planet.jpg"), "pageimage": "Mercury_planet.jpg"},      # homonymie
    "Png place": {"thumbnail": th("Place.png"), "pageimage": "Place.png"},                                                        # PNG
    "Svg place": {"thumbnail": th("Place.svg"), "pageimage": "Place.svg"},                                                        # SVG
    "Tall tower": {"thumbnail": th("Tall tower.jpg", 640, 960), "pageimage": "Tall_tower.jpg"},                                    # portrait
    "Square place": {"thumbnail": th("Square place.jpg", 960, 900), "pageimage": "Square_place.jpg"},                             # presque carrée (< 1,2)
    "Locator place": {"thumbnail": th("Testland locator map.jpg"), "pageimage": "Testland_locator_map.jpg"},                      # mots interdits
    "Montage place": {"thumbnail": th("Testland-montage-2020.jpg"), "pageimage": "Testland-montage-2020.jpg"},
    "Satellite place": {"thumbnail": th("Island (satellite view).jpg"), "pageimage": "Island_(satellite_view).jpg"},
    "No image": {},                                                                                                               # sans vignette
    "Local file": {"thumbnail": th("Poster.jpg", base="https://upload.wikimedia.org/wikipedia/en/thumb/a/ab/"), "pageimage": "Poster.jpg"},   # fichier non libre (hors Commons)
    "Titicaca Lake (test)": {"thumbnail": th("Lake Titicaca from space station.jpg"), "pageimage": "Lake_Titicaca_from_space_station.jpg"},
    "Chartres Cathedral": {"thumbnail": th("Chartres Cathedral 2008.jpg"), "pageimage": "Chartres_Cathedral_2008.jpg"},
    "Cartagena, Colombia": {"thumbnail": th("Cartagena walls.jpeg", 960, 720), "pageimage": "Cartagena_walls.jpeg"},
    "Mapungubwe": {"thumbnail": th("Mapungubwe hill.jpg"), "pageimage": "Mapungubwe_hill.jpg"},
}
NORMALIZED = {"lake_Titicaca": "Lake titicaca"}; REDIRECTS = {"Lake titicaca": "Titicaca Lake (test)", "Cartagena": "Cartagena, Colombia"}
PIEGES = [("Homonyme", "Mercury"), ("Plan PNG", "Png place"), ("Dessin SVG", "Svg place"), ("Tour verticale", "Tall tower"), ("Place carrée", "Square place"),
          ("Localisation", "Locator place"), ("Montage", "Montage place"), ("Vue satellite", "Satellite place"), ("Sans vignette", "No image"),
          ("Page absente", "Missing page"), ("Affiche locale", "Local file")]
JUSTES = [("Lac Titicaca", "lake_Titicaca"), ("Cathédrale de Chartres", "Chartres Cathedral"), ("Carthagène des Indes", "Cartagena"), ("Mapungubwe", "Mapungubwe")]
L_PIEGES = [{"nom_fr": n, "type": "culture", "wiki_en": w} for n, w in PIEGES]
L_TOUS = L_PIEGES + [{"nom_fr": n, "type": "paysage", "wiki_en": w} for n, w in JUSTES]
def wiki(pg_, mode, log, pending):
    def handler(route):
        u = up.urlparse(route.request.url); q = dict(up.parse_qsl(u.query)); host = u.hostname
        log.append(route.request.url)
        if mode == "slow" and host != "upload.wikimedia.org": pending.append(route); return
        if mode == "error" and host != "upload.wikimedia.org": return route.fulfill(status=500, body="")
        js = lambda o: route.fulfill(status=200, headers=CORS, body=json.dumps(o))
        if host == "www.wikidata.org" and q.get("action") == "wbgetclaims":
            if mode in ("full", "imgerror", "banniere"):
                return js({"claims": {"P948": [{"mainsnak": {"datavalue": {"value": "Normal banner.jpg", "type": "string"}}, "rank": "normal"},
                                               {"mainsnak": {"datavalue": {"value": "Preferred_banner.jpg", "type": "string"}}, "rank": "preferred"}]}})
            if mode == "badbanner": return js({"claims": {"P948": [{"mainsnak": {"datavalue": {"value": "Flag banner.jpg", "type": "string"}}, "rank": "normal"}]}})
            return js({"claims": {}})
        if host == "commons.wikimedia.org":
            pages = {}
            for i, t in enumerate(q.get("titles", "").split("|")):
                f = t.replace("File:", "").replace("_", " "); fq = up.quote(f.replace(" ", "_"))
                pages[str(-1 - i)] = {"title": "File:" + f, "imageinfo": [{"thumburl": C + fq + "/960px-" + fq, "url": "https://upload.wikimedia.org/wikipedia/commons/a/ab/" + fq,
                    "width": 2560, "height": 360, "extmetadata": {"Categories": {"value": "Wikivoyage banners"}, "Artist": {"value": '<a href="//x">Jean Dupont</a>'}}}]}
            return js({"batchcomplete": "", "query": {"pages": pages}})
        if host == "en.wikipedia.org":
            titles = q.get("titles", "").split("|"); norm_, red, pages = [], [], {}
            for i, t in enumerate(titles):
                if t in NORMALIZED: norm_.append({"from": t, "to": NORMALIZED[t]}); t = NORMALIZED[t]
                if t in REDIRECTS: red.append({"from": t, "to": REDIRECTS[t]}); t = REDIRECTS[t]
                if t in PAGES: pages[str(100 + i)] = {"pageid": 100 + i, "ns": 0, "title": t, **PAGES[t]}
                else: pages[str(-1 - i)] = {"ns": 0, "title": t, "missing": ""}
            qq = {"pages": pages}
            if norm_: qq["normalized"] = norm_
            if red: qq["redirects"] = red
            return js({"batchcomplete": "", "query": qq})
        if host == "upload.wikimedia.org":
            if mode == "imgerror" and "banner" in u.path: return route.fulfill(status=404, body="")
            return route.fulfill(status=200, headers={"Content-Type": "image/jpeg"}, body=jpeg_bytes(u.path))
        return route.fulfill(status=404, body="")
    for pat in ("https://www.wikidata.org/**", "https://query.wikidata.org/**", "https://*.wikivoyage.org/**", "https://*.wikipedia.org/**", "https://commons.wikimedia.org/**", "https://upload.wikimedia.org/**"):
        pg_.context.route(pat, handler)
def entities(log): return {dict(up.parse_qsl(up.urlparse(x).query)).get("entity") for x in log if "wbgetclaims" in x}
def wp_reqs(log): return [x for x in log if "en.wikipedia.org" in x]
def interdites(log): return [x for x in log if "media-list" in x or "query.wikidata.org" in x or "wikivoyage.org" in x or "fr.wikipedia.org" in x or "wbgetentities" in x]
def imgs(pg): return [up.unquote(s).split("/")[-1] for s in pg.locator("#gameStack .swipe.top .sw-photo img").evaluate_all("l => l.map(i => i.getAttribute('src'))")]
def tap_right(pg):
    box = pg.locator("#gameStack .swipe.top .sw-photo").bounding_box(); pg.mouse.click(box["x"] + box["width"] * .85, box["y"] + box["height"] / 2); pg.wait_for_timeout(500)

geo = json.load(open(os.environ["LIBS_DIR"] + "/ne50.geojson"))
TERR = ["GUF", "GLP", "MTQ", "REU", "MYT", "BES", "SJM"]
ALL = [f["properties"]["ADM0_A3"] for f in geo["features"]] + TERR
EXCLUS = {"ATA", "KAS", "HMD", "ATC", "IOT"}
# 0 : le fichier des lieux lui-même
data = json.load(open(os.environ["APP_DIR"] + "/lieux-envies.json", encoding="utf-8"))
check(f"lieux-envies.json : {len(data)} pays, {sum(len(v['lieux']) for v in data.values())} lieux, tous les codes sont ceux de la carte (Åland = ALD)",
      all(k in ALL for k in data) and "ALD" in data and all(v["lieux"] and all(l.get("wiki_en") and l.get("nom_fr") for l in v["lieux"]) for v in data.values()))

ALL_LOG = []; LIEUX_REQ = []
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=os.environ["CHROMIUM_PATH"], proxy={"server": os.environ["HTTPS_PROXY"]},
                          args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--unsafely-treat-insecure-origin-as-secure=http://nos-voyages.test"])
    def start(mode, tag, lieux=L_TOUS, refusees=None, off=False):
        log, pending = [], []
        pg = page(b, tag, {"countries": [], "memories": [], "photos": [], "picks": [], "wishes": []}, init="localStorage.setItem('nos-voyages-demo-who','demo-maxime')")
        wiki(pg, mode, log, pending); ALL_LOG.append(log)
        pg.route("http://nos-voyages.test/lieux-envies.json", lambda r: (LIEUX_REQ.append(tag), r.fulfill(status=200, content_type="application/json", body=json.dumps({c: {"pays": c, "lieux": lieux} for c in ALL}))))
        if off or refusees:
            html = open(os.environ["APP_DIR"] + "/index.html", encoding="utf-8").read()
            if off: html = html.replace("const PHOTOS_ENVIES = true;", "const PHOTOS_ENVIES = false;")
            if refusees: html = html.replace("const BANNIERES_REFUSEES = [];", "const BANNIERES_REFUSEES = " + json.dumps(refusees) + ";")
            pg.route("http://nos-voyages.test/index.html", lambda r: r.fulfill(body=html, content_type="text/html"))
        pg.goto("http://nos-voyages.test/index.html#admin"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(2000)
        if pg.locator("#loginModal.show").count(): pg.click("#loginCancel")
        return pg, log, pending
    # 1 : bannière + lieux dans l'ordre, pièges écartés
    pg, log, _ = start("full", "photos")
    check("aucune requête Wikimedia ni lieux avant d'ouvrir le jeu", len(log) == 0 and "photos" not in LIEUX_REQ)
    open_game(pg); pg.wait_for_selector("#gameStack .swipe.top.has-photo", timeout=6000); pg.wait_for_timeout(700)
    got = imgs(pg)
    check(f"bannière (1920 px) + 2 premiers lieux valides, dans l'ordre du fichier → {got}", len(got) == 3 and got[0] == "1920px-Preferred_banner.jpg" and "Lake_Titicaca" in got[1] and "Chartres" in got[2])
    cr = pg.locator("#gameStack .swipe.top .sw-credit").inner_text()
    check(f"crédit de la bannière : « {cr} »", cr == "Photo : Jean Dupont · Wikimedia Commons")
    pg.screenshot(path=f"{OUT}/009e-1-banniere.png")
    tap_right(pg); cr = pg.locator("#gameStack .swipe.top .sw-credit").inner_text()
    check(f"lieu légendé (nom français) : « {cr} »", cr == "📍 Lac Titicaca · Photo : Wikimedia Commons")
    pg.screenshot(path=f"{OUT}/009e-2-lieu.png")
    tap_right(pg); cr = pg.locator("#gameStack .swipe.top .sw-credit").inner_text()
    check(f"3e photo : « {cr} »", cr == "📍 Cathédrale de Chartres · Photo : Wikimedia Commons")
    w = wp_reqs(log)
    t0 = up.unquote(dict(up.parse_qsl(up.urlparse(w[0]).query))["titles"]).split("|") if w else []
    check(f"une seule requête Wikipédia par pays, avec tous ses lieux ({len(t0)} titres), redirections suivies", len(t0) == len(L_TOUS) and all(k in w[0] for k in ("redirects=1", "prop=pageimages%7Cpageprops", "piprop=thumbnail%7Cname", "pithumbsize=960")))
    check(f"requêtes : seulement la carte affichée et la suivante ({len(entities(log))} bannières, {len(w)} Wikipédia)", len(entities(log)) == 2 and len(w) == 2)
    swipe(pg, -1); pg.wait_for_timeout(800)
    check(f"après une réponse : un seul nouveau pays interrogé ({len(entities(log))} / {len(wp_reqs(log))})", len(entities(log)) == 3 and len(wp_reqs(log)) == 3)
    check(f"lieux-envies.json chargé une seule fois ({LIEUX_REQ.count('photos')})", LIEUX_REQ.count("photos") == 1)
    stored = pg.evaluate("[Object.keys(JSON.parse(localStorage.getItem('nos-voyages-photos-v4') || '{}')).length, localStorage.getItem('nos-voyages-photos-v3')]")
    check(f"mémoire des photos sous la clé v4 ({stored[0]} pays)", stored[0] >= 2 and stored[1] is None)
    swipe(pg, +1); pg.wait_for_timeout(500); close_match(pg)
    n0 = len(log); pg.click("#gameClose"); pg.wait_for_timeout(300); pg.click("[data-action=play]"); pg.wait_for_timeout(1500)
    check("rouvrir le jeu : pas de nouvelle requête pour les pays déjà vus", not [x for x in log[n0:] if dict(up.parse_qsl(up.urlparse(x).query)).get("entity") in entities(log[:n0])])
    pg.context.close()
    # 2 : sans bannière ; bannière refusée ; bannière invalide
    pg, log, _ = start("nobanner", "nobanner"); open_game(pg); pg.wait_for_selector("#gameStack .swipe.top.has-photo", timeout=6000)
    got = imgs(pg)
    check(f"sans bannière : 3 lieux, Titicaca, Chartres, Carthagène (redirection) → {got}", len(got) == 3 and "Titicaca" in got[0] and "Chartres" in got[1] and "Cartagena" in got[2])
    pg.context.close()
    pg, log, _ = start("full", "refusee", refusees=ALL); open_game(pg); pg.wait_for_selector("#gameStack .swipe.top.has-photo", timeout=6000)
    got = imgs(pg)
    check(f"BANNIERES_REFUSEES : bannière ni demandée ni affichée → {len(got)} lieux, {len(entities(log))} requête bannière", len(got) == 3 and "banner" not in " ".join(got) and not entities(log))
    pg.context.close()
    pg, log, _ = start("badbanner", "badbanner"); open_game(pg); pg.wait_for_selector("#gameStack .swipe.top.has-photo", timeout=6000)
    check("bannière au nom interdit (« Flag ») : écartée sans interroger Commons", "banner" not in " ".join(imgs(pg)) and not [x for x in log if "commons.wikimedia.org" in x])
    pg.context.close()
    # 3 : bannière seule ; rien de valide
    pg, log, _ = start("banniere", "banniere", lieux=L_PIEGES); open_game(pg); pg.wait_for_selector("#gameStack .swipe.top.has-photo", timeout=6000); pg.wait_for_timeout(500)
    got = imgs(pg)
    check(f"pièges (homonymie, PNG, SVG, portrait, carrée, carte, montage, satellite, sans vignette, absente, hors Commons) tous écartés : bannière seule, sans barres → {got}",
          got == ["1920px-Preferred_banner.jpg"] and pg.locator("#gameStack .swipe.top .sw-bars").count() == 0)
    pg.context.close()
    pg, log, _ = start("none", "rien", lieux=L_PIEGES); open_game(pg); pg.wait_for_timeout(2500)
    check("rien de valide : silhouette, aucun message", pg.locator("#gameStack .swipe.top .sw-photo img").count() == 0 and pg.locator("#gameStack .swipe.top .sil").count() == 1 and not pg.locator("#toast.show").count())
    pg.screenshot(path=f"{OUT}/009e-3-silhouette.png"); pg.context.close()
    # 4 : lent, erreur, image introuvable, interrupteur
    pg, log, pending = start("slow", "lent"); open_game(pg)
    first = top(pg); swipe(pg, +1)
    check("service lent : le geste ❤️ fonctionne immédiatement", counter(pg).startswith("1 /") and top(pg) != first)
    pg.wait_for_timeout(4800)
    for r in pending:
        try: r.fulfill(status=200, headers=CORS, body="{}")
        except Exception: pass
    pg.wait_for_timeout(1500)
    check("service lent : après 4 s, silhouette, sans message", pg.locator("#gameStack .swipe.top.has-photo").count() == 0 and pg.locator("#gameStack .swipe.top .sil").count() == 1 and not pg.locator("#toast.show").count())
    pg.context.close()
    pg, log, _ = start("error", "erreur"); open_game(pg); pg.wait_for_timeout(2000)
    first = top(pg); pg.click("#gameNo"); pg.wait_for_timeout(500)
    check("service en erreur : silhouette, aucun message, ✖️ fonctionne", pg.locator("#gameStack .swipe.top .sil").count() == 1 and pg.locator(".has-photo").count() == 0 and not pg.locator("#toast.show").count() and top(pg) != first)
    pg.context.close()
    pg, log, _ = start("imgerror", "image"); open_game(pg); pg.wait_for_timeout(2500)
    check(f"bannière introuvable (404) : la carte passe aux lieux ({len(imgs(pg))} photos)", len(imgs(pg)) == 2)
    pg.context.close()
    pg, log, _ = start("full", "off", off=True); open_game(pg); pg.wait_for_timeout(2000)
    swipe(pg, -1); pg.wait_for_timeout(1000)
    check("PHOTOS_ENVIES = false : aucune requête externe, silhouettes", len(log) == 0 and "off" not in LIEUX_REQ and pg.locator(".has-photo").count() == 0 and pg.locator("#gameStack .swipe.top .sil").count() == 1)
    pg.context.close()

    # 5 : page de revue
    def revue(tag, w=390, h=844, mobile=True):
        log = []
        ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=2, is_mobile=mobile, has_touch=mobile, service_workers="block")
        ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin="http://nos-voyages.test")
        setup(ctx); pg = ctx.new_page()
        pg.on("console", lambda m: m.type == "error" and errs.append(f"[{tag}] {m.text}")); pg.on("pageerror", lambda e: errs.append(f"[{tag}] {e}"))
        wiki(pg, "full", log, []); ALL_LOG.append(log)
        pg.route("http://nos-voyages.test/lieux-envies.json", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps({c: {"pays": c, "lieux": L_TOUS} for c in ALL})))
        pg.goto("http://nos-voyages.test/revue-photos.html"); pg.wait_for_selector(".pays .tirage", timeout=15000); pg.wait_for_timeout(1500)
        return pg, log
    pg, log = revue("revue")
    n = pg.locator(".pays").count()
    check(f"revue : tous les pays du jeu ({n} = {len(set(ALL) - EXCLUS)})", n == len(set(ALL) - EXCLUS))
    first = pg.locator(".pays").first
    caps = first.locator(".tirage span").all_inner_texts()
    check(f"revue : même sélection que le jeu → {caps}", caps == ["Bannière du pays", "📍 Lac Titicaca", "📍 Cathédrale de Chartres"])
    loaded = len(entities(log))
    check(f"revue : seuls les pays proches de l'écran sont chargés ({loaded} sur {n})", 0 < loaded < 40)
    pg.screenshot(path=f"{OUT}/009e-4-revue-iphone.png")
    code = first.get_attribute("data-code")
    first.locator(".tirage").nth(1).click(); pg.wait_for_timeout(300)
    check(f"toucher une vignette : « ✖ refusée », compteur « {pg.inner_text('#compte')} »", first.locator(".tirage.refus").count() == 1 and pg.inner_text("#compte") == "1 photo refusée")
    first.locator(".tirage").nth(0).click(); first.locator(".tirage").nth(2).click(); first.locator(".tirage").nth(2).click(); pg.wait_for_timeout(300)
    check("re-toucher annule le refus", first.locator(".tirage.refus").count() == 2 and pg.inner_text("#compte") == "2 photos refusées")
    pg.screenshot(path=f"{OUT}/009e-5-revue-refus.png")
    pg.reload(); pg.wait_for_selector(".pays .tirage", timeout=15000); pg.wait_for_timeout(800)
    check("refus gardés après rechargement", pg.locator(".pays").first.locator(".tirage.refus").count() == 2 and pg.inner_text("#compte") == "2 photos refusées")
    pg.click("#copier"); pg.wait_for_timeout(500)
    clip = pg.evaluate("navigator.clipboard.readText()")
    check(f"« Copier la liste des refus » : « {clip} »", clip == f"REFUS: {code}|lake_Titicaca, {code}|bannière" and pg.locator("#toast.show").count() == 1)
    pg.click("#chips [data-r='Océanie']"); pg.wait_for_timeout(1200)
    names = pg.locator(".pays h2 span:nth-child(2)").all_inner_texts()
    check(f"filtre Océanie : {len(names)} pays (ex. {names[:3]})", 10 < len(names) < 40 and any("Australie" in x for x in names) and not any("France" == x for x in names))
    pg.context.close()
    pg, log = revue("revue-mac", 1280, 860, False)
    cols = pg.evaluate("getComputedStyle(document.getElementById('liste')).gridTemplateColumns.split(' ').length")
    check(f"revue sur Mac : grille large ({cols} colonnes)", cols >= 2)
    pg.screenshot(path=f"{OUT}/009e-6-revue-mac.png")
    pg.context.close()
    b.close()
sw = open(os.environ["APP_DIR"] + "/sw.js").read()
check("revue-photos.html jamais mise en cache, cache v12", "revue-photos" in sw and "nos-voyages-v12" in sw)
bad = [x for l in ALL_LOG for x in interdites(l)]
check(f"aucune requête UNESCO, media-list, Wikivoyage, Wikipédia fr ni sitelinks ({sum(len(l) for l in ALL_LOG)} requêtes comptées, {len(bad)} interdites)", not bad)
attendues = [e for e in errs if e.startswith("[erreur]") or e.startswith("[image]")]
autres = [e for e in errs if e not in attendues]
print("Erreurs console :", *(autres or ["aucune"]), sep="\n  ")
print(f"(+ {len(attendues)} attendue(s) : réponses 500 / 404 volontaires des tests « erreur » et « image introuvable »)")
print(f"{sum(results)}/{len(results)} vérifications réussies")
