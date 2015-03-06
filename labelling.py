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
        return cls(af, set(), set(), set(af.get_arguments()))

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
                arg.set_label("In", counter)
            legally_OUT = set([a for a in self.UNDEC if self.isLegallyOUT(a)])
            for arg in legally_OUT:
                arg.set_label("Out", counter)
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
