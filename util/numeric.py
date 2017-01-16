# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Numeric utilities """

def tonum(str2cast):
    """Casts a string to the appropriate numeric type, i.e. int or float.

    :param str2cast: string to cast
    :returns: the numeric value in the appropriate type or "Impossible cast" \
        string \
    :rtype: float \
    :type str \
    """

    try:
        i = int(str2cast)
    except ValueError:
        try:
            floatstring = float(str2cast)
        except ValueError:
            return 'Impossible cast'
        else:
            return floatstring
    else:
        return i
