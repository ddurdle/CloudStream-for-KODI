'''
    xfilesharing XBMC Plugin
    Copyright (C) 2013 dmdsoftware

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

import cloudservice
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
class xfilesharing(cloudservice.cloudservice):


    # magic numbers
    MEDIA_TYPE_VIDEO = 1
    MEDIA_TYPE_FOLDER = 0

    ##
    # initialize (setting 1) username, 2) password, 3) authorization token, 4) user agent string
    ##
    def __init__(self, name, domain, user, password, auth, user_agent):
        return super(xfilesharing,self).__init__(name, domain, user, password, auth, user_agent)
        #return cloudservice.__init__(self,domain, user, password, auth, user_agent)



    ##
    # perform login
    ##
    def login(self):

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        # default User-Agent ('Python-urllib/2.6') will *not* work
        opener.addheaders = [('User-Agent', self.user_agent)]

        url = 'http://'+self.domain+'/'

        values = {
                  'op' : 'login',
                  'redirect' : '',
                  'login' : self.user,
                  'redirect' : 'http://' + self.domain + '/',
                  'password' : self.password
        }

        log('logging in')

        # try login
        try:
            response = opener.open(url,urllib.urlencode(values))

        except urllib2.URLError, e:
            if e.code == 403:
                #login denied
                xbmcgui.Dialog().ok(ADDON.getLocalizedString(30000), ADDON.getLocalizedString(30017))
            log(str(e), True)
            return
        response_data = response.read()
        response.close()


        loginResult = False
        #validate successful login
        for r in re.finditer('my_account',
                             response_data, re.DOTALL):
            loginResult = True

        if (loginResult == False):
            xbmcgui.Dialog().ok(ADDON.getLocalizedString(30000), ADDON.getLocalizedString(30017))
            log('login failed', True)
            return

        for cookie in self.cookiejar:
            for r in re.finditer(' ([^\=]+)\=([^\s]+)\s',
                        str(cookie), re.DOTALL):
                cookieType,cookieValue = r.groups()
                if cookieType == 'xfss':
                    self.auth = cookieValue


        return



    ##
    # return the appropriate "headers" for FireDrive requests that include 1) user agent, 2) authorization cookie
    #   returns: list containing the header
    ##
    def getHeadersList(self):
        if (self.auth != '' or self.auth != 0):
            return { 'User-Agent' : self.user_agent, 'Cookie' : 'lang=english; login='+self.user+'; xfss='+self.auth+';' }
        else:
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

        # retrieve all documents
        if folderID == 0:
            url = 'http://'+self.domain+'/?op=my_files'
        else:
            url = 'http://'+self.domain+'/?op=my_files&fld_id='+folderID


        videos = {}
        if True:
            log('url = %s header = %s' % (url, self.getHeadersList()))
            req = urllib2.Request(url, None, self.getHeadersList())

            # if action fails, validate login
            try:
              response = urllib2.urlopen(req)
            except urllib2.URLError, e:
              if e.code == 403 or e.code == 401:
                self.login()
                req = urllib2.Request(url, None, self.getHeadersList())
                try:
                  response = urllib2.urlopen(req)
                except urllib2.URLError, e:
                  log(str(e), True)
                  return
              else:
                log(str(e), True)
                return

            response_data = response.read()
            response.close()


            # parsing page for videos
            # video-entry
            for r in re.finditer('<a id="([^\"]+)" href="([^\"]+)">([^\<]+)</a>' ,
                                 response_data, re.DOTALL):
                fileID,url,fileName = r.groups()


                log('found video %s %s' % (fileName, url))

                # streaming
                videos[fileName] = {'url': 'plugin://plugin.video.cloudstream?mode=streamURL&instance='+self.instanceName+'&url=' + url, 'mediaType' : self.MEDIA_TYPE_VIDEO}

            # folder-entry
            for r in re.finditer('<a href=".*?fld_id=([^\"]+)"><b>([^\<]+)</b></a>' ,
                                 response_data, re.DOTALL):
                folderID,folderName = r.groups()

                log('found folder %s %s' % (folderName, url))

                # folder
                if int(folderID) != 0:
                    videos[folderName] = {'url': 'plugin://plugin.video.cloudstream?mode=folder&instance='+self.instanceName+'&folderID=' + folderID, 'mediaType' : self.MEDIA_TYPE_FOLDER}



        return videos


    ##
    # retrieve a video link
    #   parameters: title of video, whether to prompt for quality/format (optional), cache type (optional)
    #   returns: list of URLs for the video or single URL of video (if not prompting for quality)
    ##
    def getPublicLink(self,url,cacheType=0):


        log('url = %s header = %s' % (url, self.getHeadersList()))
        req = urllib2.Request(url, None, self.getHeadersList())


        # if action fails, validate login
        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError, e:
            if e.code == 403 or e.code == 401:
              self.login()
              req = urllib2.Request(url, None, self.getHeadersList())
              try:
                response = urllib2.urlopen(req)
              except urllib2.URLError, e:
                log(str(e), True)
                return
            else:
              log(str(e), True)
              return

        response_data = response.read()
        response.close()


        confirmID = 0
        # fetch video title, download URL and docid for stream link
        for r in re.finditer('<input type="hidden" name="op" value="([^\"]+)">.*?<input type="hidden" name="usr_login" value="([^\"]*)">.*?<input type="hidden" name="id" value="([^\"]+)">.*?<input type="hidden" name="fname" value="([^\"]*)">.*?<input type="hidden" name="referer" value="([^\"]*)">' ,response_data, re.DOTALL):
             op,usr_login,id,fname,referer = r.groups()


        values = {
                  'op' : op,
                  'usr_login' : usr_login,
                  'id' : id,
                  'fname' : fname,
                  'referer' : referer,
                  'method_free' : 'Free Download'

        }

        req = urllib2.Request(url, urllib.urlencode(values), self.getHeadersList())


        # if action fails, validate login
        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError, e:
            if e.code == 403 or e.code == 401:
              self.login()
              req = urllib2.Request(url,  urllib.urlencode(values), self.getHeadersList())
              try:
                response = urllib2.urlopen(req)
              except urllib2.URLError, e:
                log(str(e), True)
                return
            else:
              log(str(e), True)
              return

        response_data = response.read()
        response.close()

        streamURL = 0
        # fetch video title, download URL and docid for stream link
        for r in re.finditer('(file)\: \"([^\"]+)"\,' ,response_data, re.DOTALL):
             streamType,streamURL = r.groups()


        return streamURL




