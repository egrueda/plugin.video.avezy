import os
import sys
import urllib
import urllib2
import json
from datetime import date
from datetime import time
from datetime import datetime

print (sys.version)

thedate = "25/05/2016"
print "La fecha es: " + thedate
#showDate  = datetime.strptime(thedate, "%d/%m/%Y").date()
showDate = datetime.strptime('2015-05-24', "%Y-%m-%d").date()
showDate = datetime.strptime('2015-05-24', "%Y-%m-%d").date()
showDate = datetime.strptime('2015-05-24', "%Y-%m-%d").date()
todayDate = datetime.today().date()

mylist = []
mylist.append(showDate)
mylist.append(todayDate)
print mylist[0]
print mylist[1]

if(showDate < todayDate):
  print "Pasado"
else:
  print "Actual"

jsonUrl = 'http://arenavision.esy.es/json.php?cat=baloncesto'
jsonSrc     = urllib2.urlopen(jsonUrl)
datos       = json.load(jsonSrc)
eventos     = datos['eventos']
last_update = datos['last_update']

for evento in eventos:
  showDate  = datetime.strptime(evento['fecha'], "%d/%m/%y").date()
  todayDate = datetime.today().date()
  if(showDate < todayDate):
    print evento['fecha'] + " pasado"
    color = 'grey'
  elif(showDate > todayDate):
    print evento['fecha'] + " futuro"
    color = 'black'
  else:
    print evento['fecha'] + " actual"
    color = 'skyblue'

title = "[COLOR "+color+"]" + evento['fecha'] + " " + evento['hora'] + "[/COLOR] " + evento['titulo']
print title
