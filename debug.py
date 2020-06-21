from os import system
import sys
from getcats import run
from __init__ import geolocbot
from databases import terencode, filtersimc, updatename
from querying import coords, getqid

system('cls')
for i in range(5):
    print()
trackgoal = geolocbot.input('Wpisz nazwę miejscowości, której przetwarzanie chcesz prześledzić: ')
print()
print('--- updatename():')
updatename(trackgoal)
print()
print('--- run():')
a = run(trackgoal)
geolocbot.output(a)
print()
print('--- terencode():')
b = terencode(a)
print(b)
print()
print('--- filtersimc():')
c = filtersimc(b)
geolocbot.output(c)
print()
print('--- getqid():')
d = getqid(c)
geolocbot.output(d)
print()
print('--- coords():')
e = coords(d)
geolocbot.output(e)
sys.exit()
