# ORDRE-009D — photos du jeu des envies : bannière Wikivoyage + sites UNESCO seulement, filtres stricts (mots entiers, orientation paysage, catégories Commons).
# Réponses Wikidata, SPARQL, Commons et images simulées, iPhone 390×844, mode démo.
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
# Fichiers simulés : (largeur, hauteur, catégories Commons ou None si illisibles)
FILES = {
    "Preferred banner.jpg": (2560, 360, "Wikivoyage banners|Landscapes of Testland"),
    "Jacques Chirac 1997.jpg": (4000, 3000, "Jacques Chirac|Politicians of France|Presidents of France"),     # personnalité
    "Poste aérienne 1950.jpg": (4000, 3000, "Stamps of Testland|Airmail"),                                 # timbre (vu par les catégories)
    "Stamp of Testland 1960.jpg": (4000, 3000, "Airmail"),                                                 # timbre (vu par le nom)
    "Deux euros 2002.jpg": (4000, 3000, "Coins of Testland"),                                              # pièce
    "Billet de 50 francs.jpg": (4000, 3000, "Money"),                                                      # billet
    "Festival 1920.jpg": (4000, 3000, "Posters of festivals"),                                             # affiche
    "Carte du site.jpg": (4000, 3000, "Landscapes"),                                                       # carte
    "Flag of Testland.jpg": (4000, 3000, "Landscapes"),                                                    # drapeau
    "Vue du port.jpg": (4000, 3000, "Paintings by Claude Monet|Ports in art"),                             # tableau
    "Tour du port.jpg": (3000, 4000, "Towers of Testland"),                                                # portrait vertical
    "Place du marché.jpg": (3000, 3000, "Squares of Testland"),                                            # photo carrée
    "Vallée sans catégories.jpg": (4000, 3000, None),                                                      # catégories illisibles
    "Petite vallée.jpg": (1000, 600, "Valleys of Testland"),                                               # trop petite
    "Vue du lac.jpg": (4000, 3000, "Lakes of Testland|Women of Testland"),                                 # des gens sur la photo
    "Cathédrale de Chartres.jpg": (4000, 3000, "Chartres Cathedral|Exteriors of Chartres Cathedral"),     # faux positifs corrigés
    "Mapungubwe hills.jpg": (4000, 2600, "Mapungubwe National Park|Landscapes of South Africa"),
    "Cartagena murallas.jpg": (3600, 2400, "Walls of Cartagena|Cartagena de Indias"),
}
PIEGES = ["Jacques Chirac 1997.jpg", "Poste aérienne 1950.jpg", "Stamp of Testland 1960.jpg", "Deux euros 2002.jpg", "Billet de 50 francs.jpg", "Festival 1920.jpg",
          "Carte du site.jpg", "Flag of Testland.jpg", "Vue du port.jpg", "Tour du port.jpg", "Place du marché.jpg", "Vallée sans catégories.jpg", "Petite vallée.jpg", "Vue du lac.jpg"]
