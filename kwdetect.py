import re
import string
from thefuzz import fuzz, process
from confighandler import loadConfig, lockC
# See: https://pypi.org/project/thefuzz/
# See: https://www.datacamp.com/tutorial/fuzzy-string-python

UNSAFEKEYWORDS = []

## Templates
# NB: some browsers add text after the tab name (and before the window / app name), so focusing on the beginning of the window title string
# {} - Google Search
# {} - Search Images
# {} at DuckDuckGo
# {} - YouTube
# Search: {} | Flickr
# {} — Yandex: 4 thousand results found
# {}: 2 thousand results found in Yandex Images
# {} — \u042f\u043d\u0434\u0435\u043a\u0441
# {} | \u0414\u0437\u0435\u043d
# {}_\u767e\u5ea6\u641c\u7d22
# {}_\u767e\u5ea6\u56fe\u7247\u641c\u7d22
# {}: 2 \u0442\u044b\u0441 \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0439 \u043d\u0430\u0439\u0434\u0435\u043d\u043e \u0432 \u042f\u043d\u0434\u0435\u043a\u0441 \u041a\u0430\u0440\u0442\u0438\u043d\u043a\u0430\u0445
# reddit.com: search results - {} - Google Chrome
# {} - Reddit Search! - Google Chrome

# Included for Reference
# patternsAll = [    
#     r"^(.*)( \- Google Search)(.*)", # Google Search
#     r"^(.*)( \- Search)(.*)", # Bing Search
#     r"^(.*)( \- Search Images)(.*)", # Bing Search (Images)
#     r"^(.*)( at DuckDuckGo)(.*)", # DuckDuckGo
#     r"^(.*)( \- YouTube)(.*)", # YouTube
#     r"^Search: (.*)( \| Flickr)(.*)", # Flickr
#     r"^(.*)( \— Yandex)(.*)", # Yandex
#     r"^(.*)(\: [\w|\s]* Yandex Images)(.*)", # Yandex Images
#     r"^(.*)( \— \u042f\u043d\u0434\u0435\u043a\u0441)(.*)", # Yandex RU
#     r"^(.*)(\: [\w|\s]* \u042f\u043d\u0434\u0435\u043a\u0441 \u041a\u0430\u0440\u0442\u0438\u043d\u043a\u0430\u0445)(.*)", # Yandex RU Images
#     r"^(.*)( \| \u0414\u0437\u0435\u043d)(.*)", # Dzien
#     r"^(.*)(\_\u767e\u5ea6\u641c\u7d22)(.*)", # Baidu
#     r"^(.*)(\_\u767e\u5ea6\u56fe\u7247\u641c\u7d22)(.*)" # Baidu Image Search
# ]


def detectSearch(fgwindow):
    '''Detect search terms using regex patterns.'''
    patterns = [
        r"^(?:Search\:)?(.*)(( \-| \—| \|| at|\:) (Google |Reddit )?(Search!?|YouTube|[\w|\s]*Yandex|Flickr|DuckDuckGo)( Images)?)(.*)", # Google, Bing, YouTube, Flickr, DuckDuckGo, Yandex, Reddit
        r"^(.*)(( \—|\:) [\w|\s]*\u042f\u043d\u0434\u0435\u043a\u0441(?: \u041a\u0430\u0440\u0442\u0438\u043d\u043a\u0430\u0445)?)(.*)", # Yandex RU / Images
        r"^(.*)( \| \u0414\u0437\u0435\u043d)(.*)", # Dzien
        r"^(.*)(\_\u767e\u5ea6(?:\u641c\u7d22|\u56fe\u7247\u641c\u7d22))(.*)", # Baidu / Baidu Image Search
        r"^reddit.com: search results - (.*)-(.*)" # Old Reddit (TODO: Rough Match!)
    ] 

    searchterm = None
    for pn in patterns:
        match = re.search(pn, fgwindow)
        if match: # found match with search engine
            searchterm = match.group(1)
            # Cleaning: Remove punctuation and make sure all spaces are single spaces
            st_nodash = ''.join(searchterm.split('-')) # currently: not replacing dashes
            searchterm = ' '.join(word.strip(string.punctuation) for word in st_nodash.split())
            break
    pass

    return searchterm

