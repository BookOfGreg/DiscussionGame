import sqlite3
import os

try:
    os.remove("./db.sqlite3")
except OSError:
    pass

DB_PATH = "./db.sqlite3"


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
                                    self.name).fetchall()))

    def minus(self):
        return set(self._to_args(
            Argument.cursor.execute("""SELECT attacker_id
                              FROM attacks JOIN arguments
                              ON target_id=arguments.id
                              AND arguments.name=?""",
                                    self.name).fetchall()))

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

    @classmethod
    def get_arguments(cls):
        arguments = list()
        for arg in Argument.cursor.execute(
                "SELECT * FROM arguments").fetchall():
            arguments.append(Argument(arg[1], arg[2]))
        return arguments

    @classmethod
    def get_random(cls):
        count = Argument.cursor.execute(
            "SELECT COUNT(*) FROM arguments").fetchone()
        arg = Argument.cursor.execute(
            "SELECT * FROM arguments WHERE id=?", count).fetchone()
        if arg is None:
            raise InvalidArgumentError("Argument does not exist")
        return Argument(arg[1], arg[2])

    @classmethod
    def _find_by_id(cls, argument_id):
        arg = Argument.cursor.execute(
                "SELECT * FROM arguments WHERE id=?",
                argument_id).fetchone()
        if arg is None:
            raise InvalidArgumentError("Argument does not exist")
        return Argument(arg[1], arg[2])

    @classmethod
    def find(cls, argument_name):
        arg = Argument.cursor.execute(
                "SELECT * FROM arguments WHERE name=?",
                argument_name).fetchone()
        if arg is None:
            raise InvalidArgumentError("Argument does not exist")
        return Argument(arg[1], arg[2], arg[3])

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
        return Argument.from_af(arguments, relations)

    @classmethod
    def from_af(cls, arguments, relations):
        Argument._reset_db()
        for arg in arguments:
            Argument.cursor.execute(
                "INSERT INTO arguments (name, label) VALUES(?, 'Undec')", arg)
        for attacker, target in relations:
            Argument.cursor.execute(
                """INSERT INTO attacks (attacker_id, target_id)
                WITH attacker AS (SELECT id FROM arguments WHERE name=?),
                target AS (SELECT id FROM arguments WHERE name=?)
                SELECT * from attacker, target""", (attacker, target))
        return Argument

    @classmethod
    def set_labels(cls, labelling):
        for arg in labelling.IN:
            arg.set_label("In", labelling.steps[arg])
        for arg in labelling.OUT:
            arg.set_label("Out", labelling.steps[arg])

    @classmethod
    def _reset_db(cls):
        Argument._delete_db()
        Argument.conn = Argument._create_db()
        Argument.cursor = Argument.conn.cursor()

    @classmethod
    def _create_db(cls):
        conn = sqlite3.connect(DB_PATH)
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
    def _delete_db(cls):
        try:
            if Argument.conn is not None:
                Argument.conn.close()
            os.remove(DB_PATH)
        except OSError:
            pass


class InvalidArgumentError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
