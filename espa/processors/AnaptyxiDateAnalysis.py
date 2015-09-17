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

from espa.espa.models import Project, SubProject

'''
Finds and prints the max and min start and end dates for projects
'''
def findMaxAndMinDates():
    maxProjectDate = datetime.min
    maxProjectId = ""
    minProjectDate = datetime.max
    minProjectId = ""
    maxSubprojectDate = datetime.min
    maxSubId = ""
    minSubprojectDate = datetime.max
    minSubId = ""

    for project in Project.objects.all():
        currentDateString = project.startDate
        if currentDateString == '-':
            continue
        currentDate = datetime.strptime(currentDateString, "%d/%m/%Y")
        if currentDate > maxProjectDate:
            maxProjectDate = currentDate
            maxProjectId = project.codeNumber
        if currentDate < minProjectDate:
            minProjectDate = currentDate
            minProjectId = project.codeNumber

    for subproject in SubProject.objects.all():
        currentDateString = subproject.startDate
        if currentDateString == '-':
            continue
        currentDate = datetime.strptime(currentDateString, "%d/%m/%Y")
        if currentDate > maxSubprojectDate:
            maxSubprojectDate = currentDate
            maxSubId = subproject.owningProject.codeNumber
        if currentDate < minSubprojectDate:
            minSubprojectDate = currentDate
            minSubId = subproject.owningProject.codeNumber

    print("maxProject: %s (%s)\nminProject: %s (%s)\nmaxsub %s (%s)\nminsub: %s (%s)\n" %
          (maxProjectDate, maxProjectId, minProjectDate, minProjectId,
           maxSubprojectDate, maxSubId, minSubprojectDate, minSubId))


findMaxAndMinDates()