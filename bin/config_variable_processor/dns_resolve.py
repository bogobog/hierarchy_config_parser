
def dns_resolve( parser, *args ):

    if len( args ) < 1:
        raise Exception( 'Insufficient arguments.' )

    hostname = str( args[0] )

    hostname_list = hostname.split( ',' )
    resolved_ip_list = []

    try:
        import socket
        for hst in hostname_list:
            hostname, aliaslist, ipaddrlist = socket.gethostbyname_ex( hst )
            resolved_ip_list.append( ipaddrlist[0] )

        return ','.join( resolved_ip_list )
    except:
        return args[0]
