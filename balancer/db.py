import sqlite3

## DB schema
_transactions_schema = [
        ('id', 'integer', 'primary key'),
        ('account', 'integer not null', 'references accounts(id)'),
        ('amount', 'integer not null', ''),
        ('date', 'datetime not null', ''),
        ('payee', 'varchar not null', ''),
        # import tag
        ('import_id', 'integer not null', 'references imports(id)'),

        # classification
        ('category', 'integer', 'references categories(id)'),
        ('comment', 'varchar', ''),

        # misc supplementary info
        ('bank_memo', 'varchar', ''),
        ('bank_id', 'varchar', ''),
        ('trn_type', 'varchar', ''),
        ]

_balances_schema = [
        ('id', 'integer', 'primary key'),
        ('account', 'integer not null', 'references accounts(id)'),
        ('amount', 'integer not null', ''),
        ('date', 'datetime not null', ''),
        # import tag
        ('import_id', 'integer not null', 'references imports(id)'),
        ]

_accounts_schema = [
        ('id', 'integer', 'primary key'),
        ('number', 'varchar not null', 'unique'),
        ('nick', 'varchar', 'unique'),
        ('description', 'varchar', ''),
        ]

_categories_schema = [
        ('id', 'integer', 'primary key'),
        ('category', 'varchar not null', 'unique'),
        ]

_imports_schema = [
        ('id', 'integer', 'primary key'),
        ('date', 'datetime not null', ''),
        ('description', 'varchar', ''),
        ('raw_data', 'blob', ''),
        ]

# order is important here because of external keys
_tables = [
        ('transactions', _transactions_schema),
        ('balances', _balances_schema),
        ('accounts', _accounts_schema),
        ('categories', _categories_schema),
        ('imports', _imports_schema),
        ]

_backup_trigger = """
create trigger on_{table}_{command} after {command} on {table}
    for each row
    begin
        insert into {table}_backup values (datetime('now'), '{command}', {data});
    end
"""

_schema_version = 1


def _init_db(con):
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

    with con:
        con.execute('create table _balancer_version (version integer not null)')
        con.execute('insert into _balancer_version values (?)', [_schema_version])

def open_db(path):
        # check version in the DB
        con = sqlite3.connect(path)
        req = "select name from sqlite_master " + \
                "where type='table' and name='_balancer_version'"
        initialized = True if con.execute(req).fetchone() else False

        if initialized:
            v = con.execute("select max(Version) from _balancer_version").fetchone()
            assert(v[0] == _schema_version)
        else:
            _init_db(con)

        return Db(con)

class Db:
    def __init__(self, con):
        self.con = con
        con.execute('PRAGMA foreign_keys=ON') 

