#!/bin/python
#
# Downloads (flv) and converts all videos (mp4) from a youtube playlist ID.

from download_flv_convert_mp3 import *
import gdata.youtube
import gdata.youtube.service
from optparse import OptionParser
import re
import os
import sys
import subprocess

testing = False

usage = 'usage: python %s [options]' % sys.argv[0]
parser = OptionParser(usage=usage)
parser.add_option('-p', '--playlist-id', dest='playlist_id', help='Youtube playlist ID')
parser.add_option('-s', '--source-dir', dest='source_dir', help='Location to store FLV files downloaded from Youtube', default='./source')
parser.add_option('-o', '--output-dir', dest='output_dir', help='Location to store converted MP4 files', default='./output')
parser.add_option('-c', '--concurrent-downloads', dest='concurrent_downloads', help='Maximum simultaneous downloads from Youtube', default=1)
parser.add_option('-b', '--bitrate', dest='bitrate', help='Bitrate setting when converting FLV to MP4', default=300)
parser.add_option('--min', type='float', help='Bitrate setting when converting FLV to MP4')
parser.add_option('--max', type='float', help='Bitrate setting when converting FLV to MP4')
parser.add_option('--user')
parser.add_option('--series')
parser.add_option('--part-match')

yt_service = gdata.youtube.service.YouTubeService()
yt_service.ssl = False

def MakeUploadURI(username, start_index=1, max_results=50):
    return "http://gdata.youtube.com/feeds/api/users/%s/uploads?start-index=%d&max_results=%d" % (username, start_index, max_results)

def PrintFeed(feed, match_title, match_episode):
    for entry in feed.entry:
        title = entry.media.title.text
        if re.search(match_title, title, re.IGNORECASE):
        #if title.find(match_title) != -1:
            #if match_episode and title.find(match_episode) == -1:
            if match_episode and not re.search(match_episode, title, re.IGNORECASE):
                continue

            title = title.replace('/', '_')
            url = entry.media.player.url
            flvUrl = GetFLVURL(url)
            filename = os.path.join(options.source_dir, title + '.flv')
            output_filename = os.path.join(options.output_dir, title + '.mp4')
        
            """
            print title
            print url
            print
            """
            Download(flvUrl, filename)
            ConvertVideo(filename, output_filename)

    return len(feed.entry)

def PrintUploadsByUser(username, match_title, match_episode):
    start_index = 1
    max_results_per_request = 25
    max_results = 7500

    while True:
        uri = MakeUploadURI(username, start_index, max_results_per_request)
        feed = yt_service.GetYouTubeVideoFeed(uri)
        if not feed:
            break

        feed_entries = PrintFeed(feed, match_title, match_episode)
        if feed_entries == 0:
            break

        start_index += feed_entries
        if start_index > max_results:
            break

def SearchAndPrint(search_terms):
    query = gdata.youtube.service.YouTubeVideoQuery()
    query.vq = search_terms
    query.orderby = 'published'
    query.racy = 'include'
    feed = yt_service.YouTubeQuery(query)
    PrintFeed(feed)

#PrintUploadsByUser("maraoung", "chlorng phub")
#PrintUploadsByUser('samiamkhmai', 'snaeha neak jomreang')
#SearchAndPrint("chlorng phub")

playlistList = []

def Download(source, dest):
    if not os.path.exists(dest):
        cmd = 'curl -L -o "%s" "%s"' % (dest, source)
        print cmd
        if not testing:
            exit_code = os.system(cmd)
            print 'exit_code', exit_code

def ConvertVideo(source, dest):
    if not os.path.exists(dest):
        convert_cmd = 'ffmpeg -i "%s" -b %dkb/s "%s"' % (source, options.bitrate, dest)
        print convert_cmd
        if not testing:
            exit_code = os.system(convert_cmd)
            print 'exit_code', exit_code

def QueryPlaylist(playlistID, max_results, start_index):
    playlist_uri = 'http://gdata.youtube.com/feeds/api/playlists/%s?max-results=%d&start-index=%d' % (playlistID, max_results, start_index)
    playlist_video_feed = yt_service.GetYouTubePlaylistVideoFeed(uri=playlist_uri)

    # iterate through the feed as you would with any other
    for entry in playlist_video_feed.entry:
        playlistList.append(entry)

        title = entry.title.text
        url = entry.media.player.url
        flvUrl = GetFLVURL(url)

        # Extract episode number
        match = re.search('([0-9.]+)', title)
        if not match or len(match.groups()) == 0:
            print "Unable to parse part from %s" % title
            continue

        part = float(match.groups()[0])

        # Skip processing this episode if not in specified range
        if options.min != None:
            if part < options.min:
                continue
        if options.max != None:
            if part > options.max:
                continue

        filename = os.path.join(options.source_dir, title + '.flv')
        output_filename = os.path.join(options.output_dir, title + '.mp4')
       
        if not os.path.exists(filename):
            cmd = 'curl -L -o "%s" "%s"' % (filename, flvUrl)
            print cmd
            if not testing:
                exit_code = os.system(cmd)
                print 'exit_code', exit_code

        if not os.path.exists(output_filename):
            convert_cmd = 'ffmpeg -i "%s" -b %dkb/s "%s"' % (filename, options.bitrate, output_filename)
            print convert_cmd
            if not testing:
                exit_code = os.system(convert_cmd)
                print 'exit_code', exit_code

    if len(playlist_video_feed.entry) == 0:
        return

    QueryPlaylist(playlistID, max_results, start_index + max_results)

def PrintPlaylist():
    for entry in playlistList:
        print '%s @@@ %s' % (entry.title.text, entry.media.player.url)

def ValidArgs():
    if not os.path.exists(options.source_dir):
        print "source_dir does not exist: %s" % options.source_dir
        return False

    if not os.path.exists(options.output_dir):
        print "output_dir does not exist: %s" % options.output_dir
        return False

    return True

if __name__ == '__main__':
    (options, args) = parser.parse_args()

    if not ValidArgs():
        sys.exit(-1)

    if options.playlist_id:
        playlistID = args[0]
        QueryPlaylist(playlistID, 50, 1)

    if options.user and options.series:
        #PrintUploadsByUser('Mzchandany978', 'Snaeh oun lurs ge')
        PrintUploadsByUser(options.user, options.series, options.part_match)
