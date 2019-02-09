#! /venv/bin/python
# -*- coding: utf-8 -*-


import anosql
import psycopg2
import argparse
import sys

PGCONNSTRING = "user=dennis_adira dbname=appdev application_name=cdstore"


class Chinook(object):
    """database model and queries"""

    def __init__(self):
        self.pgconn = psycopg2.connect(PGCONNSTRING)
        self.queries = None

        for sql in [
            'sql/album.sql',
            'sql/artist.sql',
            'sql/genre-topn.sql'
        ]:
            queries = anosql.from_path(sql, 'psycopg2')
            if self.queries:
                for qname in queries.available_queries:
                    self.queries.add_query(qname, getattr(queries, qname))
            else:
                self.queries = queries

    def genre_list(self):
        return self.queries.tracks_by_genre(self.pgconn)

    def genre_top_n(self, n):
        return self.queries.genre_top_n(self.pgconn, n=n)

    def artist_by_album(self, n):
        return self.queries.top_artist_by_album(self.pgconn, n=n)

    def album_detail(self, albumid):
        return self.queries.list_tracks_by_albumid(self.pgconn, id=albumid)

    def album_by_artist(self, artist):
        return self.queries.list_albums_by_artist(self.pgconn, id=artist)


class Printer(object):
    """query results"""

    def __init__(self, columns, specs, prelude=True):
        """columns is a tuple of column titles,
        specs are tuple of python format strings"""
        self.columns = columns
        self.specs = specs
        self.fstr = " | ".join(str(i) for i in specs)

        if prelude:
            print(self.title())
            print(self.sep())

    def title(self):
        return self.fstr % self.columns

    def sep(self):
        s = ""
        for c in self.title():
            s += "+" if c == "|" else "-"
        return s

    def fmt(self, data):
        return self.fstr % data


class cdstore(object):
    """the cdstore CLI app"""

    def __init__(self, argv):
        self.db = Chinook()

        parser = argparse.ArgumentParser(
            description='cdstore utility for a chinook database',
            usage='cdstore <command> [<args>]')
        subparsers = parser.add_subparsers(help='sub-command help')

        genres = subparsers.add_parser('genres', help='list genres')
        genres.add_argument('--topn', type=int)
        genres.set_defaults(method=self.genres)

        artists = subparsers.add_parser('artists', help='list artists')
        artists.add_argument('--id', type=int, default=5)
        artists.set_defaults(method=self.artists)

        albums = subparsers.add_parser('albums', help='list albums')
        albums.add_argument('--id', type=int, default=None)
        albums.add_argument('--artist', type=int, default=None)
        albums.set_defaults(method=self.albums)

        args = parser.parse_args(argv)
        args.__setattr__('args', args)

    def genres(self, args):
        """list genres and number of tracks per game"""
        if args.topn:
            p = Printer(("Genre", "Track", "Artist"),
                        ("%20s", "%20s", "%20s"))

            for (genre, track, artist) in self.db.genre_top_n(args.topn):
                artist = artist if len(artist) < 20 else "%s..." % artist[0:18]
                print(p.fmt((genre, track, artist)))
        else:
            p = Printer(("Artist", "Albums"), ("%20s", "%s"))
            for row in self.db.genre_list():
                print(p.fmt(row))

    def artists(self, args):
        """list genres and number of tracks per genre"""
        p = Printer(("Artist", "Albums"), ("%20s", "%5s"))
        for row in self.db.artist_by_album(args.topn):
            print(p.fmt(row))

    def albums(self, args):
        # left some info
        if args.id:
            p = Printer(("Title", "Duration", "Pct"),
                        ("%25s", "%15s", "%6s"))
            for (title, ms, s, e, pct) in self.db.album_detail(args.id):
                title = title if len(title) < 25 else "%s..." % title[0:23]
                print(p.fmt(title, ms, pct))

        elif args.artist:
            p = Printer(("Album", "Duration"), ("%25s", "%s"))
            for row in self.db.album_by_artist(args.artist):
                print(p.fmt(row))


if __name__ == '__main__':
    cdstore(sys.argv[1:])
