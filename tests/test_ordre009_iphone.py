# Tests ORDRE-009 (nos envies de voyage, destinations en commun, tirage) en mode démo avec le sélecteur Maxime / Roxane, iPhone 390×844 — voir docs/ordres/ORDRE-006.
# Usage : APP_DIR=<copie du site avec CONFIG vide> LIBS_DIR=<copies locales leaflet/maplibre/supabase-js/geojson> CHROMIUM_PATH=<chromium> python3 tests/test_ordre009_iphone.py <dossier de sortie>
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
    # Wikimedia simulé « sans photo » (inaccessible depuis l'environnement de test) : les cartes gardent leur silhouette
    for pat in ("https://www.wikidata.org/**", "https://en.wikipedia.org/**", "https://commons.wikimedia.org/**"):
        ctx.route(pat, lambda r: r.fulfill(status=200, headers={"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"}, body='{"claims": {}, "entities": {}}'))
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

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=os.environ["CHROMIUM_PATH"], proxy={"server": os.environ["HTTPS_PROXY"]},
                          args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    seed = {"countries":[{"code":"AUS","name":"Australie","status":"visited","places":""},{"code":"NZL","name":"Nouvelle-Zélande","status":"dream","places":""}],
            "memories":[],"photos":[],"picks":[],"wishes":[]}
    pg = page(b, "envies", seed)
    pg.goto("http://nos-voyages.test/#admin"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(2000); pg.click("#loginCancel")
    # 8. Visiteur : « Jouer » ouvre la fenêtre du code secret
    who(pg, ""); open_list(pg)
    check("liste ☰ : carte « 💞 Nos envies de voyage » sous les statistiques", pg.locator("#sheetBody .envies").count() == 1 and "Nos envies de voyage" in pg.inner_text(".envies"))
    pg.click("[data-action=play]"); pg.wait_for_timeout(400)
    check("visiteur : « Jouer » ouvre la fenêtre du code secret", pg.locator("#codeModal.show").count() == 1 and pg.locator("#game:not([hidden])").count() == 0)
    pg.click("#codeCancel"); pg.wait_for_timeout(300)
    # 1. Maxime : 5 réponses (3 ❤️, 2 ✖️), glissement et boutons, annuler, quitter et reprendre
    who(pg, "demo-maxime"); open_game(pg, "Océanie")
    check("jeu ouvert : plein écran, filtre Océanie actif", pg.locator("#game:not([hidden])").count() == 1 and pg.locator("#gameFilters .on").inner_text() == "Océanie")
    c0 = counter(pg); tot = int(c0.split("/")[1])
    check(f"compteur « {c0} »", c0.startswith("0 /") and tot > 15)
    pg.screenshot(path=f"{OUT}/ordre009-1-jeu.png")
    mx = []
    mx.append(top(pg)); op = swipe(pg, +1); check(f"glisser à droite : tampon « J’ai envie » visible pendant le geste (opacité {op:.2f})", op > .5)
    mx.append(top(pg)); op = swipe(pg, -1); check(f"glisser à gauche : tampon « Bof » visible (opacité {op:.2f})", op > .5)
    mx.append(top(pg)); btn(pg, "oui"); mx.append(top(pg)); btn(pg, "non"); mx.append(top(pg)); btn(pg, "oui")
    check(f"5 réponses : compteur « {counter(pg)} »", counter(pg).startswith("5 /") and len(set(mx)) == 5)
    sixth = top(pg); pg.click("#gameUndo"); pg.wait_for_timeout(500)
    check("« Annuler » ramène la dernière carte", top(pg) == mx[4] and counter(pg).startswith("4 /"))
    btn(pg, "oui")
    pg.click("#gameClose"); pg.wait_for_timeout(500)
    check("quitter (×) ramène à la liste ☰", pg.locator("#game[hidden]").count() == 1 and pg.locator("#sheet.open").count() == 1)
    pg.click("[data-action=play]"); pg.wait_for_timeout(500); pg.click("#gameFilters [data-region='Océanie']"); pg.wait_for_timeout(300)
    check("reprendre : on repart là où on en était", top(pg) == sixth and counter(pg).startswith("5 /"))
    A, B, C, D, E = mx      # Maxime : A ❤️, B ✖️, C ❤️, D ✖️, E ❤️
    pg.screenshot(path=f"{OUT}/ordre009-2-maxime-reprise.png")
    pg.click("#gameClose"); pg.wait_for_timeout(400)
    # 2 + 3. Roxane : rien de Maxime n'est visible ; ❤️ sur un ❤️ de Maxime -> correspondance ; ❤️ sur un ✖️ -> rien
    who(pg, "demo-roxane"); open_game(pg, "Océanie")
    check("Roxane : son paquet repart de zéro, aucune réponse de Maxime visible", counter(pg).startswith("0 /") and "Maxime" not in pg.inner_text("#game"))
    seen_r = []
    ok_ = answer_until(pg, B, "oui", seen_r)
    check("❤️ sur un pays où Maxime a dit ✖️ : rien ne se passe", ok_ and pg.locator("#match.show").count() == 0)
    if A not in seen_r:
        ok_ = answer_until(pg, A, "oui", seen_r); pg.wait_for_timeout(400)
        nameA = pg.inner_text("#matchCountry") if pg.locator("#match.show").count() else ""
        check(f"❤️ sur un ❤️ de Maxime : « Destination en commun 💞 » ({nameA})", ok_ and pg.locator("#match.show").count() == 1 and "Destination en commun" in pg.inner_text("#matchTitle") and pg.locator("#matchMoment .sil").count() == 1)
        pg.wait_for_timeout(1300); pg.screenshot(path=f"{OUT}/ordre009-3-destination-en-commun.png"); close_match(pg)
    else:
        check("(A déjà vu par Roxane avant B — ordre inattendu)", False)
    pg.click("#gameClose"); pg.wait_for_timeout(400)
    t = pg.inner_text(".envies")
    check(f"liste : 1 destination en commun, celle-là seulement", "1 destination en commun" in t and pg.locator(".envie").count() == 1)
    pg.fill("#search", nameA); pg.wait_for_timeout(300)
    check(f"le pays commun passe en « Un jour… » (doré)", "Notre prochain rêve" in pg.inner_text("#listBody"))
    pg.fill("#search", ""); pg.wait_for_timeout(200)
    # 4. Correspondance créée par Maxime après Roxane -> célébrée une seule fois à la réouverture en Roxane
    open_game(pg, "Océanie")
    F = top(pg); btn(pg, "oui")
    pg.click("#gameClose"); pg.wait_for_timeout(300)
    who(pg, "demo-maxime")
    check("Maxime, en reprenant le téléphone : le Vanuatu (devenu commun) lui est célébré", pg.locator("#match.show").count() == 1); close_match(pg)
    open_game(pg, "Océanie")
    ok_ = answer_until(pg, F, "oui"); pg.wait_for_timeout(400)
    check("Maxime crée la correspondance : animation pour lui", ok_ and pg.locator("#match.show").count() == 1); close_match(pg)
    close_match(pg); pg.click("#gameClose"); pg.wait_for_timeout(300); close_match(pg); pg.click("#closeSheet"); pg.wait_for_timeout(300)
    who(pg, "demo-roxane"); pg.wait_for_timeout(600)
    check("Roxane : célébrée à l'ouverture", pg.locator("#match.show").count() == 1 and "Destination en commun" in pg.inner_text("#matchTitle")); close_match(pg)
    pg.goto("http://nos-voyages.test/#admin"); pg.reload(); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(2500)
    if pg.locator("#loginModal.show").count(): pg.click("#loginCancel")
    check("réouverture : pas de seconde célébration", pg.locator("#match.show").count() == 0)
    # 5 + 6. Paquet complet (Océanie) : visité absent, « Un jour » présent, fin de paquet
    open_game(pg, "Océanie"); allr = []
    for _ in range(40):
        c = top(pg)
        if c is None: break
        allr.append(c); pg.keyboard.press("ArrowLeft"); pg.wait_for_timeout(320)
    seen_all = set(allr) | set(seen_r) | {B, A, F}
    check("pays visité (Australie) absent du paquet", "AUS" not in seen_all)
    check("pays « Un jour » (Nouvelle-Zélande) présent dans le paquet", "NZL" in seen_all)
    endt = pg.inner_text("#gameStack")
    check(f"fin du paquet (filtre) : message + « Tous les continents », compteur « {counter(pg)} »", "Plus aucun pays à découvrir ici" in endt and counter(pg).split(" / ")[0] == counter(pg).split(" / ")[1])
    pg.screenshot(path=f"{OUT}/ordre009-4-fin-paquet.png")
    pg.click("#gameFilters [data-region='Europe']"); pg.wait_for_timeout(300)
    check(f"filtre Europe : nouveau compteur « {counter(pg)} »", counter(pg).startswith("0 /") and top(pg) is not None)
    pg.click("#gameClose"); pg.wait_for_timeout(300)
    pg.context.close()

    # 4 bis + 5 bis + 7. Plusieurs correspondances d'un coup, jamais de rétrogradation, tirage (globe puis carte plate)
    commun = ["JPN", "ISL", "PER", "MAR", "CAN", "NOR", "AUS"]       # AUS : déjà visité
    ws = [{"user_id": u, "country_code": c, "answer": "oui", "created_at": T} for c in commun for u in ("demo-maxime", "demo-roxane")]
    seed2 = {"countries":[{"code":"AUS","name":"Australie","status":"visited","places":""}], "memories":[],"photos":[],"picks":[],"wishes": ws}
    for mode, base in (("globe", "http://nos-voyages.test/"), ("plate", "http://nos-voyages.test/?carte=plate")):
        pg = page(b, "tirage-" + mode, seed2, init="if (!localStorage.getItem('nos-voyages-demo-who')) localStorage.setItem('nos-voyages-demo-who','demo-roxane')")
        pg.goto(base + "#admin"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(2500)
        if mode == "globe":
            n_cards = 0; titles = []
            while pg.locator("#match.show").count() and n_cards < 10:
                titles.append(pg.inner_text("#matchTitle")); btxt = pg.inner_text("#matchBtn"); n_cards += 1
                if n_cards == 1: check(f"plusieurs correspondances : bouton « {btxt} »", btxt == "Suivante 💞")
                pg.click("#matchBtn"); pg.wait_for_timeout(500)
            check(f"7 correspondances : 5 animées puis « … et 2 autres » ({n_cards} écrans)", n_cards == 6 and titles[-1].startswith("… et 2 autres"))
            open_list(pg); pg.fill("#search", "australie"); pg.wait_for_timeout(300)
            check("pays déjà visité : jamais rétrogradé en « Un jour »", "Visité ensemble" in pg.inner_text("#listBody")); pg.fill("#search", "")
            pg.click("#closeSheet"); pg.wait_for_timeout(300)
        open_list(pg)
        t = pg.inner_text(".envies")
        check(f"[{mode}] liste : 7 destinations en commun et « 🎲 Tirer notre prochain voyage »", "7 destinations en commun" in t and pg.locator("[data-action=draw]").count() == 1)
        if mode == "globe": pg.locator(".envies").screenshot(path=f"{OUT}/ordre009-5-nos-envies.png")
        names = [pg.inner_text(f".envie[data-code='{c}']").strip()[2:].strip() for c in commun]
        pg.click("[data-action=draw]"); pg.wait_for_timeout(5200 if mode == "globe" else 1800)
        t1 = pg.inner_text("#drawTitle") if pg.locator("#draw:not([hidden])").count() else ""
        check(f"[{mode}] tirage : « {t1} »", t1.startswith("Et si c’était…") and any(n in t1 for n in names))
        if mode == "globe": pg.screenshot(path=f"{OUT}/ordre009-6-tirage.png")
        pg.click("#drawAgain"); pg.wait_for_timeout(5200 if mode == "globe" else 1800)
        t2 = pg.inner_text("#drawTitle")
        check(f"[{mode}] « Retirer au sort » : autre destination (« {t2} »)", t2 != t1 and any(n in t2 for n in names))
        pg.click("#drawOpen"); pg.wait_for_timeout(1800)
        check(f"[{mode}] « Ouvrir la fiche » ouvre le pays tiré ({h2(pg)})", h2(pg) is not None and h2(pg) in t2)
        pg.context.close()

    # 9. DESTINATIONS_ACTIF = false : aucune trace
    off = page(b, "off", seed2, init="localStorage.setItem('nos-voyages-demo-who','demo-roxane')")
    off.route("http://nos-voyages.test/index.html", lambda r: r.fulfill(body=open(os.environ["APP_DIR"] + "/index.html").read().replace("const DESTINATIONS_ACTIF = true;", "const DESTINATIONS_ACTIF = false;"), content_type="text/html"))
    off.goto("http://nos-voyages.test/index.html#admin"); off.wait_for_load_state("networkidle"); off.wait_for_timeout(2500)
    check("DESTINATIONS_ACTIF = false : pas d'animation à l'ouverture", off.locator("#match.show").count() == 0)
    open_list(off)
    check("DESTINATIONS_ACTIF = false : pas de carte « Nos envies »", off.locator(".envies").count() == 0)
    off.context.close()
    b.close()
print("Erreurs console :", *(errs or ["aucune"]), sep="\n  ")
print(f"{sum(results)}/{len(results)} vérifications réussies")
