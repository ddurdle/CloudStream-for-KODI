#from resources.lib import  cloudservice
from resources.lib import  xfilesharing
from subprocess import call

import sys
import re
import os

url = str(sys.argv[1])
file = str(sys.argv[2])


domain = ''
for r in re.finditer('([^\:]+)\://.*?([^\.]+\.[^\/]+)/' ,
                         url, re.DOTALL):
    protocol,domain = r.groups()
cloudservice = xfilesharing.xfilesharing('', domain, '', '', '', "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)")
(videoURL,title) = cloudservice.getPublicLink(url)
print 'url = '+url
print 'save as = '+file
print 'domain = '+domain
print 'payload = '+videoURL
os.system('wget "' + videoURL + '" -O "'+file + '"')
