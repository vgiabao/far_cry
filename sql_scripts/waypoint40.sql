select killer_name, count(killer_name) as kill_count
from match_frag
group by killer_name
order by kill_count desc

