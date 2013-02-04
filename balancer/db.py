
## DB schema
_transactions_schema = [
        # primary key
        ('id', 'integer', 'primary key'),
        ('account', 'integer not null', 'references accounts(id)'),
        ('amount', 'integer not null', ''),
        ('date', 'datetime not null', ''),
        ('payee', 'varchar not null', ''),

        # classification
        ('category', 'integer', 'references categories(id)'),
        ('comment', 'varchar', ''),

        # misc supplementary info
        ('bank_memo', 'varchar', ''),
        ('bank_id', 'varchar', ''),
        ('bank_type', 'varchar', ''),
        ]

_accounts_schema = [
        ('id', 'integer', 'primary key'),
        ('number', 'varchar not null', 'unique'),
        ]

_categories_schema = [
        ('id', 'integer', 'primary key'),
        ('category', 'varchar not null', 'unique'),
        ]

# order is important here because of external keys
_tables = [
        ('transactions', _transactions_schema),
        ('accounts', _accounts_schema),
        ('categories', _categories_schema),
        ]

_backup_trigger = """
create trigger on_{table}_{command} after {command} on {table}
    for each row begin
        insert into {table}_backup values (datetime('now'), '{command}', {data});
    end
"""

def init_db(con):
    def create_table(name, col_defs):
        cols = map(lambda c: '{} {} {}'.format(*c), col_defs)
        return 'create table {} ({})'.format(name, ', '.join(cols))

    def create_backup(name, col_defs):
        cols = [
                'backup_date datetime not null',
                'backup_op varchar not null'
                ]
        cols += map(lambda c: '{} {}'.format(*c[0:2]), col_defs)
        return 'create table {}_backup ({})'.format(name, ', '.join(cols))

    def create_trigger(name, op, newold, col_defs):
        cols = map(lambda c: '{}.{}'.format(newold, c[0]), col_defs)
        return _backup_trigger.format(table=name, command=op, data=', '.join(cols))

    with con:
        map(lambda t: con.execute(create_table(t[0], t[1])), _tables)
        map(lambda t: con.execute(create_backup(t[0], t[1])), _tables)
        map(lambda t: con.execute(create_trigger(t[0], 'insert', 'NEW', t[1])), _tables)
        map(lambda t: con.execute(create_trigger(t[0], 'update', 'NEW', t[1])), _tables)
        map(lambda t: con.execute(create_trigger(t[0], 'delete', 'OLD', t[1])), _tables)


#con.execute('PRAGMA foreign_keys=ON')

import sqlite3
con = sqlite3.connect('t.db')
init_db(con)
