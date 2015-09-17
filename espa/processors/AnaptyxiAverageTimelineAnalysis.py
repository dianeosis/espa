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
from math import log, floor
import os

from dateutil.relativedelta import relativedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'espa.settings')

import django

django.setup()

from espa.processors.AnaptyxiBudgetAnalysis import convertAmountStringToInteger
from espa.models import Project

opProgsCodes = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "Π1", "Π4", "Π5",
                "Π5Υ", "Π7"]


class BudgetDataProjectView:
    def __init__(self, project):
        self.budget = convertAmountStringToInteger(project.budget)
        self.startDate = datetime.strptime(project.startDate, "%d/%m/%Y")
        self.opProgCode = project.operationalProgramNumber

    def __str__(self):
        return "Start date: %s, budget: %s" % (self.startDate, self.budget)


def getLogBucketForAmount(amount):
    value = convertAmountStringToInteger(amount)
    result = floor(log(value, 10)) - 2
    if result < 0:
        result = 0
    return result


def findMedian(values):
    print(len(values))
    values.sort()
    theSize = len(values)
    return values[round(theSize / 2)]


def emptyOpProSum():
    result = {}
    for code in opProgsCodes:
        result[code] = 0
    return result


def addPeriodToTotalOpProgBudgetTimeline(total, period, periodSum):
    for k, v in periodSum.items():
        total[k].append((str(period), v))


'''
Prints histogram information as a 3 month window for the budgets of projects
'''
def doSumHistogramFor3MonthWindow():
    projects = []
    for project in Project.objects.all():
        if project.startDate == "-":
            print("project %s has no start date" % project.codeNumber)
            continue
        projects.append(BudgetDataProjectView(project))

    projects.sort(key=lambda x: x.startDate)
    projects = (p for p in projects if p.budget < 100000000000000)  # generator on purpose

    firstProject = projects.__next__()
    currentUpperBound = firstProject.startDate
    threeMonthInterval = relativedelta(months=3)
    currentUpperBound += threeMonthInterval

    currentSum = firstProject.budget
    currentCount = 1
    buckets = []
    medianBuckets = []
    currentValues = [firstProject.budget]
    counts = []
    sums = []
    totalSum = 0
    currentOpProgSum = emptyOpProSum()

    opProgramBudgetsTimeline = {}
    for code in opProgsCodes:
        opProgramBudgetsTimeline[code] = []

    for p in projects:
        if p.startDate > currentUpperBound:
            buckets.append(round(currentSum / currentCount))
            counts.append(currentCount)
            currentCount = 0
            currentUpperBound += threeMonthInterval
            sums.append((str(currentUpperBound), currentSum))
            addPeriodToTotalOpProgBudgetTimeline(opProgramBudgetsTimeline, currentUpperBound, currentOpProgSum)
            currentOpProgSum = emptyOpProSum()
            currentSum = 0
            if len(currentValues) > 0:
                medianBuckets.append(findMedian(currentValues))
            currentValues = []

        currentSum += p.budget
        currentCount += 1
        currentValues.append(p.budget)
        totalSum += p.budget
        currentOpProgSum[p.opProgCode] += p.budget

    print(buckets)
    print(medianBuckets)
    print(counts)
    print(sums)
    print(str(totalSum))
    for code, timeline in opProgramBudgetsTimeline.items():
        for date, sum in timeline:
            print(str(date), end=",")
        break
    print(" ")
    for code, timeline in opProgramBudgetsTimeline.items():
        print("%s" % code, end=",")
        for date, sum in timeline:
            print(sum, end=",")
        print(" ")


def doLogCounts():
    counts = []
    for i in range(8):
        counts.append(0)

    for project in Project.objects.all():
        counts[getLogBucketForAmount(project.budget)] += 1
        if convertAmountStringToInteger(project.budget) >= 100000000:
            print("%s : %s (%s)" % (project.title, project.budget, project.codeNumber))

            # print(counts)


