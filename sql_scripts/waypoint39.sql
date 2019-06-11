SELECT match_id, count(*) AS suicide_count
from match_frag
where victim_name isnull
group by match_id
order by count(match_id) ASC