JUSTES = ["Cathédrale de Chartres.jpg", "Mapungubwe hills.jpg", "Cartagena murallas.jpg"]
def row(f, l): return {"img": {"value": "http://commons.wikimedia.org/wiki/Special:FilePath/" + up.quote(f)}, "l": {"value": l}}
def wiki(pg_, mode, log, pending):
    def handler(route):
        u = up.urlparse(route.request.url); q = dict(up.parse_qsl(u.query)); host = u.hostname
        log.append(route.request.url)
        if mode == "slow" and host in ("www.wikidata.org", "query.wikidata.org"): pending.append(route); return
        if mode == "error" and host != "upload.wikimedia.org": return route.fulfill(status=500, body="")
        js = lambda o: route.fulfill(status=200, headers=CORS, body=json.dumps(o))
        if host == "www.wikidata.org" and q.get("action") == "wbgetclaims":
            if mode in ("full", "banniere", "imgerror"):
                return js({"claims": {"P948": [{"mainsnak": {"datavalue": {"value": "Normal banner.jpg", "type": "string"}}, "rank": "normal"},
                                               {"mainsnak": {"datavalue": {"value": "Preferred_banner.jpg", "type": "string"}}, "rank": "preferred"}]}})
            return js({"claims": {}})
        if host == "query.wikidata.org":
            if mode == "banniere": return route.fulfill(status=503, body="")
            rows = [row(f, "Site " + str(i)) for i, f in enumerate(PIEGES)]
            if mode in ("full", "nobanner", "imgerror"): rows += [row("Cathédrale de Chartres.jpg", "Cathédrale de Chartres"), row("Mapungubwe hills.jpg", "Paysage culturel de Mapungubwe"), row("Cartagena murallas.jpg", "Port de Carthagène")]
            return js({"results": {"bindings": rows}})
        if host == "commons.wikimedia.org":
            titles = q.get("titles", "").split("|"); pages = {}
            for i, t in enumerate(titles):
                f = t.replace("File:", "").replace("_", " "); w, h, cats = FILES.get(f, (4000, 3000, "Landscapes"))
                fq = up.quote(f.replace(" ", "_"))
                ii = {"thumburl": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/" + fq + "/960px-" + fq,
                      "url": "https://upload.wikimedia.org/wikipedia/commons/a/ab/" + fq, "width": w, "height": h, "extmetadata": {}}
                if cats is not None: ii["extmetadata"]["Categories"] = {"value": cats}
                if f == "Preferred banner.jpg": ii["extmetadata"]["Artist"] = {"value": '<a href="//commons.wikimedia.org/wiki/User:JD">Jean Dupont</a>'}
                pages[str(-1 - i)] = {"title": "File:" + f, "imageinfo": [ii]}
            return js({"batchcomplete": "", "query": {"pages": pages}})
        if host == "upload.wikimedia.org":
            if mode == "imgerror" and "banner" in u.path: return route.fulfill(status=404, body="")
            return route.fulfill(status=200, headers={"Content-Type": "image/jpeg"}, body=jpeg_bytes(u.path))
        return route.fulfill(status=404, body="")
    for pat in ("https://www.wikidata.org/**", "https://query.wikidata.org/**", "https://*.wikivoyage.org/**", "https://*.wikipedia.org/**", "https://commons.wikimedia.org/**", "https://upload.wikimedia.org/**"):
        pg_.context.route(pat, handler)
def entities(log): return {dict(up.parse_qsl(up.urlparse(x).query)).get("entity") for x in log if "www.wikidata.org" in x}
def interdites(log): return [x for x in log if "media-list" in x or "wikivoyage.org" in x or "wikipedia.org" in x or "wbgetentities" in x]
def imgs(pg): return [up.unquote(s).split("/")[-1] for s in pg.locator("#gameStack .swipe.top .sw-photo img").evaluate_all("l => l.map(i => i.getAttribute('src'))")]

