#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

# Copyright (c) 2018,2019,2020,2021, Stephen Goadhouse <sgoadhouse@virginia.edu>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#-------------------------------------------------------------------------------
#  Control of HP/Agilent/Keysight MSO-X/DSO-X 3000A Oscilloscope with PyVISA
#-------------------------------------------------------------------------------

# For future Python3 compatibility:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os

try:
    from .rigol import Rigol
except Exception:
    sys.path.append(os.getcwd())
    from rigol import Rigol

class DHO(Rigol):
    """Basic class for controlling and accessing a Rigol Generic DHO8/9 Oscilloscope"""

    def __init__(self, resource, maxChannel=4, wait=0):
        """Init the class with the instruments resource string

        resource   - resource string or VISA descriptor, like TCPIP0::172.16.2.13::INSTR
        maxChannel - number of channels of this oscilloscope
        wait       - float that gives the default number of seconds to wait after sending each command
        """
        super(DHO, self).__init__(resource, maxChannel, wait)

        # Give the Series a name
        self._series = 'DHO'
        
    def measureStatistics(self):
        """Returns an array of dictionaries from the current statistics window.

        The definition of the returned dictionary can be easily gleaned
        from the code below.
        """

        # turn on the statistics display - these are specific to MSOX/DSOX
        self._instWrite("SYSTem:MENU MEASure")
        self._instWrite("MEASure:STATistics:DISPlay ON")

        statFlat = super(DSOX, self)._measureStatistics()
        
        # convert the flat list into a two-dimentional matrix with seven columns per row
        cols = 7
        if ((len(statFlat) % cols != 0)):
            print('Unexpected response. Oscilloscope may not have any measurements enabled.')
            statMat = []
        else:
            statMat = [statFlat[i:i+cols] for i in range(0,len(statFlat),cols)]
        
        # convert each row into a dictionary, while converting text strings into numbers
        stats = []
        for stat in statMat:
            stats.append({'label':stat[0],
                          'CURR':float(stat[1]),   # Current Value
                          'MIN':float(stat[2]),    # Minimum Value
                          'MAX':float(stat[3]),    # Maximum Value
                          'MEAN':float(stat[4]),   # Average/Mean Value
                          'STDD':float(stat[5]),   # Standard Deviation
                          'COUN':int(stat[6])      # Count of measurements
                          })

        # return the result in an array of dictionaries
        return stats

class DHOS(DHO):
    """Basic class for controlling and accessing a Rigol Generic DHOxxxS Oscilloscope"""

    def __init__(self, resource, maxChannel=4, wait=0):
        """Init the class with the instruments resource string

        resource   - resource string or VISA descriptor, like TCPIP0::172.16.2.13::INSTR
        maxChannel - number of channels of this oscilloscope
        wait       - float that gives the default number of seconds to wait after sending each command
        """
        super(DHOS, self).__init__(resource, maxChannel, wait)

        # Since DHOS have digital channels, add POD1 is for digital
        # channels 0-7 or POD2 for digital channels 8-15
        self._chanAllValidList += ['POD'+str(x) for x in range(1,3)]

        # Give the Series a name
        self._series = 'DHOS'
        
class DHO924S(DHOS):
    """Basic class for controlling and accessing a Rigol DHO924S 4-Channel Oscilloscope"""

    maxChannel = 4

    def __init__(self, resource, wait=0):
        """Init the class with the instruments resource string

        resource   - resource string or VISA descriptor, like TCPIP0::172.16.2.13::INSTR
        wait       - float that gives the default number of seconds to wait after sending each command
        """
        super(DHO924S, self).__init__(resource, maxChannel=DHO924S.maxChannel, wait=wait)

        # Give the Series a name
        self._series = 'DHO924S'
        
        
        
