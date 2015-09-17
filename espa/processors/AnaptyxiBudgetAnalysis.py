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

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'espa.settings')

import django

django.setup()
from math import floor
import string
from espa.models import Project
from espa.processors.Bucket import valueToBucketIndex


'''
Creates a histogram as a TSV formatted file, containing project counts per bucket, where one bucket is 100th of
the total budget range
'''
def extractBudgetCountsAll():
    budgetValues = []
    for project in Project.objects.all():
        budget = convertAmountStringToInteger(project.budget)
        budgetValues.append(budget)
    # Now budgetValues array contains all project budgets as
    # longs. Separate them into buckets
    numberOfBuckets = 100
    lowBudgetValue = min(budgetValues)
    highBudgetValue = max(budgetValues)

    countPerBucket = [0] * numberOfBuckets
    for budgetValue in budgetValues:
        bucketIndex = valueToBucketIndex(numberOfBuckets, lowBudgetValue, highBudgetValue + 1, budgetValue)
        countPerBucket[bucketIndex] += 1

    theTsv = open("espaHisto.tsv", "w+")

    dx = (highBudgetValue - lowBudgetValue) / numberOfBuckets
    print("high value is %f, low value is %f, interval is %f" % (highBudgetValue, lowBudgetValue, dx))
    for i in range(0, len(countPerBucket)):
        print("%d\t%d\t%d" % ((lowBudgetValue + i * dx) / 1000000, dx / 1000000, countPerBucket[i]), file=theTsv)

    theTsv.flush()
    theTsv.close()


'''
Extracts in a TSV file the bottom quartile of projects, based on budget
'''
def extractBudgetCountsBottomPercentile():
    budgetValues = []
    for project in Project.objects.all():
        budget = convertAmountStringToInteger(project.budget)
        budgetValues.append(budget)
    budgetValues.sort()
    totalBudgetCount = len(budgetValues)
    desiredBudgetCount = floor(totalBudgetCount / 4)
    budgetValues = budgetValues[:desiredBudgetCount]
    print("will work with bottom %d values out of %d which is the %f percent" %
          (desiredBudgetCount, totalBudgetCount, (len(budgetValues) * 100) / totalBudgetCount))

    # Now budgetValues array contains all project budgets as
    # longs. Separate them into buckets
    numberOfBuckets = 100
    lowBudgetValue = min(budgetValues)
    highBudgetValue = max(budgetValues)

    countPerBucket = [0] * numberOfBuckets
    for budgetValue in budgetValues:
        bucketIndex = valueToBucketIndex(numberOfBuckets, lowBudgetValue, highBudgetValue + 1, budgetValue)
        countPerBucket[bucketIndex] += 1

    theTsv = open("espaHistoSecond25Percent.tsv", "w+")

    dx = (highBudgetValue - lowBudgetValue) / numberOfBuckets
    print("high value is %f, low value is %f, interval is %f" % (highBudgetValue, lowBudgetValue, dx))
    for i in range(0, len(countPerBucket)):
        print("%d\t%d\t%d" % ((lowBudgetValue + i * dx), dx, countPerBucket[i]), file=theTsv)

    theTsv.flush()
    theTsv.close()

'''
Extracts in a TSV file the second quartile of projects, based on budget
'''
def extractBudgetCountsSecondPercentile():
    budgetValues = []
    for project in Project.objects.all():
        budget = convertAmountStringToInteger(project.budget)
        budgetValues.append(budget)
    budgetValues.sort()
    totalBudgetCount = len(budgetValues)
    desiredBudgetCount = floor(totalBudgetCount / 4)
    budgetValues = budgetValues[desiredBudgetCount:2 * desiredBudgetCount]
    print("will work with bottom %d values out of %d which is the %f percent" %
          (len(budgetValues), totalBudgetCount, (len(budgetValues) * 100) / totalBudgetCount))

    # Now budgetValues array contains all project budgets as
    # longs. Separate them into buckets
    numberOfBuckets = 100
    lowBudgetValue = min(budgetValues)
    highBudgetValue = max(budgetValues)

    countPerBucket = [0] * numberOfBuckets
    for budgetValue in budgetValues:
        bucketIndex = valueToBucketIndex(numberOfBuckets, lowBudgetValue, highBudgetValue + 1, budgetValue)
        countPerBucket[bucketIndex] += 1

    theTsv = open("espaHistoSecond25Percent.tsv", "w+")

    dx = (highBudgetValue - lowBudgetValue) / numberOfBuckets
    print("high value is %f, low value is %f, interval is %f" % (highBudgetValue, lowBudgetValue, dx))
    for i in range(0, len(countPerBucket)):
        print("%d\t%d\t%d" % ((lowBudgetValue + i * dx) / 1000, dx / 1000, countPerBucket[i]), file=theTsv)

    theTsv.flush()
    theTsv.close()


'''
Prints count of projects and subprojects, total sum of their budgets, minimum and maximum budget projects
'''
def extractBasicStats():
    from sys import maxsize

    minValue = maxsize
    maxValue = 0
    minCode = ""
    maxCode = ""
    count = 0
    totalSum = 0
    subprojectCount = 0
    for project in Project.objects.all():
        count += 1
        budget = convertAmountStringToInteger(project.budget)
        totalSum += budget
        subprojectCount += int(project.numberOfSubProjects)
        if budget > maxValue:
            maxValue = budget
            maxCode = project.codeNumber
        elif budget < minValue:
            minValue = budget
            minCode = project.codeNumber

    print(
        "Found %d projects with total budget %d. The largest budget was for %s (%d) and the lowest budget for %s (%d)."
        " The total number of subprojects is %d." %
        (count, totalSum, maxCode, maxValue, minCode, minValue, subprojectCount))


'''
Converts to an integer the string passed which represents a budget value, possibly dotted or with a sign
'''
def convertAmountStringToInteger(theString):
    if len(theString) == 0:
        return 0
    toTest = theString.strip().replace(".", "")
    if string.digits.find(toTest[-1]) == -1:
        toTest = toTest[:-1].strip()
    toTest = toTest.split(",")[0]
    return int(toTest)


extractBasicStats()
