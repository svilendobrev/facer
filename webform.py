# -*- coding: utf-8 -*-

'render facer-API as HTML page with form-per-method'

#TODO abandon textual html, use some of dirty or forgetHTML, or some else

from facer import url_doco, Types
import cgi

js2remove_empty_form_fields = '''
<script language="javascript">
 function valform( aform) {
  var i,e;
  for (i=aform.elements.length; i--; ) {
    e = aform.elements[i];
    e.disabled = (e.value=='');
  }
 }
 function subform( aform) {
  valform( aform);
  aform.submit();
  var i;
  for (i=aform.elements.length; i--; )
    aform.elements[i].disabled=false;
 }
</script>
'''

nbsp = '&nbsp; '

def form( decl, root ='', target ='out', textedit_size =18, remove_empty_form_fields =True,
            hidden_fields ={}, errors= None, endslash =False, with_doc =False):
    returns = decl._returns and cgi.escape( str( decl._returns))
    inputs = decl.sorted_inputs()
    #errors = errors.get( decl.name) if errors else None
    errors = decl._errors
    if 0:
        import dirty.html as h
        import dirty
        ''' -way for element.children.append/extend - e.g. +=... or (...)
            -list of sublists
        '''
        hbr = h.br()
        hsp = dirty.RawString( nbsp )

        br = len(inputs)>1 and hbr or None
        f = h.form( dict( target=target, action= root+decl.name),
            h.input( type='submit', value=decl.name), ' returns: '+str( decl._returns),
            h.input( type='hidden', name='dbg', value=1),
            )
        for name,type in decl.sorted_inputs():
            f.children += [ br, hsp, hsp,
                            name+'=', h.input( name=name, value='', size=textedit_size),
                                h.font( str(type), size=-2),
                          ]
        return str(f)
    if 0:
        import forgetHTML as h

    sendbutton = remove_empty_form_fields and '''
        <input type=button value="{decl.name}" onclick="subform( document.forms.{decl.name} )">
        ''' or '''
        <input type=submit value="{decl.name}">
        '''

    for name,type in inputs:
        if type.type.type is list:
            method = 'POST'
            break
    else:
        method = 'GET'

    endslash = endslash and '/' or ''
    r = '''
 <form name={decl.name} target={target} method="{method}" action="{root}{decl.name}{endslash}" >
 <table width=100% border=0 cellspacing=0><tr><td width=30%>
  ''' + sendbutton
    if returns: r += '''
  <br><b> returns:</b> {returns}'''

    if errors:
        ee = []
        errs = [ e.message or str(e) for e in errors if e.err]
        if errs: ee += ['<b> errors:</b>'] + errs
        noerrs = [ e.message +': ' + e.noerror for e in errors if not e.err]
        if noerrs: ee += [ '<b> noerrors:</b>'] +  noerrs
        r += ''.join( '<br>'+e for e in ee)
        if 0:
            if isinstance( errors, dict):
                errors = '<br>' + '<br>'.join([ code +':'+ txt for code,txt in errors.iteritems() ])
            elif isinstance( errors, (tuple,list)):
                errors = ', '.join( str(e) for e in errors)
    r = r.format( **locals())
    r += '\n<td>\n'
    if with_doc and decl.doc: r += '<i> '+cgi.escape( decl._doc )+'</i><br>\n'
    r += '\n'.join(
        '<input type=hidden name='+k+' value='+str(v)+'>'
        for k,v in hidden_fields.items()
        )
    ri = []
    for name,type in inputs:
        i = name+ '= '
        choices = getattr( type.type, 'choices', None)
        if choices: choices = choices()
        if choices is not None: #isinstance( type.type, Types.enum):
            fdheight = 0
            i += '<select name="' +name+'" '
            if fdheight: i += ' size='+str(fdheight)
            i += '>'
            for k in sorted( choices ):
                i += '\n <option'
                if k == type.default_value: i+= ' selected'
                #value=
                i+='> '+k+'</option>'
            i += '\n</select>'
        else:
            i += '<input name="' +name+ '" '
            if type.type.type is bool:
                i += 'type=checkbox value=1>'
            else:
                i += 'value="" size='+str(textedit_size)+'>'
        ri.append( i + ' ' + cgi.escape( str(type) ) )

    return r + '\n<br> '.join( ri) + '''
  </table>
 </form>'''

def ahref( url, txt =None, target ='', button= False, root =''):
    txt = cgi.escape( txt or url)
    if target: target= 'target='+target
    if button:  h= '<form action="{root}{url}" {target}> <input type=submit value="{txt}"> </form>'
    else:       h= '<a href="{root}{url}" {target}> {txt}</a>'
    return h.format( **locals())
def button( *a,**k): return ahref( button=True, *a,**k)

# <meta http-equiv="pragma" content="no-cache">
# <meta http-equiv="expires" content="-1">

def html( iface, title ='simulator', help ='', root ='',
        target ='out',
        remove_empty_form_fields =True,
        sorter =lambda x: x,
        **kargs ):
    base = root
    r = ('''\
<html><head>
<title> {title} </title>
''' + (base and '<base href="{base}" target="{target}" >' or '')).format( **locals()) + '''
<style TYPE='text/css'><!--
 * { font-size:small }
 form { margin:0 }
 hr { margin:1px }
--></style>
''' + (remove_empty_form_fields and js2remove_empty_form_fields or '') + '''
</head>

<body>
<table width=100% height=95% border=0 cellspacing=0><tr><td width=50%>
  <div style="overflow:auto; height:100%;">
''' + '\n<hr>'.join(
        form( what.decl, target= target, remove_empty_form_fields=remove_empty_form_fields, **kargs)
        for what in sorter( iface.methods_walk_instance( iface))
) + '''
 </div>
 <td height=100%> <iframe name=out width=100% height=100%> no-iframe? </iframe>
</table>
'''
    if help: r += '<hr>' + '\n<br>'.join( help.strip().split('\n'))
    urls = [cgi.escape( x) for x in url_doco( iface, sepattrs=' ; ') ]
    return r + '''
<hr>
<b>Valid URLs</b>:<br>
''' + '\n<br>'.join( urls)

#''' + '\n &nbsp; '.join( ahref( n,u) for n,u in buttonsurl) + '''


if __name__ == '__main__':
    from svd_util import optz
    optz.str( 'root', help= 'root/base url')
    optz.str( 'title', )
    optz.bool( 'dont_remove_empty_form_fields', )
    optz,args = optz.get()
    #from simu import simu as f
    from face__io import IO as f
    print html( f, **dict( (k,v) for k,v in optz.__dict__.items() if v))

# vim:ts=4:sw=4:expandtab
