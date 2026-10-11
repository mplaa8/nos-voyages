# Tests ORDRE-006 (palmarès, deux membres) en mode démo avec le sélecteur Maxime / Roxane, iPhone 390×844 — voir docs/ordres/ORDRE-006.
# Usage : APP_DIR=<copie du site avec CONFIG vide> LIBS_DIR=<copies locales leaflet/maplibre/supabase-js/geojson> CHROMIUM_PATH=<chromium> python3 tests/test_ordre006_iphone.py <dossier de sortie>
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

import base64, re
def jpeg(color):
    img = np.zeros((120, 160, 3), np.uint8); img[:] = color
    return "data:image/jpeg;base64," + base64.b64encode(cv2.imencode(".jpg", img)[1]).decode()
T = "2026-10-01T10:00:00Z"
seed = {"countries":[{"code":"PRT","name":"Portugal","status":"visited","places":"Lisbonne"}],
        "memories":[{"id":"m0","country_code":"PRT","content":"Le fou rire au tram 28","author_id":"demo-maxime","created_at":T},
                    {"id":"m1","country_code":"PRT","content":"Les pasteis de nata à Belém","created_at":T}],
        "photos":[{"id":"p0","country_code":"PRT","url":jpeg((40,120,220)),"author_id":"demo-maxime","created_at":T},
                  {"id":"p1","country_code":"PRT","url":jpeg((60,200,90)),"author_id":"demo-maxime","created_at":T},
                  {"id":"p2","country_code":"PRT","url":jpeg((200,80,160)),"author_id":"demo-maxime","created_at":T}],
        "picks":[]}
def h2(pg): return pg.inner_text("#sheetBody h2") if pg.locator("#sheet.open").count() else None
def who(pg, w): pg.click(f"#demoWho [data-who='{w}']"); pg.wait_for_timeout(400)
def open_country(pg, q, name):
    if pg.locator("#sheet.open").count(): pg.click("#closeSheet"); pg.wait_for_timeout(500)
    pg.click("#listBtn"); pg.wait_for_timeout(400); pg.fill("#search", q); pg.wait_for_timeout(200)
    pg.click(f"#listBody .list-item:has-text('{name}')"); pg.wait_for_timeout(1800)
def lb_pick(pg, i, cat):
    pg.click(f".ph img[data-i='{i}']"); pg.wait_for_timeout(400)
    pg.click(f"#lbPicks [data-cat='{cat}']"); pg.wait_for_timeout(500)
