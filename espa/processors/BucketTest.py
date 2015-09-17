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

from espa.espa.processors.Bucket import valueToBucketIndex, valueToIntervalSizeBasedBucket


def assertEquals(expected, actual):
    if expected != actual:
        print("Expected %s, got %s" % (str(expected), str(actual)))
        raise AssertionError()


def basicBucketAllocationShouldWork():
    minValue = 10
    maxValue = 120
    numberOfBuckets = 10

    # There are 110 values and 10 buckets. Every 11 values we should change buckets. Note the fencepost error
    # that 120 is not included in the last interval since intervals are open on their high value
    assertEquals(0, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 10))
    assertEquals(0, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 11))
    assertEquals(0, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 12))
    assertEquals(0, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 20))

    assertEquals(1, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 21))
    assertEquals(1, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 31))

    assertEquals(2, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 32))
    assertEquals(2, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 42))

    assertEquals(3, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 43))
    assertEquals(3, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 53))


    assertEquals(4, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 54))
    assertEquals(4, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 64))


    assertEquals(5, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 65))
    assertEquals(5, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 75))

    assertEquals(6, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 76))
    assertEquals(6, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 86))

    assertEquals(7, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 87))
    assertEquals(7, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 97))

    assertEquals(8, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 98))
    assertEquals(8, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 108))

    assertEquals(9, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 109))
    assertEquals(9, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 119))

    assertEquals(10, valueToBucketIndex(numberOfBuckets, minValue, maxValue, 120))


def basicSizeBasedBucketAllocationShouldWork():
    minValue = 0
    bucketSize = 12

    assertEquals(0, valueToIntervalSizeBasedBucket(bucketSize, minValue, 0))
    assertEquals(0, valueToIntervalSizeBasedBucket(bucketSize, minValue, 1))
    assertEquals(0, valueToIntervalSizeBasedBucket(bucketSize, minValue, 2))
    assertEquals(0, valueToIntervalSizeBasedBucket(bucketSize, minValue, 11))

    assertEquals(1, valueToIntervalSizeBasedBucket(bucketSize, minValue, 12))
    assertEquals(1, valueToIntervalSizeBasedBucket(bucketSize, minValue, 13))
    assertEquals(1, valueToIntervalSizeBasedBucket(bucketSize, minValue, 23))

    assertEquals(2, valueToIntervalSizeBasedBucket(bucketSize, minValue, 24))
    assertEquals(2, valueToIntervalSizeBasedBucket(bucketSize, minValue, 25))
    assertEquals(2, valueToIntervalSizeBasedBucket(bucketSize, minValue, 35))


def main():
    basicBucketAllocationShouldWork()
    basicSizeBasedBucketAllocationShouldWork()
    print("Success")

main()