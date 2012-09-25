# -*- coding: utf-8 -*-

'simulator of web-API. served via werkzeug'

import webform

import werkzeug
from werkzeug.wrappers import Request, Response
#from werkzeug.wsgi import responder
from werkzeug.routing import Map, Rule
from werkzeug.serving import run_simple
from werkzeug.datastructures import ImmutableDict #, ResponseCacheControl

try: from json import dumps as json_dumps
except ImportError:
    from simplejson import dumps as json_dumps

class websimu:

    iface = None #the actual simulator as face-instance
    title = 'dobr-e test simulator'

    ROOT = ''
    ENDSLASH = False
    @classmethod
    def lister( me, html =False):
        hidden_fields = dict( dbg=1)
        if html: hidden_fields.update( html=1)
        return Response( webform.html( me.iface,
            title   = me.title,
            root    = me.ROOT,
            hidden_fields = hidden_fields,
            endslash = me.ENDSLASH,
            help    = '''\
default simulator result is json (as text/plain, not application/json).
url-param dbg=1 makes a dict( req, url, result=..) - all links above are this way.
url-param txt=1 makes a python repr, not json
''' ),
            content_type = 'text/html',
            )

    @classmethod
    def fakedata( me):
        raise NotImplementedError
    @classmethod
    def load( me):
        raise NotImplementedError
    @classmethod
    def save( me):
        raise NotImplementedError

    @classmethod
    def setup( me, rules =()):
        me.url_map = Map(
            [ Rule( '/'+what.name, endpoint= what.impl )
            for what in me.iface.methods_walk_instance( me.iface) ]
            + [ Rule( '/', endpoint= me.lister),
                #Rule( '/save', endpoint= simu.data_save ),
                #Rule( '/load', endpoint= simu.data_load ),
                Rule( '/gen',  endpoint= me.fakedata ),
            ] + [ Rule( u, endpoint=f) for u,f in rules
            ] )

    htmlized = []

    @classmethod
    def item2html( me, i, params, is_html=0, is_dbg=0):
        s = sorted( i.items() )
        t = [ '']
        t += [ k+': '+unicode(v) for k,v in s ]
        return '\n<p> '.join( t)

    @staticmethod
    def _clone( params, **boolkargs):
        q = dict( (k,v) for k,v in params.items() if v is not None )
        q.update( (k,1) for k,v in boolkargs.items() if v)
        return q

    class aRequest( Request):
        parameter_storage_class = ImmutableDict     #?x=1&x=2 -> x=2

    @classmethod
    @aRequest.application
    def app( me, request):
        print me.url_map
        handler, values = me.url_map.bind_to_environ( request.environ ).match()
        #params = dict( request.values)
        params = dict( request.form or request.args)
        if callable( handler):
            name = handler.__name__
            meta = None
            is_html = False
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
            me.load()
            #if is_html and name in htmlized:
            #    params.update( _html= True)
            r = handler( **params)
        except RuntimeError, e:
            return Response( '\n'.join( ['! '+str(e) ] + tdbg ), status=400 )

        me.save()
        if isinstance( r, Response): return r

        ctype = 'text/plain'
        if is_txt:
            r = unicode(r)
            if is_dbg:
                r = '\n'.join( tdbg + [r] )
        elif is_html and name in me.htmlized:
            if isinstance( r, list):
                x = []
                for i in r:
                    if isinstance( i, dict):
                        t = me.item2html( i, params, is_html=is_html, is_dbg=is_dbg)
                    else:
                        t = unicode( i)
                    x.append( t )
                r = '\n<hr>\n'.join( x)
            elif isinstance( r, dict):
                r = me.item2html( r, params, is_html=is_html, is_dbg=is_dbg)
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

    import simu     #contain the simulator-instance and these:
    if 0:
        simu.fakedata()
        simu.test()
        simu.data_is_empty()
        simu.data_load()
        simu.data_save()

    class websimu1( websimu):
        iface = simu.simu   #the actual simulator as face-instance

        @classmethod
        def fakedata( me):
            simu.fakedata()
            simu.test()
        @classmethod
        def load( me):
            simu.data_load()
            if simu.data_is_empty(): me.fakedata()
        @classmethod
        def save( me):
            simu.data_save()
        htmlized = 'query_itemalert'.split()

        @classmethod
        def item2html( me, i, params, is_html=0, is_dbg=0):
            s = sorted( i.items() )
            t = [ '']
            t += [ k+': '+unicode(v) for k,v in
                    [ kv for kv in s if kv[0]=='title' ] +
                    [ kv for kv in s if kv[0]!='title' ]
                ]
            if 'itemi' in i:
                q = me._clone( params, is_html=is_html, is_dbg=is_dbg)
                q.update( item= i.key, grouped= 'kids', )
                q = '&'.join( k+'='+str(v) for k,v in sorted( q.items()))
                t += [ '<a href="query_itemalert?' +q+ '"> inside </a>' ]
            t = '\n<p> '.join( t)
            return t


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

    websimu1.setup()
    try:
        run_simple( optz.host, optz.port, websimu1.app, use_debugger= True, use_reloader= True)
    finally:
        if optz.save: simu.data_save()

# vim:ts=4:sw=4:expandtab
