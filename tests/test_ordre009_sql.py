# Tests ORDRE-009 : migration 003 et vérification des droits sur un PostgreSQL local imitant Supabase.
# Usage : python3 tests/test_ordre009_sql.py <dossier contenant setup-v1.sql (= setup.sql du tag v1.0-anniversaire)> <racine du dépôt>  — PostgreSQL 16 lancé sur le port 5499.
import subprocess, sys
S, REPO = sys.argv[1], sys.argv[2]
H = "/var/lib/postgresql/pgtest"
MAX, ROX, AUTRE = "11111111-1111-1111-1111-111111111111", "22222222-2222-2222-2222-222222222222", "33333333-3333-3333-3333-333333333333"
cnt = [0, 0]
def psql(db, sql, extra=()):
    r = subprocess.run(["psql", "-h", H, "-p", "5499", "-U", "postgres", "-d", db, "-v", "ON_ERROR_STOP=1", "-q", "-t", "-A", *extra], input=sql, capture_output=True, text=True)
    return r.returncode == 0, (r.stdout + r.stderr).strip()
def check(name, cond, detail=""):
    cnt[0] += cond; cnt[1] += 1; print(("OK   " if cond else "ÉCHEC"), name, ("" if cond else "→ " + detail[-400:]))
def as_user(db, uid, sql):
    role = "anon" if uid is None else "authenticated"
    who = "" if uid is None else f"set local request.jwt.claims = '{{\"sub\":\"{uid}\",\"role\":\"authenticated\"}}';"
    return psql(db, f"begin; set local role {role}; {who} {sql}; commit;")
STUB = f"""
do $$ begin create role anon nologin; exception when duplicate_object then null; end $$;
do $$ begin create role authenticated nologin; exception when duplicate_object then null; end $$;
create schema auth; create table auth.users (id uuid primary key, email text);
create function auth.uid() returns uuid language sql stable as $f$ select coalesce(nullif(current_setting('request.jwt.claim.sub', true), ''), (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'sub'))::uuid $f$;
create schema storage; create table storage.buckets (id text primary key, name text, public boolean);
create table storage.objects (id uuid primary key default gen_random_uuid(), bucket_id text, name text);
alter table storage.objects enable row level security;
create publication supabase_realtime;
grant usage on schema public, auth, storage to anon, authenticated;
grant execute on function auth.uid() to anon, authenticated;
grant select, insert, update, delete on storage.objects to anon, authenticated;
alter default privileges in schema public grant select, insert, update, delete on tables to anon, authenticated;
insert into auth.users values ('{MAX}', 'maxime@exemple.fr'), ('{ROX}', 'roxane@nos-voyages.fr'), ('{AUTRE}', 'inconnu@exemple.fr');
"""
def fresh(db):
    psql("postgres", f"drop database if exists {db};"); psql("postgres", f"create database {db};"); ok, out = psql(db, STUB); assert ok, out
emails = lambda t: t.replace("EMAIL-DE-MAXIME", "maxime@exemple.fr").replace("EMAIL-DE-ROXANE", "roxane@nos-voyages.fr")
mig2 = emails(open(f"{REPO}/migration-002-palmares.sql").read()); mig3 = open(f"{REPO}/migration-003-destinations.sql").read()
verif = open(f"{REPO}/verification-droits.sql").read()

