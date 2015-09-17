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

from espa.espa.models import PriorityProject
from espa.espa.processors.AnaptyxiBudgetAnalysis import convertAmountStringToInteger

'''
Quick finder for priority projects that have no dependent projects
'''
def statisticsAboutDependentProjectCount():
    for project in PriorityProject.objects.all():
        count = 0
        for _ in project.priorityprojectdependent_set.all():
            count += 1

        if count == 0:
            print("%s at state %s had no dependent projects" % (project.codeNumber, project.completedStatus))

'''
Calculates and prints the sum of budgets of priority projects that are in falling behind status
'''
def budgetSumForPrioProjectsFallingBehind():
    fallingBehindBudgetTotal = 0
    totalBudget = 0
    inProgressBudget = 0
    for project in PriorityProject.objects.all():
        totalBudget += convertAmountStringToInteger(project.budget)
        if project.completedStatus == "ΑΠΑΙΤΟΥΝΤΑΙ ΠΡΟΣΘΕΤΑ ΜΕΤΡΑ" or project.completedStatus == "ΕΡΓΑ ΣΕ ΚΙΝΔΥΝΟ":
            fallingBehindBudgetTotal += convertAmountStringToInteger(project.budget)
        elif project.completedStatus == "ΣΕ ΕΞΕΛΙΞΗ":
            inProgressBudget += convertAmountStringToInteger(project.budget)

    print("total budget is %d, of that falling behind is %d, in progress %d" % (
        totalBudget, fallingBehindBudgetTotal, inProgressBudget))


budgetSumForPrioProjectsFallingBehind()