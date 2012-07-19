# -*- coding: utf-8 -*-

from requester import requester, url4webpy

#some django stuff
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.http import urlquote

from your.views import login

def checklogin( request, redirect_field_name =REDIRECT_FIELD_NAME):
    if request.user.is_authenticated(): return None
    login_url = reverse( login)
    path = urlquote( request.get_full_path())
    print 'REDIRECTING', path
    return HttpResponseRedirect( '%(login_url)s?%(redirect_field_name)s=%(path)s' % locals() )

requester.HttpResponse = HttpResponse

##################

from face__io import *  #all face-decls

#one impl:
import os
from somewhere import settings, xsendfile

class FileSystem_Images( IOFace_Images):
    #path = os.path.join( settings.AS_IMAGES_PATH, 'images')
    def program_image( me, name):
        return xsendfile( os.path.join( settings.AS_IMAGES_PATH, 'events', name))

fimg = FileSystem_Images()

#... other implementations
fprg = myIOFace_Programs(
        context= DictAttr( lang='eng'),
        result_as= str,
        )
fmeta = myIOFace_Storage()

#print 'generators:', fprg.methods_as_generator

urls = []
urls+= url4webpy( fprg, #face_subset= AFace,
            requester= lambda m: requester( m,
                            face= fprg,
                            as_generator= m.name in fprg.methods_as_generator,
                            checklogin= checklogin),
            )
#simple ones
for f in [ fimg, fmeta ]:
    urls+= url4webpy( f,  requester= lambda m: requester( m, result_is_tuple= False),)
#...

''' becomes something like this
    (all are user-authenticated somehow; all are GET except some browser forms)

    /programs
    .channels              #all channels
    .programs?channel=34   #programs in channel
    .programs              #programs in all channels
    .add_program?channel=34&program=2345        #add program to channel
    .del_program?channel=34&program=2345        #del program to channel
    .new_channel?program=2345&name=..
    .save_channel?channel=34&name=..            #upd channel metadata
    .del_channel?channel=34                     #del whole channel

    /storage
    .broadcast_channels     #all
    .programs_by_filter?filter=..
    .programs_by_filter     #all programs
    .getGenre?id=345        #description of genre 345

    /images
    .program_image?program=345
    .channel_logo?channel=12
'''


if __name__ == '__main__':
    if 10:
        from facer import url_doco
        #for x in urls: print x
        #print '---doco'
        for i in fprg,fimg,fdbgz:
            print i
            for x in url_doco( i, separator='\n    '): print x

# vim:ts=4:sw=4:expandtab
