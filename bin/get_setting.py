#!/usr/bin/env python

import os, sys, config_variable_processor

class GetSettingsInvalidTierOption( Exception ): pass

DEFAULT_CONFIG_DIR = "%s/.." % os.path.dirname( os.path.abspath( __file__ ) )

def list_tier( tier, config_dir = DEFAULT_CONFIG_DIR ):
    tier_dir = '%s/variables/%s' % ( config_dir, tier )

    return list( entry[0:-3] for entry in os.listdir( tier_dir ) if os.path.isfile( '%s/%s' % ( tier_dir, entry ) ) and entry[-3:] == '.db' )

def get_variable_heirarchy( config_dir = DEFAULT_CONFIG_DIR ):
    service_config = config_variable_processor.CallableConfigParser( funcs = config_variable_processor.func_dict )
    service_config.readfp( open( '%s/variables/config.ini' % config_dir ) )

    if not 'variable_heirarchy' in service_config.sections():
        raise Exception( 'Variable heirarchy not found in global config.' )
        
    var_heirarchy = []
    for name, pos in sorted( service_config.items( 'variable_heirarchy' ), lambda x, y: cmp( int( x[1] ), int( y[1] ) ) ):
        var_heirarchy.append( name )

    return var_heirarchy

def get_config_files( base, tier, ltiers, options ):
    my_files = []
    my_files.append( '%s.db' % base )
    my_files.append( '%s/%s.db' % ( base, options[tier] ) )

    for i in range( len( ltiers ) ):
        this_tier = ltiers[i]
        lower_tiers = ltiers[0:i]

        if this_tier in options and options[ this_tier ]:
            my_files.append( get_config_files( '%s/%s/%s' % ( base, options[tier], this_tier ), this_tier, lower_tiers, options ) )

    return my_files
            
def flatten( x ):
    result = []
    to_flatten = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            to_flatten.append( el )
        else:
            result.append(el)

    for l in to_flatten:
        result.extend( flatten( l ) )

    return result

def get_service_config( var_heirarchy, options, config_dir = DEFAULT_CONFIG_DIR ):
    config_files = [ '%s/variables/global.db' % config_dir ]

    for i in range( len( var_heirarchy ) ):
        this_tier = var_heirarchy[i]
        lower_tiers = var_heirarchy[0:i]

        if this_tier in options and options[ this_tier ]:
            config_files.append( get_config_files( '%s/variables/%s' % ( config_dir, this_tier ), this_tier, lower_tiers, options ) )

    config_files = flatten( config_files )

    service_config = config_variable_processor.CallableConfigParser( funcs = config_variable_processor.func_dict )
    service_config.read( config_files )

    return service_config

def get_settings( **kwargs ):

    options = kwargs

    if not 'config_dir' in options:
        options['config_dir'] = DEFAULT_CONFIG_DIR

    var_heirarchy = get_variable_heirarchy( options['config_dir'] )

    for tier in options:
        if not tier in var_heirarchy:
            continue

        tier_opt = options.get( tier )
        if tier_opt:
            tier_list = list_tier( tier, config_dir = options['config_dir'] )
            if not tier_opt in tier_list:
                raise GetSettingsInvalidTierOption( '%s "%s" was not found.' % ( tier, tier_opt ) )

    service_config = get_service_config( var_heirarchy, options, config_dir = options['config_dir'] )

    default_vars = {}
    if 'instance' in options and options['instance']:
        default_vars['this_instance'] = str( options['instance'] )

    if 'iteration' in options and options['iteration']:
        default_vars['this_iteration'] = str( options['iteration'] )

    if 'process_dependencies' in options and options['process_dependencies']:
        if 'meta:hierarchical_dependencies' in service_config.sections():
            new_options = {}
            for name, value in service_config.items( 'meta:hierarchical_dependencies' ):
                if not options.get( name, None ) and name in var_heirarchy:
                    new_options[name] = value

            if len( new_options ):
                options.update( new_options )
                service_config = get_service_config( var_heirarchy, options, config_dir = options['config_dir'] )

    all_settings = {}

    if service_config.has_section( 'global' ):

        setting_dict = default_vars
        setting_dict = dict( service_config.items( 'global', vars = setting_dict ) )

        all_settings['global'] = setting_dict

    for section in service_config.sections():

        if section == 'global' or len(section) > 5 and section[0:5] == 'meta:':
            continue

        setting_dict = {}
        setting_dict = dict( service_config.items( section, vars = all_settings['global'] ) )

        section_options = service_config.options( section )

        all_settings[section] = dict( ( item, value ) for item, value in setting_dict.items() if item in section_options )

    return all_settings

if __name__ == '__main__':
    command = sys.argv[0]
    cmd_options = sys.argv[:]

    from optparse import OptionParser

    parser = OptionParser( add_help_option = False )
    parser.add_option( "-h", "--help", action = 'store_true', dest='help', )
    parser.add_option( "-d", "--config_dir", dest='config_dir', default = DEFAULT_CONFIG_DIR )
    parser.add_option( "-C", "--section", dest='requested_section', )
    parser.add_option( "-S", "--setting", dest='requested_option', )
    parser.add_option( "-i", "--instance", dest='instance', )
    parser.add_option( "-r", "--iteration", dest='iteration', )
    parser.add_option( "-H", "--process_dependencies", action='store_true', dest='process_dependencies', )
    parser.add_option( "", "--pretty", action='store_true', dest='pretty_output', default = False )
    parser.add_option( "", "--json", action='store_true', dest='json_output', default = False )

    old_error = parser.error
    parser.error = lambda a: True

    ( options, args ) = parser.parse_args( args = cmd_options )

    parser.error = old_error

    var_heirarchy = get_variable_heirarchy( options.config_dir )
    for tier in var_heirarchy:
        parser.add_option( "--%s" % tier, dest='%s' % tier, default = None )

    ( options, args ) = parser.parse_args( args = cmd_options )

    if options.help:
        parser.print_help()
        sys.exit() 

    get_settings_params = {}
    get_settings_params[ 'config_dir' ] = options.config_dir
    get_settings_params[ 'instance' ] = options.instance
    get_settings_params[ 'iteration' ] = options.iteration
    get_settings_params[ 'process_dependencies' ] = options.process_dependencies

    for tier in var_heirarchy:
        get_settings_params[ tier ] = getattr( options, tier )

    try:
        result = get_settings( **get_settings_params )
    except Exception, e:
        print 'Error: %s' % e
        sys.exit( 1 )

    if not result:
    	sys.exit( 1 )

    requested_section = getattr( options, 'requested_section', None )
    requested_option = getattr( options, 'requested_option', None )

    output = result

    if requested_section:
        try:
            output = result[ requested_section ]
        except KeyError:
            sys.exit( 2 )

    if requested_option:
        try:
            output = result[ ( requested_section and requested_section ) or 'global' ][ requested_option ]
        except KeyError:
            sys.exit( 2 )

    if options.json_output:
        try:
            import json
        except ImportError:
            import simplejson as json
        print json.dumps( output )
    elif options.pretty_output:
        import pprint
        pprint.pprint( output )
    else:
        print output
