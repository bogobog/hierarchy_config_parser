
def add( parser, *args ):
    if len( args ) < 2:
        raise Exception( 'Insufficient arguments.' )

    return str( int( args[0] ) + int( args[1] ) )
