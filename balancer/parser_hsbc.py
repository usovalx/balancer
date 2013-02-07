import bz2
import datetime
import os.path
import re
from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_date
from decimal import Decimal
from . import schema

def textByLabel(doc, label):
    """Some of the data we need is labelled text"""
    rlabel = re.compile(label)
    l = filter(lambda n: re.search(rlabel, n.text),
            doc('div', 'hsbcTextLeft'))
    assert(len(l) == 1)
    return l[0].find_next_sibling('div', 'hsbcTextRight').text.strip()

def parse_statement(fname):
    """Scrape account details & transaction details from HSBC html-statement"""
    raw_data = file(fname).read()
    doc = BeautifulSoup(raw_data)

    # account number
    acc_num = doc.find('div', 'hsbcAccountNumber').text.strip()
    acc_num = filter(lambda c: c.isdigit(), acc_num)

    # statement date
    st_date = parse_date(textByLabel(doc, 'Statement date')).date()

    # table with transactions
    table = doc.find('table', attrs={'summary': re.compile('statement')})
    header = map(lambda h: h.text.strip(), table.thead('th'))
    data = []
    for row in table.tbody('tr'):
        data.append(map(lambda c: c.text.strip(), row('td')))

    # now we need to parse all that stuff and convert it into well-formatted data
    # first few asserts to ensure table header is what we expect it to be
    assert(len(header) == 6)
    assert(header[0:5] == ['Date', 'Type', 'Description', 'Paid out', 'Paid in'])
    assert(re.match('Balance', header[5]))

    def get_date(txt):
        # dates in the statement don't have year on them
        # use st_date to fill in this gap, but be careful
        # when dates cross new year
        # ex: st_date = 31 Jan 2011
        # dates: 24 Dec & 24 Jan
        # naive parsing would extract them as Jan & Dec 2011
        # instead of Dec 2010 & Jan 2011
        date = parse_date(txt, default = st_date)
        if date > st_date:
            date = parse_date(
                    txt,
                    default = datetime.date(st_date.year-1, st_date.month, 1))
        return date

    def balance(date, row):
        assert(row[5] != '')
        balance = '-' + t[5] if t[6] == 'D' else t[5]
        return schema.Balance(balance = Decimal(balance), date = date)

    trns = []
    balances = []
    for t in data:
        date = get_date(t[0])
        if t[1] == '':
            balances.append(balance(date, t))
            continue
        amount = '-' + t[3] if t[3] != '' else t[4]
        trns.append(schema.Transaction(amount = Decimal(amount), date = date, payee = t[2], trn_type = t[1]))
        if t[5] != '':
            balances.append(balance(date, t))

    # finally create an import description
    import_info = schema.ImportInfo(
            description = 'HSBC statement from {} for account {}'.format(st_date, acc_num),
            raw_data = schema.RawData(
                name = os.path.basename(fname) + '.bz2',
                data = bz2.compress(raw_data)))

    return import_info, [(acc_num, trns, balances)]


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
