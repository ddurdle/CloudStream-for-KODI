XBMC-CloudStream
================

XBMC video plugin for streaming content from various cloud-streaming services

Supports the following video streaming domains
XFileSharing Pro
- daclips.in (my account videos & public URL)
- gorillavid.in (my account videos & public URL)
- movpod.in (my account videos & public URL)
- thefile.me (my account videos & public URL)
- bestreams.net (my account videos & public URL)

Supports [Tested on]:
All XBMC 12, 12.2, 13 including Linux, Windows, OS X, Android, Pivos, iOS (including ATV2), Raspberry Pi

Thoroughly tested on XBMC for Linux v13 & Raspberry Pi Raspbmc v12


Getting Started:
1) download the .zip file
2) transfer the .zip file to XBMC
3) in Video Add-on, select Install from .zip

Before starting the add-on for the first time, either "Configure" or right click and select "Add-on Settings".  Enter your Username and Password.

Features and limitations:
- will index videos on various video streaming accounts, sorted by title name
- includes support for folders

Modes:
1) standard index (folderID=0)
- starting the plugin via video add-ons will display a directory containing all video files and folders contained in the root folder of your SockShare account
- click on a video file to playback
- you can create favourites of the video files or folders
2) mode=streamURL
- playback a specific video stream video URL (format: http://domain.com/#####) via stream
- handy for playback of publicly shared videos stored in SockShare
- create .strm or .m3u files containing the following: plugin://plugin.video.cloudstream/?mode=streamURL&amp;url=http://domain.com/#####
- if your video is composed of multiple clips, you can create a .m3u that makes the above plugin:// call, one line for each clip.  You can then create a .strm file that points to the .m3u.  XBMC can index movies and shows contained in your Google Drive account by either a .strm containing a single plugin:// call to the video, or a .strm that points to a local .m3u file that contains a list of plugin:// calls representing the video


Roadmap to future releases:
- support for more services