'''
Calculates the sum of budgets for each OP
'''
def doSumsPerOperationalProgram():
    sums = {}
    mapping = {}
    for code in opProgsCodes:
        sums[code] = 0
    for project in Project.objects.all():
        sums[project.operationalProgramNumber] += convertAmountStringToInteger(project.budget)
        if project.operationalProgramNumber not in mapping:
            mapping[project.operationalProgramNumber] = project.operationalProgramTitle

    print(sums)
    total = 0
    for k, v in sums.items():
        total += v

    print(total)


class OperationalFrameworkDetails:
    def __init__(self):
        self.totalBudget = 0
        self.projectCount = 0
        self.subprojectCount = 0
        self.NLargest = [None, None, None]

    def addProject(self, project):
        self.totalBudget += convertAmountStringToInteger(project.budget)
        self.projectCount += 1
        self.subprojectCount += int(project.numberOfSubProjects)

        currentToPlace = project

        for i in range(3):
            if self.NLargest[i] is None:
                self.NLargest[i] = currentToPlace
                break
            elif convertAmountStringToInteger(self.NLargest[i].budget) < convertAmountStringToInteger(
                    currentToPlace.budget):
                temp = self.NLargest[i]
                self.NLargest[i] = currentToPlace
                currentToPlace = temp

    @staticmethod
    def getProjectString(project):
        if project is None:
            return ""
        return "%s %s (%s)" % (project.title, project.budget, project.operationalProgramTitle)

    def __str__(self):
        return ("Total Budget: %d, project count: %d, subproject count: %d\n\t1st: %s\n\t2nd: %s\n\t3rd: %s"
                % (self.totalBudget, self.projectCount, self.subprojectCount, self.getProjectString(self.NLargest[0]),
                   self.getProjectString(self.NLargest[1]), self.getProjectString(self.NLargest[2])))


'''
Prints the top 3 projects, budget wise, for each OF
'''
def getTop3BudgetPerOperationalFramework():
    opToDetails = {}
    totalProjectCount = 0
    for project in Project.objects.all():
        totalProjectCount += 1
        opNumber = project.operationalProgramNumber
        if opNumber not in opToDetails:
            opToDetails[opNumber] = OperationalFrameworkDetails()
        details = opToDetails[opNumber]
        details.addProject(project)

    projectCountSoFar = 0
    for k, v in opToDetails.items():
        projectCountSoFar += v.projectCount
        print("For OP %s, details are %s" % (k, v))

    print( "initially counted %d, finally they were %d" % (totalProjectCount, projectCountSoFar))


def testOFD():
    class DummyProject:
        def __init__(self, budgetString):
            self.budget = budgetString
            self.numberOfSubProjects = 0

        def __str__(self):
            return self.budget

    details = OperationalFrameworkDetails()
    details.addProject(DummyProject("123"))
    print("Run 1, 0 is %s\n" % details.NLargest[0])
    print("Run 1, 1 is %s\n" % details.NLargest[1])
    print("Run 1, 2 is %s\n" % details.NLargest[2])

    details.addProject(DummyProject("124"))
    print("Run 2, 0 is %s\n" % details.NLargest[0])
    print("Run 2, 1 is %s\n" % details.NLargest[1])
    print("Run 2, 2 is %s\n" % details.NLargest[2])

    details.addProject(DummyProject("121"))
    print("Run 3, 0 is %s\n" % details.NLargest[0])
    print("Run 3, 1 is %s\n" % details.NLargest[1])
    print("Run 3, 2 is %s\n" % details.NLargest[2])

    details.addProject(DummyProject("122"))
    print("Run 4, 0 is %s\n" % details.NLargest[0])
    print("Run 4, 1 is %s\n" % details.NLargest[1])
    print("Run 4, 2 is %s\n" % details.NLargest[2])

    details.addProject(DummyProject("125"))
    print("Run 5, 0 is %s\n" % details.NLargest[0])
    print("Run 5, 1 is %s\n" % details.NLargest[1])
    print("Run 5, 2 is %s\n" % details.NLargest[2])

    details.addProject(DummyProject("120"))
    print("Run 6, 0 is %s\n" % details.NLargest[0])
    print("Run 6, 1 is %s\n" % details.NLargest[1])
    print("Run 6, 2 is %s\n" % details.NLargest[2])


getTop3BudgetPerOperationalFramework()
