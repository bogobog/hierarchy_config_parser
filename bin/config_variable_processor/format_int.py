
def format_int( parser, *args ):

    if len( args ) < 2:
        raise Exception( 'Insufficient arguments.' )

    format_pattern = '%%%s' % args[0]
    int_value = int( args[1] )

    return str( format_pattern % int_value )
