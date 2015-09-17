'''
    Copyright (c) 2015 diaNEOsis [http://www.dianeosis.org]

    This file is part of ESPA.

    ESPA is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ESPA is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ESPA.  If not, see <http://www.gnu.org/licenses/>.
'''

from math import floor

'''
Utility methods for bucket manipulation
'''


def valueToBucketIndex(numberOfBuckets, minValue, maxValue, theValue):
    interval = maxValue - minValue
    scaleFactor = numberOfBuckets/interval
    return floor((theValue-minValue)*scaleFactor)


def valueToIntervalSizeBasedBucket(bucketSize, minValue, theValue):
    offset = theValue - minValue
    return floor(offset/bucketSize)

