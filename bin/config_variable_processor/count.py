
def count( parser, *args ):
    if len( args ) < 1:
        raise Exception( 'Insufficient arguments.' )

    if len( args ) == 2:
        sep = args[1]
    else:
        sep = ','

    return len( args[0].split( sep ) )
