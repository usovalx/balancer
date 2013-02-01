#!/usr/bin/python2
import re
import sys
from bs4 import BeautifulSoup

def parse(file_name):
    doc = BeautifulSoup(file(file_name))

    # statement data is in the table
    table = doc.find('table', attrs={'summary': re.compile('statement')})
    header = map(lambda h: h.text.strip(), table.thead.find_all('th'))
    data = []
    for row in table.tbody.find_all('tr'):
        data.append(map(lambda c: c.text.strip(), row.find_all('td')))

    # Account number
    account = doc.find('div', attrs={'class': 'hsbcAccountNumber'}).text.strip()

    # date, account number, 

    return doc, header, data, account

#s, h, d = parse('13 jan.html')
#fmt = u'{:6} {:4} {:20} {:10} {:10} {:10}'
#d.insert(0, h)
#for l in d:
    #print fmt.format(*l)
