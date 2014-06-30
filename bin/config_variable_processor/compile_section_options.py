
def compile_section_options( parser, *args ):
    if len( args ) < 1:
        raise Exception( 'Insufficient arguments.' )

    target_section = args[0]

    if len( args ) == 2:
        sep = args[1]
    else:
        sep = ','

    if not parser.has_section( target_section ):
        return 'none'

    all_options = []

    for name, value in parser.items( target_section ):
        if '%(' in value or '|(' in value:
            raise Exception( 'Not all options in destination section have been parsed.' )
        all_options.append( "%s=%s" % ( name, value ) )

    all_options.sort()

    if not len( all_options ):
        return ''
    else:
        return sep.join( all_options )
