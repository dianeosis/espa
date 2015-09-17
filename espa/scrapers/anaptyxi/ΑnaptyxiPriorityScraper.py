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
from bs4 import BeautifulSoup
import requests

from espa.espa.models import PriorityProject, PriorityProjectDependent


# argument {0} is the priority project code number, from 1 to 181
PRIORITY_PROJECT_DETAILS_URL = 'http://www.anaptyxi.gov.gr/ergopopup.aspx?mis=88888{0}&wnd=x&dnnprintmode=true'


def processInstance(codeString):
    detailsURI = PRIORITY_PROJECT_DETAILS_URL.format(codeString)
    details = requests.get(detailsURI)

    soup = BeautifulSoup(details.text)

    theProject = PriorityProject.objects.get_or_create(codeNumber=codeString)[0]

    # The following is a table
    overviewTable = soup.find(id="dnn_ctr521_View_normalEpiskopisi")
    rows = overviewTable.find_all("tr")
    row = rows[0]
    spans = row.find_all("span")
    theProject.budget = spans[1].get_text()
    row = rows[1]
    spans = row.find_all("span")
    theProject.amountPaid = spans[1].get_text()
    row = rows[2]
    spans = row.find_all("span")
    theProject.completedPercentage = spans[1].get_text()
    row = rows[3]
    spans = row.find_all("span")
    theProject.startDate = spans[1].get_text()
    row = rows[4]
    spans = row.find_all("span")
    theProject.endDate = spans[1].get_text()
    row = rows[5]
    spans = row.find_all("span")
    theProject.numberOfIncludedProjects = spans[1].get_text()
    row = rows[6]
    spans = row.find_all("span")
    theProject.stateSupport = spans[1].get_text()
    row = rows[7]
    spans = row.find_all("span")
    theProject.operationalProgramNumber = spans[1].get_text()
    row = rows[8]
    spans = row.find_all("span")
    theProject.operationalProgramTitle = spans[1].get_text()

    statusSpan = soup.find(id="dnn_ctr521_View_txtKatastasi")
    theProject.completedStatus = statusSpan.get_text()

    # Need to save before being used as a foreign key below
    theProject.save()

    # The following is a table containing dependent projects
    dependentProjectCount = 0
    yaOverviewTable = soup.find(id="dnn_ctr521_View_episkopisiGrid_ctl00")
    dependents = yaOverviewTable.tbody.find_all("tr")

    for dependent in dependents:
        tds = dependent.find_all("td")
        if len(tds) > 1:
            dependentProjectCount += 1
            # tds[0] is a non displayable counter
            dependentProject = PriorityProjectDependent(owningPriorityProject=theProject)
            # td[0] is empty
            # td[1] is the project code
            # td[2] is the project title
            # td[3] is the subproject count for this project
            # td[4] is the state budget
            # td[5] is the start date
            # td[6] is the end date
            dependentProject.codeNumber = tds[1].get_text()
            dependentProject.title = tds[2].get_text()
            dependentProject.numberOfSubProjects = tds[3].get_text()
            dependentProject.stateSupport = tds[4].get_text()
            dependentProject.startDate = tds[5].get_text()
            dependentProject.endDate = tds[6].get_text()
            dependentProject.save()

    if dependentProjectCount != int(theProject.numberOfIncludedProjects):
        print("project %s said it had %s dependent projects but only had %d"
              % (theProject.codeNumber, theProject.numberOfIncludedProjects, dependentProjectCount))

    print("finished %s" % codeString)


def main():
    for i in range(1, 182):
        processInstance("%d" % i)

main()