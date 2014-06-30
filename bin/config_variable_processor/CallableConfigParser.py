
import ConfigParser, re

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

class CallableConfigParser( ConfigParser.ConfigParser ):

    file_cache = {}
    
    FUNC_PATTERN = re.compile(r"\|\( ?([^ ]*) (.*)\)")
    
    def __init__(self, funcs = {}, *args, **kwargs ):
        ConfigParser.ConfigParser.__init__( self, *args, **kwargs )
        
        self.funcs = funcs
        
    def get(self, section, option, raw=False, vars=None):

        all_vars = {}
        if vars:
            all_vars.update( vars )

        for i in range( ConfigParser.MAX_INTERPOLATION_DEPTH ):
            all_vars.update( dict( ConfigParser.ConfigParser.items( self, section, raw, all_vars ) ) )

        return all_vars[ option ]

    def items(self, section, raw=False, vars=None):

        all_vars = {}
        if vars:
            all_vars.update( vars )

        for i in range( ConfigParser.MAX_INTERPOLATION_DEPTH ):
            all_vars.update( dict( ConfigParser.ConfigParser.items( self, section, raw, all_vars ) ) )

        return all_vars.items()

    def _interpolate(self, section, option, rawval, vars):
        #print vars
        #print '%s %s %s' % ( section, option, rawval )
        try:
            value = ConfigParser.ConfigParser._interpolate( self, section, option, rawval, vars )
        except ( ConfigParser.InterpolationMissingOptionError, ConfigParser.InterpolationDepthError ):
            value = rawval

        #print 'option %s' % option
        #print 'rawval %s' % rawval
        #print 'value %s' % value
        if re.search( r"\|\( ?[^ ]* +.*\|\(.*\).*\)", value ):
            value = rawval

        #print 'value2 %s' % value

        def func_sub( match ):
            func_name = match.group(1)
            func_args = match.group(2)

            if func_name is None:
                return match.group()

            #print 'func_name %s' % func_name
            #print 'func_args %s' % func_args

            error_string = '|( %s %s)' % ( func_name, func_args )                                                                                                                                                                                                              

            if '%(' in func_args or '|(' in func_args or not func_name in self.funcs:
                return error_string

            #print 'call func'
            processed_args = list( arg.strip('"') for arg in func_args.split() )
                                                                                                                                                                                                                                                                               
            try:                                                                                                                                                                                                                                                               
                value = self.funcs[ func_name ]( self, *processed_args )                                                                                                                                                                                                       
            except:                                                                                                                                                                                                                                                            
                return error_string

            return str( value )
            
        func_value = value
        value = self.FUNC_PATTERN.sub( func_sub, func_value )

        #print 'value3 %s' % value
        #print

        return value

    def _read( self, fp, filename ):
        #print filename

        processed_fp = fp

        if not filename in self.__class__.file_cache:
            #print 'not cached'
            new_fp = StringIO.StringIO()
            new_fp.writelines( processed_fp.readlines() )

            self.__class__.file_cache[ filename ] = new_fp
            processed_fp.seek( 0 )
        else:
            #print 'cached'
            processed_fp = self.__class__.file_cache[ filename ]
            processed_fp.seek(0)

        ConfigParser.ConfigParser._read( self, processed_fp, filename )

    def optionxform(self, optionstr):                                                                                                                                                                
        return optionstr
