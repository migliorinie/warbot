#!/usr/bin/python3

import random
from matplotlib import pyplot as plt
from matplotlib import cm

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import cartopy.feature as cfeature
import numpy as np
import time

import requests
#import pyimgur
import json
import webbrowser

#Changed:
# Vatican City, Serbia, Czech Republic, North Macedonia

countrylist = ["Vatican City", "United Kingdom", "Ukraine", "Switzerland", "Sweden", "Spain", "Slovakia", "Slovenia", "Serbia", "San Marino", "Russia", "Romania", "Portugal", "Poland", "Norway", "Netherlands", "Montenegro", "Moldova", "Monaco", "Malta", "North Macedonia", "Luxembourg", "Lithuania", "Liechtenstein", "Latvia", "Kosovo", "Italy", "Ireland", "Iceland", "Hungary", "Greece", "Germany", "France", "Finland", "Estonia", "Denmark", "Czech Republic", "Croatia", "Bulgaria", "Bosnia and Herzegovina", "Belgium", "Belarus", "Austria", "Andorra", "Albania"]

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

CID = ''
CSEC = ''
#im = pyimgur.Imgur(CID, CSEC)

#auth_url = im.authorization_url('pin')
#webbrowser.open(auth_url)
#pin = input("What is the pin? ") # Python 3x
#im.exchange_pin(pin)

#ab = im.create_album(title="Euro Wars")

bordict = {}
with open('borders.json') as f:
    bordict = json.load(f)
    
linklist = []
for c in countrylist:
    nbrs = bordict[c]
    for n in nbrs:
        if n in countrylist and countrylist.index(c) < countrylist.index(n):
            linklist.append((c, n))

nationColors = {}
with open('colors.json') as f:
    nationColors = json.load(f)

nationCenters = {}
with open('centers.json') as f:
    nationCenters = json.load(f)

class Nation:
    def __init__(self, name):
        self.name = name
        self.sovereign = name
        self.neighbors = []
        for i in linklist:
            if self.name == i[0]:
                self.neighbors.append(i[1])
            elif self.name == i[1]:
                self.neighbors.append(i[0])
    
    def __repr__(self):
        linkstr = ""
        if len(self.neighbors) == 1:
            linkstr = ". Confines with " + self.neighbors[0]
        elif len(self.neighbors) > 1:
            linkstr = ". Confines with " + ', '.join(self.neighbors[:-1]) + " and " + self.neighbors[-1]
        return "Nation of " + self.name + ", under the control of " + self.sovereign + linkstr + "."
    
    def __str__(self):
        return repr(self)

class World:
    def __init__(self, tgtList, boundaries):
        self.states = []
        for i in countrylist:
            n = Nation(i)
            self.states.append(n)
        self.lastMove = None
        self.turn = 0
        self.marker = 0
        
        self.tgtList = tgtList
        self.boundaries = boundaries
        self.sovereigns = list(set([s.sovereign for s in self.states]))
        
        printMap(self)
        # Each turn is made by two markers.
        self.turn += 1
        self.marker += 1
        self.year = 2020
        self.comment = "This was the political situation at the start of 2020. Soon, everything would be set ablaze..."
        
    def printStatus(self):
        print("State of the world:")
        for i in self.states:
            print(i)
    
    def winCondition(self):
        sovereigns = list(set([s.sovereign for s in self.states]))
        eliminated = [s for s in self.sovereigns if s not in sovereigns]
        self.comment = ""
        if len(eliminated) > 0:
            self.comment = "With that, the sovereignty of " + eliminated[0] + " ended."
            print("=== " + eliminated[0] + " was eliminated! ===")
            self.sovereigns = sovereigns
        
        # Here it should be nice to keep a running list and say when some sovereign nation has been eliminated.
        if len(sovereigns) > 1:
            print(str(len(sovereigns)) + " sovereign nations remain!")
            return False
        else:
            print("One winner stands! It is " + sovereigns[0] + "!")
            print("======")
            self.comment = "When the dust settled, only " + sovereigns[0] + " remained, uncontested master of Europe."
            return True
    
    def getState(self, name):
        return self.states[countrylist.index(name)]
    
    def advance(self):
        validMove = False
        targets = []
        while validMove == False:
            moveID = random.randint(0, len(countrylist)-1)
            mover = self.getState(countrylist[moveID])
            overlord = mover.sovereign
            targets = []
            for i in mover.neighbors:
                if self.getState(i).sovereign != mover.sovereign:
                    targets.append(self.getState(i))
            if targets != []:
                validMove = True
        target = targets[random.randint(0, len(targets)-1)]
        # For now, all attacks will be successful
        self.lastMove = (mover, target)
        printMove(self)
        self.comment = "In " + months[(self.turn-1)%12] + ' ' + str(self.year) + ", " + overlord + " attacked " + target.name + " from " + mover.name + "."
        saveImg(self.marker, self.comment)
        self.marker += 1
        target.sovereign = mover.sovereign
        print("Round " + str(self.turn) + ":")
        print(overlord + " attacked " + target.name + " from " + mover.name + ".")
        printMap(self)
        self.marker += 1
        self.turn += 1
        if self.turn%12 == 1:
            self.year += 1

