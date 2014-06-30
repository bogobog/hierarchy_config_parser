
def iterate( parser, *args ):

    if len( args ) < 2:
        raise Exception( 'Insufficient arguments.' )

    port_list = args[0].split(',')
    target_index = int( args[1] )

    if len( port_list ) < 1:
        raise Exception( 'Source list is empty.' )

    if len( port_list ) < target_index:
        return port_list[0]

    return port_list[ target_index - 1 ]
