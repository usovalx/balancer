from . import btypes
import re

def textByLabel(doc, label):
    """Some of the data we need is labelled text"""
    rlabel = re.compile(label)
    l = filter(lambda n: re.search(rlabel, n.text),
            doc('div', 'hsbcTextLeft'))
    assert(len(l) == 1)
    return l[0].find_next_sibling('div', 'hsbcTextRight').text.strip()

def parse_statement(raw_data):
    """Scrape account details & transaction details from HSBC html-statement"""
    from bs4 import BeautifulSoup
    from dateutil.parser import parse as parse_date

    doc = BeautifulSoup(raw_data)

    # statement data is in the table
    table = doc.find('table', attrs={'summary': re.compile('statement')})
    header = map(lambda h: h.text.strip(), table.thead('th'))
    data = []
    for row in table.tbody('tr'):
        data.append(map(lambda c: c.text.strip(), row('td')))

    # account number
    acc_num = doc.find('div', 'hsbcAccountNumber').text.strip()
    acc_num = filter(lambda c: c.isdigit(), acc_num)

    # statement date
    st_date = parse_date(textByLabel(doc, 'Statement date'))

    # now we need to parse all that stuff and convert it into well-formatted data
    # first few asserts to ensure table header is what we expect it to be
    assert(len(header) == 6)
    assert(header[0:5] == ['Date', 'Type', 'Description', 'Paid out', 'Paid in'])
    assert(re.match('Balance', header[5]))

    def balance(date, row):
        assert(row[5] != '')
        amount = '-' + t[5] if t[6] == 'D' else t[5]
        return btypes.Balance(amount, date)

    trns = []
    for t in data:
        date = parse_date(t[0], default=st_date)
        if t[1] == '':
            trns.append(balance(date, t))
            continue
        amount = '-' + t[3] if t[3] != '' else t[4]
        trn = btypes.Transaction(amount, date, t[2])
        trn.trn_type = t[1]
        trns.append(trn)
        if t[5] != '':
            trns.append(balance(date, t))

    return [(acc_num, trns)]


#def parse_ofx(file_name):
    #from ofxparse import OfxParser
    ## FIXME: in python 3 moved to html.parser 
    #from HTMLParser import HTMLParser

    #data = OfxParser.parse(file(file_name))
    #parser = HTMLParser()

    #acc_num = data.account.number
    #trns = []
    #for t in data.account.statement.transactions:
        #trn = btypes.Transaction(t.amount, t.date, parser.unescape(t.payee))
        #trn.bank_memo = parser.unescape(t.memo)
        #trn.bank_id = t.id
        #trn.trn_type = t.type
        #trns.append(trn)

    ## just for better readability
    #trns.reverse()

    ## guess -- balance is for the final date
    #trns.append(btypes.Balance(
        #data.account.statement.balance,
        #data.account.statement.end_date))

    #return [(acc_num, trns)]
