# Tests ORDRE-006 : visiteur et code secret face à un Supabase simulé (base, connexion, stockage, temps réel), iPhone 390×844.
# Usage : APP_DIR=<copie du site avec CONFIG vide> LIBS_DIR=<copies locales leaflet/maplibre/supabase-js/geojson> CHROMIUM_PATH=<chromium> python3 tests/test_ordre006_code_iphone.py <dossier de sortie>
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

import base64, time
FAKE = "https://fake.supabase.co"
def b64u(o): return base64.urlsafe_b64encode(json.dumps(o).encode()).decode().rstrip("=")
img = cv2.imencode(".jpg", np.full((120, 160, 3), (60, 200, 90), np.uint8))[1].tobytes()
CORS = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "GET,POST,PATCH,DELETE,OPTIONS", "Access-Control-Expose-Headers": "*"}
picks = [{"id": "k1", "user_id": "u-max", "country_code": "PRT", "category": "prefere", "photo_id": "ph1", "memory_id": None, "created_at": "2026-10-10T10:00:00Z"}]
posted = []
def fake(route):
    r = route.request; u = r.url
    if r.method == "OPTIONS": return route.fulfill(status=200, headers=CORS, body="")
    js = lambda o, st=200: route.fulfill(status=st, headers={**CORS, "Content-Type": "application/json"}, body=json.dumps(o))
    if "/storage/v1/object/public/photos/" in u: return route.fulfill(status=200, headers={**CORS, "Content-Type": "image/jpeg"}, body=img)
    if "/auth/v1/token" in u:
        d = json.loads(r.post_data or "{}")
        if d.get("email") == "roxane@nos-voyages.fr" and d.get("password") == "14102016":
            exp = int(time.time()) + 3600
            tok = b64u({"alg": "HS256", "typ": "JWT"}) + "." + b64u({"sub": "u-rox", "exp": exp, "role": "authenticated", "aud": "authenticated"}) + ".sig"
            return js({"access_token": tok, "token_type": "bearer", "expires_in": 3600, "expires_at": exp, "refresh_token": "r",
                       "user": {"id": "u-rox", "aud": "authenticated", "role": "authenticated", "email": d["email"], "app_metadata": {}, "user_metadata": {}, "created_at": "2026-10-01T00:00:00Z"}})
        return js({"code": 400, "error_code": "invalid_credentials", "msg": "Invalid login credentials"}, 400)
    if "/rest/v1/countries" in u: return js([{"code": "PRT", "name": "Portugal", "status": "visited", "places": "", "updated_at": "2026-10-01T00:00:00Z"}])
    if "/rest/v1/memories" in u: return js([])
    if "/rest/v1/photos" in u: return js([{"id": "ph1", "country_code": "PRT", "path": "PRT/a.jpg", "author_id": "u-max", "created_at": "2026-10-01T00:00:00Z"}])
    if "/rest/v1/members" in u: return js([{"user_id": "u-max", "prenom": "Maxime"}, {"user_id": "u-rox", "prenom": "Roxane"}])
    if "/rest/v1/picks" in u:
        if r.method == "POST":
            row = {**json.loads(r.post_data), "id": "k2", "created_at": "2026-10-11T20:00:00Z"}
            posted.append({"row": row, "auth": r.headers.get("authorization", "")}); picks.append(row)
            return js(row, 201)
        return js(picks)
    return route.fulfill(status=404, headers=CORS, body="")

def ws_handler(ws):
    def on(msg):
        try: m = json.loads(msg)
        except Exception: return
        if isinstance(m, list):
            join_ref, ref, topic, event, payload = m
            if event in ("phx_join", "heartbeat", "access_token"):
                resp = {"postgres_changes": [{"id": 1, "event": "*", "schema": "public", "table": "picks"}]} if event == "phx_join" else {}
                ws.send(json.dumps([join_ref, ref, topic, "phx_reply", {"status": "ok", "response": resp}]))
        elif isinstance(m, dict) and m.get("event") in ("phx_join", "heartbeat", "access_token"):
            resp = {"postgres_changes": [{"id": 1, "event": "*", "schema": "public", "table": "picks"}]} if m["event"] == "phx_join" else {}
            ws.send(json.dumps({"topic": m["topic"], "event": "phx_reply", "payload": {"status": "ok", "response": resp}, "ref": m.get("ref")}))
    ws.on_message(on)

