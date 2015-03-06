import sqlite3
import os
from labelling import Labelling

try:
    os.remove("./db.sqlite3")
except OSError:
    pass

DB_PATH = "./db.sqlite3"


class Argument:
    cursor = None
    conn = None

    def __init__(self, name, label):
        self.name = name
        self.label = label

    def set_label(self, labelling, step):
        Argument.cursor.execute(
            """UPDATE arguments SET label=?, step=? WHERE name=?""",
            (labelling, step, self.name))

    def plus(self):
        return set(self._attackers(
            Argument.cursor.execute("""SELECT attacks.id, attacker_id, target_id
                              FROM attacks JOIN arguments
                              ON attacker_id=arguments.id
                              AND arguments.name=?""",
                                    self.name).fetchall()))

    def minus(self):
        return set(self._attackers(
            Argument.cursor.execute("""SELECT attacks.id, attacker_id, target_id
                              FROM attacks JOIN arguments
                              ON target_id=arguments.id
                              AND arguments.name=?""",
                                    self.name).fetchall()))

    def _attackers(self, relations):
        args = list()
        for attack in relations:
            arg_tuple = Argument.cursor.execute(
                "SELECT * FROM arguments WHERE id=?",
                str(attack[1])).fetchone()
            arg = Argument(arg_tuple[1], arg_tuple[2])
            args.append(arg)
        return args

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.__repr__())

    def __repr__(self):
        return "Arg(%s)" % (self.name)

    @classmethod
    def all(cls):
        arguments = list()
        for arg in Argument.cursor.execute(
                        "SELECT * FROM arguments").fetchall():
            arguments.append(Argument(arg[1], arg[2]))
        return arguments

        # This needed?
# def get_attack_relations(self):
#     args = list()
#     relations = Argument.cursor.execute("SELECT * FROM attacks").fetchall()
#     for attack in relations:
#         attacker = Argument.cursor.execute(
#             "SELECT * FROM arguments WHERE id=?",
#             str(attack[1])).fetchone()
#         target = Argument.cursor.execute(
#             "SELECT * FROM arguments WHERE id=?",
#             str(attack[2])).fetchone()
#         attack_arg = Argument(attacker[1], attacker[2])
#         target_arg = Argument(target[1], target[2])
#         args.append((attack_arg, target_arg))
#     return args

    # Can use argument.plus instead of this check for now.
    # @classmethod
    # def has_relation(cls, relation):
    #     Argument.cursor.execute("SELECT * FROM ")

    @classmethod
    def _create_db(cls):
        conn = sqlite3.connect(DB_PATH)
        conn.isolation_level = None
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE arguments(id INTEGER PRIMARY KEY,
            name TEXT, label TEXT, step INTEGER default 4294967295);""")
        cursor.execute("""CREATE TABLE attacks(id INTEGER PRIMARY KEY,
            attacker_id INTEGER, target_id INTEGER,
            FOREIGN KEY(attacker_id) REFERENCES arguments(id),
            FOREIGN KEY(target_id) REFERENCES arguments(id),
            UNIQUE(attacker_id, target_id) ON CONFLICT IGNORE);""")
        return conn

    @classmethod
    def from_file(cls, path):
        Argument._reset_db()
        file = open(path, "r")
        argument_line = file.readline()
        for arg in argument_line.strip().split(" "):
            Argument.cursor.execute(
                "INSERT INTO arguments (name, label) VALUES(?, 'Undec')", arg)
        for line in file:
            attacker, target = line.strip().split(" ")
            Argument.cursor.execute("""INSERT INTO attacks (attacker_id, target_id)
                WITH attacker AS (SELECT id FROM arguments WHERE name=?),
                target AS (SELECT id FROM arguments WHERE name=?)
                SELECT * from attacker, target""", (attacker, target))
        file.close()
        Argument.conn.commit()
        kb = Argument(Argument.cursor)
        Argument._set_labels(Labelling.grounded(kb))

    @classmethod
    def _delete_db(cls):
        try:
            Argument.conn.close()
            os.remove(DB_PATH)
        except OSError:
            pass

    @classmethod
    def _reset_db(cls):
        Argument._delete_db()
        Argument.conn = Argument._create_db()
        Argument.cursor = Argument.conn.cursor()

    @classmethod
    def _set_labels(cls, labelling):
        for arg in labelling.IN:
            arg.set_label("In", labelling.steps[arg])
        for arg in labelling.OUT:
            arg.set_label("Out", labelling.steps[arg])
