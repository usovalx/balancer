import sqlalchemy as s
from sqlalchemy.ext.declarative import declarative_base

_schema = declarative_base()

class Task(_schema):
    __tablename__ = 'tasks'

    id = s.Column(s.Integer, primary_key=True)
    text = s.Column(s.String, nullable=False)
    date = s.Column(s.DateTime)
    done = s.Column(s.Boolean, default=False, nullable=False)

    tags = s.orm.relationship('Tag', secondary='task_tags', backref='tasks')

    def __repr__(self):
        return 'Task: ' + self.text

class Tag(_schema):
    __tablename__ = 'tags'

    id = s.Column(s.Integer, primary_key=True)
    name = s.Column(s.String, nullable=False)

    def __repr__(self):
        return 'Tag: ' + self.name

_task_tags = s.Table('task_tags', _schema.metadata,
        s.Column('task_id', s.Integer, s.ForeignKey('tasks.id', ondelete='cascade')),
        s.Column('tag_id', s.Integer, s.ForeignKey('tags.id', ondelete='cascade')))

def initDB():
    engine = s.create_engine('sqlite:///t.db', echo=False)

    @s.event.listens_for(engine, 'connect')
    def enable_foreign_keys(connection, record):
        connection.execute('PRAGMA foreign_keys=ON')

    _schema.metadata.create_all(engine)
    Session = s.orm.sessionmaker(bind=engine)
    return Session()

def main():
    db = initDB()

    green = Tag(name='green')
    red = Tag(name='red')

    t1 = Task(text='Do one', tags=[red])
    t2 = Task(text='Do two', tags=[red])
    t3 = Task(text='Do tree', tags=[green])
    t4 = Task(text='Do four', tags=[red, green])

    db.add_all([red, green])
    db.commit()
    print 'Greens:'
    print green.tasks
    print 'Reds:'
    print red.tasks
    print 'With t:'
    print db.query(Task).filter(Task.text.like('%t%')).all()

if __name__ == '__main__':
    main()

