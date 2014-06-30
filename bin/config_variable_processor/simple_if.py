
def simple_if( parser, *args ):
    if len( args ) < 3:
        raise Exception( 'Insufficient arguments.' )

    if eval( args[0] ):
        return args[1]
    else:
        return args[2]
