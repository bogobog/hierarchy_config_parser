
import re

def replace( parser, *args ):

    #print "blah"
    #print args

    if len( args ) < 3:
        raise Exception( 'Insufficient arguments.' )

    source = args[0]
    regex = args[1]
    replacement = args[2]

    match = re.search( '(.*)%s(.*)' % regex, source )
    
    if not match:
        return source

    group1, group2 = match.group( 1, 2 )
    new_string = "%s%s%s" % ( group1, replacement, group2 )

    return new_string
