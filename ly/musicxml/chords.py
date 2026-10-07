# This file is part of python-ly, https://pypi.python.org/pypi/python-ly
#
# Copyright (c) 2008 - 2015 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

r"""
Chords entered in chord mode (\chordmode or \chords), e.g. c:m7 or f/a.

The chord is built from its root and modifiers following the rules of
LilyPond (scm/chord-entry.scm). It can then be written as notes, or as a
MusicXML harmony (a kind with the degrees that differ from it).

The steps of a chord are kept in a dict mapping each step (1, 3, 5, 7, ...)
to its alteration in semitones, relative to the major scale of the root.
"""

from __future__ import unicode_literals

from fractions import Fraction

import ly.pitch


# semitones of c d e f g a b above c
SCALE = (0, 2, 4, 5, 7, 9, 11)

# the thirds stacked up to the first step number, e.g. c:9
THIRDS = {1: 0, 3: 0, 5: 0, 7: -1, 9: 0, 11: 0, 13: 0}

# the alterations of the chord steps made by the chord modifiers
# (maj and sus are handled separately)
MODIFIERS = {
    'm': {3: -1},
    'min': {3: -1},
    'dim': {3: -1, 5: -1, 7: -2},
    'aug': {5: 1},
    'maj': {},
    'sus': {},
}


def steps(text):
    """Return the steps dict for a text like '1 b3 5 bb7'."""
    return {int(s.lstrip('b#')): s.count('#') - s.count('b') for s in text.split()}


# MusicXML kinds, the closest one is used for a chord
KINDS = {
    'major': steps('1 3 5'),
    'minor': steps('1 b3 5'),
    'augmented': steps('1 3 #5'),
    'diminished': steps('1 b3 b5'),
    'dominant': steps('1 3 5 b7'),
    'major-seventh': steps('1 3 5 7'),
    'minor-seventh': steps('1 b3 5 b7'),
    'diminished-seventh': steps('1 b3 b5 bb7'),
    'augmented-seventh': steps('1 3 #5 b7'),
    'half-diminished': steps('1 b3 b5 b7'),
    'major-minor': steps('1 b3 5 7'),
    'major-sixth': steps('1 3 5 6'),
    'minor-sixth': steps('1 b3 5 6'),
    'dominant-ninth': steps('1 3 5 b7 9'),
    'major-ninth': steps('1 3 5 7 9'),
    'minor-ninth': steps('1 b3 5 b7 9'),
    'dominant-11th': steps('1 3 5 b7 9 11'),
    'major-11th': steps('1 3 5 7 9 11'),
    'minor-11th': steps('1 b3 5 b7 9 11'),
    # without the 11th, as c:13 in LilyPond
    'dominant-13th': steps('1 3 5 b7 9 13'),
    'major-13th': steps('1 3 5 7 9 13'),
    'minor-13th': steps('1 b3 5 b7 9 11 13'),
    'suspended-second': steps('1 2 5'),
    'suspended-fourth': steps('1 4 5'),
    'power': steps('1 5'),
}


class Chord(object):
    """A chord in chord mode, built from a Note and its ChordSpecifier."""
    def __init__(self, root, specifier=None):
        self.root = root
        self.steps = steps('1 3 5')
        self.inversion = None
        self.bass = None
        if specifier:
            self.read(list(specifier))

    def read(self, items):
        """Build the chord from the items of a ChordSpecifier."""
        lead_mod = None
        explicit = set()
        if items[0].token == ':':
            items = items[1:]
            if items and items[0].token in MODIFIERS:
                lead_mod = items.pop(0).token
            if items and items[0].token[0].isdigit() and lead_mod != 'sus':
                step, alter = step_number(items.pop(0).token)
                self.steps = {s: a for s, a in THIRDS.items() if s < step}
                self.steps[step] = alter
                if step == 11:
                    explicit.add(step)
            if lead_mod:
                self.modify(lead_mod)
        remove = False
        items = iter(items)
        for item in items:
            if item.token == '^':
                remove = True
            elif item.token == '/':
                self.inversion = next(items).pitch
            elif item.token == '/+':
                self.bass = next(items).pitch
            elif item.token in MODIFIERS:
                self.modify(item.token)
            elif item.token != '.':
                step, alter = step_number(item.token)
                if remove:
                    self.steps.pop(step, None)
                else:
                    self.steps[step] = alter
                    explicit.add(step)
        # an unaltered 11th clashes with an unaltered third
        if (11 not in explicit and self.steps.get(11) == 0
                and self.steps.get(3) == 0):
            del self.steps[11]
        if lead_mod == 'sus' and not explicit & {2, 4}:
            self.steps[4] = 0

    def modify(self, modifier):
        """Apply a chord modifier (m, maj, dim, ...) to the steps."""
        if modifier == 'maj':
            self.steps[7] = 0
        elif modifier == 'sus':
            self.steps.pop(3, None)
        for step, alter in MODIFIERS[modifier].items():
            if step in self.steps:
                self.steps[step] = alter

    def pitch(self, step, alter):
        """Return the pitch of a step of the chord."""
        n = self.root.note + step - 1
        semitones = (SCALE[self.root.note] + self.root.alter * 2
                     + 12 * ((step - 1) // 7) + SCALE[(step - 1) % 7] + alter)
        natural = SCALE[n % 7] + 12 * (n // 7)
        return ly.pitch.Pitch(n % 7, Fraction(semitones - natural, 2),
                              self.root.octave + n // 7)

    def below_root(self, pitch):
        """Return the pitch in the highest octave below the root."""
        octave = self.root.octave - (pitch.note >= self.root.note)
        return ly.pitch.Pitch(pitch.note, pitch.alter, octave)

    def pitches(self):
        """Return the pitches of the chord from bottom to top."""
        pitches = [self.pitch(s, a) for s, a in sorted(self.steps.items())]
        if self.inversion:
            inv = (self.inversion.note, self.inversion.alter)
            pitches = [p for p in pitches if (p.note, p.alter) != inv]
            pitches.insert(0, self.below_root(self.inversion))
        if self.bass:
            pitches.insert(0, self.below_root(self.bass))
        return pitches

    def bass_pitch(self):
        """Return the pitch written after / or /+, or None."""
        return self.bass or self.inversion

    def kind(self):
        """Return the closest MusicXML kind and the degrees that differ from it.

        The degrees are (value, alter, type) tuples.

        """
        def degrees(kind_steps):
            result = []
            for step in sorted(set(self.steps) | set(kind_steps)):
                if step not in kind_steps:
                    # relative to a dominant chord
                    alter = self.steps[step] - THIRDS.get(step, 0)
                    result.append((step, alter, 'add'))
                elif step not in self.steps:
                    result.append((step, 0, 'subtract'))
                elif self.steps[step] != kind_steps[step]:
                    alter = self.steps[step] - kind_steps[step]
                    result.append((step, alter, 'alter'))
            return result
        return min(((kind, degrees(s)) for kind, s in KINDS.items()),
                   key=lambda kind_degrees: len(kind_degrees[1]))


def step_number(token):
    """Return step and alteration of a step number like 7, 9+ or 5-."""
    step = int(token.rstrip('+-'))
    alter = -1 if step == 7 else 0
    return step, alter + token.count('+') - token.count('-')
