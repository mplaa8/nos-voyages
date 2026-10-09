# Tests ORDRE-002 au format iPhone (390×844), en mode démo — voir le compte rendu de docs/ordres/ORDRE-002.
# Usage : APP_DIR=<copie du site avec CONFIG vide> LIBS_DIR=<copies locales leaflet/supabase-js/geojson> CHROMIUM_PATH=<chromium> python3 tests/test_ordre002_iphone.py <dossier de sortie>
import os, sys, mimetypes, urllib.parse, json
import cv2
from playwright.sync_api import sync_playwright
OUT = sys.argv[1]; ROOT = os.environ["APP_DIR"]; L = os.environ["LIBS_DIR"]
errs = []
def setup(ctx):
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
    }
    for url, (f, ct) in mocks.items():
        ctx.route(url, (lambda f, ct: lambda r: r.fulfill(path=f, content_type=ct))(f, ct))
    ctx.route("**/ne_50m_admin_0_countries.geojson", lambda r: r.fulfill(path=L + "/ne50.geojson", content_type="application/json", headers={"Access-Control-Allow-Origin": "*"}))
def page(b, tag, **kw):
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True, service_workers="block", **kw)
    setup(ctx); pg = ctx.new_page()
    pg.on("console", lambda m: m.type == "error" and errs.append(f"[{tag}] {m.text}"))
    pg.on("pageerror", lambda e: errs.append(f"[{tag}] {e}"))
    return pg
def check(name, cond): print(("OK   " if cond else "ÉCHEC"), name); return cond
demo = {"countries":[{"code":"FRA","name":"France","status":"visited","places":""},{"code":"ITA","name":"Italie","status":"visited","places":""},{"code":"JPN","name":"Japon","status":"visited","places":""},{"code":"USA","name":"États-Unis","status":"dream","places":""}],"memories":[],"photos":[]}
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=os.environ["CHROMIUM_PATH"], proxy={"server": os.environ["HTTPS_PROXY"]})
    # 1. Accueil -> lettre -> carte
    pg = page(b, "parcours")
    pg.add_init_script(f"localStorage.setItem('nos-voyages-demo', {json.dumps(json.dumps(demo))})")
    pg.goto("http://nos-voyages.test/"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(2500)
    pg.screenshot(path=f"{OUT}/ordre002-1-accueil.png")
    pg.click("#openGift"); pg.wait_for_timeout(3600)
    pg.screenshot(path=f"{OUT}/ordre002-2-lettre.png")
    txt = pg.inner_text("#letterText")
    check("texte de la lettre exact", txt == "Mon amour, en ce jour si spécial, je souhaite t'offrir un cadeau que nous utiliserons jusqu'à notre dernier voyage. Peu importe où nous irons, je sais que je me sentirai à ma place, car je serai à tes côtés.")
    check("signature « Max »", pg.inner_text("#letterSign") == "Max")
    bb = pg.locator(".letter-card").bounding_box(); btn = pg.locator("#letterBtn").bounding_box()
    print("     carte lettre :", bb, " bouton :", btn, " police :", pg.eval_on_selector("#letterText", "e => getComputedStyle(e).fontSize"))
    check("lettre entière visible sans défilement", bb["y"] >= 0 and bb["y"] + bb["height"] <= 844)
    check("bouton ≥ 44 px", btn["height"] >= 44)
    check("accueil retiré", pg.locator("#welcome").count() == 0)
    pg.click("#letterBtn"); pg.wait_for_timeout(1200)
    check("lettre masquée", not pg.locator("#letter").is_visible())
    pg.screenshot(path=f"{OUT}/ordre002-3-carte.png")
    # 2. Stats
    pg.click("#listBtn"); pg.wait_for_timeout(700)
    stats = pg.inner_text(".list-stats")
    check(f"statistiques : « {stats} »", stats == "3 pays · 2 continents découverts ensemble")
    pg.screenshot(path=f"{OUT}/ordre002-4-liste.png")
    # 3. Relire
    pg.click("text=💌 Relire ta lettre"); pg.wait_for_timeout(2600)
    check("« Relire ta lettre » rouvre la lettre", pg.locator("#letter.show").count() == 1 and pg.locator("#letterBtn").is_visible())
    pg.screenshot(path=f"{OUT}/ordre002-5-relire.png")
    pg.click("#letterBtn"); pg.wait_for_timeout(1200)
    check("retour à la carte", not pg.locator("#letter").is_visible() and pg.locator("#sheet.open").count() == 0)
    # singulier
    pg2 = page(b, "singulier")
    one = {"countries":[demo["countries"][0]],"memories":[],"photos":[]}
    pg2.add_init_script(f"localStorage.setItem('nos-voyages-demo', {json.dumps(json.dumps(one))})")
    pg2.goto("http://nos-voyages.test/#admin"); pg2.wait_for_load_state("networkidle"); pg2.wait_for_timeout(1500)
    # 4. #admin
    check("#admin : pas d'accueil", pg2.locator("#welcome").count() == 0)
    check("#admin : pas de lettre", not pg2.locator("#letter").is_visible())
    pg2.screenshot(path=f"{OUT}/ordre002-6-admin.png")
    pg2.click("#loginCancel"); pg2.click("#listBtn"); pg2.wait_for_timeout(700)
    check("singulier : " + pg2.inner_text(".list-stats"), pg2.inner_text(".list-stats") == "1 pays · 1 continent découvert ensemble")
    # aucun pays visité
    pg3 = page(b, "vide"); pg3.goto("http://nos-voyages.test/#admin"); pg3.wait_for_load_state("networkidle"); pg3.wait_for_timeout(1000)
    pg3.click("#loginCancel"); pg3.click("#listBtn"); pg3.wait_for_timeout(500)
    check("aucun pays : pas de statistiques", pg3.locator(".list-stats").count() == 0)
    # 5. Carte cadeau
    pc = b.new_context(viewport={"width": 1000, "height": 1300}, device_scale_factor=2); setup(pc); cp = pc.new_page()
    cp.on("console", lambda m: m.type == "error" and errs.append(f"[carte] {m.text}")); cp.on("pageerror", lambda e: errs.append(f"[carte] {e}"))
    cp.goto("http://nos-voyages.test/carte-cadeau.html"); cp.wait_for_load_state("networkidle"); cp.wait_for_timeout(800)
    cp.screenshot(path=f"{OUT}/ordre002-7-carte-cadeau.png", full_page=True)
    cp.locator(".tile").first.screenshot(path=f"{OUT}/qr.png")
    dec = cv2.QRCodeDetector().detectAndDecode(cv2.imread(f"{OUT}/qr.png"))[0]
    check(f"QR décodé : « {dec} »", dec == "https://mplaa8.github.io/nos-voyages/")
    cp.emulate_media(media="print"); cp.pdf(path=f"{OUT}/carte-cadeau.pdf", prefer_css_page_size=True, print_background=True)
    b.close()
print("Erreurs console :", *(errs or ["aucune"]), sep="\n  ")
