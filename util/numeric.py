# Copyright (c) 2015 Intracom S.A. Telecom Solutions. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

""" Numeric utilities """

def tonum(s):
    """
    Casts a string to the appropriate numeric type, i.e. int or float

    :param s: string to cast
    :returns: the numeric value in the appropriate type or
              "Impossible cast" string
    """
    try:
        i = int(s)
    except ValueError:
        try:
            f = float(s)
        except ValueError:
            return 'Impossible cast'
        else:
            return f
    else:
        return i
