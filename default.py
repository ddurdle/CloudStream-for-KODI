'''
    cloudstream XBMC Plugin
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

from resources.lib import  cloudservice
from resources.lib import  xfilesharing
import sys
import urllib
import cgi
import re

import xbmc, xbmcgui, xbmcplugin, xbmcaddon


#helper methods
def log(msg, err=False):
    if err:
        xbmc.log(addon.getAddonInfo('name') + ': ' + msg, xbmc.LOGERROR)
    else:
        xbmc.log(addon.getAddonInfo('name') + ': ' + msg, xbmc.LOGDEBUG)

def parse_query(query):
    queries = cgi.parse_qs(query)
    q = {}
    for key, value in queries.items():
        q[key] = value[0]
    q['mode'] = q.get('mode', 'main')
    return q

def addVideo(url, infolabels, label, img='', fanart='', total_items=0,
                   cm=[], cm_replace=False):
    infolabels = decode_dict(infolabels)
    log('adding video: %s - %s' % (infolabels['title'], url))
    listitem = xbmcgui.ListItem(label, iconImage=img,
                                thumbnailImage=img)
    listitem.setInfo('video', infolabels)
    listitem.setProperty('IsPlayable', 'true')
    listitem.setProperty('fanart_image', fanart)
    if cm:
        listitem.addContextMenuItems(cm, cm_replace)
    xbmcplugin.addDirectoryItem(plugin_handle, url, listitem,
                                isFolder=False, totalItems=total_items)

def addDirectory(url, title, img='', fanart='', total_items=0):
    log('adding dir: %s - %s' % (title, url))
    listitem = xbmcgui.ListItem(decode(title), iconImage=img, thumbnailImage=img)
    if not fanart:
        fanart = addon.getAddonInfo('path') + '/fanart.jpg'
    listitem.setProperty('fanart_image', fanart)
    xbmcplugin.addDirectoryItem(plugin_handle, url, listitem,
                                isFolder=True, totalItems=total_items)

#http://stackoverflow.com/questions/1208916/decoding-html-entities-with-python/1208931#1208931
def _callback(matches):
    id = matches.group(1)
    try:
        return unichr(int(id))
    except:
        return id

def decode(data):
    return re.sub("&#(\d+)(;|(?=\s))", _callback, data).strip()

def decode_dict(data):
    for k, v in data.items():
        if type(v) is str or type(v) is unicode:
            data[k] = decode(v)
    return data

def numberOfAccounts(accountType):

    count = 1
    max_count = int(addon.getSetting(accountType+'_numaccounts'))
    actualCount = 0
    while True:
        try:
            if addon.getSetting(accountType+str(count)+'_username') != '':
                actualCount = actualCount + 1
        except:
            break
        if count == max_count:
            break
        count = count + 1
    return actualCount

#global variables
plugin_url = sys.argv[0]
plugin_handle = int(sys.argv[1])
plugin_queries = parse_query(sys.argv[2][1:])

addon = xbmcaddon.Addon(id='plugin.video.cloudstream')

try:

    remote_debugger = addon.getSetting('remote_debugger')
    remote_debugger_host = addon.getSetting('remote_debugger_host')

    # append pydev remote debugger
    if remote_debugger == 'true':
        # Make pydev debugger works for auto reload.
        # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
        import pysrc.pydevd as pydevd
        # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
        pydevd.settrace(remote_debugger_host, stdoutToServer=True, stderrToServer=True)
except ImportError:
    log(addon.getLocalizedString(30016), True)
    sys.exit(1)
except :
    pass


# retrieve settings
user_agent = addon.getSetting('user_agent')



log('plugin url: ' + plugin_url)
log('plugin queries: ' + str(plugin_queries))
log('plugin handle: ' + str(plugin_handle))

mode = plugin_queries['mode']

# make mode case-insensitive
mode = mode.lower()

accounts = []
#dump a list of videos available to play
if mode == 'main' or mode == 'folder':
    log(mode)

    folderID=0
    if (mode == 'folder'):
        folderID = plugin_queries['folderID']

    instanceName = ''
    try:
        instanceName = plugin_queries['instance']
    except:
        pass

    numberOfAccounts = numberOfAccounts('xfilesharing')

    # show list of services
    if numberOfAccounts > 1 and instanceName == '':
        count = 1
        max_count = int(addon.getSetting('xfilesharing_numaccounts'))
        while True:
            instanceName = 'xfilesharing'+str(count)
            try:
                username = addon.getSetting(instanceName+'_username')
                if username != '':
                    domain = addon.getSetting(instanceName+'_domain')
                    if domain == 'CUSTOM':
                        domain = addon.getSetting(instanceName+'_custom_domain')
                    addDirectory('plugin://plugin.video.cloudstream?mode=main&instance='+instanceName,domain + '-'+username)
            except:
                break
            if count == max_count:
                break
            count = count + 1

    else:
        cloudservice = ''
        # show index of accounts
        if instanceName == '' and numberOfAccounts == 1:

                count = 1
                max_count = int(addon.getSetting('xfilesharing_numaccounts'))
                while True:
                    instanceName = 'xfilesharing'+str(count)
                    try:
                        username = addon.getSetting(instanceName+'_username')
                        if username != '':
                            domain = addon.getSetting(instanceName+'_domain')
                            custom_domain = addon.getSetting(instanceName+'_custom_domain')
                            password  = addon.getSetting(instanceName+'_password')
                            save_auth  = addon.getSetting(instanceName+'_save_auth')
                            auth_token = addon.getSetting(instanceName+'_auth_token')
                            update_token_name = instanceName+'_auth_token'
                            cloudservice = xfilesharing.xfilesharing(instanceName, domain, username, password, auth_token, user_agent)
                    except :
                        break
                    if count == max_count:
                        break
                    count = count + 1

        # show entries of a single account (such as folder)
        elif instanceName != '':

                    username = addon.getSetting(instanceName+'_username')
                    domain = addon.getSetting(instanceName+'_domain')
                    custom_domain = addon.getSetting(instanceName+'_custom_domain')
                    password  = addon.getSetting(instanceName+'_password')
                    save_auth  = addon.getSetting(instanceName+'_save_auth')
                    auth_token = addon.getSetting(instanceName+'_auth_token')
                    update_token_name = instanceName+'_auth_token'
                    cloudservice = xfilesharing.xfilesharing(instanceName, domain, username, password, auth_token, user_agent)

        cacheType = addon.getSetting('playback_type')

        singlePlayback=''
        videos = cloudservice.getVideosList(folderID=folderID)

        for title in sorted(videos.iterkeys()):
            if videos[title]['mediaType'] == cloudservice.MEDIA_TYPE_VIDEO:
                addVideo(videos[title]['url'],
                             { 'title' : title , 'plot' : title }, title)
                if singlePlayback == '':
                    singlePlayback = title
            else:
                addDirectory(videos[title]['url'],title)

        if singlePlayback != '':
            item = xbmcgui.ListItem(path=videos[singlePlayback]['url'])
            log('play url: ' + singlePlayback)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        # update the authorization token in the configuration file if we had to login for a new one during this execution run
        if auth_token != cloudservice.auth and save_auth == 'true':
            addon.setSetting(cloudservice.instanceName+'_auth_token', cloudservice.auth)


#force stream - play a video given its exact-title
elif mode == 'streamvideo':
    try:
      filename = plugin_queries['filename']
    except:
      title = 0


    # immediately play resulting (is a video)
    videoURL = cloudservice.getVideoLink(filename)
    item = xbmcgui.ListItem(path=videoURL)
    log('play url: ' + videoURL)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

elif mode == 'streamurl':
    try:
      url = plugin_queries['url']
      instanceName = plugin_queries['instance']
    except:
      url = 0

    try:
        domain = addon.getSetting(instanceName+'_domain')
        custom_domain = addon.getSetting(instanceName+'_custom_domain')
        username = addon.getSetting(instanceName+'_username')
        password = addon.getSetting(instanceName+'_password')
        save_auth  = addon.getSetting(instanceName+'_save_auth')
        auth_token = addon.getSetting(instanceName+'_auth_token')
        cloudservice = xfilesharing.xfilesharing(instanceName,domain,username, password, auth_token, user_agent)
    except :
        pass

    # immediately play resulting (is a video)
    videoURL = cloudservice.getPublicLink(url)
    item = xbmcgui.ListItem(path=videoURL)
    log('play url: ' + videoURL)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

    # update the authorization token in the configuration file if we had to login for a new one during this execution run
    if auth_token != cloudservice.auth and save_auth == 'true':
        addon.setSetting(cloudservice.instanceName+'_auth_token', cloudservice.auth)

#clear the authorization token
elif mode == 'clearauth':
    addon.setSetting('auth_token', '')




xbmcplugin.endOfDirectory(plugin_handle)

