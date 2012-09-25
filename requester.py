
'wrap facer.methods into http-view-handlers'

if 0:
    def declmethod4user( **ka):
        return Method( **ka).features( 'useridentified')

#some django stuff
#from rpc.views import HttpResponse, checklogin

# using any IOFace_ instance, + eventualy replace arg-types, + auto arg validation
#TODO assert face-conformity
#TODO argument validation/conversion XXX
#TODO: useridentified, faceing without inheritance, reinterpret( Types)

class requester:
    'method wrapper into web-view'

    HttpResponse = None #..
    DOLOGIN = True #always require login - ignore .useridentified or not

    @property
    def NOLOGIN( me): return not me.checklogin

    def __init__( me, instmethod_meta, face =None, as_generator =False, result_is_tuple =True, checklogin =None):
        assert instmethod_meta.impl, 'no implementation: '+str(instmethod_meta)
        me.as_generator = as_generator
        me.result_is_tuple = result_is_tuple
        me.meta = instmethod_meta
        me.face = face
        me.checklogin = checklogin
        if me.NOLOGIN or not me.DOLOGIN and 'useridentified' not in me.meta.decl._features:
            me.__call__ = me.handle

    def handle_login( me, request, **kargs):
        r = me.checklogin( request)
        print '??TH USER:', getattr( request, 'COOKIES', 'nocookie')
        if r is not None: return r
        #print 'AUTH USER:', request.user
        return me.handle( request, **kargs)

    def handle( me, request, **kargs):
        meta = me.meta
        if meta.impl is None:
            raise RuntimeError( 'not implemented method: ' + meta.decl.str( meta.face, meta.name))
        params = request.POST or request.GET
        params = meta.decl.validate( params, meta.face, meta.name)
        kargs.update( params)
        return me._handle( request, meta, kargs)

    def _handle( me, request, meta, kargs):
        print meta.name, 'as_generator=', me.as_generator, 'result_is_tuple=', me.result_is_tuple, kargs
        if me.as_generator:
            return me.HttpResponse( (data for ok,data in meta.impl( as_generator=True, **kargs) if ok) )

        try:
            r = meta.impl( **kargs)
        except:
            print 55555555, meta.name, meta.impl
            raise
        #print 'rrrrrrrrrrr', r
        if me.result_is_tuple:
            http_ok, data = r
        else: data = r
        if isinstance( data, me.HttpResponse): return data
        return me.HttpResponse( data)

    __call__ = handle_login     #default

    def __str__( me):
        return 'requester'+':'+ str( me.meta.impl)
    __repr__ = __str__


def url4webpy( face, requester, face_subset =None):
    face_subset = face_subset or face
    pfx = getattr( face, 'name4url', '')
    if pfx: pfx+= '/'
    return [ ('^'+pfx +what.name, requester( what, result_is_tuple= False, as_generator= False))
            for what in face_subset.methods_walk_instance( face) ]

# vim:ts=4:sw=4:expandtab
