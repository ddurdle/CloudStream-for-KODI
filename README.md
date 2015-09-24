CloudStream for KODI / XBMC
===========================

CloudStream for KODI / XBMC is a video plugin for streaming content from various cloud-streaming services

Supports the following video streaming domains
XFileSharing Pro
- daclips.in (login & public URL) [last checked 07/2015]
- bestreams.net (login & public URL) [removed 12/2014 - no longer supported]
- sharerepo.com (login & public URL)
- filenuke.com (login & public URL) []
- gorillavid.in (login & public URL) []
- mightyupload.com (login & public URL) []
- movpod.in (login & public URL) []
- sharesix.com (login & public URL) []
- thefile.me (login & public URL) []
- thevideo.me (public URL) [updated 07/2014]
- uptobox.com (login & public URL) [updated 08/2015]
- vidhog.com  (login & public URL) []
- vidspot.net (login & public URL) [last checked 07/2015]
- vodlocker.com [updated 07/2015]
- hcbit.com [added 09/2014]
- www.uploadc.com (login & public URL)
- streamcloud.eu (login & public URL) [added 07/2015]
- letwatch.us (login & public URL) [ added 07/2015]
- vidzi.tv (public URL) [added 07/2015]
- vidto.me (public URL) [added 07/2015]
- allmyvideos.net (login & public URL) [added 07/2015]
- realvid.net (public URL) [added 07/2015]
- uptostream.com (login & public URL) [added 08/2015]

Supports [Tested on]:
- XBMC 13/13.2
- KODI 14
* including Linux, Windows, OS X, Android, Pivos, iOS (including ATV2), Raspberry Pi, OSMC


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

