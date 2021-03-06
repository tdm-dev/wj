import re
import datetime
from collections import Counter
import wj.cal

def _getTagsFromEntry(string):
    tags = string.replace(' ','').lstrip('@').split('@')
    if(len(tags)==1 and tags[0]==''):
        return set()
    else:
        return set(tags)

def _tags2str(tags):
    str = ''
    for tag in tags:
        str = str + ' @'+tag
    return str

def readFile(fname):
    """Opens and processes the file 'fname' and returns a dictionary that
contains the journal entries.

    """
    dateDict = {}
    dateRE = re.compile('(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)')
    tagRE = re.compile('\B@(\w+)')
    entryRE = re.compile('\A- ')
    with open(fname,'r') as f:
        for line in f:
            l = line.rstrip()
            dateMatch = dateRE.match(l)
            if dateMatch:
                d = datetime.date(int(dateMatch.group('year')),int(dateMatch.group('month')),int(dateMatch.group('day')))
                dateDict[d] = []
                lastDate = d
            if entryRE.match(l):
                bothSides = l.strip('- ').split('.')
                tags = _getTagsFromEntry(bothSides[1])
                dateDict[lastDate].append((bothSides[0],tags))
    return dateDict

def writeFile(fname,dateDict):
    """Saves the journal entries in a plain text format to 'fname'."""
    with open(fname,'w') as f:
        for date in sorted(dateDict.keys()):
            print(date.isoformat()+'\n',file=f)
            for (entry,tags) in dateDict[date]:
                print('- '+entry+'.'+_tags2str(tags),file=f)
            print(file=f)

def addNewEntry(entry,dateDict,date=datetime.date.today()):
    """Add a new entry to the journal for a particular date. If no date
is given, today's date is used."""
    bothSides = entry.split('.')
    if(len(bothSides)==1):
        print("Can't split on full stop.")
        return
    if date not in dateDict.keys():
        dateDict[date] = []
    tags = _getTagsFromEntry(bothSides[1])
    dateDict[date].append((bothSides[0],tags))
    
def _countTags(dateDict):
    c = Counter()
    for date,val in dateDict.items():
        for entry,tags in val:
            for tag in tags:
                c[tag] += 1
    return c

def _countEntries(dateDict):
    nentry = 0
    for date,val in dateDict.items():
        for entry,tags in val:
            nentry = nentry + 1
    return nentry

def printTags(dateDict):
    """Print a list of all the tags used within the journal."""
    tags = _countTags(dateDict)
    print('The following tags are used:')
    for tag,count in tags.most_common():
        print('    '+tag)

def printSummary(dateDict):
    """Print a short summary of the journal."""
    nentry = _countEntries(dateDict)
    l = list(dateDict.keys())
    l.sort()
    print('File contains {} entries from {} to {}.'.format(nentry,l[0].isoformat(),l[len(l)-1].isoformat()))
    printTags(dateDict)

def printEntriesWithTag(tag,dateDict):
    """Print all the journal entries that use a given tag."""
    tmpDict = {}
    for date,val in dateDict.items():
        for entry,tags in val:
            if tag in tags:
                if date not in tmpDict.keys():
                    tmpDict[date] = []
                tmpDict[date].append((entry,tags))
    for date in sorted(tmpDict):
        for entry,tags in tmpDict[date]:
            print(date.isoformat()+' '+entry+'.'+_tags2str(tags))

def printCal(tag,dateDict):
    year = datetime.date.today().year
    dateSet = set()
    for date,val in dateDict.items():
        for entry,tags in val:
            if tag in tags:
                dateSet.add(date)
    wj.cal.printYear(year,dateSet)

def printTotalEffort(tag,dateDict):
    """Print the total effort put into the task with a given tag."""
    from pint import UnitRegistry
    _ureg = UnitRegistry()
    total = None
    for date,val in dateDict.items():
        for entry,tags in val:
            if tag in tags:
                splitEntry = entry.split(';')
                if len(splitEntry)==2:
                    if total is None:
                        total = _ureg(splitEntry[1])
                    else:
                        total += _ureg(splitEntry[1])
    if total.dimensionality=={'[time]':1.0}:
        print('{0:.2f} '.format(total))
    else:
        print(total)

def printEntriesForDate(date,dateDict):
    """Print the journal entries for a particular date."""
    if date in dateDict.keys():
        for (entry,tags) in dateDict[date]:
            print('- '+entry+'.'+_tags2str(tags))

def printDateRange(startDate,endDate,dateDict):
    """Print entries that fall within a particular date range. Start and
end dates are in datetime format."""
    d = startDate
    delta = datetime.timedelta(days=1)
    while d <= endDate:
        if d in dateDict.keys():
            print(d.isoformat())
            printEntriesForDate(d,dateDict)
            print()
        d+=delta

def printTSV(dateDict):
    """Output all of the entries as a tab separated file."""
    tags = _countTags(dateDict)
    print("date\tentry",end='')
    for tag in tags:
        print('\t'+str(tag),end='')
    print()
    for date in sorted(dateDict.keys()):
        for (entry,entrytags) in dateDict[date]:
            print(date.isoformat(),end='')
            print('\t'+str(entry),end='')
            for t in tags:
                if t in entrytags:
                    print('\t'+"1",end='')
                else:
                    print('\t'+"0",end='')
            print()
    return
