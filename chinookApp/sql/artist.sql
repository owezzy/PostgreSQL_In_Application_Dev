-- name: top-artists-by-album
-- Get the List of the N artists with the most albums

select artists.name, count(*) as albums
from artists
       left join albums using (artistid)
group by artists.name
order by albums desc
         limit :n;
