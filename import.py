#!/usr/bin/python2

import StringIO
import sys
import sqlite3

from balancer import db as balancer_db, btypes, parser_hsbc

def main(argv):
    if len(argv) == 0:
        usage()
        sys.exit(1)

    try:
        db = balancer_db.open_db('t.db')
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

        # get accounts from DB or create a new ones
        for idx, (acc_num, txns) in enumerate(import_data):
            acc = get_or_create_account(db, acc_num)
            import_data[idx] = (acc, txns)

        # insert all this stuff into database
        db.save_import(import_info, import_data)

def get_or_create_account(db, num):
    acc = db.get_account(num)
    if acc:
        return acc

    say("Account {} isn't known, create new one?", num)
    r = minput('[Y/n] ', isin(['', 'y', 'Y', 'n', 'N']))
    if r in ['', 'y', 'Y']:
        while True:
            nick = minput('Short (unique) nick: ', nonempty)
            name = minput('Descriptive name: ', nonempty)
            try:
                return db.new_account(btypes.Account(num, nick, name))
            except sqlite3.IntegrityError as e:
                err(e)
    else:
        # FIXME: use different account
        raise Error('bad boy')

def usage():
    print("Usage: import <file>")

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
