# Tests ORDRE-006 : migration et règles de sécurité sur un PostgreSQL local imitant Supabase (schémas auth/storage, rôles anon/authenticated).
# Usage : python3 tests/test_ordre006_sql.py <dossier contenant setup-ancien.sql (= ancien setup.sql)> <racine du dépôt>  — PostgreSQL 16 lancé sur le port 5499.
import subprocess, sys
S, REPO = sys.argv[1], sys.argv[2]
H = "/var/lib/postgresql/pgtest"
MAX, ROX, AUTRE = "11111111-1111-1111-1111-111111111111", "22222222-2222-2222-2222-222222222222", "33333333-3333-3333-3333-333333333333"
ok_count = [0, 0]
def psql(db, sql):
    r = subprocess.run(["psql", "-h", H, "-p", "5499", "-U", "postgres", "-d", db, "-v", "ON_ERROR_STOP=1", "-q", "-t", "-A"], input=sql, capture_output=True, text=True)
    return r.returncode == 0, (r.stdout + r.stderr).strip()
def check(name, cond, detail=""):
    ok_count[0] += cond; ok_count[1] += 1
    print(("OK   " if cond else "ÉCHEC"), name, ("" if cond else "→ " + detail[-300:]))
def as_user(db, uid, sql):   # rôle et identité comme dans une requête Supabase
    role = "anon" if uid is None else "authenticated"
    who = "" if uid is None else f"set local request.jwt.claim.sub = '{uid}';"
    return psql(db, f"begin; set local role {role}; {who} {sql}; commit;")
