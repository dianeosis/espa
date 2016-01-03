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

# coding=utf-8
from django.db import models

'''
This is the set of models required for representing the anaptyxi.gov.gr dataset. Basic data types are:

project code numbers are stored in character arrays of max length 10
monetary values are represented as strings of max length 20 characters. That accounts for long values of
 up to 10 digits, with thousands separator a space, currency character and some space to spare
percentages are represented as character strings of max length 5
Dates are stored as strings, possibly empty, under the same reasoning

This database is supposed to represent the result of scraping the web site, so it assumes no conversions are made
 and things are stored as the original strings.
'''


class Prefecture(models.Model):
    code = models.CharField(max_length=2, unique=True)  # looks like XX
    name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.code)

    def __str__(self):
        return self.__unicode__()


class Municipality(models.Model):
    code = models.CharField(max_length=5)  # looks like XX_XX
    name = models.CharField(max_length=100)


class Project(models.Model):
    title = models.CharField(max_length=500)
    codeNumber = models.CharField(max_length=10, unique=True)
    budget = models.CharField(max_length=20)
    amountPaid = models.CharField(max_length=20)
    completedPercentage = models.CharField(max_length=5)
    stateSupport = models.CharField(max_length=20)  # hidden in the results, perhaps meaningless
    startDate = models.CharField(max_length=12)
    endDate = models.CharField(max_length=12)
    numberOfSubProjects = models.CharField(max_length=3)
    operationalProgramNumber = models.CharField(max_length=4)
    operationalProgramTitle = models.CharField(max_length=200)
    municipalitiesOwning = models.ManyToManyField(Municipality)
    prefecturesOwning = models.ManyToManyField(Prefecture)

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.codeNumber)

    def __str__(self):
        return self.__unicode__()


class SubProject(models.Model):
    owningProject = models.ForeignKey(Project)
    position = models.CharField(max_length=5)
    title = models.CharField(max_length=500)
    contractor = models.CharField(max_length=500)
    budget = models.CharField(max_length=20)
    startDate = models.CharField(max_length=12)
    endDate = models.CharField(max_length=12)

    def __unicode__(self):
        return "Subproject %s for project %s" % (self.title, self.owningProject.codeNumber)

    def __str__(self):
        return self.__unicode__()


class PriorityProject(models.Model):
    title = models.CharField(max_length=500)
    codeNumber = models.CharField(max_length=10, unique=True)
    budget = models.CharField(max_length=20)
    amountPaid = models.CharField(max_length=20)
    completedPercentage = models.CharField(max_length=5)
    stateSupport = models.CharField(max_length=20)  # hidden in the results, perhaps meaningless
    startDate = models.CharField(max_length=12)
    endDate = models.CharField(max_length=12)
    numberOfIncludedProjects = models.CharField(max_length=3)
    completedStatus = models.CharField(max_length=20)

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.codeNumber)

    def __str__(self):
        return self.__unicode__()


class PriorityProjectDependent(models.Model):
    owningPriorityProject = models.ForeignKey(PriorityProject)
    title = models.CharField(max_length=500)
    codeNumber = models.CharField(max_length=10)
    numberOfSubProjects = models.CharField(max_length=3)
    stateSupport = models.CharField(max_length=20)
    startDate = models.CharField(max_length=12)
    endDate = models.CharField(max_length=12)

    def __unicode__(self):
        return "%s (%s)" % (self.title, self.codeNumber)

    def __str__(self):
        return self.__unicode__()