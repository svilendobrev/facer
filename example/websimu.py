# -*- coding: utf-8 -*-

'simulator of web-API. served via werkzeug'

import simu     #contain the simulator-instance and these:
if 0:
    simu.fakedata()
    simu.test()
    simu.data_is_empty()
    simu.data_load()
    simu.data_save()

iface = simu.simu   #the actual simulator as face-instance
import webform

import werkzeug
from werkzeug.wrappers import Request, Response
from werkzeug.wsgi import responder
from werkzeug.routing import Map, Rule
from werkzeug.serving import run_simple
from werkzeug.datastructures import ImmutableDict #, ResponseCacheControl

try: from json import dumps as json_dumps
except ImportError:
    from simplejson import dumps as json_dumps

ROOT = ''
def lister( html =False):
    hidden_fields = dict( dbg=1)
    if html: hidden_fields.update( html=1)
    return Response( webform.html( iface, title='dobr test simulator',
        root= ROOT,
        hidden_fields= hidden_fields,
        help= '''\
default simulator result is json (as text/plain, not application/json).
url-param dbg=1 makes a dict( req, url, result=..) - all links above are this way.
url-param txt=1 makes a python repr, not json
''' ),
        content_type= 'html',
        )

def fakedata():
    simu.fakedata()
    simu.test()


url_map = Map( [ Rule( '/'+what.name, endpoint= what )
    for what in iface.methods_walk_instance( iface) ]
    + [ Rule( '/', endpoint= lister),
        #Rule( '/save', endpoint= simu.data_save ),
        #Rule( '/load', endpoint= simu.data_load ),
        Rule( '/gen',  endpoint= fakedata ),
    ] )

htmlized = 'query_itemalert'.split()

class aRequest( Request):
    parameter_storage_class = ImmutableDict     #?x=1&x=2 -> x=2

def item2html( i, params, is_html=0, is_dbg=0):
    s = sorted( i.items() )
    t = [ '']
    t += [ k+': '+unicode(v) for k,v in
            [ kv for kv in s if kv[0]=='title' ] +
            [ kv for kv in s if kv[0]!='title' ]
        ]
    if 'itemi' in i:
        q = dict( (k,v) for k,v in params.items() if v is not None )
        q.update( item= i.key, grouped= 'kids', )
        if is_html: q.update( html=1)
        if is_dbg: q.update( dbg=1)
        q = '&'.join( k+'='+str(v) for k,v in sorted( q.items()))
        t += [ '<a href="query_itemalert?' +q+ '"> inside </a>' ]
    t = '\n<p> '.join( t)
    return t


@aRequest.application
def app( request):
    handler, values = url_map.bind_to_environ( request.environ ).match()
    #params = dict( request.values)
    params = dict( request.form or request.args)
    if callable( handler):
        name = handler.__name__
        meta = None
    else:
        meta = handler
        handler = meta.impl
        name = meta.name
        is_html = bool( params.pop( 'html', None))

    is_dbg = bool( params.pop( 'dbg', None))
    is_txt = bool( params.pop( 'txt', None))
    adbg = dict( req= name +' '+ str(params), url= request.url )
    tdbg = [ k+': '+v for k,v in sorted( adbg.items()) ]

    try:
        if meta:
            params = meta.decl.validate( params, meta.face, meta.name)
        simu.data_load()
        if simu.data_is_empty(): fakedata()
        #if is_html and name in htmlized:
        #    params.update( _html= True)
        r = handler( **params)
    except RuntimeError, e:
        return Response( '\n'.join( ['! '+str(e) ] + tdbg ), status=400 )
    simu.data_save()
    if isinstance( r, Response): return r
    ctype = 'text/plain'
    if is_txt:
        r = unicode(r)
        if is_dbg:
            r = '\n'.join( tdbg + [r] )
    elif is_html and name in htmlized:
        if isinstance( r, list):
            x = []
            for i in r:
                if isinstance( i, dict):
                    t = item2html( i, params, is_html=is_html, is_dbg=is_dbg)
                else:
                    t = unicode( i)
                x.append( t )
            r = '\n<hr>\n'.join( x)
        elif isinstance( r, dict):
            r = item2html( r, params, is_html=is_html, is_dbg=is_dbg)
        else:
            r = unicode( r)
        if is_dbg:
            r = '\n<br> '.join( tdbg + ['<hr>', r] )
        ctype = 'text/html'
        r = '''<html><head>
<style TYPE='text/css'><!--
 p { text-indent:1em;  margin:0 }
--></style>
</head><body>
''' + r
    else:   #json
        #if isinstance( r, (list,tuple, dict)):
        if is_dbg:
            adbg[ 'result' ] = r
            r = adbg
        r = json_dumps( r, indent=2)
        #ctype = 'text/json'
    #print datetime.datetime.now(), dbg+r
    r = Response( r, content_type= ctype )
    r.cache_control.nocache = True
    return r

if __name__ == '__main__':
    from svd_util import optz, eutf
    eutf.fix_std_encoding()
    optz.int( 'port', default= 5000,        help='[%default]' )
    optz.str( 'host', default= 'localhost', help='[%default]' )
    optz.bool( 'load', help= 'load saved data' )
    optz.bool( 'gen',  help= 'make fake data' )
    optz.bool( 'noautogen',  help= 'dont make fake data if nothing loaded' )
    optz.bool( 'save', help= 'save data at end' )
    optz.bool( 'notest', help= 'dont run test before serving' )
    optz,args = optz.get()

    if optz.argus: argus()

    if optz.load: simu.data_load()
    if optz.gen or simu.data_is_empty() and not optz.noautogen: simu.fakedata()
    if not optz.notest: simu.test()
    try:
        run_simple( optz.host, optz.port, app, use_debugger= True, use_reloader= True)
    finally:
        if optz.save: simu.data_save()

# vim:ts=4:sw=4:expandtab
