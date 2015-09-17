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

from espa.espa.models import SubProject
from espa.espa.processors.AnaptyxiBudgetAnalysis import convertAmountStringToInteger

searchingFor = ["συμβο", "σύμβο", "μελέτ", "μελετ" # , "επικ"
                ]

avoiding = ["κατασκ", "ανισόπεδος"]


def titleContains(lowerTitle):
    for searching in searchingFor:
        if lowerTitle.find(searching) >= 0:
            return True
    return False


def titleNotContains(lowerTitle):
    for avoid in avoiding:
        if lowerTitle.find(avoid) >= 0:
            return False
    return True

'''
Finds all projects containing in their title the strings in array searchingFor, ignoring projects that
contain elements in array avoiding
'''
def searchTitleForString():
    count = 0
    totalBudget = 0
    for subproject in SubProject.objects.all():
        lowerTitle = subproject.title.lower()
        if titleContains(lowerTitle) and titleNotContains(lowerTitle):
            count += 1
            currentBudget = convertAmountStringToInteger(subproject.budget)
            totalBudget += currentBudget
            if currentBudget > 1000000:
                print("%s has budget %d (belonging to %s)" % (lowerTitle, currentBudget, subproject.owningProject.codeNumber))

    print("Total count is %d, budget sum is %d" % (count, totalBudget))

searchTitleForString()