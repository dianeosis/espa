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

import json

from bs4 import BeautifulSoup
import requests

from espa.espa.models import Project, SubProject, Prefecture, Municipality


PROJECT_DETAILS_URL = "http://anaptyxi.gov.gr/ergopopup.aspx?mis={0}&wnd=x&dnnprintmode=true"

# {0} is the area code
# {1} is the number of results to fetch
# {2} takes one of two values: 0 if you want to search based on prefecture, 1 if you want to search by state
SINGLE_AREA_SEARCH_URL = "http://anaptyxi.gov.gr/DesktopModules/AVMap.ErgaReports_v2/SearchHandler.ashx?" \
                         "filterscount=0&groupscount=0&pagenum=0&pagesize={1}&recordstartindex=0&recordendindex=18&lang=el-GR&" \
                         "pageMode=1&searchValue=&searchField=&perioxesMode={2}&" \
                         "selectedPerioxes%5B%5D={0}&" \
                         "ergaType%5B%5D=1&ergaType%5B%5D=2&ergaType%5B%5D=3&" \
                         "epix%5B%5D=01&epix%5B%5D=02&epix%5B%5D=03&epix%5B%5D=04&epix%5B%5D=05&epix%5B%5D=06&" \
                         "epix%5B%5D=07&epix%5B%5D=08&epix%5B%5D=09&epix%5B%5D=10&epix%5B%5D=11&epix%5B%5D=12&" \
                         "epix%5B%5D=13&epix%5B%5D=14&includePollaplhs=1"

prefectures = {"01": "Ανατολικής Μακεδονίας & Θράκης", "09": "Αττικής", "11": "Βορείου Αιγαίου",
               "07": "Δυτικής Ελλάδας", "03": "Δυτικής Μακεδονίας", "04": "Ηπείρου", "05": "Θεσσαλίας",
               "06": "Ιονίων Νήσων", "02": "Κεντρικής Μακεδονίας", "13": "Κρήτης", "12": "Νοτίου Αιγαίου",
               "10": "Πελοποννήσου", "08": "Στερεάς Ελλάδας", "14": "Χωρίς χωροθέτηση"}

municipalities = {"02_65": "Αγιον Όρος", "09_52": "Αθηνών", "07_01": "Αιτωλοακαρνανίας",
                  "09_53": "Ανατολικής Αττικής", "10_02": "Αργολίδος", "10_03": "Αρκαδίας", "04_04": "Αρτας",
                  "07_06": "Αχαϊας", "08_07": "Βοιωτίας", "03_51": "Γρεβενών", "01_08": "Δράμας",
                  "09_54": "Δυτικής Αττικής", "12_09": "Δωδεκανήσου", "01_10": "Εβρου", "08_11": "Ευβοίας",
                  "08_12": "Ευρυτανίας", "06_13": "Ζακύνθου", "07_14": "Ηλείας", "02_15": "Ημαθίας",
                  "13_16": "Ηρακλείου", "04_17": "Θεσπρωτίας", "02_18": "Θεσσαλονίκης", "04_19": "Ιωαννίνων",
                  "01_20": "Καβάλας", "05_21": "Καρδίτσας", "03_22": "Καστοριάς", "06_23": "Κερκύρας",
                  "06_24": "Κεφαλληνίας", "02_25": "Κιλκίς", "03_26": "Κοζάνης", "10_27": "Κορινθίας",
                  "12_28": "Κυκλάδων", "10_29": "Λακωνίας", "05_30": "Λαρίσης", "13_31": "Λασιθίου", "11_32": "Λέσβου",
                  "06_33": "Λευκάδας", "05_34": "Μαγνησίας", "10_35": "Μεσσηνίας", "01_36": "Ξάνθης",
                  "09_55": "Πειραιώς", "02_37": "Πέλλας", "02_38": "Πιερίας", "04_39": "Πρεβέζης", "13_40": "Ρεθύμνης",
                  "01_41": "Ροδόπης", "11_42": "Σάμου", "02_43": "Σερρών", "05_44": "Τρικάλων", "08_45": "Φθιώτιδος",
                  "03_46": "Φλωρίνης", "08_47": "Φωκίδος", "02_48": "Χαλκιδικής", "13_49": "Χανίων", "11_50": "Χίου"}

prefectureCodeToNUTSCodeMapping = {
    "01": "EL11",
    "02": "EL12",
    "03": "EL13",
    "04": "EL21",
    "05": "EL14",
    "06": "EL22",
    "07": "EL23",
    "08": "EL24",
    "09": "EL300",
    "10": "EL25",
    "11": "EL41",
    "12": "EL42",
    "13": "EL43",
    "14": "empty"

}

'''
http://www.anaptyxi.gov.gr/ergopopup.aspx?mis=88888181&wnd=x&dnnprintmode=true#
'''
'''
The following values and allocations come entirely from
http://www.espa.gr/en/pages/staticfinanced.aspx

The values in the following map represent:
OC: Objective convergence
PO: Phasing out
PI: Phasing in
'''
prefectureCodeToCategoryMapping = {
    "02": "PO",  # Central Macedonia
    "03": "PO",  # Western Macedonia
    "09": "PO",  # Attika
    "08": "PI",  # Mainland Greece
    "12": "PI",  # Southern Aegean
    # The rest are OC
    "01": "OC",  # Eastern Macedonia
    "04": "OC",  # ipiros
    "05": "OC",  # Thessalia
    "06": "OC",  # Ionio
    "07": "OC",  # Western Greece
    "10": "OC",  # Peloponnese
    "11": "OC",  # Northern Aegean
    "13": "OC"   # Crete
}

