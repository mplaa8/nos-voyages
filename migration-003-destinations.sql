-- =========================================================
-- Carte de nos voyages — migration 003 : nos envies de voyage (destinations en commun)
-- À coller dans Supabase > SQL Editor > New query, puis Run. Rien à remplacer.
--
-- Purement additive : une nouvelle table « wishes », aucune table ni règle existante modifiée.
-- Rejouable : on peut la relancer sans risque.
-- Prérequis : migration-002-palmares.sql (les deux membres et la fonction is_member()).
-- =========================================================
begin;

do $$
begin
  if to_regprocedure('public.is_member()') is null then
    raise exception 'Lance d''abord migration-002-palmares.sql (les deux membres), puis relance celle-ci. Rien n''a été modifié.';
  end if;
end $$;

-- Une réponse par personne et par pays : « oui » (j'ai envie) ou « non » (bof). Changer d'avis = remplacer.
-- Pas de clé étrangère vers countries : on répond aussi pour des pays pas encore sur notre carte.
create table if not exists public.wishes (
  user_id       uuid not null default auth.uid() references auth.users(id) on delete cascade,
  country_code  text not null,
  answer        text not null check (answer in ('oui','non')),
  created_at    timestamptz default now(),
  primary key (user_id, country_code)
);
alter table public.wishes enable row level security;
drop policy if exists "lecture wishes" on public.wishes;
drop policy if exists "mes wishes"     on public.wishes;
-- Lecture publique (comme le palmarès) : le secret est géré par l'app, qui ne montre que les « oui » communs
create policy "lecture wishes" on public.wishes for select using (true);
create policy "mes wishes"     on public.wishes for all to authenticated
  using (user_id = auth.uid() and public.is_member()) with check (user_id = auth.uid() and public.is_member());

-- Temps réel : l'app est prévenue quand l'autre répond
do $$
begin
  if not exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = 'wishes') then
    alter publication supabase_realtime add table public.wishes;
  end if;
end $$;

commit;
