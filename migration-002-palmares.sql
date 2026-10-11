-- =========================================================
-- Carte de nos voyages — migration 002 : nos deux téléphones + palmarès
-- À coller dans Supabase > SQL Editor > New query, puis Run.
--
-- AVANT de lancer :
--   1. Authentication > Users > Add user : le compte de Roxane (adresse fictive,
--      celle de CONFIG.ROXANE_EMAIL dans index.html), mot de passe = le code secret,
--      « Auto Confirm User » coché.
--   2. Ci-dessous, remplace EMAIL-DE-MAXIME et EMAIL-DE-ROXANE par les adresses
--      exactes de la liste Authentication > Users (garde les apostrophes).
--
-- Rejouable : on peut la relancer sans risque. Tout se fait d'un bloc : si un des
-- deux comptes est introuvable, le script s'arrête avec un message et NE CHANGE RIEN
-- (sinon Maxime perdrait l'accès à l'édition).
-- =========================================================
begin;

-- 1. Les deux membres (lecture publique pour afficher les prénoms, aucune écriture depuis l'app)
create table if not exists public.members (
  user_id  uuid primary key references auth.users(id) on delete cascade,
  prenom   text not null
);
alter table public.members enable row level security;
drop policy if exists "lecture members" on public.members;
create policy "lecture members" on public.members for select using (true);

-- 2. Inscription des deux membres par e-mail, puis vérification
insert into public.members select id, 'Maxime' from auth.users where email = 'EMAIL-DE-MAXIME' on conflict do nothing;
insert into public.members select id, 'Roxane' from auth.users where email = 'EMAIL-DE-ROXANE' on conflict do nothing;
do $$
begin
  if not exists (select 1 from public.members where prenom = 'Maxime') then
    raise exception 'Compte de Maxime introuvable : remplace EMAIL-DE-MAXIME par ton adresse exacte (Authentication > Users), puis relance. Rien n''a été modifié.';
  end if;
  if not exists (select 1 from public.members where prenom = 'Roxane') then
    raise exception 'Compte de Roxane introuvable : crée-le (Authentication > Users > Add user) et remplace EMAIL-DE-ROXANE par son adresse, puis relance. Rien n''a été modifié.';
  end if;
end $$;

-- 3. Auteur des contenus (pour la signature « — Roxane », pas pour les droits)
alter table public.memories add column if not exists author_id uuid default auth.uid() references auth.users(id) on delete set null;
alter table public.photos   add column if not exists author_id uuid default auth.uid() references auth.users(id) on delete set null;

create or replace function public.is_member() returns boolean
language sql stable security definer set search_path = public
as $$ select exists (select 1 from public.members where user_id = auth.uid()) $$;

-- Écriture réservée aux deux membres (mêmes droits) ; la lecture publique ne change pas
drop policy if exists "admin countries"   on public.countries;
drop policy if exists "membres countries" on public.countries;
create policy "membres countries" on public.countries for all to authenticated using (public.is_member()) with check (public.is_member());
drop policy if exists "admin memories"    on public.memories;
drop policy if exists "membres memories"  on public.memories;
create policy "membres memories"  on public.memories  for all to authenticated using (public.is_member()) with check (public.is_member());
drop policy if exists "admin photos"      on public.photos;
drop policy if exists "membres photos"    on public.photos;
create policy "membres photos"    on public.photos    for all to authenticated using (public.is_member()) with check (public.is_member());

drop policy if exists "photos ajout" on storage.objects;
drop policy if exists "photos suppr" on storage.objects;
create policy "photos ajout" on storage.objects for insert to authenticated with check (bucket_id = 'photos' and public.is_member());
create policy "photos suppr" on storage.objects for delete to authenticated using (bucket_id = 'photos' and public.is_member());

-- 4. Le palmarès : un choix par personne, par pays, par catégorie
create table if not exists public.picks (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null default auth.uid() references auth.users(id) on delete cascade,
  country_code  text not null references public.countries(code) on delete cascade,
  category      text not null check (category in ('vue','assiette','drole','prefere')),
  photo_id      uuid references public.photos(id) on delete cascade,
  memory_id     uuid references public.memories(id) on delete cascade,
  created_at    timestamptz default now(),
  constraint picks_un_seul_moment check ((photo_id is null) <> (memory_id is null)),
  constraint picks_un_par_categorie unique (user_id, country_code, category)
);
alter table public.picks enable row level security;
drop policy if exists "lecture picks" on public.picks;
drop policy if exists "mes picks"     on public.picks;
create policy "lecture picks" on public.picks for select using (true);
create policy "mes picks"     on public.picks for all to authenticated
  using (user_id = auth.uid() and public.is_member()) with check (user_id = auth.uid() and public.is_member());

-- 5. Temps réel : l'app est prévenue quand l'autre fait un choix
do $$
begin
  if not exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = 'picks') then
    alter publication supabase_realtime add table public.picks;
  end if;
end $$;

commit;
