# This file is part of python-ly, https://pypi.python.org/pypi/python-ly
#
# Copyright (c) 2011 - 2015 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
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

"""
Implementation of tools to edit rests of selected music.

All functions except a ly.document.Cursor with the selected range.

"""

from __future__ import unicode_literals

import ly.document
import ly.lex.lilypond


def fmrest2spacer(cursor):
    """Replace full measusure rests (R) with spacer rests (s). """
    source = ly.document.Source(cursor, True, tokens_with_position=True)
    with cursor.document as d:
        for token in source:
            if isinstance(token, ly.lex.lilypond.Rest):
                if token == 'R':
                    d[token.pos:token.end] = 's'

def spacer2fmrest(cursor):
    """Replace spacer rests (s) with full measusure rests (R). """
    source = ly.document.Source(cursor, True, tokens_with_position=True)
    with cursor.document as d:
        for token in source:
            if isinstance(token, ly.lex.lilypond.Spacer):
                d[token.pos:token.end] = 'R'

def restcomm2rest(cursor):
    """Replace rests by rest comman (\\rest) with plain rests (r). """
    prev_note = None
    source = ly.document.Source(cursor, True, tokens_with_position=True)
    with cursor.document as d:
        for token in source:
            if isinstance(token, ly.lex.lilypond.Note):
                prev_note = token
                continue
            if isinstance(token, ly.lex.lilypond.Command):
                if token == '\\rest' and prev_note:
                    d[prev_note.pos:prev_note.end] = 'r'
                    del d[token.pos:token.end]