print("— Base « jour J » (setup v1.0) puis migration 003")
fresh("d1"); ok, out = psql("d1", emails(open(f"{S}/setup-v1.sql").read())); check("base v1.0-anniversaire installée", ok, out)
psql("d1", "insert into countries (code, name) values ('PRT', 'Portugal'); insert into picks (user_id, country_code, category, photo_id) select '%s', 'PRT', 'vue', null where false;" % MAX)
ok, out = psql("d1", verif); check("vérification AVANT migration 003 : lignes ⚠️ « table absente », le reste ✅", ok and out.count("⚠️ table absente") == 2 and out.count("✅") == 4, out)
before = psql("d1", "select string_agg(tablename||':'||policyname, ',' order by tablename, policyname) from pg_policies")[1]
ok, out = psql("d1", mig3); check("migration 003 : Success", ok, out)
ok, out = psql("d1", mig3); check("migration 003 relancée : Success (rejouable)", ok, out)
after = psql("d1", "select string_agg(tablename||':'||policyname, ',' order by tablename, policyname) from pg_policies where tablename <> 'wishes'")[1]
check("purement additive : aucune règle existante modifiée", before == after, before + " ≠ " + after)
ok, out = psql("d1", "select count(*) from pg_publication_tables where pubname = 'supabase_realtime' and tablename = 'wishes'"); check("wishes dans le temps réel (une seule fois)", out == "1", out)
ok, out = psql("d1", verif); check("vérification APRÈS migration 003 : 6 lignes ✅", ok and out.count("✅") == 6 and "❌" not in out and "⚠️" not in out, out)
print(out)
print("— Droits sur wishes")
ok, out = as_user("d1", None, "insert into wishes (user_id, country_code, answer) values ('%s', 'JPN', 'oui')" % MAX); check("visiteur ne peut pas répondre", not ok and "row-level security" in out, out)
ok, out = as_user("d1", AUTRE, "insert into wishes (country_code, answer) values ('JPN', 'oui')"); check("compte non membre ne peut pas répondre", not ok, out)
ok, out = as_user("d1", MAX, "insert into wishes (country_code, answer) values ('JPN', 'oui') returning user_id"); check("Maxime répond (user_id automatique)", ok and out.splitlines()[0] == MAX, out)
ok, out = as_user("d1", ROX, "insert into wishes (country_code, answer) values ('JPN', 'non'); insert into wishes (user_id, country_code, answer) values ('%s', 'JPN', 'oui') on conflict (user_id, country_code) do update set answer = excluded.answer returning answer" % ROX); check("Roxane répond puis change d'avis (upsert)", ok and out.splitlines()[-1] == "oui", out)
ok, out = as_user("d1", ROX, "insert into wishes (user_id, country_code, answer) values ('%s', 'ISL', 'oui')" % MAX); check("Roxane ne peut pas répondre à la place de Maxime", not ok, out)
ok, out = as_user("d1", MAX, "delete from wishes where user_id = '%s' returning country_code" % ROX); check("Maxime ne peut pas effacer les réponses de Roxane (0 ligne)", ok and out == "", out)
ok, out = as_user("d1", MAX, "delete from wishes where country_code = 'JPN' returning country_code"); check("« Annuler » : Maxime retire sa propre réponse", ok and out.splitlines()[0] == "JPN", out)
ok, out = as_user("d1", ROX, "insert into wishes (country_code, answer) values ('GUF', 'peutetre')"); check("réponse autre que oui/non refusée", not ok, out)
ok, out = as_user("d1", ROX, "insert into wishes (country_code, answer) values ('GUF', 'oui')"); check("territoire hors de « countries » (Guyane) accepté (pas de clé étrangère)", ok, out)
ok, out = as_user("d1", None, "select count(*) from wishes"); check("lecture publique (le secret est géré par l'app)", ok and out.endswith("2"), out)
print("— Migration 003 sans la 002")
fresh("d2"); psql("d2", "create table public.countries (code text primary key, name text not null);")
ok, out = psql("d2", mig3); check("migration 003 sans la 002 : arrêt avec message clair, rien de créé", not ok and "migration-002" in out and psql("d2", "select count(*) from pg_tables where tablename = 'wishes'")[1] == "0", out)
print("— Installation neuve")
fresh("d3"); ok, out = psql("d3", emails(open(f"{REPO}/setup.sql").read())); check("setup.sql (avec wishes) : Success", ok, out)
ok, out = psql("d3", verif); check("installation neuve : vérification 6 lignes ✅", ok and out.count("✅") == 6, out)
print(f"{cnt[0]}/{cnt[1]} vérifications SQL réussies")
