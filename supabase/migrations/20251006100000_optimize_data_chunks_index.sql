-- Optimize data_chunks ordering queries by (original_data_id, created_at desc)
create index if not exists idx_data_chunks_original_created_at
  on public.data_chunks(original_data_id, created_at desc);
