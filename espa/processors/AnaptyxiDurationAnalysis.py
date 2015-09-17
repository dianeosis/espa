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

from datetime import datetime

import os
from math import ceil

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'espa.espa.settings')

import django

django.setup()

from espa.espa.models import Project
from espa.espa.processors.Bucket import valueToIntervalSizeBasedBucket, valueToBucketIndex


def getDurationOfProjectInDays(project):
    startDate = datetime.strptime(project.startDate, "%d/%m/%Y")
    endDate = datetime.strptime(project.endDate, "%d/%m/%Y")
    return (endDate - startDate).days


def getDurationOfProjectInMonths(project):
    startDate = datetime.strptime(project.startDate, "%d/%m/%Y")
    endDate = datetime.strptime(project.endDate, "%d/%m/%Y")
    return (endDate.year-startDate.year)*12 + (endDate.month-startDate.month)


'''
Creates a histogram of duration, in 100 buckets, for all projects
'''
def extractDurationCountsAll():
    durationValues = []
    for project in Project.objects.all():
        if project.startDate == "-":
            print("project %s has no start date" % project.codeNumber)
            continue
        duration = getDurationOfProjectInDays(project)
        if duration <= 0:
            print("project %s ended before it started" % project.codeNumber)
            continue
        durationValues.append(duration)

    numberOfBuckets = 100
    lowDurationValue = min(durationValues)
    highDurationValue = max(durationValues)

    countPerBucket = [0]*numberOfBuckets
    for durationValue in durationValues:
        bucketIndex = valueToBucketIndex(numberOfBuckets, lowDurationValue, highDurationValue+1, durationValue)
        countPerBucket[bucketIndex] += 1

    theTsv = open("espaHistoDuration.tsv", "w+")

    dx = (highDurationValue-lowDurationValue)/numberOfBuckets
    print("high value is %f, low value is %f, interval is %f" % (highDurationValue, lowDurationValue, dx))
    for i in range(0, len(countPerBucket)):
        print("%d\t%d\t%d" % ((lowDurationValue+i*dx), dx, countPerBucket[i]), file=theTsv)

    theTsv.flush()
    theTsv.close()

'''
Creates a histogram of project counts in buckets of size 12 month
'''
def extractBudgetCountsPer12Months():
    durationValues = []
    for project in Project.objects.all():
        if project.startDate == "-":
            print("project %s has no start date" % project.codeNumber)
            continue
        duration = getDurationOfProjectInMonths(project)
        if duration < 0:
            print("project %s ended before it started" % project.codeNumber)
            continue
        durationValues.append(duration)

    lowDurationValue = min(durationValues)
    highDurationValue = max(durationValues)
    bucketSize = 12
    bucketCount = ceil((highDurationValue-lowDurationValue)/bucketSize)

    countPerBucket = [0]*bucketCount
    for durationValue in durationValues:
        bucketIndex = valueToIntervalSizeBasedBucket(bucketSize, lowDurationValue, durationValue)
        countPerBucket[bucketIndex] += 1

    theTsv = open("espaHistoDurationMonths.tsv", "w+")

    dx = bucketSize
    print("high value is %f, low value is %f, interval is %f" % (highDurationValue, lowDurationValue, dx))
    for i in range(0, len(countPerBucket)):
        print("%d\t%d\t%d" % ((lowDurationValue+i*dx), dx, countPerBucket[i]), file=theTsv)

    theTsv.flush()
    theTsv.close()

extractBudgetCountsPer12Months()