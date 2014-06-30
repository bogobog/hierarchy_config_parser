
def range_list( parser, *args ):
    if len( args ) < 2:
        raise Exception( 'Insufficient arguments.' )

    if len( args ) == 3:
        sep = args[2]
    else:
        sep = ' '

    items = list( str( i ) for i in range( int( args[0] ), int( args[1] ) + 1 ) )
    return sep.join( items )
