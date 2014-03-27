'''
    movpod XBMC Plugin
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
class movpod:


    ##
    # initialize (setting 1) username, 2) password, 3) authorization token, 4) user agent string
    ##
    def __init__(self, user, password, auth, user_agent):
        self.user = user
        self.password = password
        self.auth = auth
        self.user_agent = user_agent
        self.cookiejar = cookielib.CookieJar()


        # if we have an authorization token set, try to use it
        if auth != '':
          log('using token')

          return
        else:
          log('no token - logging in')
#          self.login();
          return



    ##
    # perform login
    ##
    def login(self):

        self.auth = ''

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        # default User-Agent ('Python-urllib/2.6') will *not* work
        opener.addheaders = [('User-Agent', self.user_agent)]

        url = 'http://www.movpod.com/authenticate.php?login'

        try:
            response = opener.open(url)

        except urllib2.URLError, e:
            log(str(e), True)
            return
        response_data = response.read()
        response.close()

        # fetch captcha url
        for r in re.finditer('<td>(CAPTCHA)</td>.*?<td><img src="([^\"]+)\"',
                             response_data, re.DOTALL):
            ceptchaType,captchaURL = r.groups()

        url = 'http://www.movpod.com' + captchaURL

        try:
            response = opener.open(url)
        except urllib2.URLError, e:
                log(str(e), True)

        output = open('/tmp/test.png','wb')
        output.write(response.read())
        output.close()
        response.close()



        img = xbmcgui.ControlImage(450,15,400,130,  '/tmp/test.png')
        wdlg = xbmcgui.WindowDialog()
        wdlg.addControl(img)
        wdlg.show()

        xbmc.sleep(3000)

        kb = xbmc.Keyboard('', 'Type the letters in the image', False)
        kb.doModal()
        capcode = kb.getText()

        if (kb.isConfirmed()):
           userInput = kb.getText()
           if userInput != '':
               solution = kb.getText()
           elif userInput == '':
               raise Exception ('You must enter text in the image to access video')
        else:
           raise Exception ('Captcha Error')
        wdlg.close()


        url = 'http://www.movpod.com/authenticate.php?login'

        values = {
                  'pass' : self.password,
                  'user' : self.user,
                  'remember' : 1,
                  'captcha_code' : solution,
                  'login_submit' : 'Login',
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


        loginResult = 0
        #validate successful login
        for r in re.finditer('class="(header-right-auth)"><strong>([^\<]+)</strong>',
                             response_data, re.DOTALL):
            loginType,loginResult = r.groups()

        if (loginResult == 0 or loginResult != self.user):
            xbmcgui.Dialog().ok(ADDON.getLocalizedString(30000), ADDON.getLocalizedString(30017))
            log('login failed', True)
            return

        for cookie in self.cookiejar:
            for r in re.finditer(' ([^\=]+)\=([^\s]+)\s',
                        str(cookie), re.DOTALL):
                cookieType,cookieValue = r.groups()
                if cookieType == 'auth':
                    self.auth = cookieValue


        return



    ##
    # return the appropriate "headers" for FireDrive requests that include 1) user agent, 2) authorization cookie
    #   returns: list containing the header
    ##
    def getHeadersList(self):
        if (self.auth != '' or self.auth != 0):
            return { 'User-Agent' : self.user_agent, 'Cookie' : 'auth='+self.auth+'; exp=1' }
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
        url = 'http://www.movpod.com/cp.php'

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
            for r in re.finditer('input name="file_\d+" type="checkbox" value="([^\"]+)"></td>.*?<div style="background-image:url\(([^\)]+)\);.*?<strong><a href="[^\"]+">([^\<]+)</a>' ,
                                 response_data, re.DOTALL):
                fileID,img,title = r.groups()


                log('found video %s %s' % (title, fileID))

                # streaming
                videos[title] = {'url': 'plugin://plugin.video.movpod?mode=streamVideo&filename=' + fileID, 'thumbnail' : img}



        return videos


    ##
    # retrieve a list of folders
    #   parameters: folder is the current folderID
    #   returns: list of videos
    ##
    def getFolderList(self, folderID=0):

        # retrieve all documents
        params = urllib.urlencode({'getFolders': folderID, 'format': 'large', 'term': '', 'group':0, 'user_token': self.auth, '_': 1394486104901})

        url = 'http://www.movpod.in/'+ params

        folders = {}
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

            # parsing page for videos
            # video-entry
            for r in re.finditer('"f_id":"([^\"]+)".*?"f_fullname":"([^\"]+)"' ,response_data, re.DOTALL):
                folderID, folderName = r.groups()

                log('found folder %s %s' % (folderID, folderName))

                # streaming
                folders[folderName] = 'plugin://plugin.video.movpod?mode=folder&folderID=' + folderID

            response.close()

        return folders



    ##
    # retrieve a video link
    #   parameters: title of video, whether to prompt for quality/format (optional), cache type (optional)
    #   returns: list of URLs for the video or single URL of video (if not prompting for quality)
    ##
    def getVideoLink(self,filename,cacheType=0):



        return 'http://dl.movpod.com/?alias='+filename+'&stream' + '|'+self.getHeadersEncoded()

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




