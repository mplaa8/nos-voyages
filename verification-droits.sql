-- =========================================================
-- Carte de nos voyages — vérifier les droits (à lancer APRÈS migration-002-palmares.sql)
-- Supabase > SQL Editor > New query : coller tout, Run.
-- Le résultat est un petit tableau : chaque ligne doit commencer par ✅.
-- (Une ligne ⚠️ « table absente » signifie seulement qu'une migration n'a pas encore été lancée.)
-- Rien n'est modifié : chaque essai d'écriture est annulé aussitôt.
-- =========================================================
create temp table verif (n int, etape text, resultat text);
grant all on verif to public;

-- 1. Un visiteur (toute personne ayant le lien) ne peut RIEN écrire
set role anon;
do $$ declare accepte boolean := false; begin
  begin
    insert into public.countries (code, name) values ('ZZT', 'Test'); accepte := true;
    raise exception using errcode = 'ZZ001';                 -- annule l'essai
  exception when sqlstate 'ZZ001' or insufficient_privilege then null;
  end;
  insert into verif values (1, 'Visiteur : ajouter un pays', case when accepte then '❌ PROBLÈME : écriture acceptée' else '✅ refusé' end);
end $$;
do $$ declare accepte boolean := false; begin
  begin
    insert into storage.objects (bucket_id, name) values ('photos', 'verif/test.jpg'); accepte := true;
    raise exception using errcode = 'ZZ001';
  exception when sqlstate 'ZZ001' or insufficient_privilege then null;
  end;
  insert into verif values (2, 'Visiteur : envoyer une photo', case when accepte then '❌ PROBLÈME : envoi accepté' else '✅ refusé' end);
end $$;
do $$ declare accepte boolean := false; absente boolean := false; begin
  begin
    insert into public.wishes (user_id, country_code, answer) values (gen_random_uuid(), 'ZZT', 'oui'); accepte := true;
    raise exception using errcode = 'ZZ001';
  exception when sqlstate 'ZZ001' or insufficient_privilege then null; when undefined_table then absente := true;
  end;
  insert into verif values (3, 'Visiteur : répondre au jeu des envies', case when absente then '⚠️ table absente : lancer migration-003-destinations.sql' when accepte then '❌ PROBLÈME : réponse acceptée' else '✅ refusé' end);
end $$;
reset role;

-- 2. Maxime puis Roxane peuvent écrire (pays, souvenir, palmarès), avec les mêmes droits
set role authenticated;
select set_config('request.jwt.claims', json_build_object('sub', (select user_id from public.members where prenom = 'Maxime'), 'role', 'authenticated')::text, false);
do $$ declare erreur text := 'compte de Maxime absent de members'; begin
  begin
    if exists (select 1 from public.members where prenom = 'Maxime') then
      insert into public.countries (code, name) values ('ZZT', 'Test');
      insert into public.memories (country_code, content) values ('ZZT', 'test');
      insert into public.picks (country_code, category, memory_id) select 'ZZT', 'drole', id from public.memories where country_code = 'ZZT';
      erreur := null;
    end if;
    raise exception using errcode = 'ZZ001';
  exception when sqlstate 'ZZ001' then null; when others then erreur := sqlerrm;
  end;
  insert into verif values (4, 'Maxime : pays, souvenir, palmarès', coalesce('❌ PROBLÈME : ' || erreur, '✅ autorisé'));
end $$;
select set_config('request.jwt.claims', json_build_object('sub', (select user_id from public.members where prenom = 'Roxane'), 'role', 'authenticated')::text, false);
do $$ declare erreur text := 'compte de Roxane absent de members'; begin
  begin
    if exists (select 1 from public.members where prenom = 'Roxane') then
      insert into public.countries (code, name) values ('ZZT', 'Test');
      insert into public.memories (country_code, content) values ('ZZT', 'test');
      insert into public.picks (country_code, category, memory_id) select 'ZZT', 'drole', id from public.memories where country_code = 'ZZT';
      erreur := null;
    end if;
    raise exception using errcode = 'ZZ001';
  exception when sqlstate 'ZZ001' then null; when others then erreur := sqlerrm;
  end;
  insert into verif values (5, 'Roxane : pays, souvenir, palmarès', coalesce('❌ PROBLÈME : ' || erreur, '✅ autorisé'));
end $$;
-- 3. Le jeu des envies : chacun peut répondre (table de la migration 003)
do $$ declare erreur text := null; absente boolean := false; qui text; begin
  foreach qui in array array['Maxime', 'Roxane'] loop
    begin
      perform set_config('request.jwt.claims', json_build_object('sub', (select user_id from public.members where prenom = qui), 'role', 'authenticated')::text, false);
      insert into public.wishes (country_code, answer) values ('ZZT', 'oui');
      raise exception using errcode = 'ZZ001';
    exception when sqlstate 'ZZ001' then null; when undefined_table then absente := true; when others then erreur := coalesce(erreur, qui || ' : ' || sqlerrm);
    end;
  end loop;
  insert into verif values (6, 'Maxime et Roxane : jeu des envies', case when absente then '⚠️ table absente : lancer migration-003-destinations.sql' else coalesce('❌ PROBLÈME : ' || erreur, '✅ autorisé') end);
end $$;
reset role;
select set_config('request.jwt.claims', '', false);

select etape as "Vérification", resultat as "Résultat" from verif order by n;