budgetForPO = 6.5
budgetForPI = 0.63
budgetForOC = 9.4
budgetForPOPerPrefecture = budgetForPO / 3
budgetForPIPerPrefecture = budgetForPI / 2
budgetForOCPerPrefecture = budgetForOC / 8

ratioToBudgetForEachPrefecture = {
    "02": budgetForPOPerPrefecture,
    "03": budgetForPOPerPrefecture,
    "09": budgetForPOPerPrefecture,

    "08": budgetForPIPerPrefecture,
    "12": budgetForPIPerPrefecture,

    "01": budgetForOCPerPrefecture,
    "04": budgetForOCPerPrefecture,
    "05": budgetForOCPerPrefecture,
    "06": budgetForOCPerPrefecture,
    "07": budgetForOCPerPrefecture,
    "10": budgetForOCPerPrefecture,
    "11": budgetForOCPerPrefecture,
    "13": budgetForOCPerPrefecture,
}

duplicateCount = 0


def processInstance(instance, **kwargs):
    global duplicateCount

    codeString = instance["kodikos"]
    incomingPrefecture = None
    incomingMunicipality = None

    if "prefecture" in kwargs:
        incomingPrefecture = kwargs["prefecture"]
    if "municipality" in kwargs:
        incomingMunicipality = kwargs["municipality"]

    existingForCode = Project.objects.filter(codeNumber=codeString)

    if len(existingForCode) > 1:
        raise Exception("Database contains duplicates for project code %s " % codeString)
    elif len(existingForCode) == 1:
        duplicateCount += 1
        # we have a duplicate. it probably comes from being registered for multiple prefectures/municipalities
        # so we need to update the corresponding fields
        theExistingEntry = existingForCode[0]

        if incomingMunicipality is not None:
            for municipality in theExistingEntry.municipalitiesOwning.all():
                if municipality.code == incomingMunicipality.code:
                    return  # it is already in there
            theExistingEntry.municipalitiesOwning.add(incomingMunicipality)
            return  # we have either prefecture or municipality incoming

        if incomingPrefecture is not None:
            for prefecture in theExistingEntry.prefecturesOwning.all():
                if prefecture.code == incomingPrefecture.code:
                    return  # it is already in there
            theExistingEntry.prefecturesOwning.add(incomingPrefecture)

        theExistingEntry.save()
        return
    # else we go ahead and create and store the thing

    detailsURI = PROJECT_DETAILS_URL.format(codeString)
    # print("doing %s for details" % detailsURI)
    details = requests.get(detailsURI)

    soup = BeautifulSoup(details.text)

    theProject = Project(title=instance["title"], codeNumber=codeString)
    if incomingPrefecture is not None:
        theProject.prefecturesOwning.add(incomingPrefecture)
    if incomingMunicipality is not None:
        theProject.municipalitiesOwning.add(incomingMunicipality)

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
    theProject.numberOfSubProjects = spans[1].get_text()
    row = rows[6]
    spans = row.find_all("span")
    theProject.stateSupport = spans[1].get_text()
    row = rows[7]
    spans = row.find_all("span")
    theProject.operationalProgramNumber = spans[1].get_text()
    row = rows[8]
    spans = row.find_all("span")
    theProject.operationalProgramTitle = spans[1].get_text()

    # Need to save before being used as a foreign key below
    theProject.save()

    # The following is a table containing subprojects
    subprojectCount = 0
    yaOverviewTable = soup.find(id="dnn_ctr521_View_episkopisiGrid_ctl00")
    for row in yaOverviewTable.tbody.find_all("tr"):
        subprojectCount += 1
        tds = row.find_all("td")
        # tds[0] is a non displayable counter
        subproject = SubProject(owningProject=theProject)
        subproject.position = tds[1].get_text()
        subproject.title = tds[2].get_text()
        subproject.contractor = tds[3].get_text()
        subproject.budget = tds[4].get_text()
        subproject.startDate = tds[5].get_text()
        subproject.endDate = tds[6].get_text()
        subproject.save()

    if subprojectCount != int(theProject.numberOfSubProjects):
        print("project % said it had %s subprojects but only had %d"
              % (theProject.codeNumber, theProject.numberOfSubProjects, subprojectCount))


def main():
    for prefectureCode, prefectureName in prefectures.items():
        thePrefecture = Prefecture.objects.get_or_create(code=prefectureCode, name=prefectureName)[0]
        thePrefecture.save()
        targetURL = SINGLE_AREA_SEARCH_URL.format(prefectureCode, "1000000", "0")
        result = json.loads(requests.get(targetURL).text)
        processList(result["Rows"], prefecture=thePrefecture)
    for municipalityCode, municipalityName in municipalities.items():
        theMunicipality = Municipality.objects.get_or_create(code=municipalityCode, name=municipalityName)[0]
        theMunicipality.save()
        targetURL = SINGLE_AREA_SEARCH_URL.format(municipalityCode, "1000000", "1")
        result = json.loads(requests.get(targetURL).text)
        processList(result["Rows"], municipality=theMunicipality)

    print("Done, duplicates found are %d " % duplicateCount)

    # totalCost = 0
    # for (code, details) in projectTable.items():
    # totalCost += convertAmountStringToInteger(details["Προϋπ/σμός Δημόσιας Δαπάνης"])
    #
    # print("total rows found as %d, total areas found as %d, duplicates were %d"
    # % (totalRowCount, totalCallCount, duplicateCount))
    # print("total length: %d, total cost %d" % (len(projectTable), totalCost))


def processList(toProcess, **kwargs):
    for row in toProcess:
        processInstance(row, **kwargs)
