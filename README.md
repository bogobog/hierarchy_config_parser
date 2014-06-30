hierarchy_config_parser
=========================================

Hierarchy-enforced Extended Config Parser

This set of scripts is an expansion of the Python 2.6 ConfigParser module.  It is used to define a hierarchy of config domains which are then compiled in turn to develop a final set of key-value pairs.  These scripts were developed because my organization had a need to manage a base set of config files for interdependent services.  However, these service were frequently deployed into slightly different fault domains that each required slightly different configs.  For instance, two deployments of the same backend web service ( eg, tomcat ) would require configs that references different database host names.  This requirement moved us in the direction of templatized config files that were interpolated when they were compiled and packaged in fault domain specific packages.  

The organization also had a need to track and audit when what changes happened to what fault domains and whom commited those changes.  This hierarchical system which allowed us to split you domain specific config values into separate files allowed us to easily check the entire config state into git.  This provided all of the auditing capabilities that we needed.

These scripts were developed on RHEL6 hosts under Python 2.6.  I have been able to execute them with success on Python 2.7 but I have not tested them on Python 3.

I am providing these scripts as a means to one perspective on how to solve the problems described above.  I would be surprised to find that a group outside of my organization was able to take these scripts without modification and use them effectively in their own environments.  By providing these scripts, I hope that I may be able to grant some insight to those looking to solve similar issues on whether or not methods similar to my own could be effective.

# Requirements #

Python 2.6/2.7

# Usage #

Basic usage of this system requires a user to establish a hierarchy of config tiers and then populate those tiers with config variables.  The directory structure is important to the default operation of the provides scripts. However, it should be simply to change the location of the default variables directory and the get_settings.py script accepts options which change the used directory at run time.

The current directory structure looks like this:

```
./bin
./bin/config_variable_processor
./variables
```

The `bin` dir is home to the get_settings.py script which is the script used to compile and return the full, interpolated settings.

The `bin/config_variable_processor` dir is home to the CallableConfigParser class and its plugins.

The `variables` dir is the base dir for the setting hierarchy.

The CallableConfigParser is an class derived from the standard library ConfigParser class.  The CallableConfigParser class extends the interpolation capabilities of its base class by adding the ability to call subroutines for resolving setting values.  I have included the basic set of subroutines that my organization has found useful.

To establish the config hierarchy, update the `config.ini` file under the `variables` dir with a set of tier definitons.

The `config.ini` file:
```
[variable_heirarchy]
service_tier=1
service=2
datacenter=3
env=4
```

This setup defines four levels.  The first is `service_tier` and the last is `env`.  When compiling the settings, the levels will be evaluated in ascending order.  This means that `service_tier` will be evaluted first and `env` will be evaluated last.  As levels are evaluated, any setting values from a higher level will overwrite setting values from a lower level.

Before any level within the heirarchy is evaluated, the get_settings.py script will evaluate a `global.db` file if found in the `variables` dir.  Settings defined in the global.db will also be included.

The `global.db` file.
```
[global]
global_setting_1=global_value_1
global_setting_2=global_value_2
```

This `global.db` defines a section named `global` and two settings.  Though you can define as many sections as you like, values will only be interpolated across settings within the same sections.  If you define a `section1` and a `section2`, `section1` will not have access to settings and values defined in `section2` and vice versa.  However, the `global` section is handled especially and is interpolated and resolved before any other section.  During the interpolation of any further section, all settings and values from the `global` section are avaiable to each additional section.

The top levels of the `variables` dir.

```
./service
./service_tier
./global.db
./config.ini
./datacenter
```

Besides the `config.ini` and the `global.db` a directory has been created by the user for almost all of the defined hierarchy levels.  No directory has been defined for the `env` level.  During compilation and interpolation, if a level is missing, it is ignored and normal processing continues.

The first defined level is `service_tier`.  Within this directory we find the following contents.
```
./service_tier_one.db
./service_tier_two.db
```

This shows that there are two different service_tier's defined, `service_tier_one` and `service_tier_two`.  These files contain the following content.

