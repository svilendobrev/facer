facer
=====

interface/protocol/API declaration language (www or not). Methods, arguments, results -
types, cardinality, optionality; inheritance, specialization, cloning. Use
visitors to do/generate all else.

svilen.dobrev 2010

    methoddecl: name, argdecls, returns, features
    argdecl:    name, type/converter, optional/defaultvalue

abstract faces cannot be instantiated - only faces with fully all methods implemented

WARNING/TODO: implementation methods are NOT checked for compliance with the declaration

example:

```
class ChannelFace( FaceDeclaration):     #pure declaration - abstract face
    class Types( Types):
        channel = Types.intplus
        rate    = int, Types.minmax(-2,+2)

    new_channel = Method(   name = optional( Types.text)
                            ).returns( Types.channel)
    del_channel = Method( channel = Types.channel ).returns( bool)

class MoreChannelFace( ChannelFace):  #implementing one method, declaring one more - still abstract
    class Types( ChannelFace.Types):
        program = str
    like_program= Method(   program = Types.program,
                            dislike = optional( bool, False)
                        )
    def del_channel( me, channel):
        return me.doer.channel_delete( channel)

class TheChannelFace( MoreChannelFace):  #implementing all methods
    def new_channel( me, program, name =None, **kargs): ...
    def like_program( me, program, dislike =False): ...
```

see example/ directory :

 * requester.py : method-wrapper as web-view
 * webform.py   : render a facer into HTML-page of form-per-method
 * websimu.py   : simulator of web-API, using webform. served via werkzeug
 * face4django.py: links (a missing) implementation with django
