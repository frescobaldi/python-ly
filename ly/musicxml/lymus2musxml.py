# This file is part of python-ly, https://pypi.python.org/pypi/python-ly
#
# Copyright (c) 2008 - 2015 by Wilbert Berendsen
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
Using the tree structure from ly.music to initiate the conversion to MusicXML.

Uses functions similar to ly.music.items.Document.iter_music() to iter through
the node tree. But information about where a node branch ends
is also added. During the iteration the information needed for the conversion
is captured.
"""

from __future__ import unicode_literals
from __future__ import print_function

import ly.document
import ly.music
from fractions import Fraction

from . import create_musicxml
from . import ly2xml_mediator
from . import xml_objs

# excluded from parsing
excl_list = ['Version', 'Midi', 'Layout']


# Defining contexts in relation to musicXML
group_contexts = ['StaffGroup', 'ChoirStaff']

pno_contexts = ['PianoStaff', 'GrandStaff']

staff_contexts = ['Staff', 'RhythmicStaff', 'TabStaff',
                  'DrumStaff', 'VaticanaStaff', 'MensuralStaff']

part_contexts = pno_contexts + staff_contexts


class End():
    """ Extra class that gives information about the end of Container
    elements in the node list. """

    def __init__(self, node):
        self.node = node

    def __repr__(self):
        return '<{0} {1}>'.format(self.__class__.__name__, self.node)


class ParseSource():
    """ creates the XML-file from the source code according to the Music XML standard """

    def __init__(self):
        self.musxml = create_musicxml.CreateMusicXML()
        self.mediator = ly2xml_mediator.Mediator()
        self.relative = False
        self.tuplet = []
        self.scale = ''
        self.grace_seq = False
        self.trem_rep = 0
        self.piano_staff = 0
        self.numericTime = False
        self.voice_sep = False
        self.voice_sep_start_total_time = 0
        self.voice_sep_start_time_since_bar = 0
        self.voice_sep_length = 0
        self.voice_sep_first_meas = False
        self.sims_and_seqs = []
        self.override_dict = {}
        self.ottava = False
        self.with_contxt = None
        self.schm_assignm = None
        self.tempo = ()
        self.tremolo = False
        self.tupl_span = False
        self.unset_tuplspan = False
        self.alt_mode = None
        self.rel_pitch_isset = False
        self.slurcount = 0
        self.slurnr = 0
        self.phrslurnr = 0
        # Variables to keep track of place in music, and place of \bar barlines and chord symbols
        self.time_sig = Fraction(1, 1)
        self.partial = 0
        self.first_meas = False
        self.prev_note_dur = 0
        self.total_time = 0
        self.time_since_bar = 0
        self.barline_locations = {}
        self.chord_locations = {}

    def parse_text(self, ly_text, filename=None):
        """Parse the LilyPond source specified as text.

        If you specify a filename, it can be used to resolve \\include commands
        correctly.

        """
        doc = ly.document.Document(ly_text)
        doc.filename = filename
        self.parse_document(doc)

    def parse_document(self, ly_doc, relative_first_pitch_absolute=False):
        """Parse the LilyPond source specified as a ly.document document.

        If relative_first_pitch_absolute is set to True, the first pitch in a
        \relative expression without startpitch is considered to be absolute
        (LilyPond 2.18+ behaviour).

        """
        # The document is copied and the copy is converted to absolute mode to
        # facilitate the export. The original document is unchanged.
        doc = ly_doc.copy()
        import ly.pitch.rel2abs
        cursor = ly.document.Cursor(doc)
        ly.pitch.rel2abs.rel2abs(cursor, first_pitch_absolute=relative_first_pitch_absolute)
        mustree = ly.music.document(doc)
        self.parse_tree(mustree)

    def parse_tree(self, mustree):
        """Parse the LilyPond source as a ly.music node tree."""
        # print(mustree.dump())
        header_nodes = self.iter_header(mustree)
        if header_nodes:
            self.parse_nodes(header_nodes)
        score = self.get_score(mustree)
        if score:
            mus_nodes = self.iter_score(score, mustree)
        else:
            mus_nodes = self.find_score_sub(mustree)
        self.mediator.new_section("fallback")  # fallback/default section
        self.parse_nodes(mus_nodes)

    def parse_nodes(self, nodes):
        """Work through all nodes by calling the function with the
        same name as the nodes class."""
        if nodes:
            for m in nodes:
                # print(m)
                func_name = m.__class__.__name__  # get instance name
                if func_name not in excl_list:
                    try:
                        func_call = getattr(self, func_name)
                        func_call(m)
                    except AttributeError as ae:
                        print("Warning:", func_name, "not implemented!")
                        print(ae)
                        pass
        else:
            print("Warning! Couldn't parse source!")

    def musicxml(self, prettyprint=True):
        self.mediator.check_score()
        xml_objs.IterateXmlObjs(
            self.mediator.score, self.musxml, self.mediator.divisions)
        xml = self.musxml.musicxml(prettyprint)
        return xml

    ##
    # The different source types from ly.music are here sent to translation.
    ##

    def Assignment(self, a):
        """
        Variables should already have been substituted
        so this need only cover other types of assignments.
        """
        if isinstance(a.value(), ly.music.items.Markup):
            val = a.value().plaintext()
        elif isinstance(a.value(), ly.music.items.String):
            val = a.value().value()
        elif isinstance(a.value(), ly.music.items.Scheme):
            val = a.value().get_string()
            if not val:
                self.schm_assignm = a.name()
        elif isinstance(a.value(), ly.music.items.UserCommand):
            # Don't know what to do with this:
            return
        if self.look_behind(a, ly.music.items.With):
            if self.with_contxt in group_contexts:
                self.mediator.set_by_property(a.name(), val, True)
            else:
                self.mediator.set_by_property(a.name(), val)
        else:
            self.mediator.new_header_assignment(a.name(), val)

    def MusicList(self, musicList):
        if musicList.token == '<<':
            if self.look_ahead(musicList, ly.music.items.VoiceSeparator):
                self.mediator.new_snippet('sim-snip')
                self.voice_sep = True
                # Store information at beginning of voice separator
                self.voice_sep_start_total_time = self.total_time
                self.voice_sep_start_time_since_bar = self.time_since_bar
                self.voice_sep_first_meas = self.first_meas
            else:
                self.mediator.new_section('simultan')
                self.sims_and_seqs.append('sim')
        elif musicList.token == '{':
            self.sims_and_seqs.append('seq')

    def Chord(self, chord):
        self.mediator.clear_chord()

    def Q(self, q):
        self.mediator.copy_prev_chord(q.duration)

    def Context(self, context):
        r""" \context """
        self.in_context = True
        self.check_context(context.context(), context.context_id(), context.token)

    def check_context(self, context, context_id=None, token=""):
        """Check context and do appropriate action (e.g. create new part)."""
        # Check first if part already exists
        if context_id:
            match = self.mediator.get_part_by_id(context_id)
            if match:
                self.mediator.new_part(to_part=match)
                return
        if context in pno_contexts:
            self.mediator.new_part(context_id, piano=True)
            self.piano_staff = 1
        elif context in group_contexts:
            self.mediator.new_group()
        elif context in staff_contexts:
            if self.piano_staff:
                if self.piano_staff > 1:
                    self.mediator.set_voicenr(nr=self.piano_staff+3)
                self.mediator.new_section('piano-staff'+str(self.piano_staff))
                self.mediator.set_staffnr(self.piano_staff)
                self.piano_staff += 1
            else:
                if token != '\\context' or self.mediator.part_not_empty():
                    self.mediator.new_part(context_id)
                self.mediator.set_voicenr(nr=1)
            self.mediator.add_staff_id(context_id)
            self.total_time = 0
            self.time_since_bar = 0
            self.first_meas = True
        elif context == 'Voice':
            self.total_time = 0
            self.time_since_bar = 0
            self.sims_and_seqs.append('voice')
            if context_id:
                self.mediator.new_section(context_id)
            else:
                self.mediator.new_section('voice')
            self.first_meas = True
        elif context == 'Devnull':
            self.mediator.new_section('devnull', True)
        elif context == 'Lyrics':
            pass  # The way lyrics are implemented, they don't need a new section here (prevents irrelevant warning)
        elif context == 'ChordNames':
            pass  # Without using ChordMode to write actual chords, ChordNames doesn't need a new section
        else:
            print("Context not implemented:", context)

    def VoiceSeparator(self, voice_sep):
        self.mediator.new_snippet('sim')
        self.mediator.set_voicenr(add=True)
        if self.voice_sep:
            # Reset time info
            self.total_time = self.total_time - self.voice_sep_length
            self.time_since_bar = self.voice_sep_start_time_since_bar
            self.first_meas = self.voice_sep_first_meas

    def Change(self, change):
        r""" A \change music expression. Changes the staff number. """
        if change.context() == 'Staff':
            self.mediator.set_staffnr(0, staff_id=change.context_id())

    def PipeSymbol(self, barcheck):
        """ PipeSymbol = | """
        pass  # Barlines are automatically generated at correct locations by check_for_barline()

    def Clef(self, clef):
        r""" Clef \clef"""
        self.mediator.new_clef(clef.specifier())

    def KeySignature(self, key):
        self.mediator.new_key(key.pitch().output(), key.mode())

    def Relative(self, relative):
        r"""A \relative music expression."""
        self.relative = True

    def ChordSpecifier(self, specifier):
        """
        A ChordSpecifier occurs with : or / in ChordMode

        Function modifies current chord symbol in self.chord_locations
        to include additional text and bass note
        """
        for item in specifier:
            if isinstance(item, ly.music.items.Note):
                self.chord_locations[self.total_time - self.prev_note_dur]["bass"] = item.token.capitalize()[0]
                self.chord_locations[self.total_time - self.prev_note_dur]["bass-alter"] = int(item.pitch.alter * 2)
            elif item.token != ":" and item.token != "/":
                self.chord_locations[self.total_time - self.prev_note_dur]["text"] += item.token

    def ChordItem(self, item):
        """A ChordItem :, /, m, maj, etc."""
        pass

    def check_for_chord(self, note):
        """
        Checks the current note to see if a chord symbol is needed above
        Adds one to current note if needed
        Based on whether a chord symbol was defined at this point in the music
        Removes current chord symbol from dictionary of chord symbols to ensure the symbol is only placed once
        """
        if isinstance(note.parent(), ly.music.items.Chord):
            if (self.total_time - note.parent().duration[0]) in self.chord_locations:
                chord_dict = self.chord_locations[self.total_time - note.parent().duration[0]]
                self.mediator.current_note.set_harmony(chord_dict["root"], chord_dict["root-alter"],
                                                       chord_dict["bass"], chord_dict["bass-alter"],
                                                       chord_dict["text"])
                self.chord_locations.pop(self.total_time - note.parent().duration[0])
        else:
            if (self.total_time - note.length()) in self.chord_locations:
                chord_dict = self.chord_locations[self.total_time - note.length()]
                self.mediator.current_note.set_harmony(chord_dict["root"], chord_dict["root-alter"],
                                                       chord_dict["bass"], chord_dict["bass-alter"],
                                                       chord_dict["text"])
                self.chord_locations.pop(self.total_time - note.length())

    def check_for_barline(self, node=None):
        """
        Checks at the current location in music to see if a barline is needed
        Creates a barline if needed
        """
        # Prevent a regular bar from being made and then a \bar being made
        if node and self.get_next_node(node):
            if self.get_next_node(node).token == "\\bar":
                return False
        # Create a \bar if found in same location in earlier part
        if self.total_time in self.barline_locations and self.time_since_bar != 0:
            self.mediator.create_barline(self.barline_locations[self.total_time])
            # Reset time since bar if the \bar coincides with actual end of measure
            if self.first_meas and self.partial != 0:
                if self.time_since_bar == self.partial:
                    self.time_since_bar = 0
                    self.first_meas = False
            else:
                if self.time_since_bar == self.time_sig:
                    self.time_since_bar = 0
            return True
        # Create regular measure if there has been enough time since prev bar
        if self.first_meas and self.partial != 0:
            if self.time_since_bar == self.partial:
                self.time_since_bar = 0
                self.mediator.new_bar()
                self.first_meas = False
                return True
        else:
            if self.time_since_bar == self.time_sig:
                self.time_since_bar = 0
                self.mediator.new_bar()
                return True
        return False

    def update_time_and_check(self, mus_obj):
        """
        Takes a note, rest, skip, etc. and updates total_time and time_since_bar accordingly
        Also records chord symbol locations when in 'chord' alt_mode
        After updating times, checks for barlines and/or chord symbols when applicable
        """
        if mus_obj.length():
            self.prev_note_dur = mus_obj.length()
            # When in chord alt_mode, record chord symb locations
            if self.alt_mode == "chord":
                if not isinstance(mus_obj, ly.music.items.Skip):
                    self.chord_locations[self.total_time] = {"root": mus_obj.token.capitalize()[0],
                                                             "root-alter": int(mus_obj.pitch.alter * 2),
                                                             "bass": False, "bass-alter": 0, "text": ""}
                self.total_time += mus_obj.length()
            # When not in chord alt_mode, treat notes as notes
            else:
                self.time_since_bar += mus_obj.length()
                self.total_time += mus_obj.length()
                # Check for bar unless final note in voice separator (in which case, wait until after)
                if not self.voice_sep:
                    self.check_for_barline(mus_obj)
                else:
                    node = mus_obj
                    while True:
                        if not self.get_next_node(node):
                            break
                        elif isinstance(self.get_next_node(node), ly.music.items.Durable):
                            self.check_for_barline(mus_obj)
                            break
                        else:
                            node = self.get_next_node(node)
                self.check_for_chord(mus_obj)
        # First note of chord is used to update time and check for chord symbols,
        #     but must wait for end of chord to check for barlines (see End() )
        elif isinstance(mus_obj.parent(), ly.music.items.Chord):
            self.prev_note_dur = mus_obj.parent().duration[0]
            self.time_since_bar += mus_obj.parent().duration[0]
            self.total_time += mus_obj.parent().duration[0]
            self.check_for_chord(mus_obj)

    def Note(self, note):
        """ notename, e.g. c, cis, a bes ... """
        # print(note.token)
        # if the note is a bass note in a chord symbol, break out of function
        if not isinstance(note.parent(), ly.music.items.ChordSpecifier):
            if note.length() and self.alt_mode != "chord":
                if self.relative and not self.rel_pitch_isset:
                    self.mediator.new_note(note, False)
                    self.mediator.set_relative(note)
                    self.rel_pitch_isset = True
                else:
                    self.mediator.new_note(note, self.relative)
                self.check_note(note)
                self.update_time_and_check(note)
            else:
                if self.alt_mode == "chord":  # if chord symbols are being written, record location of chord
                    self.update_time_and_check(note)
                elif isinstance(note.parent(), ly.music.items.Relative):
                    self.mediator.set_relative(note)
                    self.rel_pitch_isset = True
                elif isinstance(note.parent(), ly.music.items.Chord):
                    if self.mediator.current_chord:
                        self.mediator.new_chord(note, chord_base=False)
                    else:
                        self.mediator.new_chord(note, note.parent().duration, self.relative)
                        self.check_tuplet()
                        self.update_time_and_check(note)
                    # chord as grace note
                    if self.grace_seq:
                        self.mediator.new_chord_grace()

    def Unpitched(self, unpitched):
        """A note without pitch, just a standalone duration."""
        if unpitched.length():
            if self.alt_mode == 'drum':
                self.mediator.new_iso_dura(unpitched, self.relative, True)
            else:
                self.mediator.new_iso_dura(unpitched, self.relative)
            self.check_note(unpitched)
        self.update_time_and_check(unpitched)

    def DrumNote(self, drumnote):
        """A note in DrumMode."""
        if drumnote.length():
            self.mediator.new_note(drumnote, is_unpitched=True)
            self.check_note(drumnote)
        self.update_time_and_check(drumnote)

    def check_note(self, note):
        """Generic check for all notes, both pitched and unpitched."""
        self.check_tuplet()
        if self.grace_seq:
            self.mediator.new_grace()
        if self.trem_rep and not self.look_ahead(note, ly.music.items.Duration):
            self.mediator.set_tremolo(trem_type='start', repeats=self.trem_rep)

    def check_tuplet(self):
        """Generic tuplet check."""
        if self.tuplet:
            tlevels = len(self.tuplet)
            nested = True if tlevels > 1 else False
            for td in self.tuplet:
                if nested:
                    self.mediator.change_to_tuplet(td['fraction'], td['ttype'],
                                                   td['nr'], td['length'])
                else:
                    self.mediator.change_to_tuplet(td['fraction'], td['ttype'],
                                                   td['nr'])
                td['ttype'] = ""
            self.mediator.check_divs()

    def Duration(self, duration):
        """A written duration"""
        if self.tempo:
            self.mediator.new_tempo(duration.token, duration.tokens, *self.tempo)
            self.tempo = ()
        elif self.tremolo:
            self.mediator.set_tremolo(duration=int(duration.token))
            self.tremolo = False
        elif self.tupl_span:
            self.mediator.set_tuplspan_dur(duration.token, duration.tokens)
            self.tupl_span = False
        else:
            if self.alt_mode != "chord":
                self.mediator.new_duration_token(duration.token, duration.tokens)
                if self.trem_rep:
                    self.mediator.set_tremolo(trem_type='start', repeats=self.trem_rep)

    def Tempo(self, tempo):
        """ Tempo direction, e g '4 = 80' """
        if self.look_ahead(tempo, ly.music.items.Duration):
            self.tempo = (tempo.tempo(), tempo.text())
        else:
            self.mediator.new_tempo(0, (), tempo.tempo(), tempo.text())

    def Tie(self, tie):
        """ tie ~ """
        self.mediator.tie_to_next()

    def Rest(self, rest):
        r""" rest, r or R. Note: NOT by command, i.e. \rest """
        if rest.token == 'R':
            self.scale = 'R'
        self.mediator.new_rest(rest)
        self.update_time_and_check(rest)

    def Skip(self, skip):
        r""" invisible rest/spacer rest (s or command \skip)"""
        if self.alt_mode == 'lyric':
            self.mediator.new_lyrics_item(skip.token)
        elif self.alt_mode == "chord":
            self.total_time += skip.length()
        else:
            if not self.break_skip_at_barline(skip):
                self.mediator.new_rest(skip)
                self.update_time_and_check(skip)

    def break_skip_at_barline(self, skip):
        r"""
        When a skip is longer than one measure, break skip into measure length pieces
        NOTES: This only works with barlines at ends of complete measures (not \bar)
               Length of skip must be a multiple of the length of one measure
        """
        if skip.length() > self.time_sig:
            for i in range(skip.length() // self.time_sig):
                self.mediator.current_is_rest = True
                self.mediator.clear_chord()
                self.mediator.current_note = xml_objs.BarRest((self.time_sig, Fraction(1, 1)), self.mediator.voice, skip=True)
                self.mediator.check_current_note(rest=True)
                self.total_time += self.time_sig
                self.time_since_bar += self.time_sig
                self.check_for_barline()
            return True
        else:
            return False

    def Scaler(self, scaler):
        r"""
        \times \tuplet \scaleDurations

        """
        if scaler.token == '\\scaleDurations':
            ttype = ""
            fraction = (scaler.denominator, scaler.numerator)
        elif scaler.token == '\\times':
            ttype = "start"
            fraction = (scaler.denominator, scaler.numerator)
        elif scaler.token == '\\tuplet':
            ttype = "start"
            fraction = (scaler.numerator, scaler.denominator)
        nr = len(self.tuplet) + 1
        self.tuplet.append({'set': False,
                            'fraction': fraction,
                            'ttype': ttype,
                            'length': scaler.length(),
                            'nr': nr})
        if self.look_ahead(scaler, ly.music.items.Duration):
            self.tupl_span = True
            self.unset_tuplspan = True

    def Number(self, number):
        pass

    def Articulation(self, art):
        """An articulation, fingering, string number, or other symbol."""
        self.mediator.new_articulation(art.token)

    def Postfix(self, postfix):
        pass

    def Beam(self, beam):
        pass

    def Partial(self, partial):
        r""" \partial # """
        self.partial = partial.partial_length()

    def Slur(self, slur):
        """ Slur, '(' = start, ')' = stop. """
        if slur.token == '(':
            self.slurcount += 1
            self.slurnr = self.slurcount
            self.mediator.set_slur(self.slurnr, "start")
        elif slur.token == ')':
            self.mediator.set_slur(self.slurnr, "stop")
            self.slurcount -= 1

    def PhrasingSlur(self, phrslur):
        r"""A \( or \)."""
        if phrslur.token == r'\(':
            self.slurcount += 1
            self.phrslurnr = self.slurcount
            self.mediator.set_slur(self.phrslurnr, "start")
        elif phrslur.token == r'\)':
            self.mediator.set_slur(self.phrslurnr, "stop")
            self.slurcount -= 1

    def Dynamic(self, dynamic):
        """Any dynamic symbol."""
        self.mediator.new_dynamics(dynamic.token[1:])

    def Grace(self, grace):
        self.grace_seq = True

    def TimeSignature(self, timeSign):
        self.time_sig = timeSign.measure_length()
        self.mediator.new_time(timeSign.numerator(), timeSign.fraction(), self.numericTime)

    def Repeat(self, repeat):
        if repeat.specifier() == 'volta':
            self.mediator.new_repeat('forward')
        elif repeat.specifier() == 'tremolo':
            self.trem_rep = repeat.repeat_count()

    def Tremolo(self, tremolo):
        """A tremolo item ":"."""
        if self.look_ahead(tremolo, ly.music.items.Duration):
            self.tremolo = True
        else:
            self.mediator.set_tremolo()

    def With(self, cont_with):
        r"""A \with ... construct."""
        self.with_contxt = cont_with.parent().context()

    def Set(self, cont_set):
        r"""A \set command."""
        if isinstance(cont_set.value(), ly.music.items.Scheme):
            if cont_set.property() == 'tupletSpannerDuration':
                moment = cont_set.value().get_ly_make_moment()
                if moment:
                    self.mediator.set_tuplspan_dur(fraction=moment)
                else:
                    self.mediator.unset_tuplspan_dur()
                return
            val = cont_set.value().get_string()
        else:
            val = cont_set.value().value()
        if cont_set.context() in part_contexts:
            self.mediator.set_by_property(cont_set.property(), val)
        elif cont_set.context() in group_contexts:
            self.mediator.set_by_property(cont_set.property(), val, group=True)

    def Command(self, command):
        r""" \bar, \rest etc """
        excls = ['\\major', '\\minor', '\\bar']
        if command.token == '\\rest':
            self.mediator.note2rest()
        elif command.token == '\\numericTimeSignature':
            self.numericTime = True
        elif command.token == '\\defaultTimeSignature':
            self.numericTime = False
        elif command.token.find('voice') == 1:
            self.mediator.set_voicenr(command.token[1:], piano=self.piano_staff)
        elif command.token == '\\glissando':
            try:
                self.mediator.new_gliss(self.override_dict["Glissando.style"])
            except KeyError:
                self.mediator.new_gliss()
        elif command.token == '\\startTrillSpan':
            self.mediator.new_trill_spanner()
        elif command.token == '\\stopTrillSpan':
            self.mediator.new_trill_spanner("stop")
        elif command.token == '\\ottava':
            self.ottava = True
        elif command.token == '\\default':
            if self.tupl_span:
                self.mediator.unset_tuplspan_dur()
                self.tupl_span = False
        else:
            if command.token not in excls:
                print("Unknown command:", command.token)

    def UserCommand(self, usercommand):
        """Music variables are substituted so this must be something else."""
        if usercommand.name() == 'tupletSpan':
            self.tupl_span = True

    def String(self, string):
        prev = self.get_previous_node(string)
        # If a new \bar is found: record its position and style-type, and create appropriate barline
        if prev and prev.token == '\\bar':
            self.barline_locations[self.total_time] = string.value()
            self.check_for_barline()

    def LyricsTo(self, lyrics_to):
        r"""A \lyricsto expression. """
        self.mediator.new_lyric_section('lyricsto'+lyrics_to.context_id(), lyrics_to.context_id())
        self.sims_and_seqs.append('lyrics')

    def LyricText(self, lyrics_text):
        """A lyric text (word, markup or string), with a Duration."""
        self.mediator.new_lyrics_text(lyrics_text.token)

    def LyricItem(self, lyrics_item):
        """Another lyric item (skip, extender, hyphen or tie)."""
        self.mediator.new_lyrics_item(lyrics_item.token)

    def NoteMode(self, notemode):
        r"""A \notemode or \notes expression."""
        self.alt_mode = 'note'

    def ChordMode(self, chordmode):
        r"""A \chordmode or \chords expression."""
        self.alt_mode = 'chord'

    def DrumMode(self, drummode):
        r"""A \drummode or \drums expression.

        If the shorthand form \drums is found, DrumStaff is implicit.

        """
        if drummode.token == '\\drums':
            self.check_context('DrumStaff')
        self.alt_mode = 'drum'

    def FigureMode(self, figmode):
        r"""A \figuremode or \figures expression."""
        self.alt_mode = 'figure'

    def LyricMode(self, lyricmode):
        r"""A \lyricmode, \lyrics or \addlyrics expression."""
        self.alt_mode = 'lyric'

    def Override(self, override):
        r"""An \override command."""
        self.override_key = ''

    def PathItem(self, item):
        r"""An item in the path of an \override or \revert command."""
        self.override_key += item.token

    def Scheme(self, scheme):
        """A Scheme expression inside LilyPond."""
        pass

    def SchemeItem(self, item):
        """Any scheme token."""
        if self.ottava:
            self.mediator.new_ottava(item.token)
            self.ottava = False
        elif self.look_behind(item, ly.music.items.Override):
            self.override_dict[self.override_key] = item.token
        elif self.schm_assignm:
            self.mediator.set_by_property(self.schm_assignm, item.token)
        else:
            print("SchemeItem not implemented:", item.token)

    def SchemeQuote(self, quote):
        """A ' in scheme."""
        pass

    def End(self, end):
        if isinstance(end.node, ly.music.items.Scaler):
            if self.unset_tuplspan:
                self.mediator.unset_tuplspan_dur()
                self.unset_tuplspan = False
            if end.node.token != '\\scaleDurations':
                self.mediator.change_tuplet_type(len(self.tuplet) - 1, "stop")
            self.tuplet.pop()
            self.fraction = None
        elif isinstance(end.node, ly.music.items.Grace):  # Grace
            self.grace_seq = False
        elif end.node.token == '\\repeat':
            if end.node.specifier() == 'volta':
                self.mediator.new_repeat('backward')
            elif end.node.specifier() == 'tremolo':
                if self.look_ahead(end.node, ly.music.items.MusicList):
                    self.mediator.set_tremolo(trem_type="stop")
                else:
                    self.mediator.set_tremolo(trem_type="single")
                self.trem_rep = 0
        elif isinstance(end.node, ly.music.items.Context):
            self.in_context = False
            if end.node.context() == 'Voice':
                self.mediator.check_voices()
                self.sims_and_seqs.pop()
            elif end.node.context() in group_contexts:
                self.mediator.close_group()
            elif end.node.context() in staff_contexts:
                if not self.piano_staff:
                    self.mediator.check_part()
            elif end.node.context() in pno_contexts:
                self.mediator.check_voices()
                self.mediator.check_part()
                self.piano_staff = 0
                self.mediator.set_voicenr(nr=1)
            elif end.node.context() == 'Devnull':
                self.mediator.check_voices()
            elif end.node.context() == 'Lyrics':
                self.mediator.check_voices()
        elif end.node.token == '<<':
            if self.voice_sep:
                self.mediator.check_voices_by_nr()
                self.mediator.revert_voicenr()
                self.voice_sep = False
                self.voice_sep_length = 0
                self.check_for_barline(end.node)
            elif not self.piano_staff:
                self.mediator.check_simultan()
                if self.sims_and_seqs:
                    self.sims_and_seqs.pop()
        elif end.node.token == '{':
            if self.sims_and_seqs:
                self.sims_and_seqs.pop()
            if self.voice_sep:
                self.voice_sep_length = self.total_time - self.voice_sep_start_total_time
            if end.node.parent().token in ["\\notemode", "\\notes", "\\chordmode", "\\chords",
                                           "\\drummode", "\\drums", "\\figuremode", "\\figures",
                                           "\\lyricmode", "\\lyrics", "\\addlyrics"]:
                self.alt_mode = None
        elif end.node.token == '<':  # chord
            self.mediator.chord_end()
            # Check for bar unless final note in voice separator (in which case, wait until after)
            if not self.voice_sep:
                self.check_for_barline(end.node)
            else:
                node = end.node
                while True:
                    if not self.get_next_node(node):
                        break
                    elif isinstance(self.get_next_node(node), ly.music.items.Durable):
                        self.check_for_barline(end.node)
                        break
                    else:
                        node = self.get_next_node(node)
        elif end.node.token == '\\lyricsto':
            self.mediator.check_lyrics(end.node.context_id())
            self.sims_and_seqs.pop()
            self.mediator.new_lyric_nr(self.mediator.lyric_nr + 1)
        elif end.node.token == '\\with':
            self.with_contxt = None
        elif end.node.token == '\\drums':
            self.mediator.check_part()
        elif isinstance(end.node, ly.music.items.Relative):
            self.relative = False
            self.rel_pitch_isset = False
        else:
            # print("end:", end.node.token)
            pass

    ##
    # Additional node manipulation
    ##

    def get_previous_node(self, node):
        """ Returns the node's previous node
        or false if the node is first in its branch. """
        parent = node.parent()
        i = parent.index(node)
        if i > 0:
            return parent[i-1]
        else:
            return False

    def get_next_node(self, node):
        """ Returns the node's next node
        or false if the node is last in its branch. """
        parent = node.parent()
        i = parent.index(node)
        try:
            return parent[i+1]
        except IndexError:
            return False

    def simple_node_gen(self, node):
        """Unlike iter_score are the subnodes yielded without substitution."""
        for n in node:
            yield n
            for s in self.simple_node_gen(n):
                yield s

    def iter_header(self, tree):
        """Iter only over header nodes."""
        for t in tree:
            if isinstance(t, ly.music.items.Header):
                return self.simple_node_gen(t)

    def get_score(self, node):
        """ Returns (first) Score node or false if no Score is found. """
        for n in node:
            if isinstance(n, ly.music.items.Score) or isinstance(n, ly.music.items.Book):
                return n
        return False

    def iter_score(self, scorenode, doc):
        r"""
        Iter over score.

        Similarly to items.Document.iter_music user commands are substituted.

        Furthermore \repeat unfold expressions are unfolded.
        """
        for s in scorenode:
            if isinstance(s, ly.music.items.Repeat) and s.specifier() == 'unfold':
                for u in self.unfold_repeat(s, s.repeat_count(), doc):
                    yield u
            else:
                n = doc.substitute_for_node(s) or s
                yield n
                for c in self.iter_score(n, doc):
                    yield c
                if isinstance(s, ly.music.items.Container):
                    yield End(s)

    def unfold_repeat(self, repeat_node, repeat_count, doc):
        r"""
        Iter over node which represent a \repeat unfold expression
        and do the unfolding directly.
        """
        for r in range(repeat_count):
            for n in repeat_node:
                for c in self.iter_score(n, doc):
                    yield c

    def find_score_sub(self, doc):
        """Find substitute for scorenode. Takes first music node that isn't
        an assignment."""
        for n in doc:
            if not isinstance(n, ly.music.items.Assignment):
                if isinstance(n, ly.music.items.Music):
                    return self.iter_score(n, doc)

    def look_ahead(self, node, find_node):
        """Looks ahead in a container node and returns True
        if the search is successful."""
        for n in node:
            if isinstance(n, find_node):
                return True
        return False

    def look_behind(self, node, find_node):
        """Looks behind on the parent node(s) and returns True
        if the search is successful."""
        parent = node.parent()
        if parent:
            if isinstance(parent, find_node):
                ret = True
            else:
                ret = self.look_behind(parent, find_node)
            return ret
        else:
            return False

    ##
    # Other functions
    ##
    def gen_med_caller(self, func_name, *args):
        """Call any function in the mediator object."""
        func_call = getattr(self.mediator, func_name)
        func_call(*args)
