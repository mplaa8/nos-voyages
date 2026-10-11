-- =========================================================
-- Carte de nos voyages — installation neuve, à coller dans Supabase > SQL Editor > Run
-- (modèle complet : pays, souvenirs, photos, deux membres, palmarès)
--
-- AVANT de lancer : créer les deux comptes dans Authentication > Users > Add user
-- (« Auto Confirm User » coché) : celui de Maxime, et celui de Roxane avec l'adresse
-- fictive de CONFIG.ROXANE_EMAIL et le code secret comme mot de passe.
-- Puis remplacer EMAIL-DE-MAXIME et EMAIL-DE-ROXANE tout en bas.
-- Une base déjà installée avant octobre 2026 se met à jour avec migration-002-palmares.sql.
-- =========================================================
begin;

create table if not exists public.countries (
  code        text primary key,               -- code pays (ex : FRA, ITA, JPN)
  name        text not null,
  status      text not null default 'visited' check (status in ('visited','dream')),
  places      text default '',
  updated_at  timestamptz default now()
);
create table if not exists public.memories (
  id            uuid primary key default gen_random_uuid(),
  country_code  text not null references public.countries(code) on delete cascade,
  content       text not null,
  author_id     uuid default auth.uid() references auth.users(id) on delete set null,
  created_at    timestamptz default now()
);
create table if not exists public.photos (
  id            uuid primary key default gen_random_uuid(),
  country_code  text not null references public.countries(code) on delete cascade,
  path          text not null,
  author_id     uuid default auth.uid() references auth.users(id) on delete set null,
  created_at    timestamptz default now()
);
create table if not exists public.members (
  user_id  uuid primary key references auth.users(id) on delete cascade,
  prenom   text not null
);
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

create or replace function public.is_member() returns boolean
language sql stable security definer set search_path = public
as $$ select exists (select 1 from public.members where user_id = auth.uid()) $$;

-- Sécurité : tout le monde peut LIRE ; seuls les deux membres (mêmes droits) peuvent MODIFIER
alter table public.countries enable row level security;
alter table public.memories  enable row level security;
alter table public.photos    enable row level security;
alter table public.members   enable row level security;
alter table public.picks     enable row level security;
drop policy if exists "lecture countries" on public.countries;
drop policy if exists "membres countries" on public.countries;
drop policy if exists "lecture memories"  on public.memories;
drop policy if exists "membres memories"  on public.memories;
drop policy if exists "lecture photos"    on public.photos;
drop policy if exists "membres photos"    on public.photos;
drop policy if exists "lecture members"   on public.members;
drop policy if exists "lecture picks"     on public.picks;
drop policy if exists "mes picks"         on public.picks;
create policy "lecture countries" on public.countries for select using (true);
create policy "membres countries" on public.countries for all to authenticated using (public.is_member()) with check (public.is_member());
create policy "lecture memories"  on public.memories  for select using (true);
create policy "membres memories"  on public.memories  for all to authenticated using (public.is_member()) with check (public.is_member());
create policy "lecture photos"    on public.photos    for select using (true);
create policy "membres photos"    on public.photos    for all to authenticated using (public.is_member()) with check (public.is_member());
create policy "lecture members"   on public.members   for select using (true);
create policy "lecture picks"     on public.picks     for select using (true);
create policy "mes picks"         on public.picks     for all to authenticated
  using (user_id = auth.uid() and public.is_member()) with check (user_id = auth.uid() and public.is_member());

-- Espace de stockage des photos
insert into storage.buckets (id, name, public) values ('photos', 'photos', true) on conflict (id) do nothing;
drop policy if exists "photos lecture" on storage.objects;
drop policy if exists "photos ajout"   on storage.objects;
drop policy if exists "photos suppr"   on storage.objects;
create policy "photos lecture" on storage.objects for select using (bucket_id = 'photos');
create policy "photos ajout"   on storage.objects for insert to authenticated with check (bucket_id = 'photos' and public.is_member());
create policy "photos suppr"   on storage.objects for delete to authenticated using (bucket_id = 'photos' and public.is_member());

-- Temps réel pour le palmarès
do $$
begin
  if not exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and schemaname = 'public' and tablename = 'picks') then
    alter publication supabase_realtime add table public.picks;
  end if;
end $$;

-- Les deux membres (remplacer les adresses)
insert into public.members select id, 'Maxime' from auth.users where email = 'EMAIL-DE-MAXIME' on conflict do nothing;
insert into public.members select id, 'Roxane' from auth.users where email = 'EMAIL-DE-ROXANE' on conflict do nothing;
do $$
begin
  if not exists (select 1 from public.members where prenom = 'Maxime') or not exists (select 1 from public.members where prenom = 'Roxane') then
    raise exception 'Un des deux comptes est introuvable : vérifie EMAIL-DE-MAXIME et EMAIL-DE-ROXANE (Authentication > Users), puis relance. Rien n''a été modifié.';
  end if;
end $$;

commit;
