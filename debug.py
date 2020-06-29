from os import system
import sys
from getcats import run
from __init__ import geolocbotMain
from databases import terencode, filtersimc, updatename
from querying import coords, getqid

system('cls')
for i in range(5):
    print()
trackgoal = geolocbotMain.input('Wpisz nazwę miejscowości, której przetwarzanie chcesz prześledzić: ')
print()
print('--- updatename():')
updatename(trackgoal)
print()
print('--- run():')
a = run(trackgoal)
geolocbotMain.output(a)
print()
print('--- terencode():')
b = terencode(a)
print(b)
print()
print('--- filtersimc():')
c = filtersimc(b)
geolocbotMain.output(c)
print()
print('--- getqid():')
d = getqid(c)
geolocbotMain.output(d)
print()
print('--- coords():')
e = coords(d)
geolocbotMain.output(e)
sys.exit()
