import sqlite3
import os

try:
    os.remove("./db.sqlite3")
except OSError:
    pass

DB_PATH = "./db.sqlite3"


def create_db():
    global conn
    global cursor
    conn = sqlite3.connect(DB_PATH)
    conn.isolation_level = None
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE arguments(id INTEGER PRIMARY KEY,
        name TEXT, label TEXT, step INTEGER default 9223372036854775806);""")
    cursor.execute("""CREATE TABLE attacks(id INTEGER PRIMARY KEY,
        attacker_id INTEGER, target_id INTEGER,
        FOREIGN KEY(attacker_id) REFERENCES arguments(id),
        FOREIGN KEY(target_id) REFERENCES arguments(id),
        UNIQUE(attacker_id, target_id) ON CONFLICT IGNORE);""")
    return conn


def delete_db():
    global conn
    try:
        conn.close()
        os.remove(DB_PATH)
    except OSError:
        pass


def reset_db():
    global conn
    global cursor
    delete_db()
    conn = create_db()
    cursor = conn.cursor()

create_db()


class Proponent:

    def __init__(self, game):
        self.game = game

    def has_to_be(self, argument):
        if self.is_valid_move(argument):
            return self.game.add(argument)
        raise InvalidMoveError("My Argument is BullShit")

    def is_valid_move(self, argument):
        if self.game.last_argument is None:
            return True
        return self.game.is_valid(argument)


class Opponent:

    def __init__(self, game):
        self.game = game

    def could_be(self, argument):
        if self.is_valid_move(argument):
            return self.game.add(argument)
        raise InvalidMoveError("My Argument is BullShit")

    def concede(self, argument):
        return self.game.concede(argument)

    def retract(self, argument):
        return self.game.retract(argument)

    def is_valid_move(self, argument):
        return self.game.is_valid(argument)


class Bot:

    def __init__(self, game):
        self.game = game

    def next_move(self):
        args = self.game.last_argument.minus()
        if not args:
            return self.game.last_argument
        return list(args).sort(key=lambda arg: arg.step if arg.step else 1000,
                               reverse=True)[0]


class Argument:

    def __init__(self, name, label):
        self.name = name
        self.label = label

    def minus(self):
        return set(self._attackers(cursor.execute("""SELECT attacks.id, attacker_id, target_id FROM attacks
            JOIN arguments ON target_id=arguments.id AND arguments.name=?""", self.name).fetchall()))

    def _attackers(self, relations):
        args = list()
        for attack in relations:
            arg_tuple = cursor.execute("SELECT * FROM arguments WHERE id=?", str(attack[1])).fetchone()
            arg = Argument(arg_tuple[1], arg_tuple[2])
            args.append(arg)
        return args

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.__repr__())

    def __repr__(self):
        return "Arg(%s)" % (self.name)


class ArgumentFramework:

    def __init__(self, arguments, attack_relations):
        if arguments is None:
            arguments = set()
        if attack_relations is None:
            attack_relations = list()

        self.arguments = arguments
        self.attack_relations = attack_relations

    def get_attack_relations(self):
        return self.attack_relations


class DBArgumentFramework:

    def __init__(self, cursor):
        self.cursor = cursor

    def arguments(self):
        arguments = list()
        for arg in self.cursor.execute("SELECT * FROM arguments").fetchall():
            arguments.append(Argument(arg[1], arg[2]))
        return arguments

    def get_attack_relations(self):
        args = list()
        relations = self.cursor.execute("SELECT * FROM attacks").fetchall()
        for attack in relations:
            attacker = cursor.execute("SELECT * FROM arguments WHERE id=?", str(attack[1])).fetchone()
            target = cursor.execute("SELECT * FROM arguments WHERE id=?", str(attack[2])).fetchone()
            attack_arg = Argument(attacker[1], attacker[2])
            target_arg = Argument(target[1], target[2])
            args.append((attack_arg, target_arg))
        return args


class Game:

    def __init__(self, knowledge_base, arguments=None, attack_relations=None, complete_arguments=None, complete_attack_relations=None):
        if arguments is None:
            arguments = set()
        if complete_arguments is None:
            complete_arguments = set()
        if attack_relations is None:
            attack_relations = list()
        if complete_attack_relations is None:
            complete_attack_relations = list()

        self.knowledge_base = knowledge_base
        self.arguments = arguments
        self.complete_arguments = complete_arguments
        self.attack_relations = attack_relations
        self.complete_attack_relations = complete_attack_relations
        self.last_argument = None

    @classmethod
    def from_file(self, path):
        reset_db()
        file = open(path, "r")
        argument_line = file.readline()
        for arg in argument_line.strip().split(" "):
            cursor.execute("INSERT INTO arguments (name, label) VALUES(?, 'Undec')", arg)
        for line in file:
            attacker, target = line.strip().split(" ")
            cursor.execute("""INSERT INTO attacks (attacker_id, target_id)
                WITH attacker AS (SELECT id FROM arguments WHERE name=?),
                target AS (SELECT id FROM arguments WHERE name=?)
                SELECT * from attacker, target""", (attacker, target))
        file.close()
        conn.commit()
        kb = DBArgumentFramework(cursor)
        Game._set_labels(Labelling.grounded(kb))
        return Game(kb)

    @classmethod
    def _set_labels(self, labelling):
        for arg in labelling.IN:
            cursor.execute("""UPDATE arguments SET label=?, step=? WHERE name=?""", ("In", labelling.steps[arg], arg.name))
        for arg in labelling.OUT:
            cursor.execute("""UPDATE arguments SET label=?, step=? WHERE name=?""", ("Out", labelling.steps[arg], arg.name))

    def add(self, argument):
        if self.last_argument is not None: self.attack_relations.append((argument, self.last_argument))
        self.arguments.add(argument)
        self.last_argument = argument
        return self

    def concede(self, argument):
        for attacker, target in self.attack_relations:
            if target is argument:
                raise InvalidMoveError("An attacker of this argument is not out.")
        return self.remove(argument)

    def retract(self, argument):
        for attacker, target in self.complete_attack_relations:
            if target is argument:
                if attacker.label == "In":
                    return self.remove(argument)
        raise InvalidMoveError("There is no attacker of this argument that is in.")

    def remove(self, argument):
        self.arguments = self.arguments.difference({argument})
        self.complete_arguments.add(argument)
        if len(self.attack_relations) > 0:
            last_attack_relation = self.attack_relations.pop(-1)
            self.complete_attack_relations.append(last_attack_relation)
            self.last_argument = last_attack_relation[-1]
        return self

    def is_valid(self, attacker):
        return (attacker, self.last_argument) in self.knowledge_base.get_attack_relations()

    def open_arguments(self):
        return self.arguments


class InvalidMoveError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def main():
    pass

if __name__ == "__main__":
    main()


class Labelling:

    """Labelling (possibly partial)"""
    _framework, IN, OUT, UNDEC = None, None, None, None

    def __init__(self, frame, IN=set(), OUT=None, UNDEC=None):
        self.steps = dict()
        self._framework = frame
        self.IN = IN
        self.OUT = OUT
        self.UNDEC = UNDEC

    @classmethod
    def grounded(cls, af):
        """ Return grounded labeling created from a framework. """
        return cls.all_UNDEC(af).up_complete_update()

    @classmethod
    def all_UNDEC(cls, af):
        """ Return labelling where all arguments are labelled as UNDEC. """
        return cls(af, set(), set(), set(af.arguments()))

    def isLegallyOUT(self, arg):
        return arg.minus() & self.IN

    def isLegallyIN(self, arg):
        return arg.minus() <= self.OUT

    def up_complete_update(self):
        counter = 0
        while True:
            counter += 1
            legally_IN = set([a for a in self.UNDEC if self.isLegallyIN(a)])
            for arg in legally_IN:
                cursor.execute("""UPDATE arguments SET label=?, step=? WHERE name=?""", ("In", counter, arg.name))
            legally_OUT = set([a for a in self.UNDEC if self.isLegallyOUT(a)])
            for arg in legally_OUT:
                cursor.execute("""UPDATE arguments SET label=?, step=? WHERE name=?""", ("Out", counter, arg.name))
            if not legally_IN and not legally_OUT:
                for a in self.UNDEC:
                    if a not in self.steps:
                        self.steps[a] = counter
                return self
            self.IN |= legally_IN
            self.OUT |= legally_OUT
            self.UNDEC -= legally_IN
            self.UNDEC -= legally_OUT
            # assign the number of the step to the updated arguments
            this_step = legally_IN | legally_OUT
            for a in this_step:
                if a not in self.steps:
                    self.steps[a] = counter

"""
    author: Greg Myers

    Based on the SAsSy APIC- implementation of the Abstract Argumentation
    Library by
    Roman Kutlak <roman@kutlak.net>
    Mikolaj Podlaszewski <mikolaj.podlaszewski@gmail.com>

    You may use this file under the terms of the BSD license as follows:

    "Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:
        * Redistributions of source code must retain the above copyright
        notice, this list of conditions and the following disclaimer.
        * Redistributions in binary form must reproduce the above copyright
        notice, this list of conditions and the following disclaimer in
        the documentation and/or other materials provided with the
        distribution.
        * Neither the name of University of Aberdeen nor
        the names of its contributors may be used to endorse or promote
        products derived from this software without specific prior written
        permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
    OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
    THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
"""
