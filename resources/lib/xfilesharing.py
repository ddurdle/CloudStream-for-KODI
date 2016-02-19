'''
    xfilesharing XBMC Plugin
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

import cloudservice
import os
import re
import urllib, urllib2
import cookielib


import xbmc, xbmcaddon, xbmcgui, xbmcplugin

# global variables
PLUGIN_NAME = 'plugin.video.cloudstream'
PLUGIN_URL = 'plugin://'+PLUGIN_NAME+'/'
ADDON = xbmcaddon.Addon(id=PLUGIN_NAME)

# helper methods
def log(msg, err=False):
    if err:
        xbmc.log(ADDON.getAddonInfo('name') + ': ' + msg, xbmc.LOGERROR)
    else:
        xbmc.log(ADDON.getAddonInfo('name') + ': ' + msg, xbmc.LOGDEBUG)


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

        if self.domain == 'uptostream.com':
            self.domain = 'uptobox.com'

        if 'http://' in self.domain:
            url = self.domain
            values = {
                                'op' : 'login',
                                'login' : self.user,
                                'redirect' : url,
                                'password' : self.password
                                }
        elif self.domain == 'uptobox.com':
            url = 'http://' + self.domain + '/log'
            values = {
                                'op' : 'login',
                                'login' : self.user,
                                'password' : self.password
                                }

        else:
            url = 'http://' + self.domain + '/'

            values = {
                                'op' : 'login',
                                'login' : self.user,
                                'redirect' : url,
                                'password' : self.password
                                }



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
        #validate successful login
        for r in re.finditer('logout',
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
                if cookieType == 'xfsts':
                    self.auth = cookieValue

        return



    ##
    # return the appropriate "headers" for FireDrive requests that include 1) user agent, 2) authorization cookie
    #   returns: list containing the header
    ##
    def getHeadersList(self,referer=''):
        if ((self.auth != '' or self.auth != 0) and referer == ''):
            return { 'User-Agent' : self.user_agent, 'Cookie' : 'lang=english; login='+self.user+'; xfsts='+self.auth+'; xfss='+self.auth+';' }
        elif (self.auth != '' or self.auth != 0):
            return { 'User-Agent' : self.user_agent, 'Referer': referer, 'Cookie' : 'lang=english; login='+self.user+'; xfsts='+self.auth+'; xfss='+self.auth+';' }
        else:
            return { 'User-Agent' : self.user_agent }

    ##
    # return the appropriate "headers" for FireDrive requests that include 1) user agent, 2) authorization cookie
    #   returns: URL-encoded header string
    ##
    def getHeadersEncoded(self, referer=''):
        return urllib.urlencode(self.getHeadersList(referer))

    ##
    # retrieve a list of videos, using playback type stream
    #   parameters: prompt for video quality (optional), cache type (optional)
    #   returns: list of videos
    ##
    def getVideosList(self, folderID=0, cacheType=0):

        if 'http://' in self.domain:
            url = self.domain
        else:
            url = 'http://' + self.domain

        if 'streamcloud.eu' in self.domain:

            url = url + '/'

        # retrieve all documents
        if folderID == 0:
            url = url+'?op=my_files'
        else:
            url = url+'?op=my_files&fld_id='+folderID


        videos = {}
        if True:
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

            for r in re.finditer('placeholder\=\"(Username)\" id\=i\"(nputLoginEmail)\" name\=\"login\"' ,
                                 response_data, re.DOTALL):
                loginUsername,loginUsernameName = r.groups()
                self.login()

                req = urllib2.Request(url, None, self.getHeadersList())
                try:
                  response = urllib2.urlopen(req)
                except urllib2.URLError, e:
                  log(str(e), True)
                  return

                response_data = response.read()
                response.close()


            # parsing page for videos
            # video-entry
            for r in re.finditer('<a id="([^\"]+)" href="([^\"]+)">([^\<]+)</a>' ,
                                 response_data, re.DOTALL):
                fileID,url,fileName = r.groups()


                # streaming
                videos[fileName] = {'url': 'plugin://plugin.video.cloudstream?mode=streamURL&instance='+self.instanceName+'&url=' + url, 'mediaType' : self.MEDIA_TYPE_VIDEO}

            for r in re.finditer('<input type="checkbox" name="file_id".*?<a href="([^\"]+)">([^\<]+)</a>' ,
                                 response_data, re.DOTALL):
                url,fileName = r.groups()


                # streaming
                videos[fileName] = {'url': 'plugin://plugin.video.cloudstream?mode=streamURL&instance='+self.instanceName+'&url=' + url, 'mediaType' : self.MEDIA_TYPE_VIDEO}

            # video-entry - bestream
            for r in re.finditer('<TD align=left>[^\<]+<a href="([^\"]+)">([^\<]+)</a>' ,
                                 response_data, re.DOTALL):
                url,fileName = r.groups()


                # streaming
                videos[fileName] = {'url': 'plugin://plugin.video.cloudstream?mode=streamURL&instance='+self.instanceName+'&url=' + url, 'mediaType' : self.MEDIA_TYPE_VIDEO}

            # video-entry - uptobox
            for r in re.finditer('<td><a href="([^\"]+)".*?>([^\<]+)</a></td>' ,
                                 response_data, re.DOTALL):
                url,fileName = r.groups()


                # streaming
                videos[fileName] = {'url': 'plugin://plugin.video.cloudstream?mode=streamURL&instance='+self.instanceName+'&url=' + url, 'mediaType' : self.MEDIA_TYPE_VIDEO}

            if 'realvid.net' in self.domain:
                for r in re.finditer('<a href="[^\"]+">([^\<]+)</a>\s+</TD>' ,
                                 response_data, re.DOTALL):
                    url,fileName = r.groups()

            #flatten folders (no clean way of handling subfolders, so just make the root list all folders & subfolders
            #therefore, skip listing folders if we're not in root
#            if folderID == 0:
                # folder-entry
                #            for r in re.finditer('<a href=".*?fld_id=([^\"]+)"><b>([^\<]+)</b></a>' ,
#                folderID = 0
#                for r in re.finditer('<option value="(\d\d+)">([^\<]+)</option>' ,
#                                 response_data, re.DOTALL):
#                    folderID,folderName = r.groups()

                    #remove &nbsp; from folderName
#                    folderName = re.sub('\&nbsp\;', '', folderName)

                    # folder
#                    if int(folderID) != 0:
#                        videos[folderName] = {'url': 'plugin://plugin.video.cloudstream?mode=folder&instance='+self.instanceName+'&folderID=' + folderID, 'mediaType' : self.MEDIA_TYPE_FOLDER}
#            if folderID == 0:
            for r in re.finditer('<a href=".*?fld_id=([^\"]+)"><b>([^\<]+)</b></a>' ,
                                 response_data, re.DOTALL):
                    folderID,folderName = r.groups()

                    # folder
                    if int(folderID) != 0 and folderName != '&nbsp;. .&nbsp;':
                        videos[folderName] = {'url': 'plugin://plugin.video.cloudstream?mode=folder&instance='+self.instanceName+'&folderID=' + folderID, 'mediaType' : self.MEDIA_TYPE_FOLDER}

        return videos


    ##
    # retrieve a video link
    #   parameters: title of video, whether to prompt for quality/format (optional), cache type (optional)
    #   returns: list of URLs for the video or single URL of video (if not prompting for quality)
    ##
    def getPublicLink(self,url,cacheType=0):

        fname = ''
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [ ('User-Agent' , self.user_agent)]
        req = urllib2.Request(url)
        try:
            response = opener.open(req)
        except urllib2.URLError, e:
            pass
        response.close()
        url = response.url

#        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar), MyHTTPErrorProcessor)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        opener.addheaders = [ ('User-Agent' , self.user_agent), ('Referer', url), ('Cookie', 'lang=english; login='+self.user+'; xfsts='+self.auth+'; xfss='+self.auth+';')]

        req = urllib2.Request(url)


        # if action fails, validate login
        try:
            response = opener.open(req)
        except urllib2.URLError, e:
            if e.code == 403 or e.code == 401:
              self.login()

              req = urllib2.Request(url, None, self.getHeadersList())
              try:
                  response = opener.open(req)
              except urllib2.URLError, e:
                log(str(e), True)
                return ('','')
            else:
              log(str(e), True)
              return ('','')

        response_data = response.read()
        response.close()

        for r in re.finditer('\<title\>([^\<]+)\<',
                             response_data, re.DOTALL | re.I):
                  title = r.group(1)
                  if fname == '':
                      fname = title

        url = response.url
        req = urllib2.Request(url)

        for r in re.finditer('name\=\"(code)\" class\=\"(captcha_code)' ,
                                 response_data, re.DOTALL):
                loginUsername,loginUsernameName = r.groups()
                self.login()

                req = urllib2.Request(url, None, self.getHeadersList())
                try:
                  response = urllib2.urlopen(req)
                except urllib2.URLError, e:
                  log(str(e), True)
                  return ('','')

                response_data = response.read()
                response.close()


        if self.domain == 'vidzi.tv':
            for r in re.finditer('(file)\: \"([^\"]+)\.mp4\"' ,response_data, re.DOTALL):
                streamType,streamURL = r.groups()
                return (streamURL + '.mp4', fname)

        confirmID = 0
        values = {}
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


        for r in re.finditer('<input type="hidden" name="op" value="([^\"]+)">.*?<input type="hidden" name="usr_login" value="([^\"]*)">.*?<input type="hidden" name="id" value="([^\"]+)">.*?<input type="hidden" name="fname" value="([^\"]*)">.*?<input type="hidden" name="referer" value="([^\"]*)">.*?<input type="hidden" name="hash" value="([^\"]*)">.*?<input type="submit" name="imhuman" value="([^\"]*)" id="btn_download">' ,response_data, re.DOTALL):
             op,usr_login,id,fname,referer,hash,submit = r.groups()
             values = {
                  'op' : op,
                  'usr_login' : usr_login,
                  'id' : id,
                  'fname' : fname,
                  'referer' : referer,
                  'hash' : hash,
                  'imhuman' : submit

             }

        for r in re.finditer('<input type="hidden" name="op" value="([^\"]+)">.*?<input type="hidden" name="usr_login" value="([^\"]*)">.*?<input type="hidden" name="id" value="([^\"]+)">.*?<input type="hidden" name="fname" value="([^\"]*)">.*?<input type="hidden" name="referer" value="([^\"]*)">.*?<input type="hidden" name="hash" value="([^\"]*)">.*?<input type="hidden" name="inhu" value="([^\"]*)">.*?<input type="submit" name="imhuman" value="([^\"]*)" id="btn_download">' ,response_data, re.DOTALL):
             op,usr_login,id,fname,referer,hash,inhu,submit = r.groups()
             values = {

                  '_vhash' : 'i1102394cE',
                  'gfk' : 'i22abd2449',
                  'op' : op,
                  'usr_login' : usr_login,
                  'id' : id,
                  'fname' : fname,
                  'referer' : referer,
                  'hash' : hash,
                  'inhu' : inhu,
                  'imhuman' : submit

             }

        for r in re.finditer('<input type="hidden" name="op" value="([^\"]+)">.*?<input type="hidden" name="id" value="([^\"]+)">.*?<input type="hidden" name="referer" value="([^\"]*)">.*?<input type="hidden" name="method_free" value="([^\"]*)">' ,response_data, re.DOTALL):
             op,id,referer,submit = r.groups()
             values = {
                  'op' : op,
                  'id' : id,
                  'referer' : referer,
                  'method_free' : submit,
                  'download_direct' : 1

             }

        for r in re.finditer('<input type="hidden" name="op" value="([^\"]+)">.*?<input type="hidden" name="id" value="([^\"]+)">.*?<input type="hidden" name="rand" value="([^\"]*)">.*?<input type="hidden" name="referer" value="([^\"]*)">.*?<input type="hidden" name="method_free" value="([^\"]*)">' ,response_data, re.DOTALL):
             op,id,rand,referer,submit = r.groups()
             values = {
                  'op' : op,
                  'id' : id,
                  'rand' : rand,
                  'referer' : referer,
                  'method_free' : submit,
                  'download_direct' : 1

             }
        for r in re.finditer('<input type="hidden" name="ipcount_val"  id="ipcount_val" value="([^\"]+)">.*?<input type="hidden" name="op" value="([^\"]+)">.*? <input type="hidden" name="usr_login" value="([^\"]*)">.*?<input type="hidden" name="id" value="([^\"]+)">.*?<input type="hidden" name="fname" value="([^\"]*)">.*?<input type="hidden" name="referer" value="([^\"]*)">' ,response_data, re.DOTALL):
             ipcount,op,usr_login,id,fname,referer = r.groups()
             values = {
                  'ipcount_val' : ipcount,
                  'op' : op,
                  'usr_login' : usr_login,
                  'id' : id,
                  'fname' : fname,
                  'referer' : referer,
                  'method_free' : 'Slow access'
             }

        values = {}
        variable = 'op'
        for r in re.finditer('<input type="(hidden)" name="'+variable+'" value="([^\"]*)">' ,response_data, re.DOTALL):
             hidden,value = r.groups()
             values[variable] = value

        variable = 'usr_login'
        for r in re.finditer('<input type="(hidden)" name="'+variable+'" value="([^\"]*)">' ,response_data, re.DOTALL):
             hidden,value = r.groups()
             values[variable] = value

        variable = 'id'
        for r in re.finditer('<input type="(hidden)" name="'+variable+'" value="([^\"]*)">' ,response_data, re.DOTALL):
             hidden,value = r.groups()
             values[variable] = value

        variable = 'fname'
        for r in re.finditer('<input type="(hidden)" name="'+variable+'" value="([^\"]*)">' ,response_data, re.DOTALL):
             hidden,value = r.groups()
             values[variable] = value

        variable = 'referer'
        for r in re.finditer('<input type="(hidden)" name="'+variable+'" value="([^\"]*)">' ,response_data, re.DOTALL):
             hidden,value = r.groups()
             values[variable] = value


        variable = 'hash'
        for r in re.finditer('<input type="(hidden)" name="'+variable+'" value="([^\"]*)">' ,response_data, re.DOTALL):
             hidden,value = r.groups()
             values[variable] = value

        variable = 'inhu'
        for r in re.finditer('<input type="(hidden)" name="'+variable+'" value="([^\"]*)">' ,response_data, re.DOTALL):
             hidden,value = r.groups()
             values[variable] = value

        variable = 'method_free'
        for r in re.finditer('<input type="(hidden)" name="'+variable+'" value="([^\"]*)">' ,response_data, re.DOTALL):
             hidden,value = r.groups()
             values[variable] = value

        variable = 'method_premium'
        for r in re.finditer('<input type="(hidden)" name="'+variable+'" value="([^\"]*)">' ,response_data, re.DOTALL):
             hidden,value = r.groups()
             values[variable] = value

        variable = 'rand'
        for r in re.finditer('<input type="(hidden)" name="'+variable+'" value="([^\"]*)">' ,response_data, re.DOTALL):
             hidden,value = r.groups()
             values[variable] = value

        variable = 'down_direct'
        for r in re.finditer('<input type="(hidden)" name="'+variable+'" value="([^\"]*)">' ,response_data, re.DOTALL):
             hidden,value = r.groups()
             values[variable] = value

        variable = 'file_size_real'
        for r in re.finditer('<input type="(hidden)" name="'+variable+'" value="([^\"]*)">' ,response_data, re.DOTALL):
             hidden,value = r.groups()
             values[variable] = value

        variable = 'imhuman'
        for r in re.finditer('<input type="(submit)" name="'+variable+'" value="([^\"]*)" id="btn_download">' ,response_data, re.DOTALL):
             hidden,value = r.groups()
             values[variable] = value

        variable = 'gfk'
        for r in re.finditer('(name): \''+variable+'\', value: \'([^\']*)\'' ,response_data, re.DOTALL):
             hidden,value = r.groups()
             values[variable] = value

        variable = '_vhash'
        for r in re.finditer('(name): \''+variable+'\', value: \'([^\']*)\'' ,response_data, re.DOTALL):
             hidden,value = r.groups()
             values[variable] = value

#        values['referer'] = ''

        for r in re.finditer('<input type="hidden" name="op" value="([^\"]+)">.*?<input type="hidden" name="id" value="([^\"]+)">.*?<input type="hidden" name="rand" value="([^\"]*)">.*?<input type="hidden" name="referer" value="([^\"]*)">.*?<input type="hidden" name="plugins_are_not_allowed" value="([^\"]+)"/>.*?<input type="hidden" name="method_free" value="([^\"]*)">' ,response_data, re.DOTALL):
             op,id,rand,referer,plugins,submit = r.groups()

             values = {
                  'op' : op,
                  'id' : id,
                  'rand' : rand,
                  'referer' : referer,
                  'plugins_are_not_allowed' : plugins,
                  'method_free' : submit,
                  'download_direct' : 1

             }




#        req = urllib2.Request(url, urllib.urlencode(values), self.getHeadersList(url))
        req = urllib2.Request(url)

        if self.domain == 'thefile.me':
            values['method_free'] = 'Free Download'
        elif self.domain == 'sharesix.com':
            values['method_free'] = 'Free'

        elif 'streamcloud.eu' in self.domain:
            xbmcgui.Dialog().ok(ADDON.getLocalizedString(30000), ADDON.getLocalizedString(30037) + str(10))
            xbmc.sleep((int(10)+1)*1000)

        elif self.domain == 'vidhog.com':
            xbmcgui.Dialog().ok(ADDON.getLocalizedString(30000), ADDON.getLocalizedString(30037) + str(15))
            xbmc.sleep((int(15)+1)*1000)

        elif self.domain == 'vidto.me':
            xbmcgui.Dialog().ok(ADDON.getLocalizedString(30000), ADDON.getLocalizedString(30037) + str(6))
            xbmc.sleep((int(6)+1)*1000)

        elif self.domain == 'vodlocker.com':
            xbmcgui.Dialog().ok(ADDON.getLocalizedString(30000), ADDON.getLocalizedString(30037) + str(3))
            xbmc.sleep((int(3)+1)*1000)



        elif self.domain == 'hcbit.com':

            try:
#                response = urllib2.urlopen(req)
                response = opener.open(req, urllib.urlencode(values))

            except urllib2.URLError, e:
                if e.code == 403 or e.code == 401:
                    self.login()

                    try:
                        response = opener.open(req, urllib.urlencode(values))
                    except urllib2.URLError, e:
                        log(str(e), True)
                        return ('', '')
                else:
                    log(str(e), True)
                    return ('', '')
            try:
                if response.info().getheader('Location') != '':
                    return (response.info().getheader('Location') + '|' + self.getHeadersEncoded(url), fname)
            except:
                for r in re.finditer('\'(file)\'\,\'([^\']+)\'' ,response_data, re.DOTALL):
                    streamType,streamURL = r.groups()
                    return (streamURL  + '|' + self.getHeadersEncoded(url), fname)
                for r in re.finditer('\<td (nowrap)\>([^\<]+)\<\/td\>' ,response_data, re.DOTALL):
                    deliminator,fileName = r.groups()
                for r in re.finditer('(\|)([^\|]{42})\|' ,response_data, re.DOTALL):
                    deliminator,fileID = r.groups()
                    streamURL = 'http://cloud1.hcbit.com/cgi-bin/dl.cgi/'+fileID+'/'+fileName
                    return (streamURL  + '|' + self.getHeadersEncoded(url), fname)

        if self.domain == 'bestreams.net':

            file_id = ''
            aff = ''
            variable = 'file_id'
            for r in re.finditer('\''+variable+'\', (\')([^\']*)\'' ,response_data, re.DOTALL):
                hidden,value = r.groups()
                file_id = value

            variable = 'aff'
            for r in re.finditer('\''+variable+'\', (\')([^\']*)\'' ,response_data, re.DOTALL):
                hidden,value = r.groups()
                aff = value

            xbmc.sleep((int(2)+1)*1000)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
            opener.addheaders = [ ('User-Agent' , self.user_agent), ('Referer', url), ('Cookie', 'lang=1; file_id='+file_id+'; aff='+aff+';')]

        elif self.domain == 'thevideo.me':

            for r in re.finditer('\,\s+file\:\s+\'([^\']+)\'',
                             response_data, re.DOTALL):
                  streamURL = r.group(1)
                  return (streamURL,fname)

        elif self.domain == 'vodlocker.com':

            for r in re.finditer('\file\:\s+\"([^\"]+v.mp4)\"',
                             response_data, re.DOTALL):
                  streamURL = r.group(1)
                  return (streamURL,fname)

        elif self.domain == 'vidzi.tv':

            for r in re.finditer('\s+file:\s+\"([^\"]+)\"',
                             response_data, re.DOTALL):
                  streamURL = r.group(1)
                  return (streamURL,fname)

        # if action fails, validate login
        try:
#              response = urllib2.urlopen(req)
            response = opener.open(req, urllib.urlencode(values))

        except urllib2.URLError, e:
            if e.code == 403 or e.code == 401:
                    self.login()

                    try:
                        response = opener.open(req, urllib.urlencode(values))
                    except urllib2.URLError, e:
                        log(str(e), True)
                        return ('','')
            else:
                    log(str(e), True)
                    return ('','')

        response_data = response.read()
        response.close()

        op=''
        for r in re.finditer('<input type="hidden" name="op" value="([^\"]+)">.*?<input type="hidden" name="id" value="([^\"]+)">.*?<input type="hidden" name="rand" value="([^\"]*)">.*?<input type="hidden" name="referer" value="([^\"]*)">.*?<input type="hidden" name="method_free" value="([^\"]*)">' ,response_data, re.DOTALL):
             op,id,rand,referer,submit = r.groups()
             values = {
                  'op' : op,
                  'id' : id,
                  'rand' : rand,
                  'referer' : referer,
                  'method_free' : submit,
                  'download_direct' : 1

             }

        streamURL=''

        title = ''
        for r in re.finditer('\<(title)\>([^\>]*)\<\/title\>' ,response_data, re.DOTALL):
             titleID,title = r.groups()


        # for thefile
        if self.domain == 'thefile.me':

            downloadAddress = ''
            for r in re.finditer('\<(img) src\=\"http\:\/\/([^\/]+)\/[^\"]+\" style' ,response_data, re.DOTALL):
             downloadTag,downloadAddress = r.groups()

            for r in re.finditer('(\|)([^\|]{56})\|' ,response_data, re.DOTALL):
                deliminator,fileID = r.groups()
                streamURL = 'http://'+str(downloadAddress)+'/d/'+fileID+'/video.mp4'

        elif self.domain == 'sharerepo.com':
            for r in re.finditer('(file)\: \'([^\']+)\'\,' ,response_data, re.DOTALL):
                streamType,streamURL = r.groups()

            for r in re.finditer('(\|)([^\|]{60})\|' ,response_data, re.DOTALL):
                deliminator,fileID = r.groups()
                streamURL = 'http://37.48.80.43/d/'+fileID+'/video.mp4?start=0'

        elif self.domain == 'filenuke.com':
            for r in re.finditer('(\|)([^\|]{56})\|' ,response_data, re.DOTALL):
                deliminator,fileID = r.groups()
                streamURL = 'http://37.252.3.244/d/'+fileID+'/video.flv?start=0'
        elif self.domain == 'sharerepo.com':
            for r in re.finditer('(file)\: \'([^\']+)\'\,' ,response_data, re.DOTALL):
                streamType,streamURL = r.groups()

        elif self.domain == 'letwatch.us':

            for r in re.finditer('\[IMG\]http://([^\/]+)\/',
                             response_data, re.DOTALL):
                  IP = r.group(1)

            for r in re.finditer('\|([^\|]{60})\|',
                             response_data, re.DOTALL):
                  fileID = r.group(1)
                  streamURL = 'http://'+IP+'/'+fileID+'/v.flv'

        elif self.domain == 'thevideo.me':

            for r in re.finditer('\,\s+file\:\s+\'([^\']+)\'',
                             response_data, re.DOTALL):
                  streamURL = r.group(1)

        elif self.domain == 'vodlocker.com':

            for r in re.finditer('\file\:\s+\"([^\"]+v.mp4)\"',
                             response_data, re.DOTALL):
                  streamURL = r.group(1)

        elif self.domain == 'vidto.me':

            for r in re.finditer('var file_link = \'([^\']+)\'',
                             response_data, re.DOTALL):
                  streamURL = r.group(1)

        elif self.domain == 'allmyvideos.net':

            for r in re.finditer('\"file\" : \"([^\"]+)\"',
                             response_data, re.DOTALL):
                  streamURL = r.group(1)

        elif self.domain == 'realvid.net':

            for r in re.finditer('file:\s?\'([^\']+)\'',
                             response_data, re.DOTALL):
                  streamURL = r.group(1)

        elif self.domain == 'uptobox.com' or self.domain == 'uptostream.com':

            for r in re.finditer('\<a href\=\"([^\"]+)\"\>\s+\<span class\=\"button_upload green\"\>',
                             response_data, re.DOTALL):
                  streamURL = r.group(1)
                  return (streamURL, fname)

            for r in re.finditer('\<source src=\'([^\']+)\'',
                             response_data, re.DOTALL):
                  streamURL = 'http:' + r.group(1)
                  return (streamURL, fname)

        timeout = 0
        if op != "" and streamURL == '':
            for r in re.finditer('Wait<strong><span id="(.*?)">(\d+)</span> seconds</strong>' ,response_data, re.DOTALL):
                id,timeout = r.groups()

            for r in re.finditer('<p class="(err)"><center><b>(.*?)</b>' ,response_data, re.DOTALL):
                id,error = r.groups()
                xbmcgui.Dialog().ok(ADDON.getLocalizedString(30000), error)
                return ('','')




            req = urllib2.Request(url)

            if timeout > 0:
                xbmcgui.Dialog().ok(ADDON.getLocalizedString(30000), ADDON.getLocalizedString(30037) + str(timeout))

                xbmc.sleep((int(timeout)+1)*1000)

            # if action fails, validate login
            try:
                response = opener.open(req, urllib.urlencode(values))

            except urllib2.URLError, e:
                if e.code == 403 or e.code == 401:
                    self.login()

                    try:
                        response = opener.open(req, urllib.urlencode(values))
                    except urllib2.URLError, e:
                        log(str(e), True)
                        return ('','')
                else:
                    log(str(e), True)
                    return ('','')

            response_data = response.read()
            response.close()

            for r in re.finditer('<a href="([^\"]+)">(Click here to start your download)</a>' ,response_data, re.DOTALL):
                streamURL,downloadlink = r.groups()

        #vodlocker.com
        if streamURL == '':
            # fetch video title, download URL and docid for stream link
            for r in re.finditer('(file)\: \"([^\"]+)"\,' ,response_data, re.DOTALL):
                streamType,streamURL = r.groups()
                if 'mp4' in streamURL:
                    break

        # mightyupload.com
        if streamURL == '':
            # fetch video title, download URL and docid for stream link
            for r in re.finditer('var (file_link) = \'([^\']+)\'' ,response_data, re.DOTALL):
                streamType,streamURL = r.groups()

        # vidhog.com
        if streamURL == '':
            # fetch video title, download URL and docid for stream link
            for r in re.finditer('(product_download_url)=([^\']+)\'' ,response_data, re.DOTALL):
                streamType,streamURL = r.groups()

        # vidspot.net
        if streamURL == '':
            # fetch video title, download URL and docid for stream link
            for r in re.finditer('"(file)" : "([^\"]+)"\,' ,response_data, re.DOTALL):
                streamType,streamURL = r.groups()

        # uploadc.com
        if streamURL == '':
            # fetch video title, download URL and docid for stream link
            for r in re.finditer('\'(file)\',\'([^\']+)\'\)\;' ,response_data, re.DOTALL):
                streamType,streamURL = r.groups()
                streamURL = streamURL + '|' + self.getHeadersEncoded(url)

#        return 'http://93.120.27.101:8777/pgjtbhuu6coammfvg5gfae6xogigs5cw6gsx3ey7yt6hmihwhpcixuiaqmza/v.mp4'


        return (streamURL, fname)

class MyHTTPErrorProcessor(urllib2.HTTPErrorProcessor):

    def http_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.info()

        # only add this line to stop 302 redirection.
        if code == 302: return response

        if not (200 <= code < 300):
            response = self.parent.error(
                'http', request, response, code, msg, hdrs)
        return response

    https_response = http_response