'''
def saveImg(marker, com):
    success = False
    while not success:
        print("Uploading " + "maps/advance_" + str(marker).zfill(5) + ".png")
        try:
            im.upload_image(path="maps/advance_" + str(marker).zfill(5) + ".png", description=com, album=ab)
            success = True
        except requests.exceptions.HTTPError:
            print("Too many requests: waiting 10 minutes.")
            time.sleep(700) # A bit more than 10 minutes if I go over limit
            im.refresh_access_token()
'''

def printMap(world):
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())
    ax.coastlines(resolution='50m')
            
    for country in world.tgtList:
        ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                          facecolor=nationColors[world.getState(country.attributes['ADMIN']).sovereign],
                          label=country.attributes['ADMIN'])
    ax.set_extent(world.boundaries, ccrs.PlateCarree())
    ax.add_feature(cfeature.NaturalEarthFeature('cultural', 'admin_0_boundary_lines_land',
                              '50m', edgecolor='black', facecolor='none'))
    # A color legend might help, if I can put it to the side.
    print("Saving " + "maps/advance_" + str(world.marker).zfill(5) + ".png")
    plt.savefig("maps/advance_" + str(world.marker).zfill(5) + ".png", bbox_inches = 'tight')
    plt.close()
    
def printMove(world):
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())
    ax.coastlines(resolution='50m')
            
    for country in world.tgtList:
        ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                          facecolor=nationColors[world.getState(country.attributes['ADMIN']).sovereign],
                          label=country.attributes['ADMIN'])
    ax.set_extent(world.boundaries, ccrs.PlateCarree())
    ax.add_feature(cfeature.NaturalEarthFeature('cultural', 'admin_0_boundary_lines_land',
                              '50m', edgecolor='black', facecolor='none'))
    
    if w.lastMove is not None:
        atkCountry = [c for c in world.tgtList if c.attributes['ADMIN'] == w.lastMove[0].name][0]
        tgtCountry = [c for c in world.tgtList if c.attributes['ADMIN'] == w.lastMove[1].name][0]
        
        start_lat, start_lon = nationCenters[w.lastMove[0].name]
        end_lat, end_lon = nationCenters[w.lastMove[1].name]
        plt.plot([start_lon, end_lon], [start_lat, end_lat],
            color='red', linewidth=2,
            transform=ccrs.PlateCarree(),
        )
        
        ax.add_geometries(tgtCountry.geometry, ccrs.PlateCarree(),
                          edgecolor='red',
                          facecolor=nationColors[world.getState(tgtCountry.attributes['ADMIN']).sovereign],
                          label=tgtCountry.attributes['ADMIN'])
        ax.add_geometries(atkCountry.geometry, ccrs.PlateCarree(),
                          edgecolor='green',
                          facecolor=nationColors[world.getState(atkCountry.attributes['ADMIN']).sovereign],
                          label=tgtCountry.attributes['ADMIN'])
        print("Saving " + "maps/advance_" + str(world.marker).zfill(5) + ".png")
        plt.savefig("maps/advance_" + str(world.marker).zfill(5) + ".png", bbox_inches = 'tight')
    plt.close()
               

shapename = 'admin_0_countries'
countries_shp = shpreader.natural_earth(resolution='50m',
                                        category='cultural', name=shapename)

euroList = [s for s in shpreader.Reader(countries_shp).records() if s.attributes['REGION_UN'] == 'Europe'
            and s.attributes['ADMIN'] == s.attributes['SOVEREIGNT']]
boundaries = [-25, 50, 32, 72]

# Fixing some names
for country in euroList:
    if country.attributes['ADMIN'] == "Vatican":
        country.attributes['ADMIN'] = "Vatican City"
    elif country.attributes['ADMIN'] == "Republic of Serbia":
        country.attributes['ADMIN'] = "Serbia"
    elif country.attributes['ADMIN'] == "Macedonia":
        country.attributes['ADMIN'] = "North Macedonia"
    elif country.attributes['ADMIN'] == "Czechia":
        country.attributes['ADMIN'] = "Czech Republic"

euroList = [e for e in euroList if e.attributes['ADMIN'] in countrylist]

w = World(euroList, boundaries)
#w.printStatus()

print()
print("=== Battles! ===")
while w.winCondition() == False:
    if w.marker == 1:
        w.comment = "This was the political situation at the start of 2020. Soon, everything would be set ablaze..."
    #saveImg(w.marker-1, w.comment)
    w.advance()

#saveImg(w.marker-1, w.comment)
#webbrowser.open(ab.link)