from django.shortcuts import render
from django.http import HttpResponse
from .models import pokemon
from django.template import loader
import datetime


# my views

def home(request):
    return render(request, 'base_search.html')

# perhaps in the future | could be a table of all mons and their counters
def pokemonAll(request):
    html = "<html><body> snorlax </body></html>"
    return HttpResponse(html)

# main page that is seen after searching for a mon
def pokemonBio(request, name):
    mon = pokemon()
    mon.name = name.lower()
    found = 0;
    with open('lists/pokedex.txt', 'r') as f:
        while found == 0:
            line = f.readline().lower()
            i = line.find(mon.name)
            if i != -1:
                found = 1
                mon.type = findTypes(line)[:-1]
    indef = "a"
    vowels = ['a', 'e', 'i', 'o', 'u']
    if mon.type[0] in vowels:
        indef = "an"
    typePrimary   = ""
    typeSecondary = ""
    t2Display = "hidden"
    if len(mon.type.split("|")) > 1:
        typePrimary   = mon.type.split("|")[0]
        typeSecondary = mon.type.split("|")[1]
        t2Display = "visible"
    else:
        typePrimary = mon.type
    lastItemInNoEffList = ""
    if len(getNoEffectDefense(mon.type)) != 0:
        lastItemInNoEffList = getNoEffectDefense(mon.type)[-1]
    context = {
        "article": indef,
        "name": mon.name,
        "type": mon.type,
        "type1": typePrimary,
        "type2": typeSecondary,
        "icon1": "icon " + typePrimary,
        "iconPath1": "links/images/svg/" + typePrimary + ".svg",
        "type2Display": t2Display,
        "icon2": "icon " + typeSecondary,
        "iconPath2": "links/images/svg/" + typeSecondary + ".svg",
        "wkList": cleanse(getWeaknesses(mon.type)),
        "notEffList": cleanse(getNotEffective((mon.type))),
        "noEffList": cleanse(getNoEffectDefense(mon.type)),
        "lastItemWk": getWeaknesses(mon.type)[-1],
        "lastItemNotEff": getNotEffective(mon.type)[-1],
        "lastItemNoEff": lastItemInNoEffList,
        "lenWk": len(getWeaknesses(mon.type)),
        "lenNotEff": len(getNotEffective(mon.type)),
        "lenNoEff": len(getNoEffectDefense(mon.type)),
        # "weaknesses": getWeaknesses(mon.type),            these are unneeded, but
        # "notEffective": getNotEffective(mon.type),        to implement the (2x) feature with
        # "noEffect": getNoEffectDefense(mon.type),         types that are 2x as effective, this will be neededd
    }
    return render(request, 'mon_page.html', context)


# returns a string | determines the types of the mon given a line from the pokedex.txt
def findTypes(line):
    line = line.replace("{", "")
    line = line.replace("}", "")
    typeList = line.split("|")
    type1 = typeList[5]
    if len(typeList) == 7:
        type2 = typeList[6]
        return type1 + "|" + type2
    return type1


# returns the types that are super effective on the mon
def getWeaknesses(type):
    wks = []
    if type.find("|") == -1:
        return weakDict.get(type)
    type1 = type.split("|")[0]
    type2 = type.split("|")[1]
    for t in weakDict.get(type1):  # for every item in the list of types that do 2x dmg to type1
        if t in strongDict.get(type2) or t in noneToList(noeffDict.get(type2)):  # if item does 1/2 dmg to type 2
            continue  # if item does 0 dmg to type 2, item is not added
        if t in weakDict.get(type2):  # if item also does 2x dmg to type2, it is uppercased to signify 4x dmg
            wks.append(t.upper())
        else:
            wks.append(t)
    for t in weakDict.get(type2):  # for every item in the list of types that do 2x dmg to type2
        if t.upper() not in wks and t not in strongDict.get(type1) and t not in noneToList(noeffDict.get(type1)):
            wks.append(t)  # if the item is alr in wks, the item does 1/2 dmg to type1,
    return wks  # or the item does 0 dmg to type1, then it is not appended


# returns the types that the mon is not effective against, uses similar logic as method above
def getNotEffective(type):
    neff = []
    if type.find("|") == -1:
        return weakAtkDict.get(type)
    type1 = type.split("|")[0]
    type2 = type.split("|")[1]
    for t in weakAtkDict.get(type1):
        if t in strongAtkDict.get(type2) or t in noneToList(noeffDict.get(type2)):
            continue
        if t in weakAtkDict.get(type2):
            neff.append(t.upper())
        else:
            neff.append(t)
    for t in weakAtkDict.get(type2):
        if t.upper() not in neff and t not in strongAtkDict.get(type1) and t not in noneToList(noeffDict.get(type1)):
            neff.append(t)
    return neff


# returns the types that have no effect against the mon
def getNoEffectDefense(type):
    if type.find("|") == -1:
        return noneToList(noeffDictOffense.get(type))
    type1 = type.split("|")[0]
    type2 = type.split("|")[1]
    return noneToList(noeffDictOffense.get(type1)) + noneToList((noeffDictOffense.get(type2)))


# converts a none value to a list, if the arg is a list, it doesn't change
def noneToList(list):
    if list is None:
        return []
    return list

