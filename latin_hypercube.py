"""Module with functions required to generate a latin hypercube of given variables (with ranges)
"""
import numpy as np

def normalized(d,n):
    """ Generates a normalized latin hypercube 
        (uniform distribution from 0 to 1 for d dimensions with n points)

    Args:
        d (int): number of dimensions of the latin hypercube (number of independent variables)
        n (int): number of desired sampling points

    Returns:
        np.array: dxn array containing the latin hypercube
    """
    lower_limits = np.arange(0,n)/n
    upper_limits = np.arange(1,n+1)/n      

    points = np.random.uniform(low=lower_limits, high=upper_limits, size=[d,n]).T

    for i in range(0,d):
        np.random.shuffle(points[:,i])

    return points

def sampling(LOW,UP,p):
    """Generates the latin hypercube of the desired ranges of variables

    Args:
        LOW (np.array): array with lower bound of the variables
        UP (np.array): array with upper bound of the variables
        p (np.array): normalized nxd latin hypercube (use function latin_hypercube_normalized)

    Returns:
        _np.array: array containin a latin hypercube within the specified ranges
    """
    for i in range(0,len(UP)):
        p[:,i]=p[:,i]*(UP[i]-LOW[i])+LOW[i]

    return p

def int_vars(int_list, lh_samples):
    """Provided a list of the variables that are integers, this function transforms the float data 
    into the closest integer for all the values of that variable in the latin hypercube.

    Args:
        int_list (bool list): list with boolean values to determine 
        if a variable should be only integers.
        
        lh_samples (np.array): array with latin hypercube samples

    Returns:
        np.array: latin hypercube with the desired variables transformed to integers.
    """
    for i in enumerate(int_list):
        if i[1]:
            lh_samples = lh_samples.astype(object)
            lh_samples[:,i[0]] = np.int32(np.round(lh_samples[:,i[0]].astype('f')))
    return lh_samples
    