def readKeyWords():
    '''Read Unsafe keywords from config, for keyword match'''
    #print('Reading Keywords')
    #with lockK:
    global UNSAFEKEYWORDS
    kws = loadConfig(lockC)['Unsafe_Keywords']['unsafe_kws']
    UNSAFEKEYWORDS = kws.split('\n')
    #print('Finished Reading Keywords')
    return UNSAFEKEYWORDS

def kw_check(fgwindow, kwissearch = False):
    '''Keyword check using Python kw... in for...'''
    # Defaults
    kwfound = False
    kw = None
    score = None

    #kwfound = any(kw in fgwindow for kw in UNSAFEKEYWORDS)

    # Is this a search term?
    if kwissearch == True:
        searchterm = fgwindow
    else:
        searchterm = detectSearch(fgwindow)

    # If this is a search, use the search term, else use the whole window text
    if (searchterm == None): # no match with search engine (could be another site)
        testingwords = fgwindow
    else:
        kwissearch = True
        testingwords = searchterm

    #with lockK:
    for kw in UNSAFEKEYWORDS:
        if kw in testingwords:
            kwfound = True
            return kwfound, kwissearch, kw, score

    if (kwissearch == True) and (not kwfound): # try fuzzy string matching, but only if kw is a search term
        # TODO: maybe add a feature that probes other sites in future, for now focusing on search
        #searchterm = ''.join(fgwindow.split('-')[:-1]).strip() # use the whole window text, leaving out the app name
        kwfound, kw, score = kw_check_fuzz(testingwords)

    return kwfound, kwissearch, kw, score

def kw_check_fuzz(testingwords):
    '''Keyword check using fuzzy string matching with thefuzz'''

    similaritythreshold = 80 # default

    #kwmatch = process.extractOne(testingwords, UNSAFEKEYWORDS, scorer=fuzz.token_set_ratio) # doesn't care about order
    kwmatch = process.extractOne(testingwords, UNSAFEKEYWORDS, scorer=fuzz.partial_ratio) # cares about order (searches for shorter string in longer)
    if not kwmatch:
        return False, None, None # kwfound, kw, score
    score = int(kwmatch[1])
    if score == 100:
        # run an intervention?
        return True, kwmatch[0], kwmatch[1] # kwfound, kw, score
    elif int(kwmatch[1]) >= similaritythreshold:
        # run an extra check for obfuscation (with numbers)
        testingwords_nodigits = ''.join((x for x in testingwords if not x.isdigit()))
        if kwmatch[0] == testingwords_nodigits:
            return True, kwmatch[0], None # kwfound, kw, score (None for score: triggers an intervention if keyword is search term)
        elif testingwords != testingwords_nodigits:
            kwfound, kwissearch, kw, score = kw_check(testingwords_nodigits,True) # recursive call. True because this is a search term.
            return kwfound, kw, score
        else:
            return True, kwmatch[0], kwmatch[1] # kwfound, kw, score
    else: 
        return False, None, None # kwfound, kw, score

def kw_check_test(fgwindow):
    '''Keyword check using Python kw... in for...'''
    for kw in UNSAFEKEYWORDS:
        if kw in fgwindow:
            return kw
    return False


# Keep for testing
if __name__ == "__main__":
    #from threading import Lock
    #lock = Lock()
    print(readKeyWords())
    #print(kw_check('A bucket of fish - Google Search - Google Chrome'))
    #print(kw_check_test('A bucket of fish - Google Search - Google Chrome'))
    #print(kw_check_fuzz ('A bucket of fish - Google Search - Google Chrome'))
    #print(kw_check_fuzz ('Dragons - Abracadabra Website Now - Microsoft Edge'))
