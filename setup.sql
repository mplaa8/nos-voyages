-- =========================================================
-- Carte de nos voyages — à coller dans Supabase > SQL Editor > Run
-- =========================================================
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
  created_at    timestamptz default now()
);
create table if not exists public.photos (
  id            uuid primary key default gen_random_uuid(),
  country_code  text not null references public.countries(code) on delete cascade,
  path          text not null,
  created_at    timestamptz default now()
);

-- Sécurité : tout le monde peut LIRE, seul l'admin connecté peut MODIFIER
alter table public.countries enable row level security;
alter table public.memories  enable row level security;
alter table public.photos    enable row level security;
create policy "lecture countries" on public.countries for select using (true);
create policy "admin countries"   on public.countries for all to authenticated using (true) with check (true);
create policy "lecture memories"  on public.memories  for select using (true);
create policy "admin memories"    on public.memories  for all to authenticated using (true) with check (true);
create policy "lecture photos"    on public.photos    for select using (true);
create policy "admin photos"      on public.photos    for all to authenticated using (true) with check (true);

-- Espace de stockage des photos
insert into storage.buckets (id, name, public) values ('photos', 'photos', true) on conflict (id) do nothing;
create policy "photos lecture" on storage.objects for select using (bucket_id = 'photos');
create policy "photos ajout"   on storage.objects for insert to authenticated with check (bucket_id = 'photos');
create policy "photos suppr"   on storage.objects for delete to authenticated using (bucket_id = 'photos');
