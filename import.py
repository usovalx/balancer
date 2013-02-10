#!/usr/bin/python2

import sys
import sqlalchemy.exc
import sqlalchemy
from balancer import db as balancer_db, schema, parser_hsbc

def main(argv):
    if len(argv) == 0:
        usage()
        sys.exit(1)

    try:
        db = balancer_db.Db('t.db')
    except Exception as e:
        err("can't open database: {}", e)
        sys.exit(1)

    for fname in argv:
        say("Importing {!r}", fname)

        try:
            # FIXME: hsbc_statement only for now
            import_info, import_data = parser_hsbc.parse_statement(fname)
        except Exception as e:
            err("can't parse document {!r}: {}", fname, e)
            continue

        # collate all data into single import
        # on the way, we need to find(create) account record for it
        for acc_num, txns, balances in import_data:
            acc = get_or_create_account(db, acc_num)
            for t in txns:
                t.account = acc
                import_info.transactions.append(t)
            for b in balances:
                b.account = acc
                import_info.balances.append(b)

        db.add(import_info)
        db.flush()

        # delete duplicate balances
        #b1 = schema.Balance
        #b2 = sqlalchemy.orm.aliased(schema.Balance)
        #c1 = db.query(b1).filter_by(import_info_id = import_info.id)\
                #.filter(sqlalchemy.sql.exists()
                        #.where(b1.id > b2.id)
                        #.where(b1.account_id == b2.account_id)
                        #.where(b1.balance == b2.balance)
                        #.where(b1.date == b2.date)
                        #).delete(synchronize_session=False)
        ## delete duplicate transactions
        #t1 = schema.Transaction
        #t2 = sqlalchemy.orm.aliased(schema.Transaction)
        #c2 = db.query(t1).filter_by(import_info_id = import_info.id)\
                #.filter(sqlalchemy.sql.exists()
                        #.where(t1.id > t2.id)
                        #.where(t1.account_id == t2.account_id)
                        #.where(t1.amount == t2.amount)
                        #.where(t1.date == t2.date)
                        #.where(t1.payee == t2.payee)
                        #).delete(synchronize_session=False)
        #print("Duplicates removed: {} balances and {} transactions".format(c1,c2))
        db.commit()

def get_or_create_account(db, num):
    acc = db.query(schema.Account).filter_by(number = num).first()
    if acc:
        return acc

    say("Account {} isn't known, create new one?", num)
    r = minput('[Y/n] ', isin(['', 'y', 'Y', 'n', 'N']))
    if r in ['', 'y', 'Y']:
        while True:
            nick = minput('Short (unique) nick: ', nonempty)
            name = minput('Descriptive name: ', nonempty)
            try:
                acc = schema.Account(number = num, nick = nick, name = name)
                db.add(acc)
                return acc
            except sqlalchemy.exc.IntegrityError as e:
                err(e)
    else:
        # FIXME: use different account
        raise Error('bad boy')

def usage():
    print("Usage: import <file> [<file> ...]")

def minput(prompt, stop_fcn):
    while True:
        r = raw_input(prompt)
        if stop_fcn(r):
            return r

def isin(variants):
    def check(s):
        return s.lower() in variants
    return check

def nonempty(s):
    return len(s) != 0

def err(fmt, *args):
    print("Error: " + fmt.format(*args))

def say(fmt, *args):
    print(fmt.format(*args))

if __name__ == "__main__":
    main(sys.argv[1:])