remote_html = open(os.environ["APP_DIR"] + "/index.html").read().replace('SUPABASE_URL: ""', f'SUPABASE_URL: "{FAKE}"').replace('SUPABASE_ANON_KEY: ""', 'SUPABASE_ANON_KEY: "sb_publishable_test"')
assert FAKE in remote_html
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=os.environ["CHROMIUM_PATH"], proxy={"server": os.environ["HTTPS_PROXY"]},
                          args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    pg = page(b, "visiteur")
    pg.context.route(FAKE + "/**", fake)
    pg.context.route_web_socket("**/realtime/**", ws_handler)
    pg.route("http://nos-voyages.test/", lambda r: r.fulfill(body=remote_html, content_type="text/html"))
    pg.goto("http://nos-voyages.test/"); pg.wait_for_load_state("networkidle"); pg.wait_for_timeout(1500)
    pg.click("#openGift"); pg.wait_for_timeout(3600); pg.click("#letterBtn"); pg.wait_for_timeout(1500)
    check("visiteur : pas de sélecteur de démo", not pg.locator("#demoWho").is_visible())
    pg.click("#listBtn"); pg.wait_for_timeout(400)
    check("table « wishes » absente (migration 003 pas lancée) : aucune trace des envies, aucun message", pg.locator(".envies").count() == 0 and not pg.locator("#toast.show").count())
    check("liste : « ➕ Ajouter nos souvenirs » pour le visiteur", pg.locator("[data-action=join]").count() == 1 and pg.locator("[data-action=logout]").count() == 0)
    pg.fill("#search", "portugal"); pg.click("#listBody .list-item:has-text('Portugal')"); pg.wait_for_timeout(1800)
    t = pg.inner_text(".pal")
    check("visiteur : le 💗 de Maxime est caché (🔒), pas d'emoji sur la photo", "🔒 Choisis le tien pour découvrir celui de Maxime" in t and pg.locator(".award").count() == 0)
    check("fiche : « ➕ Ajouter nos souvenirs » en bas", pg.locator("#sheetBody [data-action=join]").count() == 1)
    pg.click(".ph img[data-i='0']"); pg.wait_for_timeout(500)
    check("visionneuse : barre 🌅 🍽️ 😂 💗 visible pour le visiteur", pg.locator("#lightbox.picks #lbPicks .pick-btn").count() == 4)
    pg.click("#lbPicks [data-cat='prefere']"); pg.wait_for_timeout(500)
    box = pg.locator("#codeForm").bounding_box()
    top_el = pg.evaluate(f"document.elementFromPoint({box['x'] + box['width']/2}, {box['y'] + 30}).closest('#codeModal') !== null")
    check("toucher 💗 ouvre la fenêtre du code secret, au-dessus de la photo", pg.locator("#codeModal.show").count() == 1 and top_el)
    mt = pg.inner_text("#codeModal")
    check("fenêtre : indice affiché, aucune mention du mode édition", "Notre date secrète (JJMMAAAA) 💕" in mt and "dition" not in mt)
    attrs = pg.eval_on_selector("#codeInput", "e => [e.inputMode, getComputedStyle(e).fontSize]")
    check(f"champ : clavier numérique, police ≥ 16 px ({attrs})", attrs[0] == "numeric" and float(attrs[1][:-2]) >= 16)
    pg.screenshot(path=f"{OUT}/ordre006-6-code-secret.png")
    pg.fill("#codeInput", "0000"); pg.click("#codeForm button[type=submit]"); pg.wait_for_timeout(1200)
    check(f"mauvais code : message doux (« {pg.inner_text('#codeErr')} »)", pg.inner_text("#codeErr") == "Ce n’est pas tout à fait ça… essaie encore 💭" and pg.locator("#codeModal.show").count() == 1)
    pg.screenshot(path=f"{OUT}/ordre006-7-mauvais-code.png")
    pg.fill("#codeInput", "14102016"); pg.click("#codeForm button[type=submit]"); pg.wait_for_timeout(1500)
    check("bon code : connectée en Roxane, le choix 💗 en attente est enregistré", pg.locator("#codeModal.show").count() == 0 and len(posted) == 1 and posted[0]["row"]["category"] == "prefere" and posted[0]["row"]["user_id"] == "u-rox" and posted[0]["auth"].startswith("Bearer ey"))
    check("même photo que Maxime : animation « même moment »", pg.locator("#match.show").count() == 1)
    pg.wait_for_timeout(1300); pg.screenshot(path=f"{OUT}/ordre006-8-code-puis-meme-moment.png")
    pg.click("#matchBtn"); pg.wait_for_timeout(400); pg.click("[data-lb=close]"); pg.wait_for_timeout(400)
    check("palmarès : « Votre moment préféré à tous les deux 💞 »", "Votre moment préféré à tous les deux 💞" in pg.inner_text(".pal"))
    check("connexion par un choix : pas de mode édition, mais ➕ entre sans code", pg.locator("body.admin").count() == 0)
    pg.click("#sheetBody [data-action=join]"); pg.wait_for_timeout(400)
    check("➕ : mode édition sans redemander le code", pg.locator("body.admin").count() == 1 and pg.locator("#codeModal.show").count() == 0)
    pg.context.close()
    b.close()
attendues = [e for e in errs if "400" in e or "404" in e]
print("Erreurs console :", *(errs or ["aucune"]), sep="\n  ")
print(f"(dont {len(attendues)} attendue(s) : 400 = mauvais code ; 404 = table « wishes » volontairement absente)")
print(f"{sum(results)}/{len(results)} vérifications réussies")
