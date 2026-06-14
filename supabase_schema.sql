create table if not exists public.user_agents (
  record_id text primary key,
  owner_name text,
  profile jsonb not null,
  agent jsonb not null,
  created_at bigint not null
);

create table if not exists public.match_requests (
  record_id text primary key,
  user_name text,
  profile jsonb not null,
  demand text not null,
  intent jsonb,
  created_at bigint not null
);

create table if not exists public.match_results (
  record_id text primary key,
  match_request_record_id text references public.match_requests(record_id) on delete cascade,
  candidate_id text not null,
  candidate jsonb not null,
  score integer,
  outcome text not null,
  reasons jsonb,
  created_at bigint not null
);

create table if not exists public.agent_conversations (
  record_id text primary key,
  match_request_record_id text references public.match_requests(record_id) on delete cascade,
  candidate_id text not null,
  source text,
  messages jsonb not null,
  created_at bigint not null
);

create table if not exists public.collaboration_briefs (
  record_id text primary key,
  match_request_record_id text references public.match_requests(record_id) on delete cascade,
  candidate_id text not null,
  outcome text not null,
  status text,
  brief jsonb not null,
  created_at bigint not null
);

create index if not exists idx_user_agents_owner_name on public.user_agents(owner_name);
create index if not exists idx_match_requests_user_name on public.match_requests(user_name);
create index if not exists idx_match_results_match_request on public.match_results(match_request_record_id);
create index if not exists idx_agent_conversations_match_request on public.agent_conversations(match_request_record_id);
create index if not exists idx_collaboration_briefs_match_request on public.collaboration_briefs(match_request_record_id);
