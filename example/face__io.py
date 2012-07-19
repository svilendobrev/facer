#$Id$
'example intarface declarations'

from facer import Types, MTypes, Types_auto, optional, Method, FaceDeclaration

class Types( Types):
    @staticmethod
    def bool(x):    #on,true,number>0
        return isinstance( x,basestring) and x.lower() in ('on', 'true') or bool(int(x))
    int = int
    text = unicode

class IOFace_base( FaceDeclaration):
    class Types( Types):
        program     = int
        rprogram    = Types.text_stream
        rprograms   = Types.text_stream
        limit       = int

class IOFace_Images( IOFace_base):
    class Types( IOFace_base.Types):
        image_name  = Types.text
        channel     = Types.intplus
        image       = Types.text_stream
    MTypes = MTypes( Types)
    program_image   = Method( program = MTypes.image_name ).returns( MTypes.image)
    channel_logo    = Method( channel = MTypes.channel ).returns( MTypes.image)

class IOFace_Storage( IOFace_Images):
    class Types( IOFace_base.Types):
        channel     = Types.intplus
        filter      = str
        rbchannels  = Types.text_stream

        meta_id     = int
        rmeta       = Types.text_stream

    MTypes = MTypes( Types)

    #broadcast
    broadcast_channels  = Method().returns( MTypes.rbchannels)
    program_details     = Method(   program = MTypes.program,).returns( MTypes.rprogram)
    programs_by_filter  = Method(   filter  = MTypes.filter,
                                    limit   = optional( MTypes.limit)
                                    ).returns( MTypes.rprograms)
    #metadata
    getGenre        = Method( id= MTypes.meta_id ).returns( MTypes.rmeta)


class IOFace_Programs( IOFace_base):
    class Types( IOFace_base.Types):
        pchannel= str
        rate    = int, Types.minmax(-2,+2)
        rpchannel   = Types.text_stream
        rpchannels  = Types.text_stream
    MTypes = MTypes( Types)

    channels        = Method().returns( MTypes.rpchannels)
    new_channel     = Method(   name    = MTypes.text,
                                    program = optional( MTypes.program),
                                ).returns( MTypes.rpchannel )
    save_channel    = Method(   channel   = MTypes.pchannel,
                                    name      = MTypes.text,
                                    is_news   = optional( MTypes.bool),
                                    size      = optional( MTypes.int),
                                ).returns( MTypes.rpchannel )
    del_channel     = Method(   channel = MTypes.pchannel)

    programs        = Method(    channel = MTypes.pchannel,
                            limit = optional( MTypes.limit)
                        ).returns( MTypes.rprograms)
    add_program     = Method( channel = MTypes.pchannel, program = MTypes.program)
    del_program     = Method( channel = MTypes.pchannel, program = MTypes.program)


class IOFace( IOFace_Storage, IOFace_Programs):
    pass

class IO( IOFace, IOFace_Images):   #all of it
    pass

if __name__ == '__main__':
    from facer import test
    test()

# vim:ts=4:sw=4:expandtab
