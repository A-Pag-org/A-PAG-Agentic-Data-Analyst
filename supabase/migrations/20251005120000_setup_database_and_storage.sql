-- Supabase setup: extensions, schema, RLS, and storage buckets
-- Note: Requires the 'vector' and 'pgcrypto' extensions

-- 1) Extensions
create extension if not exists vector with schema extensions;
create extension if not exists pgcrypto with schema extensions;

-- 2) Tables
create table if not exists public.original_data (
  id uuid primary key default gen_random_uuid(),
  filename text not null,
  file_size integer,
  upload_date timestamptz default now(),
  user_id uuid references auth.users(id) on delete cascade,
  metadata jsonb,
  created_at timestamptz default now()
);

create table if not exists public.data_chunks (
  id uuid primary key default gen_random_uuid(),
  original_data_id uuid references public.original_data(id) on delete cascade,
  chunk_index integer,
  content text,
  metadata jsonb,
  embedding vector(3072), -- OpenAI text-embedding-3-large
  created_at timestamptz default now()
);

create table if not exists public.analysis_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  query text,
  response jsonb,
  artifacts jsonb,
  created_at timestamptz default now()
);

-- 3) Indexes
create index if not exists idx_original_data_user_id on public.original_data(user_id);
create index if not exists idx_original_data_created_at on public.original_data(created_at desc);

create index if not exists idx_data_chunks_original_data_id on public.data_chunks(original_data_id);
create unique index if not exists uq_data_chunks_original_chunk on public.data_chunks(original_data_id, chunk_index);
-- Vector similarity index (cosine distance)
create index if not exists idx_data_chunks_embedding_ivfflat
  on public.data_chunks using ivfflat (embedding vector_cosine_ops) with (lists = 100);

create index if not exists idx_analysis_sessions_user_id on public.analysis_sessions(user_id);
create index if not exists idx_analysis_sessions_created_at on public.analysis_sessions(created_at desc);

-- 4) Row Level Security (RLS)
alter table public.original_data enable row level security;
alter table public.data_chunks enable row level security;
alter table public.analysis_sessions enable row level security;

-- original_data policies
-- Allow owners to select their own rows
create policy original_data_select_own
  on public.original_data for select
  to authenticated
  using (user_id = auth.uid());

-- Allow owners to insert their own rows
create policy original_data_insert_own
  on public.original_data for insert
  to authenticated
  with check (user_id = auth.uid());

-- Allow owners to update their own rows
create policy original_data_update_own
  on public.original_data for update
  to authenticated
  using (user_id = auth.uid())
  with check (user_id = auth.uid());

-- Allow owners to delete their own rows
create policy original_data_delete_own
  on public.original_data for delete
  to authenticated
  using (user_id = auth.uid());

-- data_chunks policies (scoped via parent original_data)
create policy data_chunks_select_via_parent
  on public.data_chunks for select
  to authenticated
  using (exists (
    select 1 from public.original_data od
    where od.id = original_data_id and od.user_id = auth.uid()
  ));

create policy data_chunks_insert_via_parent
  on public.data_chunks for insert
  to authenticated
  with check (exists (
    select 1 from public.original_data od
    where od.id = original_data_id and od.user_id = auth.uid()
  ));

create policy data_chunks_update_via_parent
  on public.data_chunks for update
  to authenticated
  using (exists (
    select 1 from public.original_data od
    where od.id = original_data_id and od.user_id = auth.uid()
  ))
  with check (exists (
    select 1 from public.original_data od
    where od.id = original_data_id and od.user_id = auth.uid()
  ));

create policy data_chunks_delete_via_parent
  on public.data_chunks for delete
  to authenticated
  using (exists (
    select 1 from public.original_data od
    where od.id = original_data_id and od.user_id = auth.uid()
  ));

-- analysis_sessions policies
create policy analysis_sessions_select_own
  on public.analysis_sessions for select
  to authenticated
  using (user_id = auth.uid());

create policy analysis_sessions_insert_own
  on public.analysis_sessions for insert
  to authenticated
  with check (user_id = auth.uid());

create policy analysis_sessions_update_own
  on public.analysis_sessions for update
  to authenticated
  using (user_id = auth.uid())
  with check (user_id = auth.uid());

create policy analysis_sessions_delete_own
  on public.analysis_sessions for delete
  to authenticated
  using (user_id = auth.uid());

-- 5) Storage buckets and policies
-- Create buckets (private by default)
insert into storage.buckets (id, name, public)
values
  ('original-files', 'original-files', false),
  ('chroma-collections', 'chroma-collections', false),
  ('exports', 'exports', false)
on conflict (id) do nothing;

-- Ensure RLS is enabled on storage.objects (usually enabled by default)
alter table storage.objects enable row level security;

-- Policies for each bucket: owner-only access for authenticated users
-- original-files
create policy original_files_read_own
  on storage.objects for select
  to authenticated
  using (bucket_id = 'original-files' and owner = auth.uid());

create policy original_files_insert_own
  on storage.objects for insert
  to authenticated
  with check (bucket_id = 'original-files' and owner = auth.uid());

create policy original_files_update_own
  on storage.objects for update
  to authenticated
  using (bucket_id = 'original-files' and owner = auth.uid())
  with check (bucket_id = 'original-files' and owner = auth.uid());

create policy original_files_delete_own
  on storage.objects for delete
  to authenticated
  using (bucket_id = 'original-files' and owner = auth.uid());

-- chroma-collections
create policy chroma_collections_read_own
  on storage.objects for select
  to authenticated
  using (bucket_id = 'chroma-collections' and owner = auth.uid());

create policy chroma_collections_insert_own
  on storage.objects for insert
  to authenticated
  with check (bucket_id = 'chroma-collections' and owner = auth.uid());

create policy chroma_collections_update_own
  on storage.objects for update
  to authenticated
  using (bucket_id = 'chroma-collections' and owner = auth.uid())
  with check (bucket_id = 'chroma-collections' and owner = auth.uid());

create policy chroma_collections_delete_own
  on storage.objects for delete
  to authenticated
  using (bucket_id = 'chroma-collections' and owner = auth.uid());

-- exports
create policy exports_read_own
  on storage.objects for select
  to authenticated
  using (bucket_id = 'exports' and owner = auth.uid());

create policy exports_insert_own
  on storage.objects for insert
  to authenticated
  with check (bucket_id = 'exports' and owner = auth.uid());

create policy exports_update_own
  on storage.objects for update
  to authenticated
  using (bucket_id = 'exports' and owner = auth.uid())
  with check (bucket_id = 'exports' and owner = auth.uid());

create policy exports_delete_own
  on storage.objects for delete
  to authenticated
  using (bucket_id = 'exports' and owner = auth.uid());
