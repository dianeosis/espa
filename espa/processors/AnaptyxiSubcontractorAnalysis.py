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

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'espa.espa.settings')

import django

django.setup()

from espa.espa.processors.AnaptyxiBudgetAnalysis import convertAmountStringToInteger
from espa.espa.models import SubProject

'''
Finds and prints the top 10 subcontractors in terms of subproject count
'''
def printTop10CountSubcontractors():
    allOfThem = {}
    for sub in SubProject.objects.all():
        contractors = sub.contractor.strip()
        if len(contractors) == 0:
            continue
        contractors = contractors.split(",")
        for singleContractor in contractors:
            singleContractor = singleContractor.strip().lower()
            if singleContractor in allOfThem:
                allOfThem[singleContractor] += 1
            else:
                allOfThem[singleContractor] = 1

    topToPrint = 10
    for top in sorted(allOfThem, key=lambda k: allOfThem[k], reverse=True):
        print("Subcontractor %s appeared %d times" % (top, allOfThem[top]))
        topToPrint -= 1
        if topToPrint == 0:
            break

    print("Total is %d" % len(allOfThem))

'''
Finds and prints the top 10 subcontractors in terms of total subproject budget
'''
def printTop10BudgetSubcontractors():
    # the method name is a lie, this ignores subprojects which have multiple contractors
    allOfThem = {}
    ignoredBecauseOfCount = 0
    budgetOfIgnored = 0
    for sub in SubProject.objects.all():
        contractors = sub.contractor.strip()
        if len(contractors) == 0:
            continue
        contractors = contractors.split(",")
        if len(contractors) != 1:
            ignoredBecauseOfCount += 1
            budgetOfIgnored += convertAmountStringToInteger(sub.budget)
        for singleContractor in contractors:
            singleContractor = singleContractor.strip().lower()
            if singleContractor in allOfThem:
                allOfThem[singleContractor] += convertAmountStringToInteger(sub.budget)
            else:
                allOfThem[singleContractor] = convertAmountStringToInteger(sub.budget)

    topToPrint = 10
    for top in sorted(allOfThem, key=lambda k: allOfThem[k], reverse=True):
        print("Subcontractor %s had budget %s" % (top, allOfThem[top]))
        topToPrint -= 1
        if topToPrint == 0:
            break

    print("Ignored %d of the projects, with total budget %d" % (ignoredBecauseOfCount, budgetOfIgnored))


printTop10BudgetSubcontractors()