ALL_LOG = []
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=os.environ["CHROMIUM_PATH"], proxy={"server": os.environ["HTTPS_PROXY"]},
                          args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    def start(mode, tag, off=False):
        log, pending = [], []
        pg = page(b, tag, {"countries": [], "memories": [], "photos": [], "picks": [], "wishes": []}, init="localStorage.setItem('nos-voyages-demo-who','demo-maxime')")
        wiki(pg, mode, log, pending); ALL_LOG.append(log)
        if off: pg.route("http://nos-voyages.test/index.html", lambda r: r.fulfill(body=open(os.environ["APP_DIR"] + "/index.html").read().replace("const PHOTOS_ENVIES = true;", "const PHOTOS_ENVIES = false;"), content_type="text/html"))
        pg.goto("http://nos-voyages.test/" + ("index.html" if off else "") + "#admin"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(2000)
        if pg.locator("#loginModal.show").count(): pg.click("#loginCancel")
        return pg, log, pending
    # 0 : les filtres eux-mêmes, appelés directement dans la page
    pg, log, _ = start("none", "filtres")
    # Le script de l'app est enfermé dans une fonction : on recopie ici, tels quels, ses filtres (et norm) depuis index.html
    src = open(os.environ["APP_DIR"] + "/index.html", encoding="utf-8").read()
    code = re.search(r"^const norm = .*$", src, re.M).group(0) + "\n" + src[src.index("const MOTS_FICHIER"):src.index("const PHOTOS_KEY")]
    pg.evaluate("code => { window.__f = new Function(code + '; return { fichierValide, photoValide };')(); }", code)
    def valide(f, banniere=False):
        w, h, cats = FILES[f]; ii = {"thumburl": "https://upload.wikimedia.org/x/960px-a.jpg", "width": w, "height": h, "extmetadata": {} if cats is None else {"Categories": {"value": cats}}}
        return pg.evaluate("([f, ii, b]) => __f.fichierValide(f, b) && __f.photoValide(ii, b)", [f, ii, banniere])
    rej = [f for f in PIEGES if valide(f)]
    check(f"cas pièges (personnalité, timbres, pièce, billet, affiche, carte, drapeau, tableau, portrait vertical, carrée, sans catégories, petite, gens) : {len(PIEGES) - len(rej)}/{len(PIEGES)} rejetés {rej or ''}", not rej)
    acc = [f for f in JUSTES if valide(f)]
    check(f"faux positifs corrigés acceptés : {acc}", acc == JUSTES)
    mots = pg.evaluate("""() => { const { fichierValide } = __f; return [
      fichierValide('Plage.png', true), fichierValide('Plage.gif', false), fichierValide('Château de Chambord.JPG', false), fichierValide('Chartreuse.jpg', false),
      fichierValide('Statue de la Liberté.jpg', false), fichierValide('Statue de la Liberté.jpg', true), fichierValide('Pièce montée.jpg', false),
      fichierValide('Carte postale de Nice.jpg', false), fichierValide('Le Roi-Soleil.jpg', false), fichierValide('Royan.jpg', false),
      fichierValide('Emblème-national.jpg', false), fichierValide('Coat_of_arms.jpg', true), fichierValide('Les Champs (Plan) 2.jpg', false)] }""")
    check(f"noms de fichier : PNG/GIF refusés, mots entiers sans casse ni accents, « statue » toléré sur la bannière seule → {mots}",
          mots == [False, False, True, True, False, True, False, False, False, True, False, False, False])
    ban = pg.evaluate("""() => { const { photoValide } = __f; const ii = c => ({ thumburl: 'https://upload.wikimedia.org/x/960px-a.jpg', width: 2560, height: 360, extmetadata: c === null ? {} : { Categories: { value: c } } });
      return [photoValide(ii('Wikivoyage banners'), true), photoValide(ii('Statues in Rome|Interiors'), true), photoValide(ii('Statues in Rome'), false),
              photoValide(ii('Flags of Testland'), true), photoValide(ii(null), true), photoValide(ii('People at the beach'), true)] }""")
    check(f"bannière : orientation libre, catégories quand même vérifiées (sculptures/intérieurs tolérés) → {ban}", ban == [True, True, False, False, False, False])
    pg.context.close()
    # 1 : bannière + sites UNESCO filtrés
    pg, log, _ = start("full", "photos")
    check("aucune requête Wikimedia avant d'ouvrir le jeu", len(log) == 0)
    open_game(pg); pg.wait_for_selector("#gameStack .swipe.top.has-photo", timeout=6000); pg.wait_for_timeout(700)
    got = imgs(pg)
    check(f"bannière + 2 sites UNESCO, tous les pièges écartés → {got}", len(got) == 3 and "Preferred_banner" in got[0] and got[0].startswith("1920px-") and "Chartres" in got[1] and "Mapungubwe" in got[2])
    cr = pg.locator("#gameStack .swipe.top .sw-credit").inner_text()
    check(f"crédit de la bannière : « {cr} »", cr == "Photo : Jean Dupont · Wikimedia Commons")
    com = [x for x in log if "commons.wikimedia.org" in x]
    check("Commons interrogé une fois par pays, avec taille et catégories", bool(com) and all("iiprop=url%7Csize%7Cextmetadata" in x and "iiextmetadatafilter=Artist%7CCategories" in x for x in com))
    titles = up.unquote(dict(up.parse_qsl(up.urlparse(com[0]).query))["titles"]).split("|") if com else []
    check(f"noms de fichier piégés écartés avant même d'interroger Commons ({len(titles)} candidats)", not any(t in " ".join(titles) for t in ("Stamp of", "Billet", "Carte du site", "Flag of")))
    pg.screenshot(path=f"{OUT}/009d-1-banniere-et-unesco.png")
    box = pg.locator("#gameStack .swipe.top .sw-photo").bounding_box()
    pg.mouse.click(box["x"] + box["width"] * .85, box["y"] + box["height"] / 2); pg.wait_for_timeout(600)
    cr = pg.locator("#gameStack .swipe.top .sw-credit").inner_text()
    check(f"photo UNESCO légendée : « {cr} »", cr == "📍 Cathédrale de Chartres · Photo : Wikimedia Commons")
    pg.screenshot(path=f"{OUT}/009d-2-monument.png")
    check(f"requêtes : seulement la carte affichée et la suivante ({len(entities(log))} pays)", len(entities(log)) == 2)
    swipe(pg, -1); pg.wait_for_timeout(800)
    check(f"après une réponse : un seul nouveau pays interrogé ({len(entities(log))} au total)", len(entities(log)) == 3)
    stored = pg.evaluate("[Object.keys(JSON.parse(localStorage.getItem('nos-voyages-photos-v3') || '{}')).length, localStorage.getItem('nos-voyages-photos-v2')]")
    check(f"mémoire des photos sous la clé v3 ({stored[0]} pays), plus rien en v2", stored[0] >= 2 and stored[1] is None)
    pg.context.close()
    # 2 : sans bannière, les trois faux positifs passent
    pg, log, _ = start("nobanner", "nobanner"); open_game(pg); pg.wait_for_selector("#gameStack .swipe.top.has-photo", timeout=6000)
    got = imgs(pg)
    check(f"sans bannière : Chartres, Mapungubwe, Cartagena acceptés → {got}", len(got) == 3 and "Chartres" in got[0] and "Mapungubwe" in got[1] and "Cartagena" in got[2])
    pg.context.close()
    # 3 : bannière seule valide ; rien de valide
    pg, log, _ = start("banniere", "banniere"); open_game(pg); pg.wait_for_selector("#gameStack .swipe.top.has-photo", timeout=6000); pg.wait_for_timeout(500)
    got = imgs(pg)
    check(f"bannière seule (UNESCO en panne) : une photo, sans barres → {got}", len(got) == 1 and "Preferred_banner" in got[0] and pg.locator("#gameStack .swipe.top .sw-bars").count() == 0)
    pg.screenshot(path=f"{OUT}/009d-3-banniere-seule.png"); pg.context.close()
    pg, log, _ = start("none", "rien"); open_game(pg); pg.wait_for_timeout(2500)
    check("que des pièges : silhouette, aucun message", pg.locator("#gameStack .swipe.top .sw-photo img").count() == 0 and pg.locator("#gameStack .swipe.top .sil").count() == 1 and not pg.locator("#toast.show").count())
    pg.screenshot(path=f"{OUT}/009d-4-silhouette.png"); pg.context.close()
    # 4 : lent, erreur, image introuvable, interrupteur
    pg, log, pending = start("slow", "lent"); open_game(pg)
    first = top(pg); swipe(pg, +1)
    check("service lent : le geste ❤️ fonctionne immédiatement", counter(pg).startswith("1 /") and top(pg) != first)
    pg.wait_for_timeout(4800)
    for r in pending:
        try: r.fulfill(status=200, headers=CORS, body=json.dumps({"claims": {"P948": [{"mainsnak": {"datavalue": {"value": "Late.jpg"}}, "rank": "normal"}]}, "results": {"bindings": []}}))
        except Exception: pass
    pg.wait_for_timeout(1500)
    check("service lent : après 4 s, silhouette, sans message", pg.locator("#gameStack .swipe.top.has-photo").count() == 0 and pg.locator("#gameStack .swipe.top .sil").count() == 1 and not pg.locator("#toast.show").count())
    pg.context.close()
    pg, log, _ = start("error", "erreur"); open_game(pg); pg.wait_for_timeout(2000)
    first = top(pg); pg.click("#gameNo"); pg.wait_for_timeout(500)
    check("service en erreur : silhouette, aucun message, ✖️ fonctionne", pg.locator("#gameStack .swipe.top .sil").count() == 1 and pg.locator(".has-photo").count() == 0 and not pg.locator("#toast.show").count() and top(pg) != first)
    pg.context.close()
    pg, log, _ = start("imgerror", "image"); open_game(pg); pg.wait_for_timeout(2500)
    got = imgs(pg)
    check(f"bannière introuvable (404) : la carte passe aux 2 sites UNESCO ({len(got)} photos)", len(got) == 2)
    pg.context.close()
    pg, log, _ = start("full", "off", off=True); open_game(pg); pg.wait_for_timeout(2000)
    swipe(pg, -1); pg.wait_for_timeout(1000)
    check("PHOTOS_ENVIES = false : aucune requête externe, silhouettes", len(log) == 0 and pg.locator(".has-photo").count() == 0 and pg.locator("#gameStack .swipe.top .sil").count() == 1)
    pg.context.close()
    b.close()
bad = [x for l in ALL_LOG for x in interdites(l)]
check(f"aucune requête vers media-list, Wikipédia, Wikivoyage ni sitelinks ({sum(len(l) for l in ALL_LOG)} requêtes comptées, {len(bad)} interdites)", not bad)
attendues = [e for e in errs if e.startswith("[erreur]") or e.startswith("[image]") or e.startswith("[banniere]")]
autres = [e for e in errs if e not in attendues]
print("Erreurs console :", *(autres or ["aucune"]), sep="\n  ")
print(f"(+ {len(attendues)} attendue(s) : réponses 500 / 503 / 404 volontaires des tests « erreur », « bannière seule » et « image introuvable »)")
print(f"{sum(results)}/{len(results)} vérifications réussies")