def lb_close(pg): pg.click("[data-lb=close]"); pg.wait_for_timeout(300)
def match_shown(pg): return pg.locator("#match.show").count() == 1
def close_match(pg): pg.click("#matchBtn"); pg.wait_for_timeout(400)
def top(pg): pg.evaluate("document.getElementById('sheetBody').scrollTop = 0"); pg.wait_for_timeout(200)
def pal(pg): return pg.inner_text(".pal") if pg.locator(".pal").count() else ""
def award(pg, i): return pg.locator(f".ph:nth-child({i+1}) .award").inner_text() if pg.locator(f".ph:nth-child({i+1}) .award").count() else ""

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=os.environ["CHROMIUM_PATH"], proxy={"server": os.environ["HTTPS_PROXY"]},
                          args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    for mode, base in (("globe", "http://nos-voyages.test/"), ("plate", "http://nos-voyages.test/?carte=plate")):
        pg = page(b, mode, seed)
        pg.goto(base + "#admin"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(2000)
        pg.click("#loginCancel")
        check(f"[{mode}] démo : sélecteur Maxime / Roxane visible", pg.locator("#demoWho").is_visible())
        # 1. Maxime : 🌅 photo 0, 💗 photo 1, 😂 souvenir 0
        who(pg, "demo-maxime"); open_country(pg, "portugal", "Portugal")
        lb_pick(pg, 0, "vue"); t = pg.inner_text("#toast")
        check(f"[{mode}] toast « {t} »", t == "🌅 Ta plus belle vue au Portugal")
        check(f"[{mode}] bouton 🌅 actif dans la visionneuse", pg.locator("#lbPicks [data-cat='vue'].on").count() == 1)
        pg.click("[data-lb=next]"); pg.wait_for_timeout(300); pg.click("#lbPicks [data-cat='prefere']"); pg.wait_for_timeout(500); lb_close(pg)
        pg.click("[data-action=memPicks][data-id='m0']"); pg.wait_for_timeout(300); pg.click("[data-action=pickMem][data-id='m0'][data-cat='drole']"); pg.wait_for_timeout(500)
        t = pal(pg)
        if mode == "globe": pg.wait_for_timeout(2700); top(pg); shot(pg, "ordre006-1-maxime")
        check(f"[{mode}] palmarès de Maxime : vue, drôle, préféré", "Plus belle vue" in t and "Moment le plus drôle" in t and "Préféré de Maxime" in t and "Préféré de Roxane" in t and "Pas encore choisi" in t)
        check(f"[{mode}] emojis sur les vignettes (🌅 / 💗) : « {award(pg,0)} » « {award(pg,1)} »", award(pg, 0) == "🌅" and award(pg, 1) == "💗")
        # 2. Roxane : 💗 de Maxime caché, elle choisit une autre photo
        who(pg, "demo-roxane"); t = pal(pg)
        check(f"[{mode}] Roxane : le 💗 de Maxime est caché (🔒)", "🔒 Choisis le tien pour découvrir celui de Maxime" in t and award(pg, 1) == "")
        if mode == "globe": top(pg); shot(pg, "ordre006-2-roxane-secret"); pg.locator(".pal").screenshot(path=f"{OUT}/ordre006-2b-palmares-secret.png")
        lb_pick(pg, 2, "prefere"); lb_close(pg)
        t = pal(pg)
        check(f"[{mode}] Roxane choisit une autre photo : les deux se révèlent, pas d'animation", not match_shown(pg) and t.count("Préféré de") == 2 and "🔒" not in t and pg.locator(".pal-cols .pal-thumb").count() == 2)
        # 3. Roxane change d'avis : la même photo que Maxime -> animation
        lb_pick(pg, 1, "prefere")
        check(f"[{mode}] même moment : animation", match_shown(pg) and "Vous avez choisi le même moment" in pg.inner_text("#match") and "Portugal" in pg.inner_text("#match"))
        if mode == "globe": pg.wait_for_timeout(1300); shot(pg, "ordre006-3-meme-moment")
        close_match(pg); lb_close(pg)
        check(f"[{mode}] « Votre moment préféré à tous les deux 💞 »", "Votre moment préféré à tous les deux 💞" in pal(pg))
        if mode == "globe": pg.wait_for_timeout(2700); top(pg); shot(pg, "ordre006-4-vous-deux"); pg.locator(".pal").screenshot(path=f"{OUT}/ordre006-4b-palmares-vous-deux.png")
        # 4. Correspondance créée par Maxime après Roxane -> une seule fois à la « réouverture » en Roxane
        lb_pick(pg, 2, "prefere"); lb_close(pg)
        who(pg, "demo-maxime"); lb_pick(pg, 2, "prefere")
        check(f"[{mode}] Maxime crée la correspondance : animation pour lui", match_shown(pg)); close_match(pg); lb_close(pg)
        pg.click("#closeSheet"); pg.wait_for_timeout(400)
        who(pg, "demo-roxane"); pg.wait_for_timeout(500)
        check(f"[{mode}] Roxane : animation à l'ouverture (correspondance non vue)", match_shown(pg)); close_match(pg)
        pg.goto(base + "#admin"); pg.reload(); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(2500)
        if pg.locator("#loginModal.show").count(): pg.click("#loginCancel")
        check(f"[{mode}] réouverture : l'animation ne se rejoue pas (et les choix sont bien là)", not match_shown(pg) and "Plus belle vue" in (open_country(pg, "portugal", "Portugal") or pal(pg)))
        if pg.locator("body.admin").count():
            pg.click("#closeSheet"); pg.wait_for_timeout(400); pg.click("#logoutBtn"); pg.wait_for_timeout(300); open_country(pg, "portugal", "Portugal")
        # 5. 😂 : deux votes différents puis même vote
        pg.click("[data-action=memPicks][data-id='m1']"); pg.wait_for_timeout(300); pg.click("[data-action=pickMem][data-id='m1'][data-cat='drole']"); pg.wait_for_timeout(500)
        row = pg.locator(".pal-row:has-text('Moment le plus drôle')").inner_text()
        check(f"[{mode}] 😂 deux votes différents : Maxime et Roxane", "Maxime" in row and "Roxane" in row and "Vous deux" not in row)
        pg.click("[data-action=memPicks][data-id='m0']"); pg.wait_for_timeout(300); pg.click("[data-action=pickMem][data-id='m0'][data-cat='drole']"); pg.wait_for_timeout(500)
        row = pg.locator(".pal-row:has-text('Moment le plus drôle')").inner_text()
        check(f"[{mode}] 😂 même vote : « Vous deux »", "Vous deux" in row)
        # 8. Supprimer une photo récompensée (🌅 de Maxime, photo 0) -> choix retiré proprement
        pg.click("[data-action=join]"); pg.wait_for_timeout(400)
        check(f"[{mode}] Roxane : « ➕ Ajouter nos souvenirs » ouvre le mode édition sans code", pg.locator("body.admin").count() == 1 and pg.locator("#codeModal.show").count() == 0)
        pg.once("dialog", lambda d: d.accept())
        pg.click(".ph:nth-child(1) .del"); pg.wait_for_timeout(700)
        check(f"[{mode}] photo récompensée supprimée : le 🌅 disparaît du palmarès", "Plus belle vue" not in pal(pg) and pg.locator(".ph img").count() == 2)
        # 7. Roxane : photo, souvenir, nouveau pays, retrait
        pg.set_input_files("input[data-action=addPhotos]", {"name": "rox.jpg", "mimeType": "image/jpeg", "buffer": base64.b64decode(jpeg((10,10,200)).split(",")[1])}); pg.wait_for_timeout(1500)
        check(f"[{mode}] Roxane ajoute une photo", pg.locator(".ph img").count() == 3)
        pg.fill("#newMem", "Le coucher de soleil à Sintra"); pg.click("[data-action=addMem]"); pg.wait_for_timeout(600)
        m = pg.locator(".mem:has-text('Sintra')").inner_text()
        check(f"[{mode}] son souvenir est signé « — Roxane »", "— Roxane" in m)
        check(f"[{mode}] l'ancien souvenir sans auteur n'a pas de signature", "—" not in pg.locator("#mem-m1 .mem-sign").all_inner_texts().__str__() and pg.locator("#mem-m1 .mem-sign").count() == 0)
        if mode == "globe": shot(pg, "ordre006-5-roxane-edition")
        open_country(pg, "italie", "Italie"); pg.click("text=❤️ Visité"); pg.wait_for_timeout(600)
        check(f"[{mode}] Roxane marque l'Italie visitée", "Visité ensemble" in pg.inner_text("#sheetBody"))
        pg.click("text=Pas encore"); pg.wait_for_timeout(600)
        check(f"[{mode}] Roxane retire l'Italie", "Encore à découvrir" in pg.inner_text("#sheetBody"))
        pg.click("#closeSheet"); pg.wait_for_timeout(400); pg.click("#logoutBtn"); pg.wait_for_timeout(300); open_country(pg, "portugal", "Portugal")
        check(f"[{mode}] « Quitter » : hors édition mais toujours connectée (➕ visible, choix possibles sans code)", pg.locator("body.admin").count() == 0 and pg.locator("[data-action=join]").count() == 1 and pg.locator(".mem-award").count() > 0)
        pg.click("[data-action=join]"); pg.wait_for_timeout(300)
        check(f"[{mode}] ➕ rouvre l'édition sans redemander le code", pg.locator("body.admin").count() == 1 and pg.locator("#codeModal.show").count() == 0)
        pg.context.close()

    # 9. PALMARES_ACTIF = false
    off = page(b, "off", {**seed, "picks":[{"id":"x","user_id":"demo-maxime","country_code":"PRT","category":"vue","photo_id":"p0","memory_id":None}]}, init="localStorage.setItem('nos-voyages-demo-who','demo-maxime')")
    off.route("http://nos-voyages.test/index.html", lambda r: r.fulfill(body=open(os.environ["APP_DIR"] + "/index.html").read().replace("const PALMARES_ACTIF = true;", "const PALMARES_ACTIF = false;"), content_type="text/html"))
    off.goto("http://nos-voyages.test/index.html#admin"); off.wait_for_load_state("networkidle"); off.wait_for_timeout(2000)
    open_country(off, "portugal", "Portugal")
    off.click(".ph img[data-i='0']"); off.wait_for_timeout(400)
    check("PALMARES_ACTIF = false : aucune trace (bloc, 🏅, emojis, barre de la visionneuse)",
          off.locator(".pal, .mem-award, .award").count() == 0 and off.locator("#lightbox.picks").count() == 0)
    off.context.close()
    b.close()
print("Erreurs console :", *(errs or ["aucune"]), sep="\n  ")
print(f"{sum(results)}/{len(results)} vérifications réussies")
