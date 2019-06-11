select match.match_id, match.start_time, match.end_time,
       count(distinct killer_name) as player_count,
       count(killer_name) as kill_suicide_count
from match
 join match_frag on match.match_id = match_frag.match_id
group by match.match_id
order by start_time