STUB = f"""
do $$ begin create role anon nologin; exception when duplicate_object then null; end $$;
do $$ begin create role authenticated nologin; exception when duplicate_object then null; end $$;
create schema auth; create table auth.users (id uuid primary key, email text);
create function auth.uid() returns uuid language sql stable as $f$ select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid $f$;
create schema storage;
create table storage.buckets (id text primary key, name text, public boolean);
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
    psql("postgres", f"drop database if exists {db}; create database {db};"); ok, out = psql(db, STUB); assert ok, out
mig = open(f"{REPO}/migration-002-palmares.sql").read()
mig_ok = mig.replace("EMAIL-DE-MAXIME", "maxime@exemple.fr").replace("EMAIL-DE-ROXANE", "roxane@nos-voyages.fr")

print("— Base existante (ancien setup.sql) + données")
fresh("t1"); ok, out = psql("t1", open(f"{S}/setup-ancien.sql").read()); check("ancien setup.sql s'installe", ok, out)
psql("t1", "insert into countries (code, name) values ('PRT', 'Portugal'); insert into memories (country_code, content) values ('PRT', 'ancien souvenir'); insert into photos (id, country_code, path) values ('aaaaaaaa-0000-0000-0000-000000000001', 'PRT', 'PRT/a.jpg');")
ok, out = psql("t1", mig); check("migration SANS remplacer les e-mails : arrêt avec message clair", not ok and "Compte de Maxime introuvable" in out, out)
ok, out = psql("t1", "select count(*) from pg_tables where tablename in ('members','picks')"); check("… et rien n'a été modifié (ni members ni picks créés)", out == "0", out)
ok, out = as_user("t1", MAX, "insert into countries (code, name) values ('ESP', 'Espagne')"); check("… Maxime garde l'accès à l'édition (anciennes règles intactes)", ok, out)
ok, out = psql("t1", mig.replace("EMAIL-DE-MAXIME", "maxime@exemple.fr")); check("e-mail de Roxane manquant : arrêt avec message clair", not ok and "Compte de Roxane introuvable" in out, out)
ok, out = psql("t1", mig_ok); check("migration avec les deux e-mails : Success", ok, out)
ok, out = psql("t1", mig_ok); check("migration relancée une 2e fois : Success (rejouable)", ok, out)
ok, out = psql("t1", "select string_agg(prenom, ',' order by prenom) from members"); check("members : Maxime et Roxane", out == "Maxime,Roxane", out)
ok, out = psql("t1", "select count(*) from memories where author_id is null"); check("anciens souvenirs : sans auteur", out == "1", out)
ok, out = psql("t1", "select count(*) from pg_publication_tables where pubname = 'supabase_realtime' and tablename = 'picks'"); check("picks dans la publication temps réel (une seule fois)", out == "1", out)

print("— Droits après migration")
for who, uid in (("visiteur", None), ("compte non membre", AUTRE)):
    for t, sql in (("ajouter un pays", "insert into countries (code, name) values ('ITA', 'Italie')"),
                   ("ajouter un souvenir", "insert into memories (country_code, content) values ('PRT', 'x')"),
                   ("ajouter une photo (stockage)", "insert into storage.objects (bucket_id, name) values ('photos', 'PRT/x.jpg')")):
        ok, out = as_user("t1", uid, sql); check(f"{who} ne peut pas {t}", not ok and "row-level security" in out, out)
    ok, out = as_user("t1", uid, "delete from countries where code = 'PRT' returning code"); check(f"{who} ne peut pas supprimer un pays (0 ligne)", ok and out == "", out)
    ok, out = as_user("t1", uid, "select count(*) from countries"); check(f"{who} peut lire la carte", ok and out.endswith("2"), out)
for who, uid in (("Maxime", MAX), ("Roxane", ROX)):
    ok, out = as_user("t1", uid, f"insert into countries (code, name) values ('T{who[0]}X', 'Test') ; update countries set places = 'Lisbonne' where code = 'PRT'; delete from countries where code = 'T{who[0]}X'"); check(f"{who} : ajouter, modifier, retirer un pays", ok, out)
    ok, out = as_user("t1", uid, "insert into memories (country_code, content) values ('PRT', 'souvenir') returning author_id"); check(f"{who} : ajouter un souvenir, signé de son auteur", ok and out.splitlines()[0] == uid, out)
    ok, out = as_user("t1", uid, "insert into storage.objects (bucket_id, name) values ('photos', 'PRT/" + who + ".jpg'); insert into photos (country_code, path) values ('PRT', 'PRT/" + who + ".jpg') returning author_id"); check(f"{who} : ajouter une photo (stockage + table)", ok and uid in out, out)
ok, out = as_user("t1", ROX, f"delete from photos where author_id = '{MAX}' returning id"); check("Roxane peut supprimer une photo ajoutée par Maxime", ok and len(out) > 30, out)
ok, out = as_user("t1", ROX, "delete from storage.objects where name = 'PRT/Maxime.jpg' returning name"); check("Roxane peut supprimer le fichier de Maxime dans le stockage", ok and out.splitlines()[0] == "PRT/Maxime.jpg", out)

print("— Palmarès")
ok, out = as_user("t1", ROX, "insert into picks (country_code, category, photo_id) values ('PRT', 'prefere', 'aaaaaaaa-0000-0000-0000-000000000001') returning user_id"); check("Roxane fait un choix (user_id rempli automatiquement)", ok and out.splitlines()[0] == ROX, out)
ok, out = as_user("t1", ROX, f"insert into picks (user_id, country_code, category, photo_id) values ('{ROX}', 'PRT', 'prefere', 'aaaaaaaa-0000-0000-0000-000000000001') on conflict (user_id, country_code, category) do update set photo_id = excluded.photo_id returning id"); check("changer d'avis : upsert sur (personne, pays, catégorie)", ok, out)
ok, out = as_user("t1", ROX, f"insert into picks (user_id, country_code, category, photo_id) values ('{MAX}', 'PRT', 'vue', 'aaaaaaaa-0000-0000-0000-000000000001')"); check("Roxane ne peut pas choisir à la place de Maxime", not ok and "row-level security" in out, out)
ok, out = as_user("t1", MAX, f"insert into picks (country_code, category, photo_id) values ('PRT', 'prefere', 'aaaaaaaa-0000-0000-0000-000000000001'); delete from picks where user_id = '{ROX}' returning id"); check("Maxime ne peut pas effacer le choix de Roxane (0 ligne)", ok and out == "", out)
ok, out = as_user("t1", None, "insert into picks (user_id, country_code, category, photo_id) values (gen_random_uuid(), 'PRT', 'vue', 'aaaaaaaa-0000-0000-0000-000000000001')"); check("visiteur ne peut pas voter", not ok, out)
ok, out = as_user("t1", ROX, "insert into picks (country_code, category, photo_id, memory_id) values ('PRT', 'vue', 'aaaaaaaa-0000-0000-0000-000000000001', (select id from memories limit 1))"); check("un choix = une photo OU un souvenir, pas les deux", not ok and "picks_un_seul_moment" in out, out)
ok, out = as_user("t1", ROX, "insert into picks (country_code, category, photo_id) values ('PRT', 'beurk', 'aaaaaaaa-0000-0000-0000-000000000001')"); check("catégorie inconnue refusée", not ok, out)
ok, out = as_user("t1", ROX, "delete from photos where id = 'aaaaaaaa-0000-0000-0000-000000000001'"); ok2, out2 = psql("t1", "select count(*) from picks"); check("supprimer une photo récompensée efface ses choix", ok and out2 == "0", out + out2)
ok, out = as_user("t1", None, "select count(*) from members"); check("les prénoms sont lisibles par tous", ok and out.endswith("2"), out)

print("— Installation neuve (nouveau setup.sql)")
fresh("t2"); setup = open(f"{REPO}/setup.sql").read()
ok, out = psql("t2", setup); check("setup.sql sans e-mails : arrêt avec message clair", not ok and "introuvable" in out, out)
ok, out = psql("t2", "select count(*) from pg_tables where schemaname = 'public'"); check("… rien n'a été créé", out == "0", out)
ok, out = psql("t2", setup.replace("EMAIL-DE-MAXIME", "maxime@exemple.fr").replace("EMAIL-DE-ROXANE", "roxane@nos-voyages.fr")); check("setup.sql avec les deux e-mails : Success", ok, out)
ok, out = as_user("t2", ROX, "insert into countries (code, name) values ('PRT', 'Portugal'); insert into memories (country_code, content) values ('PRT', 'x')"); check("installation neuve : Roxane écrit", ok, out)
ok, out = as_user("t2", None, "insert into countries (code, name) values ('ESP', 'Espagne')"); check("installation neuve : visiteur ne peut rien écrire", not ok, out)
print(f"{ok_count[0]}/{ok_count[1]} vérifications SQL réussies")