service_tier_one.db
```
[global]
service_tier_one_setting_1=service_tier_one_value_1
service_tier_one_setting_2=service_tier_one_value_2
service_tier_one_setting_3=service_tier_one_value_3
```

service_tier_two.db
```
[global]
service_tier_two_setting_1=service_tier_two_value_1
service_tier_two_setting_2=service_tier_two_value_2
service_tier_two_setting_3=%(service_tier_two_setting_2)s
```

Each of these files defines three settings under the `global` section.  The `service_tier_two.db` file declares a `service_tier_two_setting_3` setting with a `%(service_tier_two_setting_2)s` value.  This value is a normal ConfigParser format string which refers to the value of another setting.  In this case, during interpolation, the `%(service_tier_two_setting_2)s` value will be replaced with the value of the `service_tier_two_setting_2` setting, `service_tier_two_value_2`.

To view the current output of this setup, you can run the following command from the base directory.
```
$ bin/get_setting.py --pretty
{'global': {'global_setting_1': 'global_value_1',
            'global_setting_2': 'global_value_2'}}
```

Without any options, `get_settings.py` will load only the `global.db` file and present its output.  With the `--pretty` option, the script will print the resulting settings dictionary in a formatted output.

The `get_settings.py` usage output:
```
$ bin/get_setting.py -h
Usage: get_setting.py [options]

Options:
  -h, --help
  -d CONFIG_DIR, --config_dir=CONFIG_DIR
  -C REQUESTED_SECTION, --section=REQUESTED_SECTION
  -S REQUESTED_OPTION, --setting=REQUESTED_OPTION
  -i INSTANCE, --instance=INSTANCE
  -r ITERATION, --iteration=ITERATION
  -H, --process_dependencies
  --pretty
  --json
  --service_tier=SERVICE_TIER
  --service=SERVICE
  --datacenter=DATACENTER
  --env=ENV
```

The `service_tier`, `service`, `datacenter`, and `env` options are dynamically created after reading the content of the `config.ini` file.  To output the compiled and interpolated settings for the `service_tier_one` service tier, the following options can be used.

```
$ bin/get_setting.py --pretty --service_tier=service_tier_one
{'global': {'global_setting_1': 'global_value_1',
            'global_setting_2': 'global_value_2',
            'service_tier_one_setting_1': 'service_tier_one_value_1',
            'service_tier_one_setting_2': 'service_tier_one_value_2',
            'service_tier_one_setting_3': 'service_tier_one_value_3'}}
```

The above output shows the final state of all of the settings declared for the `service_tier_one` service tier and includes the settings defined within both the `global.db` and `service_tier_one.db` files.

The next level of the hierarchy is the `service` level.  The following content can be found under the `service` directory of the `varaibles` directory.

```
service/service_one.db
service/service_two/service_tier/service_tier_one.db
service/service_two/service_tier/service_tier_two.db
service/service_two.db
service/service_one/service_tier/service_tier_one.db
service/service_one/service_tier/service_tier_two.db
```

Here we see two services `service_one` and `service_two` defined.  Each service has a "global" file ( eg, `service_one.db` ) defined.  Depending on the service chosen on the `get_settings.py` command line options, these files will be compiled in order by descending down the directory structure.  Under `service_one` the `service_tier_one.db` config file will only be loaded and evaluated if both `service_one` and `service_tier_one` are defined in the command line options.

```
$ bin/get_setting.py --pretty --service_tier=service_tier_one --service=service_one
{'global': {'global_setting_1': 'global_value_1',
            'global_setting_2': 'global_value_2',
            'service_one_global_setting_1': 'service_one_global_value_1',
            'service_one_global_setting_2': 'service_one_global_value_2',
            'service_one_tier_one_setting_1': 'service_one_tier_one_value_1',
            'service_one_tier_one_setting_2': 'service_one_tier_one_value_2',
            'service_one_tier_one_setting_3': '74.125.224.51',
            'service_tier_one_setting_1': 'service_tier_one_value_1',
            'service_tier_one_setting_2': 'service_tier_one_value_2',
            'service_tier_one_setting_3': 'service_tier_one_value_3'}}
```

