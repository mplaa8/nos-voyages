# Tests ORDRE-009B (photos Wikimedia dans le jeu des envies) avec Wikidata, Wikipédia, Commons et images simulés, iPhone 390×844, mode démo.
# Usage : APP_DIR=<copie du site avec CONFIG vide> LIBS_DIR=<copies locales leaflet/maplibre/supabase-js/geojson> CHROMIUM_PATH=<chromium> python3 tests/test_ordre009b_photos.py <dossier de sortie>
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
MEDIA = ["Flag of Testland.svg", "Drapeau du pays.jpg", "Carte du pays.jpg", "Blason_de_Testland.jpg", "Portrait du président.jpg",
         "Map locator.jpg", "Plage turquoise.png", "Animation.gif", "Emblème national.jpg", "Plage de sable.jpg", "Marché coloré.JPG", "Troisième belle photo.jpg"]
def jpeg_bytes(seed):
    h = hashlib.md5(seed.encode()).digest(); img = np.zeros((450, 800, 3), np.uint8); img[:] = (h[0], h[1], h[2])
    cv2.circle(img, (400, 225), 120, (h[3], h[4], 255), -1); return cv2.imencode(".jpg", img)[1].tobytes()
CORS = {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"}
def wiki(pg_, mode, log, pending):
    def handler(route):
        u = up.urlparse(route.request.url); q = dict(up.parse_qsl(u.query)); host = u.hostname
        log.append(route.request.url)
        if mode == "slow" and "wikidata" in host: pending.append(route); return          # ne répond pas (service lent)
        if mode == "error" and host != "upload.wikimedia.org": return route.fulfill(status=500, body="")
        js = lambda o: route.fulfill(status=200, headers=CORS, body=json.dumps(o))
        if host == "www.wikidata.org" and q.get("action") == "wbgetclaims":
            if mode in ("full", "noextra", "imgerror"):
                return js({"claims": {"P948": [{"mainsnak": {"datavalue": {"value": "Normal banner.jpg", "type": "string"}}, "rank": "normal"},
                                               {"mainsnak": {"datavalue": {"value": "Preferred_banner.jpg", "type": "string"}}, "rank": "preferred"},
                                               {"mainsnak": {"datavalue": {"value": "Old banner.jpg", "type": "string"}}, "rank": "deprecated"}]}})
            return js({"claims": {}})
        if host == "www.wikidata.org" and q.get("action") == "wbgetentities":
            Q = q.get("ids")
            if mode in ("full", "nobanner", "imgerror"): return js({"entities": {Q: {"sitelinks": {"frwiki": {"site": "frwiki", "title": "Pays de test"}}}}})
            return js({"entities": {Q: {"sitelinks": {}}}})
        if host == "fr.wikipedia.org":
            items = [{"title": "Fichier:" + f, "type": "image"} for f in MEDIA] + [{"title": "Fichier:Film.webm", "type": "video"}]
            return js({"items": items})
        if host == "commons.wikimedia.org":
            titles = q.get("titles", "").split("|"); pages = {}
            for i, t in enumerate(titles):
                f = t.replace("File:", "").replace("_", " ")
                art = {"Preferred banner.jpg": '<a href="//commons.wikimedia.org/wiki/User:JD">Jean Dupont</a>',
                       "Plage de sable.jpg": 'Marie <b>Curie</b><img src="x" onerror="window.__xss=1">'}.get(f)
                fq = up.quote(f.replace(" ", "_")); banner = "banner" in f
                ii = {"thumburl": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/" + fq + "/960px-" + fq,
                      "url": "https://upload.wikimedia.org/wikipedia/commons/a/ab/" + fq,
                      "width": 2560 if banner else 4000, "height": 360 if banner else 3000, "extmetadata": {}}
                if art: ii["extmetadata"]["Artist"] = {"value": art}
                pages[str(-1 - i)] = {"title": "File:" + f, "imageinfo": [ii]}
            return js({"batchcomplete": "", "query": {"pages": pages}})
        if host == "upload.wikimedia.org":
            if mode == "imgerror" and "banner" in u.path: return route.fulfill(status=404, body="")
            return route.fulfill(status=200, headers={"Content-Type": "image/jpeg"}, body=jpeg_bytes(u.path))
        return route.fulfill(status=404, body="")
    for pat in ("https://www.wikidata.org/**", "https://fr.wikipedia.org/**", "https://commons.wikimedia.org/**", "https://upload.wikimedia.org/**"):
        pg_.context.route(pat, handler)
def entities(log): return {dict(up.parse_qsl(up.urlparse(x).query)).get("entity") or dict(up.parse_qsl(up.urlparse(x).query)).get("ids") for x in log if "wikidata.org" in x}

geo = json.load(open(os.environ["LIBS_DIR"] + "/ne50.geojson"))
ALL = [f["properties"]["ADM0_A3"] for f in geo["features"]] + ["GUF", "GLP", "MTQ", "REU", "MYT", "BES", "SJM"]
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=os.environ["CHROMIUM_PATH"], proxy={"server": os.environ["HTTPS_PROXY"]},
                          args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    def start(mode, tag, seed=None, off=False):
        log, pending = [], []
        sd = seed or {"countries": [], "memories": [], "photos": [], "picks": [], "wishes": []}
        pg = page(b, tag, sd, init="localStorage.setItem('nos-voyages-demo-who','demo-maxime')")
        wiki(pg, mode, log, pending)
        if off: pg.route("http://nos-voyages.test/index.html", lambda r: r.fulfill(body=open(os.environ["APP_DIR"] + "/index.html").read().replace("const PHOTOS_ENVIES = true;", "const PHOTOS_ENVIES = false;"), content_type="text/html"))
        pg.goto("http://nos-voyages.test/" + ("index.html" if off else "") + "#admin"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(2000)
        if pg.locator("#loginModal.show").count(): pg.click("#loginCancel")
        return pg, log, pending
    # 1 + 2 + 6 : bannière + 2 photos, filtrage, requêtes limitées
    roxane_oui = [{"user_id": "demo-roxane", "country_code": c, "answer": "oui", "created_at": "2026-10-01T00:00:00Z"} for c in ALL]
    pg, log, _ = start("full", "photos", {"countries": [], "memories": [], "photos": [], "picks": [], "wishes": roxane_oui})
    check("aucune requête Wikimedia avant d'ouvrir le jeu", len(log) == 0)
    open_game(pg); pg.wait_for_selector("#gameStack .swipe.top.has-photo", timeout=6000); pg.wait_for_timeout(700)
    top_ = pg.locator("#gameStack .swipe.top")
    check(f"carte avec photos : {top_.locator('.sw-photo img').count()} photos, {top_.locator('.sw-bars i').count()} barres", top_.locator(".sw-photo img").count() == 3 and top_.locator(".sw-bars i").count() == 3)
    srcs = top_.locator(".sw-photo img").evaluate_all("l => l.map(i => i.getAttribute('src'))")
    check(f"bannière panoramique en 1920 px, photos en 960 px", "/1920px-Preferred_banner.jpg" in srcs[0] and all("/960px-" in x for x in srcs[1:]))
    cr = top_.locator(".sw-credit").inner_text()
    check(f"crédit : « {cr} »", cr == "Photo : Jean Dupont · Wikimedia Commons")
    titles = [up.unquote(dict(up.parse_qsl(up.urlparse(x).query))["titles"]) for x in log if "commons.wikimedia.org" in x]
    check(f"filtrage : bannière « preferred » + 2 JPG (drapeaux, cartes, blasons, portraits, emblèmes, SVG, PNG, GIF écartés) → {titles[0] if titles else None}",
          bool(titles) and titles[0].split("|") == ["File:Preferred_banner.jpg", "File:Plage de sable.jpg", "File:Marché coloré.JPG"])
    pg.screenshot(path=f"{OUT}/ordre009b-1-carte-photo.png")
    ents = entities(log)
    check(f"requêtes : seulement la carte affichée et la suivante ({len(ents)} pays interrogés)", len(ents) == 2)
    box = top_.locator(".sw-photo").bounding_box()
    pg.mouse.click(box["x"] + box["width"] * .85, box["y"] + box["height"] / 2); pg.wait_for_timeout(500)
    on = [i for i in range(3) if "on" in (top_.locator(".sw-bars i").nth(i).get_attribute("class") or "")]
    cr2 = top_.locator(".sw-credit").inner_text()
    check(f"toucher à droite : photo suivante (barre {on}), crédit « {cr2} » sans HTML", on == [1] and cr2 == "Photo : Marie Curie · Wikimedia Commons")
    check("crédit nettoyé : aucun code exécuté (onerror)", pg.evaluate("window.__xss === undefined"))
    pg.mouse.click(box["x"] + box["width"] * .85, box["y"] + box["height"] / 2); pg.wait_for_timeout(400)
    cr3 = top_.locator(".sw-credit").inner_text()
    check(f"3e photo sans auteur : « {cr3} »", cr3 == "Photo : Wikimedia Commons")
    pg.mouse.click(box["x"] + box["width"] * .15, box["y"] + box["height"] / 2); pg.wait_for_timeout(400)
    on = [i for i in range(3) if "on" in (top_.locator(".sw-bars i").nth(i).get_attribute("class") or "")]
    check(f"toucher à gauche : photo précédente (barre {on})", on == [1])
    pg.wait_for_timeout(600); pg.screenshot(path=f"{OUT}/ordre009b-2-photo-suivante.png")
    check("toucher la photo ne répond pas à la carte", counter(pg).startswith("0 /"))
    # 5 : glisser sur la photo, annuler, correspondance
    first = top(pg); op = swipe(pg, -1)
    check(f"glisser ✖️ sur une photo : tampon visible ({op:.2f}), réponse enregistrée", op > .5 and counter(pg).startswith("1 /") and top(pg) != first)
    pg.wait_for_selector("#gameStack .swipe.top.has-photo", timeout=6000)
    check("la carte suivante (préchargée) arrive directement avec ses photos", pg.locator("#gameStack .swipe.top.has-photo").count() == 1)
    ents2 = entities(log)
    check(f"après une réponse : un seul nouveau pays interrogé (le nouveau « suivant ») → {len(ents2)} au total", len(ents2) == 3)
    pg.click("#gameUndo"); pg.wait_for_timeout(600)
    check("« Annuler » ramène la carte (avec ses photos)", top(pg) == first and pg.locator("#gameStack .swipe.top.has-photo").count() == 1)
    swipe(pg, +1); pg.wait_for_timeout(500)
    check("❤️ sur une photo, Roxane avait dit ❤️ : « Destination en commun 💞 »", pg.locator("#match.show").count() == 1 and "Destination en commun" in pg.inner_text("#matchTitle"))
    close_match(pg)
    stored = pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('nos-voyages-photos-v1') || '{}')).length")
    check(f"liste des photos mémorisée par pays ({stored} pays)", stored >= 3)
    n0 = len(log); pg.click("#gameClose"); pg.wait_for_timeout(300); pg.click("[data-action=play]"); pg.wait_for_timeout(1500)
    check("rouvrir le jeu : pas de nouvelle requête pour les pays déjà vus", not [x for x in log[n0:] if "wikidata" in x and (dict(up.parse_qsl(up.urlparse(x).query)).get("entity") or dict(up.parse_qsl(up.urlparse(x).query)).get("ids")) in ents2 - {None}])
    pg.context.close()
    # 3 : replis
    for mode, exp_imgs, label in (("nobanner", 2, "pas de bannière : les 2 photos de l'article"), ("noextra", 1, "pas de photos complémentaires : la bannière seule"), ("none", 0, "rien du tout : silhouette")):
        pg, log, _ = start(mode, mode); open_game(pg); pg.wait_for_timeout(2500)
        n = pg.locator("#gameStack .swipe.top .sw-photo img").count()
        sil = pg.locator("#gameStack .swipe.top .sil").count() == 1
        bars = pg.locator("#gameStack .swipe.top .sw-bars").count()
        check(f"{label} ({n} photo(s), barres : {bars})", n == exp_imgs and sil and (bars == (1 if exp_imgs > 1 else 0)))
        if mode == "none": pg.screenshot(path=f"{OUT}/ordre009b-3-repli-silhouette.png")
        pg.context.close()
    # 4 : service lent (> 4 s) ou en erreur ; image introuvable
    pg, log, pending = start("slow", "lent"); open_game(pg)
    first = top(pg); swipe(pg, +1)
    check("service lent : le geste ❤️ fonctionne immédiatement", counter(pg).startswith("1 /") and top(pg) != first)
    pg.wait_for_timeout(4800)
    for r in pending:
        try: r.fulfill(status=200, headers=CORS, body=json.dumps({"claims": {"P948": [{"mainsnak": {"datavalue": {"value": "Late.jpg"}}, "rank": "normal"}]}, "entities": {}}))
        except Exception: pass
    pg.wait_for_timeout(1500)
    check("service lent : après 4 s, la carte reste sur la silhouette, sans message", pg.locator("#gameStack .swipe.top.has-photo").count() == 0 and pg.locator("#gameStack .swipe.top .sil").count() == 1 and not pg.locator("#toast.show").count())
    pg.context.close()
    pg, log, _ = start("error", "erreur"); open_game(pg); pg.wait_for_timeout(2000)
    first = top(pg); pg.click("#gameNo"); pg.wait_for_timeout(500)
    check("service en erreur : silhouette, aucun message, ✖️ fonctionne", pg.locator("#gameStack .swipe.top .sil").count() == 1 and pg.locator(".has-photo").count() == 0 and not pg.locator("#toast.show").count() and top(pg) != first)
    pg.context.close()
    pg, log, _ = start("imgerror", "image"); open_game(pg); pg.wait_for_timeout(2500)
    n = pg.locator("#gameStack .swipe.top .sw-photo img").count()
    check(f"bannière introuvable (404) : la carte passe aux 2 autres photos ({n} photo(s))", n == 2 and pg.locator("#gameStack .swipe.top.has-photo").count() == 1)
    pg.context.close()
    # 7 : PHOTOS_ENVIES = false
    pg, log, _ = start("full", "off", off=True); open_game(pg); pg.wait_for_timeout(2000)
    swipe(pg, -1); pg.wait_for_timeout(1000)
    check("PHOTOS_ENVIES = false : aucune requête externe, cartes avec silhouette", len(log) == 0 and pg.locator(".has-photo").count() == 0 and pg.locator("#gameStack .swipe.top .sil").count() == 1)
    pg.context.close()
    b.close()
attendues = [e for e in errs if e.startswith("[erreur]") or e.startswith("[image]")]
autres = [e for e in errs if e not in attendues]
print("Erreurs console :", *(autres or ["aucune"]), sep="\n  ")
print(f"(+ {len(attendues)} attendue(s) : réponses 500 / 404 volontaires des tests « erreur » et « image introuvable »)")
print(f"{sum(results)}/{len(results)} vérifications réussies")
