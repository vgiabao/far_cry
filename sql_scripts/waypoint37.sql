SELECT match_id, count(match_id) as kill_suicide_count
from match_frag
group by match_id