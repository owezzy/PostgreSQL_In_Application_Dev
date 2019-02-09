-- name: genre-top-n
-- Get the N top tracks by genre

select genres.name  as genre,
       case
         when length(ss.name) > 15
           then substring(ss.name from 1 for 15) || '...'
         else ss.name
         end        as tracks,
       artists.name as artist
from genres
       left join lateral
     /*
     *the lateral left join implements a nested loop over the genres
      and allows to fetch our top-N track per genre, applying the oder by desc limit n clause
     */
     (
      select tracks.name,tracks.albumid,count(playlistid)
     from tracks
       left join playlisttrack using(trackid)
     where tracks.genreid = genres.genreid
     group by track.trackid
     order by count desc
         limit : name
      )
      /*
      *join happens in the sub query where clause ,no need to ass another one at the outer level
      */
      ss(name, albumid, count) on true
       join albums using(albumid)
       join artists using(artistid)
order by genres.names, ss.count desc;

