import sqlite3
from . import btypes

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
        ('balance', 'integer not null', ''),
        ('date', 'datetime not null', ''),
        # import tag
        ('import_id', 'integer not null', 'references imports(id)'),
        ]

_accounts_schema = [
        ('id', 'integer', 'primary key'),
        ('number', 'varchar not null', 'unique'),
        ('nick', 'varchar', 'unique'),
        ('name', 'varchar', ''),
        ('comments', 'varchar', ''),
        ]

_categories_schema = [
        ('id', 'integer', 'primary key'),
        ('category', 'varchar not null', 'unique'),
        ]

_imports_schema = [
        ('id', 'integer', 'primary key'),
        ('date', 'datetime not null', ''),
        ('description', 'varchar', ''),
        ('raw_data_name', 'varchar', ''),
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

        if not initialized:
            _init_db(con)

        ver = con.execute("select max(version) from _balancer_version").fetchone()
        if len(ver) != 1 or ver[0] != _schema_version:
            raise Exception('Database schema incomplete or has wrong version number')

        return Db(con)

class Db(object):
    def __init__(self, con):
        self.con = con
        self.con.row_factory = sqlite3.Row
        con.execute('PRAGMA foreign_keys=ON') 

    def __insert(self, table, obj):
        import decimal
        req = 'insert into {table} ({fields}) values ({placeholders})'
        req = req.format(
                table = table,
                fields = ', '.join(obj.__dict__.keys()),
                placeholders = ', '.join(['?']*len(obj.__dict__)))
        values = map(
                lambda v: btypes._scale * int(v) if isinstance(v, decimal.Decimal) else v,
                obj.__dict__.values())
        return self.con.execute(req, values)

    def __select(self, table, cond = None, values = None):
        if cond:
            assert(values is not None)
            req = 'select * from {table} where {cond}'
            req = req.format(table = table, cond=cond)
            return self.con.execute(req, values)
        else:
            return self.con.execute('select * from {}'.format(table))

    def get_account(self, number):
        c = self.__select('accounts', 'number = ?', [number])
        r = c.fetchone()
        if r is not None:
            return btypes.Account.fromdb(r)

    def get_all_accounts(self):
        return map(btypes.Account.fromdb, self.__select('accounts').fetchall())

    def new_account(self, acc):
        with self.con:
            c = self.__insert('accounts', acc)
            c = self.__select('accounts', 'rowid = ?', [c.lastrowid])
            return btypes.Account.fromdb(c.fetchone())

    def save_import(self, info, data):
        with self.con:
            info.raw_data = sqlite3.Binary(info.raw_data)
            c = self.__insert('imports', info)
            import_id = c.lastrowid
            for accnt, txns in data:
                assert(accnt.id is not None)
                for t in txns:
                    t.account = accnt.id
                    t.import_id = import_id
                    # FIXME: move schema info into types themselves
                    if isinstance(t, btypes.Transaction):
                        self.__insert('transactions', t)
                    elif isinstance(t, btypes.Balance):
                        self.__insert('balances', t)
                    else:
                        raise TypeError("Objects of type {} are not supported".format(type(t)))
