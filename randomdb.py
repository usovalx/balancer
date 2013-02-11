#!/usr/bin/python2
import datetime
import decimal
import random

from balancer import schema, db

payees = random.sample(file('/usr/share/dict/words').readlines(), 200)
accts = ['11223344', '77659394', '843942342']
accts = map(lambda n: schema.Account(number = n, nick = n), accts)
imports = map(lambda x: schema.ImportInfo(), range(10))


d1 = datetime.date(2006, 1, 1)
while d1 < datetime.date(2013, 2, 1):
    imp = random.choice(imports)
    acc = random.choice(accts)

    for n in range(random.randint(1, 10)):
        v = random.random()*400 - 200
        v = decimal.Decimal(int(v*100))/100
        t = schema.Transaction(
                account = acc, 
                amount=v, 
                date = d1, 
                payee = random.choice(payees),
                import_info = imp)
        imp.transactions.append(t)
    imp.balances.append(schema.Balance(
        account = acc,
        balance = v,
        date = d1,
        import_info = imp))
    d1 += datetime.timedelta(days = random.randint(1, 5))

d = db.Db('t.db')
d.add_all(accts)
d.add_all(imports)
d.commit()

