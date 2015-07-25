'''
    cloudservice XBMC Plugin
    Copyright (C) 2013-2014 ddurdle

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


'''

import os
import re
import urllib, urllib2
import cookielib


import xbmc, xbmcaddon, xbmcgui, xbmcplugin

# global variables
addon = xbmcaddon.Addon(id='plugin.video.cloudstream')

# helper methods
def log(msg, err=False):
    if err:
        xbmc.log(addon.getAddonInfo('name') + ': ' + msg, xbmc.LOGERROR)
    else:
        xbmc.log(addon.getAddonInfo('name') + ': ' + msg, xbmc.LOGDEBUG)


#
#
#
class cloudservice(object):


    # magic numbers
    MEDIA_TYPE_VIDEO = 1
    MEDIA_TYPE_FOLDER = 0
    MEDIA_TYPE_MUSIC = 2


    ##
    # initialize (setting 1) domain 2) username, 3) password, 4) authorization token, 5) user agent string
    ##
    def __init__(self, name, domain, user, password, auth, user_agent):
        self.instanceName = name
        self.domain = domain
        self.user = user
        self.password = password
        self.auth = auth
        self.user_agent = user_agent
        self.cookiejar = cookielib.CookieJar()


        # if we have an authorization token set, try to use it
        if user == '':
            return
#        elif auth != '':
#          log('using token')

#          return
        else:
          log('no token - logging in')
          self.login();
          return



    ##
    # perform login
    ##
    def login(self):

        self.auth = ''


        return



    ##
    # return the appropriate "headers" for FireDrive requests that include 1) user agent, 2) authorization cookie
    #   returns: list containing the header
    ##
    def getHeadersList(self):
        return { 'User-Agent' : self.user_agent }

    ##
    # return the appropriate "headers" for FireDrive requests that include 1) user agent, 2) authorization cookie
    #   returns: URL-encoded header string
    ##
    def getHeadersEncoded(self):
        return urllib.urlencode(self.getHeadersList())

    ##
    # retrieve a list of videos, using playback type stream
    #   parameters: prompt for video quality (optional), cache type (optional)
    #   returns: list of videos
    ##
    def getVideosList(self, folderID=0, cacheType=0):

        pass


    ##
    # retrieve a video link
    #   parameters: title of video, whether to prompt for quality/format (optional), cache type (optional)
    #   returns: list of URLs for the video or single URL of video (if not prompting for quality)
    ##
    def getPublicLink(self,url,cacheType=0):


        pass




