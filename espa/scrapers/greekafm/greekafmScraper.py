import datetime
import json
from math import floor
import threading
import requests


def isValidAFM(candidate, digits):
    return generateAFMControlForValue(int(candidate / 10), digits) == candidate % 10

# def isValidAFM(candidate, digits):
# for i in range(8, -1, -1):
# mask = 10 ** i
# currentDigit = floor(candidate / mask)
# digits[i] = currentDigit
# candidate %= mask
# print(digits)
# currentSum = 0
#     for i in range(1, 9):
#         currentSum += digits[i] * (2 ** i)
#     control = (currentSum % 11) % 10
#     print("control is %d" % control)
#     return control == digits[0]


'''
Generates the control digit for the given AFM candidate which should
be 8 digits long. The digits argument is an integer array of length
at least 8 and is used as temporary storage for calculation. No
assumptions should be made about digits' contents before or after
calling this method.
The control digit is the returned value
'''


def generateAFMControlForValue(candidate, digits):
    for i in range(7, -1, -1):
        mask = 10 ** i
        currentDigit = floor(candidate / mask)
        digits[i] = currentDigit
        candidate %= mask
    # Now digits has a digit of candidate in each position

    currentSum = 0
    for i in range(0, 8):
        currentSum += digits[i] * (2 ** (i + 1))
    control = (currentSum % 11) % 10

    return control


def iterateAFM():
    digits = []
    for i in range(8):
        digits.append(0)
    for i in range(100000000):  # A hundred million, the full range of 8 digit numbers
        yield i * 10 + generateAFMControlForValue(i, digits)


# {0} is the AFM to search for
SINGLE_AFM_SEARCH_URL = "http://www.anaptyxi.gov.gr/DesktopModules/AVMap.ErgaReports_v2/SearchHandler.ashx?filterscount=0&" \
            "groupscount=0&pagenum=0&pagesize=50&recordstartindex=0&recordendindex=18&lang=el-GR&pageMode=3&" \
            "searchValue={0}&searchField=6&perioxesMode=0&selectedPerioxes%5B%5D=01&selectedPerioxes%5B%5D=09&" \
            "selectedPerioxes%5B%5D=11&selectedPerioxes%5B%5D=07&selectedPerioxes%5B%5D=03&selectedPerioxes%5B%5D=04&" \
            "selectedPerioxes%5B%5D=05&selectedPerioxes%5B%5D=06&selectedPerioxes%5B%5D=02&selectedPerioxes%5B%5D=13&" \
            "selectedPerioxes%5B%5D=12&selectedPerioxes%5B%5D=10&selectedPerioxes%5B%5D=08&selectedPerioxes%5B%5D=14&" \
            "ergaType%5B%5D=1&ergaType%5B%5D=2&ergaType%5B%5D=3&enisx=&kad=&company=&includePollaplhs=1"

'''
afmToCheckFor is the string representation of a 9 digit number, potentially zero padded to the left. The result is
a boolean indicating whether there were results returned when querying for the argument or not
'''


def getSingleResult(afmToCheckFor):
    startAt = datetime.datetime.now()
    targetURL = SINGLE_AFM_SEARCH_URL.format(afmToCheckFor)
    result = json.loads(requests.get(targetURL).text)
    print(result["TotalRows"])
    endAt = datetime.datetime.now()

    print("for retrieving non existing we require %d seconds" % (endAt-startAt).seconds)


fetchExisting1 = threading.Thread(target=getSingleResult, args=("998188105",))
fetchExisting2 = threading.Thread(target=getSingleResult, args=("998188105",))
fetchNonExisting1 = threading.Thread(target=getSingleResult, args=("998188106",))
fetchNonExisting2 = threading.Thread(target=getSingleResult, args=("998188107",))
fetchNonExisting3 = threading.Thread(target=getSingleResult, args=("102348365",))
fetchExisting1.start()
fetchExisting2.start()
fetchNonExisting1.start()
fetchNonExisting2.start()
fetchNonExisting3.start()
fetchExisting1.join()
fetchExisting2.join()
fetchNonExisting1.join()
fetchNonExisting2.join()
fetchNonExisting3.join()


def runTests():
    digits = []
    for i in range(8):
        digits.append(0)

    if not isValidAFM(102348365, digits):
        raise AssertionError
    if isValidAFM(102348375, digits):
        raise AssertionError
    if not isValidAFM(999650433, digits):
        raise AssertionError
    if isValidAFM(999650434, digits):
        raise AssertionError

    if isValidAFM(1, digits):
        raise AssertionError
    if isValidAFM(13, digits):
        raise AssertionError
    if isValidAFM(1020005, digits):
        raise AssertionError
