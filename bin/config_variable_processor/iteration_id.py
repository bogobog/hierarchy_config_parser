
def iteration_id( parser, *args ):

    if len( args ) < 4:
        raise Exception( 'Insufficient arguments.' )

    total_instances = int( args[0] )
    total_iterations = int( args[1] )
    this_instance = int( args[2] )
    this_iteration = int( args[3] )

    if this_instance > total_instances or this_instance < 0 or this_iteration > total_iterations or this_iteration < 0:
        raise Exception( 'Arguments are out of bounds.' )

    combined_iterations = total_instances * total_iterations

    my_combined_iteration = ( ( this_instance - 1 ) * total_iterations ) + this_iteration

    if my_combined_iteration > combined_iterations or my_combined_iteration < 0:
        raise Exception( 'Results are out of bounds.' )

    return my_combined_iteration
