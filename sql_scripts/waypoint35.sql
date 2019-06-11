SELECT count(match_id) as kill_count
FROM match_frag
where victim_name is not null
