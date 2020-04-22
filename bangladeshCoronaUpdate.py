# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 15:55:36 2020

BDMap: https://geodash.gov.bd/layers/geonode:level_2_administrative_areas
COVID data: https://www.iedcr.gov.bd/
Reading table from PDF: https://medium.com/@umerfarooq_26378/python-for-pdf-ef0fac2808b0
colorMaps = https://matplotlib.org/tutorials/colors/colormaps.html


@author: Shimanto
"""

# Load all importance packages
import geopandas
import numpy as np
import pandas as pd
from shapely.geometry import Point
import missingno as msn
import seaborn as sns
import matplotlib.pyplot as plt

# Getting to know GEOJSON file:
country = geopandas.read_file("bangladesh.json")

#check the data
country.head()
type(country)
type(country.geometry)
type(country.geometry[0])

#plot the map
country.plot()

#create an empty dataframe to store the lat,long, name, and cases
myDF = pd.DataFrame()
myDF['Lat'] = country.geometry.centroid.x
myDF['Long'] = country.geometry.centroid.y
myDF['Zilla'] = country['NAME_2']

#read table from pdf and store it into a dataframe
import tabula
df = tabula.read_pdf("Confirmed COVID-19 cases_upto_22_April 2020_latest.pdf")

#get rid of excess columns
df.drop(labels=['Division','Division.1','Total','%'],axis='columns',inplace = True)
#remove the nan values
df.dropna(axis='index',inplace=True)
#merge dhaka district and dhaka city and name it to Dhaka
df.iloc[0,1] += df.iloc[1,1]
df.drop(index = 1,inplace = True)
df.iloc[0,0] = 'Dhaka'
df.rename( columns={'Unnamed: 3':'Total'}, inplace=True )

#check the data
df.head()
df.info()
df.describe()

#spell-checker
import enchant

#write the name of all zillas in a text file and prepare the custom dictionary
allZilla = '\n'.join(zillas for zillas in list(myDF.iloc[:,2]))
with open("zillaNames.txt", "w") as outfile:
    outfile.write(allZilla)

zillaList = enchant.PyPWL("zillaNames.txt")

#create the dictionary of total cases
df.set_index('District/City',inplace = True)
caseDict = df.to_dict(orient = 'dict')
caseDict = caseDict['Total']

#the name of B. Baria is too tough to map to Brahamanbaria
caseDict['Brahamanbaria'] = caseDict['B. Baria']
del caseDict['B. Baria']

#correct the zilla name in the data according to the administrative name
#I have no clue why "Chapainawabganj" is not in the list of administrative map!
#and I don't know - "ami ekhon oke niye ki korbo? -_-"
for zilla,cases in caseDict.items():
    if(zillaList.check(zilla)):
        print(zilla,cases)
    else:
        #get suggestions for the input word
        suggestions = zillaList.suggest(zilla)
        if(len(suggestions)==0): #if there is no suggestion found
            print('No suggestion found for {}'.format(zilla))
            continue;
        print('{} has been corrected to {} and has cases {}'.format(zilla,suggestions[0],cases))
        caseDict[suggestions[0]] = caseDict[zilla]
        del caseDict[zilla]

#arrange the total cases according to the serial of administrative zilla list
caseList = []
for zilla in myDF.iloc[:,2]:
    if zilla in caseDict:
        caseList.append(caseDict[zilla])
    else:
        caseList.append(0)
#add a new column in the dataFrame
myDF['Cases'] = caseList
plt.plot(caseList)
newCaseList = [np.log(x+1) for x in caseList]
plt.plot(newCaseList)

country['cases'] = newCaseList

fig, ax = plt.subplots(figsize=(15,10))
myPlt = country.plot(column = 'cases',cmap='YlOrRd',ax=ax,edgecolor='k')
ax.set_axis_off()
ax.set(title='Confirmed COVID-19 Cases Until 20 April')

fig = myPlt.get_figure()
fig.savefig("output.png")