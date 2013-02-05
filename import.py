#!/usr/bin/python2

import StringIO
import bz2
import os.path
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
            raw_data = file(fname).read()
        except IOError as e:
            err("can't read {!r}: {}", fname, e)
            continue

        # FIXME: hsbc_statement only for now
        try:
            import_data = parser_hsbc.parse_statement(raw_data)
        except Exception as e:
            err("can't parse document {!r}: {}", fname, e)
            continue

        blob_name = os.path.basename(fname) + ".bz2"
        blob_data = bz2.compress(raw_data)

        # get accounts from DB or create a new ones
        for idx, (acc_num, _) in enumerate(import_data):
            acc = get_or_create_account(db, acc_num)

def get_or_create_account(db, num):
    acc = db.get_account(num)

    if acc is None:
        say("Account {} isn't registered, create new one?", num)
        r = minput('[Y/n] ', isin(['', 'y', 'Y', 'n', 'N']))
        if r in ['', 'y', 'Y']:
            while True:
                name = minput('Account name: ', nonempty)
                nick = minput('Shorter nick for convenience: ', nonempty)
                try:
                    acc = db.new_account(btypes.Account(num, name, nick))
                    break
                except sqlite3.IntegrityError as e:
                    err(e)
        else:
            # FIXME: use different account
            raise Error('bad boy')

    return acc

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
