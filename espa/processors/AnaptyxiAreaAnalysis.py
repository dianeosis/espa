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

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'espa.espa.settings')

import django

django.setup()

from espa.espa.models import Project
from espa.espa.processors.AnaptyxiBudgetAnalysis import convertAmountStringToInteger
from espa.espa.scrapers.anaptyxi.ΑnaptyxiScraper import ratioToBudgetForEachPrefecture, prefectures, prefectureCodeToNUTSCodeMapping

'''
Prints a list of budget per municipality.
'''
def municipalityAnalysis():
    prefectureSums = {}

    for code in prefectures.keys():
        prefectureSums[code] = {}
        for i in range(1996, 2016):  # we magically know that project years are in this range
            prefectureSums[code][i] = 0

    totalBudgetSum = 0  # for checking
    countOfProjects = 0
    ignoredBecauseOfDateBudgetSum = 0

    for project in Project.objects.all():
        countOfProjects += 1
        prefTotalWeight = 0
        projectBudget = convertAmountStringToInteger(project.budget)
        totalBudgetSum += projectBudget
        if project.startDate == "-":
            ignoredBecauseOfDateBudgetSum += projectBudget
            continue
        for prefecture in project.prefecturesOwning.all():
            if prefecture.code != "14":
                prefTotalWeight += ratioToBudgetForEachPrefecture[prefecture.code]

        localPrefectureSum = 0
        for prefecture in project.prefecturesOwning.all():
            if prefecture.code != "14":
                currentPrefWeight = ratioToBudgetForEachPrefecture[prefecture.code] / prefTotalWeight
                currentPrefectureAllocation = projectBudget * currentPrefWeight
                projectYear = datetime.strptime(project.startDate, "%d/%m/%Y").year
                prefectureSums[prefecture.code][projectYear] += currentPrefectureAllocation
                localPrefectureSum += currentPrefectureAllocation
        if abs(localPrefectureSum - projectBudget) > 1:
            print("project %s has prefectures %s but the budget does not equal the allocation (%d vs %d)"
                  % (project, project.prefecturesOwning.all(), projectBudget, localPrefectureSum))
    print(totalBudgetSum)
    valuesSum = 0
    for yearValue in prefectureSums.values():
        for value in yearValue.values():
            valuesSum += value
    prettyPrintBudgets(prefectureSums)
    print(valuesSum)
    print(totalBudgetSum - valuesSum)
    print("ignored because of date sum up to %d " % ignoredBecauseOfDateBudgetSum)


def prettyPrintBudgets(budgets):
    # Prints csv with AreaCode, Year, Value
    print('"AreaCode","Year","Value"')
    for areaCode, yearValues in budgets.items():
        nutsValue = prefectureCodeToNUTSCodeMapping[areaCode]
        for year, value in yearValues.items():
            print('"%s","%d","%d"' % (nutsValue, year, value))
