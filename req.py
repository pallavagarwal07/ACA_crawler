import requests
from bs4 import BeautifulSoup
from tabulate import tabulate


numItems = int(raw_input("How many items to retrieve? "))
url = "http://en.wikipedia.org/w/index.php?title=Special:RecentChanges&limit="+str(numItems)+"&days=30"

# Try without proxy first, and if it doesn't work, switch to ironport.
try:
    r = requests.get(url).text
    if 'authenticate yourself' in r:
        throw(requests.exceptions.ProxyError)
except requests.exceptions.ProxyError:
    try:
        r = requests.get(url, proxies={'http':'http://ironport1.iitk.ac.in:3128/'}).text
    except requests.exceptions.SSLError:
        try:
            r = requests.get(url, proxies={'http':'http://ironport2.iitk.ac.in:3128/'}).text
        except requests.exceptions.SSLError:
            print "SSLError! Try logging to ironport1\/2 in browser and rerunning the script."
            exit()



soup = BeautifulSoup(r)
links = soup.find_all("ul", {"class": "special"})
arr = []
arr[:] = ([s, 'Edit', "", "", "", ""] for s in links[0].contents if 'Navigable' not in str(type(s)))

# Classify the retrieved data as Page created, deleted, minor edit, edit, user added, user blocked.
for itr in arr:
    dat = itr[0]
    for a in dat.contents:
        if 'Navigable' not in str(type(a)):
            class_ = unicode(a.get("class")).encode('utf8')
            if 'newpage' in class_:
                itr[1] = 'Page Created'
            elif 'blockExpiry' in class_:
                itr[1] = 'User Block'
            elif 'minoredit' in class_:
                itr[1] = 'Minor Edit'
            elif 'Special:Log/newusers'in unicode(a.get("title")).encode('utf8'):
                itr[1] = 'New User'
            elif 'Special:Log/delete' in unicode(a.get("title")).encode('utf8'):
                itr[1] = 'Page Deleted'
            elif 'mw-plusminus' in class_:
                itr[2] = a.string.replace(",","")
            elif 'mw-userlink' in class_:
                itr[3] = a.string
            elif 'mw-title' in class_:
                itr[4] = a.find_all("a")[0].string 
            elif 'mw-changeslist-date' in class_:
                itr[5] = a.string
    itr[0] = ""

# Print the data in a neat and clean table
print tabulate(arr, headers=["", "Type", "Change", "User", "Page", "Time"])
