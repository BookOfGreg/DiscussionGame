import sqlite3
import os
import operator
from random import randint

try:
    os.remove("./db.sqlite3")
except OSError:
    pass

DB_PATH = "./db.sqlite3"  # to be used when no file specified


class Argument:
    cursor = None
    conn = None

    def __init__(self, name, label=None, step=None):
        if label is None:
            label = "Undec"
        if step is None:
            step = 0
        self.name = name
        self.label = label
        self.step = step

    def set_label(self, labelling, step=0):
        Argument.cursor.execute(
            """UPDATE arguments SET label=?, step=? WHERE name=?""",
            (labelling, step, self.name))

    def plus(self):
        return set(self._to_args(
            Argument.cursor.execute("""SELECT target_id
                              FROM attacks JOIN arguments
                              ON attacker_id=arguments.id
                              AND arguments.name=?""",
                                    (self.name,)).fetchall()))

    targets = plus

    def minus(self):
        return set(self._to_args(
            Argument.cursor.execute("""SELECT attacker_id
                              FROM attacks JOIN arguments
                              ON target_id=arguments.id
                              AND arguments.name=?""",
                                    (self.name,)).fetchall()))

    attackers = minus

    def _to_args(self, relations):
        args = list()
        for attack in relations:
            arg = Argument._find_by_id(str(attack[0]))
            args.append(arg)
        return args

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.__repr__())

    def __repr__(self):
        return "Arg(%s)" % (self.name)

    def is_out(self):
        return self.label == "Out"

    def is_in(self):
        return self.label == "In"

    def get_name(self):
        return self.name

    @classmethod
    def set_all_labels(cls, arguments, labelling, step):
        argument_names = list(map(operator.methodcaller('get_name'), arguments))
        for name_batch in batch(argument_names, 900):
            Argument.cursor.execute(
                "UPDATE arguments SET label=?, step=? WHERE name IN ({seq})".format(
                    seq=','.join(['?']*len(name_batch))),
                    tuple([labelling, step] + name_batch))

    @classmethod
    def get_arguments(cls):
        arguments = list()
        for arg in Argument.cursor.execute(
                "SELECT * FROM arguments").fetchall():
            arguments.append(Argument(arg[1], arg[2], arg[3]))
        return arguments

    @classmethod
    def get_unattacked_arguments(cls):
        arguments = list()
        for arg in Argument.cursor.execute(
                """SELECT * FROM arguments
                WHERE id NOT IN
                (SELECT target_id FROM attacks)""").fetchall():
            arguments.append(Argument(arg[1], arg[2], arg[3]))
        return arguments

    @classmethod
    def get_random(cls):
        count = Argument.cursor.execute(
            "SELECT COUNT(*) FROM arguments").fetchone()
        arg = Argument.cursor.execute(
            "SELECT * FROM arguments WHERE id=?", (randint(1, count[0]),)).fetchone()
        if arg is None:
            raise InvalidArgumentError("Argument does not exist")
        return Argument(arg[1], arg[2], arg[3])

    @classmethod
    def _find_by_id(cls, argument_id):
        arg = Argument.cursor.execute(
                "SELECT * FROM arguments WHERE id=?",
                (argument_id,)).fetchone()
        if arg is None:
            raise InvalidArgumentError("Argument does not exist")
        return Argument(arg[1], arg[2], arg[3])

    @classmethod
    def find(cls, argument_name):
        arg = Argument.cursor.execute(
                "SELECT * FROM arguments WHERE name=?",
                (argument_name,)).fetchone()
        if arg is None:
            raise InvalidArgumentError("Argument does not exist")
        return Argument(arg[1], arg[2], arg[3])

    @classmethod
    def from_database(cls, path):
        if Argument.conn is not None:
            Argument.conn.close()
        Argument.conn = sqlite3.connect(path)
        Argument.conn.isolation_level = None
        Argument.cursor = Argument.conn.cursor()
        return Argument

    @classmethod
    def from_file(cls, path):
        file = open(path, "r")
        arguments = set()
        relations = list()
        argument_line = file.readline()
        arguments = argument_line.strip().split(" ")
        for line in file:
            attacker, target = line.strip().split(" ")
            relations.append((attacker, target))
        file.close()
        return Argument.from_af(arguments, relations, path+".sqlite")

    @classmethod
    def from_af(cls, arguments, relations, path=DB_PATH):
        Argument._reset_db(path)
        for arg in arguments:
            Argument.cursor.execute(
                "INSERT INTO arguments (name, label) VALUES(?, 'Undec')", (arg,))
        for attacker, target in relations:
            Argument.cursor.execute(
                """INSERT INTO attacks(attacker_id, target_id)
                SELECT * FROM (SELECT id FROM arguments WHERE name=?) attacker,
                (SELECT id FROM arguments WHERE name=?) target""", (attacker, target))
        return Argument

    @classmethod
    def _reset_db(cls, path):
        Argument._delete_db(path)
        Argument.conn = Argument._create_db(path)
        Argument.cursor = Argument.conn.cursor()

    @classmethod
    def _create_db(cls, path):
        conn = sqlite3.connect(path)
        conn.isolation_level = None
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE arguments(id INTEGER PRIMARY KEY,
            name TEXT, label TEXT, step INTEGER default 4294967295,
            UNIQUE(name) ON CONFLICT IGNORE);""")
        cursor.execute("""CREATE TABLE attacks(id INTEGER PRIMARY KEY,
            attacker_id INTEGER, target_id INTEGER,
            FOREIGN KEY(attacker_id) REFERENCES arguments(id),
            FOREIGN KEY(target_id) REFERENCES arguments(id),
            UNIQUE(attacker_id, target_id) ON CONFLICT IGNORE);""")
        return conn

    @classmethod
    def _delete_db(cls, path):
        try:
            if Argument.conn is not None:
                Argument.conn.close()
            os.remove(path)
        except OSError:
            pass


class InvalidArgumentError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def batch(iterable, n=1):
    l = len(iterable)
    for item in range(0, l, n):
        yield iterable[item:min(item+n, l)]
