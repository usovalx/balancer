import decimal
import sqlalchemy as s
from sqlalchemy.ext.declarative import declarative_base

# TODO:
# * see if non-declarative definition of tables + classes is more compact
# * read more about Column and relationship attributes
#   * lazy relationships
#   * query-based relationsips
#   * noload relations
#   * cascade
#   * passive_delete
# * figure out how create and configure backup tables
# * ?? use changesets to track units of changes

_schema = declarative_base()

# s doesn't properly handle conversions of decimal values
# to/from sqlite (yet). Store them as fixed-point integers
class _Decimal(s.TypeDecorator):
    impl = s.Integer
    def process_bind_param(self, value, dialect):
        return int(value*1000)

    def process_result_value(self, value, dialect):
        return decimal.Decimal(value)/1000

class Transaction(_schema):
    """Transaction info"""
    __tablename__ = 'transactions'

    # mandatory fields
    id = s.Column(s.Integer, primary_key=True)
    account_id = s.Column(s.Integer, s.ForeignKey('accounts.id'), nullable=False)
    account = s.orm.relationship('Account')
    amount = s.Column(_Decimal, nullable=False)
    date = s.Column(s.Date, nullable=False)
    payee = s.Column(s.String, nullable=False)
    import_info_id = s.Column(s.Integer, s.ForeignKey('import_info.id'), nullable=False)
    import_info = s.orm.relationship("ImportInfo")

    # classification
    category_id = s.Column(s.Integer, s.ForeignKey('categories.id'))
    category = s.orm.relationship('Category')

    # misc supplementary info
    bank_memo = s.Column(s.String)
    bank_id = s.Column(s.String)
    trn_type = s.Column(s.String)
    note_id = s.Column(s.Integer, s.ForeignKey('notes.id'))
    note = s.orm.relationship('Note')

    def __repr__(self):
        return '<Transaction({}, {}, {})>'.format(self.amount, self.date, self.payee)

class Balance(_schema):
    """Balance information as provided by bank"""
    __tablename__ = 'balances'

    id = s.Column(s.Integer, primary_key=True)
    account_id = s.Column(s.Integer, s.ForeignKey('accounts.id'), nullable=False)
    account = s.orm.relationship('Account')
    balance = s.Column(_Decimal, nullable=False)
    date = s.Column(s.Date, nullable=False)
    import_info_id = s.Column(s.Integer, s.ForeignKey('import_info.id'), nullable=False)
    import_info = s.orm.relationship("ImportInfo")

    def __repr__(self):
        return '<Balance({}, {})>'.format(self.balance, self.date)

class Account(_schema):
    """Known accounts"""
    __tablename__ = 'accounts'

    id = s.Column(s.Integer, primary_key=True)
    number = s.Column(s.String, nullable=False, unique=True)
    nick = s.Column(s.String, unique=True)
    name = s.Column(s.String)
    note_id = s.Column(s.Integer, s.ForeignKey('notes.id'))
    note = s.orm.relationship('Note')

    transactions = s.orm.relationship('Transaction')
    balances = s.orm.relationship('Balance')

    def __repr__(self):
        return '<Account({}, {})>'.format(self.number, self.nick)

class Category(_schema):
    """Categories we use to classify transactions"""
    __tablename__ = 'categories'

    id = s.Column(s.Integer, primary_key=True)
    category = s.Column(s.String, nullable=False, unique=True)
    note_id = s.Column(s.Integer, s.ForeignKey('notes.id'))
    note = s.orm.relationship('Note')

    transactions = s.orm.relationship('Transaction')

    def __repr__(self):
        return '<Category({})>'.format(self.category)

class ImportInfo(_schema):
    """Information about origin of the transactions/balances"""
    __tablename__ = 'import_info'

    id = s.Column(s.Integer, primary_key=True)
    date = s.Column(s.DateTime, nullable=False, server_default=s.text("(datetime('now'))"))
    description = s.Column(s.String)
    raw_data_id = s.Column(s.Integer, s.ForeignKey('raw_data.id'))
    raw_data = s.orm.relationship('RawData')

    transactions = s.orm.relationship('Transaction')
    balances = s.orm.relationship('Balance')

    def __repr__(self):
        return '<ImportInfo({}, {})>'.format(self.date, self.description)

class RawData(_schema):
    """Store compressed raw data from imports separately from ImportInfo to leverage lazy loading"""
    __tablename__ = 'raw_data'

    id = s.Column(s.Integer, primary_key=True)
    name = s.Column(s.String, nullable=False)
    data = s.Column(s.Binary, nullable=False)

    def __repr__(self):
        return '<RawData({}, {}b)>'.format(self.name, len(self.data))

class Note(_schema):
    """Notes storage for all tables which need it"""
    __tablename__ = 'notes'

    id = s.Column(s.Integer, primary_key=True)
    note = s.Column(s.String)

#backup = s.Table('backup', _schema.metadata,
        #s.Column('id', s.Integer, primary_key=True))
