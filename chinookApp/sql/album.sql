-- name: top-artists-by-artist
-- List the album titles  and duration of a  given artist

select albums.title as albums,
       sum(milliseconds) *
       interval
       '1ms' as
       duration
from albums
     join
     artists
     using(
     artistid)
     left
     join
     tracks
     using(
     albumid)
where artists.name = : name
group by albums
order by albums;