This behavior continues on through all of the defined hierarchy levels until all configs are compiled.  For instance, the file for the `service_tier_one` service_tier under the `service_one` service under the `datacenter_one` datacenter one datacenter would be `datacenter/datacenter_one/service/service_one/service_tier/service_tier_one.db`.  And would be evaluated with the following command line options.

```
$ bin/get_setting.py --pretty --service_tier=service_tier_one --service=service_one --datacenter=datacenter_one
{'global': {'datacenter_one_global_setting_1': 'datacenter_one_global_value_1',
            'datacenter_one_global_setting_2': 'datacenter_one_global_value_2',
            'datacenter_one_service_one_setting_1': 'datacenter_one_service_one_value_1',
            'datacenter_one_service_one_setting_2': 'datacenter_one_service_one_value_2',
            'datacenter_one_service_one_tier_one_setting_1': 'datacenter_one_service_one_tier_one_value_1',
            'datacenter_one_service_one_tier_one_setting_2': 'datacenter_one_service_one_tier_one_value_2',
            'global_setting_1': 'datacenter_one_global_value_3',
            'global_setting_2': 'global_value_2',
            'service_one_global_setting_1': 'datacenter_one_service_one_tier_one_value_3',
            'service_one_global_setting_2': 'service_one_global_value_2',
            'service_one_tier_one_setting_1': 'datacenter_one_service_one_value_3',
            'service_one_tier_one_setting_2': 'service_one_tier_one_value_2',
            'service_one_tier_one_setting_3': '74.125.239.50',
            'service_tier_one_setting_1': 'service_tier_one_value_1',
            'service_tier_one_setting_2': 'service_tier_one_value_2',
            'service_tier_one_setting_3': 'service_tier_one_value_3'}}
```

# CallableConfigParser #

The CallableConfigParser class extends the ConfigParser class by adding support for calling function definitions to generate the value of a config setting.  Usage of this can be seen in the `service/service_one/service_tier/service_tier_one.db` settings file.

```
[global]
service_one_tier_one_setting_1=service_one_tier_one_value_1
service_one_tier_one_setting_2=service_one_tier_one_value_2
service_one_tier_one_setting_3=|( dns_resolve www.google.com )
```

The `|( dns_resolve www.google.com )` value is caught by the CallableConfigParser interpolation method.  When caught, the function associated with the `dns_resolve` tag is executed with the `www.google.com` parameter.  Paremeters should be space delemited. The result of this execution is used as the interpolated value of the `service_one_tier_one_setting_3` setting.  The effective result is the first IP returned by DNS for the `www.google.com` FQDN.

A list of the already existing 'tags' or functions can be see within the `bin/config_variable_processor/__init__.py` file.  In this file, the modules within the `bin/config_variable_processor` directory are imported and registered with the CallableConfigParser class.  Each of these modules is a simply function definition that accepts a pre-defined argument interface.

dns_resolve.py
```python
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
```

The `parser` parameter is the CallableConfigParser instance and the `args` parameter is a list of the parameters define in the config file.  The return value is used as the resolved value.  If any exception is encountered in the process, the interpolation for that setting is aborted and the setting value is not modified.

To use the value of a setting as a parameter for a function, define the function call with the normal setting interpolation format.

variables/datacenter/datacenter_one/service/service_two.db
```
[global]
datacenter_one_service_two_setting_1=10
datacenter_one_service_two_setting_2=40
datacenter_one_service_two_setting_3=|( add %(datacenter_one_service_two_setting_1)s %(datacenter_one_service_two_setting_2)s )
datacenter_one_service_two_setting_4=|( add %(datacenter_one_service_two_setting_1)s %(datacenter_one_service_two_setting_none)s )
```

In the above example, the `add` function for the `datacenter_one_service_two_setting_3` setting will be called with the setting values for the `datacenter_one_service_two_setting_1` and the `datacenter_one_service_two_setting_2` settings.  If for some reason the settings arguments cannot be resolved, the `add` function will not be called and the `datacenter_one_service_two_setting_3` value will not be replaced or modified.