# converts a list into a grammatically correct string
def listToString(list):
    str = ""
    for x in range(0, len(list)):
        if list[x] == list[x].upper():
            list[x] = list[x].lower() + "(2x)"
    if len(list) == 1:
        return list[0] + ""
    if len(list) == 2:
        return list[0] + " and " + list[1]
    for item in list:
        if item == list[len(list) - 1]:
            return str + "and " + item
        str = str + item + ", "
    return "no types"

# lowers all strings in a list
def cleanse(list):
    for i in range(0,len(list)):
        list[i] = list[i].lower()
    return list
# I'll make something more efficient eventually
# global dictionary | each key is a type and each value is a list of types that do 2x dmg against the key
weakDict = {"normal": ["fighting"], "fire": ["ground", "water", "rock"],
            "water": ["electric", "grass"], "electric": ["ground"],
            "grass": ["fire", "ice", "poison", "flying", "bug"],
            "ice": ["fire", "fighting", "rock", "steel"], "fighting": ["flying", "psychic", "fairy"],
            "poison": ["ground", "psychic"], "ground": ["water", "grass", "ice"],
            "flying": ["electric", "ice", "rock"], "psychic": ["bug", "ghost", "dark"],
            "bug": ["fire", "flying", "rock"],
            "rock": ["water", "grass", "fighting", "ground", "steel"], "ghost": ["ghost", "dark"],
            "dragon": ["ice", "dragon", "fairy"],
            "dark": ["fighting", "bug", "fairy"], "steel": ["fighting", "ground", "fire"],
            "fairy": ["poison", "steel"]}

# global dictionary | each key is a type and each value is a list of types that do 1/2 dmg against the key
strongDict = {"normal": [], "fire": ["fire", "grass", "bug", "ice", "steel, fairy"],
              "water": ["fire", "water", "ice", "steel"], "electric": ["electric", "flying", "steel"],
              "grass": ["water", "electric", "grass", "ground"], "ice": ["ice"],
              "fighting": ["bug", "rock", "dark"], "poison": ["grass", "fighting", "poison", "bug", "fairy"],
              "ground": ["poison", "rock"], "flying": ["grass", "fighting", "bug"],
              "psychic": ["fighting", "psychic"], "bug": ["grass", "fighting", "ground"],
              "rock": ["normal", "fire", "poison", "flying"], "ghost": ["poison", "bug"],
              "dragon": ["fire", "water", "electric", "grass"],
              "dark": ["dark", "ghost"],
              "steel": ["normal", "grass", "ice", "psychic", "flying", "bug", "rock", "dragon", "steel", "fairy"],
              "fairy": ["fighting", "bug", "dark"]}

# global dictionary | each key is a type and each value is a type that has no effect on the key
noeffDict = {"normal": ["ghost"], "ground": ["electric"], "flying": ["ground"],
             "ghost": ["normal", "fighting"], "dark": ["psychic"], "steel": ["poison"], "fairy": ["dragon"]}

# global dictionary | same thing, keys and vals reversed
noeffDictOffense = {"ghost": ["normal"], "normal": ["ghost"], "electric": ["ground"], "fighting": ["ghost"],
                    "poison": ["steel"], "ground": ["flying"], "psychic": ["dark"], "dragon": ["fairy"]}

# global dictionary | each key is a type and each value is a list of types that the key is weak against (on attack)
weakAtkDict = {"normal": ["rock", "steel"], "fire": ["fire", "water", "rock", "dragon"],
               "water": ["water", "grass", "dragon"], "electric": ["electric", "grass", "dragon"],
               "grass": ["fire", "grass", "poison", "flying", "bug", "dragon", "steel"],
               "ice": ["fire", "water", "ice", "steel"], "fighting": ["poison", "flying", "psychic", "bug", "fairy"],
               "poison": ["poison", "ground", "rock", "ghost"], "ground": ["grass", "bug"],
               "flying": ["electric", "rock", "steel"], "psychic": ["psychic", "steel"],
               "bug": ["fire", "fighting", "poison", "flying", "ghost", "steel", "fairy"],
               "rock": ["fighting", "ground", "steel"], "ghost": ["dark"], "dragon": ["steel"],
               "dark": ["fighting", "dark", "fairy"], "steel": ["fire", "water", "electric", "steel"],
               "fairy": ["fire", "poison", "steel"]}

# global dictionary | each key is a type and each value is a list of types that the key is strong against
strongAtkDict = {"normal": ["rock", "steel"], "fire": ["grass", "ice", "bug", "steel"],
                 "water": ["fire", "ground", "rock"], "electric": ["water", "flying"],
                 "grass": ["water", "ground", "rock"], "ice": ["grass", "ground", "flying", "dragon"],
                 "fighting": ["normal", "ice", "rock", "dark", "steel"], "poison": ["grass", "fairy"],
                 "ground": ["fire", "electric", "poison", "rock", "steel"], "flying": ["grass", "fighting", "bug"],
                 "psychic": ["fighting", "poison"], "bug": ["grass", "psychic", "dark"],
                 "rock": ["fire", "ice", "flying", "bug"], "ghost": ["psychic", "dark"], "dragon": ["dragon"],
                 "dark": ["psychic", "ghost"], "steel": ["fighting", "dragon", "dark"],
                 "fairy": ["fire", "poison", "steel"]}
