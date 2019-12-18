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

import sys
import ly.document
import ly.music
from ly.pitch.transpose import Transposer
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


def eprint(*args, **kwargs):
    """
    From https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
    Prints to stderr
    """
    print(*args, file=sys.stderr, **kwargs)


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
        self.grace_slash = False
        self.grace_slur = False
        self.prev_was_grace_slur = False
        self.trem_rep = 0
        self.trem_note_count = 0
        self.trem_is_started = False
        self.piano_staff = 0
        self.staves_in_piano_staff = False
        self.staff = 0
        self.voice_count = 0
        self.numericTime = False
        self.voice_sep = False
        self.voice_sep_start_time_sig = Fraction(1, 1)
        self.voice_sep_start_total_time = 0
        self.voice_sep_start_time_since_bar = 0
        self.voice_sep_start_voice_name = None
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
        self.tie_types = []
        self.phr_slur_types = []
        self.slur_types = []
        self.slurcount = 0
        self.slurnr = 0
        self.phrslurnr = 0
        self.auto_beam = True
        self.beam = None  # Values include None, "Normal", and "Manual" (for beams made with [])
        self.prev_beam_type = None
        self.shortest_length_in_beam = Fraction(1, 4)
        self.beam_ends = []
        self.beam_exceptions = []
        self.base_moment = Fraction(1, 4)
        self.transposer = None
        self.volta_counts = []
        self.alt_endings = []
        # Variables to keep track of place in music, and place of \bar barlines and chord symbols
        self.time_sig = Fraction(1, 1)
        self.time_sig_locations = {}
        self.partial = 0
        self.first_meas = False
        self.prev_note_dur = 0
        self.total_time = 0
        self.time_since_bar = 0
        self.barline_locations = {}
        self.chord_locations = {}
        self.prev_len_before_tuplet = 0

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
        # eprint(mustree.dump())
        header_nodes = self.iter_header(mustree)
        if header_nodes:
            self.parse_nodes(header_nodes)
        score = self.get_score(mustree)
        if score:
            mus_nodes = self.iter_score(score, mustree)
        else:
            mus_nodes = self.find_score_sub(mustree)
        self.generate_location_dicts(mus_nodes)
        self.mediator.new_section("fallback")  # fallback/default section
        if score:
            mus_nodes = self.iter_score(score, mustree)
        else:
            mus_nodes = self.find_score_sub(mustree)
        self.parse_nodes(mus_nodes)

    def generate_location_dicts(self, nodes):
        r"""
        Work through all nodes in order to preemptively formulate dictionaries containing
            positions of `\bar`s and time signature changes (self.barline_locations and self.time_sig_locations)
        They will look something like {3/4: "||"} for `\bar`s
            and {3/2: {'numerator': 4, 'denominator': 4, 'length': 1, 'numeric': {1: True, 2: False}}} for time sig changes
            (The 'numeric' key contains a dictionary which indicates whether a staff number's time sig should be numeric or not)
        (The last seen '\bar' type or time signature in a given location will be prioritized over the others)

        Note: this function should be updated with any elements which affect the passage of time in the music
        """
        if nodes:
            class_name = ''
            dur = (0, 1)
            total_time = 0
            chord_mode = False
            tuplet = []
            trem_rep = 0
            grace_seq = False
            slashed_grace = False
            voice_sep = False
            voice_sep_start_total_time = 0
            voice_sep_length = 0
            prev = False
            numeric_time = False
            piano_staff = False
            staves_in_piano_staff = False
            staff = 0
            note_locations = [[(0, False)]]
            for m in nodes:
                class_name = m.__class__.__name__
                # Notes should advance total_time by their length (but not chord or grace notes)
                if (isinstance(m, ly.music.items.Durable) and not isinstance(m, ly.music.items.LyricText)
                        and not chord_mode and not isinstance(m.parent(), ly.music.items.Chord)):
                    if not grace_seq:
                        dur = m.duration
                        # In the instance of a tuplet or tremolo repeat, change the duration
                        if len(tuplet) != 0:
                            dur = (Fraction((dur[0] * tuplet[-1][1]) / tuplet[-1][0]), dur[1])
                        if trem_rep != 0:
                            dur = (dur[0] * trem_rep, dur[1])
                        total_time += dur[0] * dur[1]
                        # Log the end time of this Durable and whether it is a Skip
                        if isinstance(m, ly.music.items.Skip):
                            note_locations[-1].append((total_time, True))
                        else:
                            note_locations[-1].append((total_time, False))
                    # End slashed grace note
                    # TODO: Handle multiple/chord \slashedGrace notes
                    elif slashed_grace:
                        grace_seq = False
                        slashed_grace = False
                # Indicate chord mode (ignore notes in this mode)
                elif isinstance(m, (ly.music.items.ChordMode)):
                    chord_mode = True
                # Store scalar info (things like \times or \tuplet)
                elif isinstance(m, ly.music.items.Scaler):
                    if m.token == '\\tuplet':
                        tuplet.append((m.numerator, m.denominator))
                    else:  # \scaleDurations or \times
                        tuplet.append((m.denominator, m.numerator))
                # Store the number of repeats in a tremolo
                elif class_name == 'Repeat' and m.specifier() == 'tremolo':
                    trem_rep = m.repeat_count()
                # Indicate grace note(s)
                elif class_name == 'Grace':
                    grace_seq = True
                # Store info at beginning of voice separator section
                elif class_name == 'MusicList' and m.token == '<<' and self.look_ahead(m, ly.music.items.VoiceSeparator):
                    voice_sep = True
                    voice_sep_start_total_time = total_time
                # Reset time at a voice separator (only do so for final \\ if multiple in a row)
                elif class_name == 'VoiceSeparator' and voice_sep and self.get_next_node(m) and not self.get_next_node(m).token == r'\\':
                    note_locations.append([(voice_sep_start_total_time, False)])
                    total_time = total_time - voice_sep_length
                # A string could be a \bar type, so record its position and type if so
                elif class_name == 'String':
                    prev = self.get_previous_node(m)
                    if prev and prev.token == '\\bar':
                        self.barline_locations[total_time] = m.value()
                # Handle numeric vs default time sig commands
                elif class_name == 'Command':
                    if m.token == '\\numericTimeSignature':
                        numeric_time = True
                    elif m.token == '\\defaultTimeSignature':
                        numeric_time = False
                    if total_time in self.time_sig_locations:
                        self.time_sig_locations[total_time]['numeric'][staff] = numeric_time
                # Handle user commands (like slashedGrace notes)
                elif class_name == 'UserCommand':
                    if m.token == '\\slashedGrace':
                        grace_seq = True
                        slashed_grace = True
                # Store the location of time signature changes
                elif class_name == 'TimeSignature':
                    if total_time not in self.time_sig_locations:
                        self.time_sig_locations[total_time] = {'numerator': m.numerator(), 'denominator': m.fraction().denominator,
                                                               'length': m.measure_length(), 'numeric': {staff: numeric_time}}
                    else:
                        self.time_sig_locations[total_time]['numerator'] = m.numerator()
                        self.time_sig_locations[total_time]['denominator'] = m.fraction().denominator
                        self.time_sig_locations[total_time]['length'] = m.measure_length()
                # Handle piano staff beginning
                elif class_name == 'Context' and m.context() in pno_contexts:
                    piano_staff = True
                # Reset total_time to 0 at new voices and staves
                elif class_name == 'Context' and (m.context() == 'Voice' or m.context() in staff_contexts):
                    note_locations.append([(0, False)])
                    total_time = 0
                    if m.context() in staff_contexts and piano_staff:
                        staves_in_piano_staff = True
                    # With staves or new voices without staves in a piano staff, indicate the start of a new staff
                    if m.context() in staff_contexts or (m.context() == 'Voice' and piano_staff and not staves_in_piano_staff):
                        staff += 1
                        numeric_time = False
                # End currently running nodes
                elif class_name == 'End':
                    if m.node.token == '{':
                        # End chord mode
                        if m.node.parent().token in ['\\chordmode', '\\chords']:
                            chord_mode = False
                        # End voice separator music list (record its length)
                        elif voice_sep:
                            voice_sep_length = total_time - voice_sep_start_total_time
                    # End Voice separator section
                    elif m.node.token == '<<':
                        voice_sep = False
                        voice_sep_length = 0
                    # End scaler (\tuplet, \times, etc.)
                    elif isinstance(m.node, ly.music.items.Scaler):
                        tuplet.pop()
                    # End tremolo repeat
                    elif m.node.token == '\\repeat' and m.node.specifier() == 'tremolo':
                        trem_rep = 0
                    # End grace note(s)
                    elif isinstance(m.node, ly.music.items.Grace):
                        grace_seq = False
                    # End piano staff
                    elif isinstance(m.node, ly.music.items.Context) and m.node.context() in pno_contexts:
                        piano_staff = False
                        staves_in_piano_staff = False
            # Find any (\bar) barlines which occur during some note
            barline_locations_to_skip = []
            barline_conflict = False
            # Iterate through all found barlines
            for bar_loc in self.barline_locations.keys():
                # Iterate through sections of note locations
                for part in note_locations:
                    # Iterate through the note end locations themselves
                    for note_num in range(len(part)):
                        note_loc = part[note_num][0]
                        skip = part[note_num][1]
                        # Note ends at barline is ok
                        if note_loc == bar_loc:
                            break
                        # First note to end after barline
                        elif note_loc > bar_loc:
                            # If the note is the first in the part or is a skip then ok
                            if note_num == 0 or skip:
                                break
                            # Barline occurs during some note
                            else:
                                eprint("Warning: Barline found during note, skipping barline!")
                                barline_locations_to_skip.append(bar_loc)
                                barline_conflict = True
                                break
                    # If current barline location has a conflict, go on to check next barline location
                    if barline_conflict:
                        barline_conflict = False
                        break
            # Clear the conflicting barlines
            for loc in barline_locations_to_skip:
                if loc in self.barline_locations:
                    self.barline_locations.pop(loc)

    def parse_nodes(self, nodes):
        """Work through all nodes by calling the function with the
        same name as the nodes class."""
        if nodes:
            for m in nodes:
                # eprint(m)
                func_name = m.__class__.__name__  # get instance name
                if func_name not in excl_list:
                    try:
                        func_call = getattr(self, func_name)
                        func_call(m)
                    except AttributeError as ae:
                        eprint("Warning:", func_name, "not implemented!")
                        eprint(ae)
                        pass
        else:
            eprint("Warning! Couldn't parse source!")

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
                self.voice_sep_start_time_sig = self.time_sig
                self.voice_sep_start_total_time = self.total_time
                self.voice_sep_start_time_since_bar = self.time_since_bar
                self.voice_sep_first_meas = self.first_meas
                self.voice_sep_start_voice_name = self.mediator.voice_name
                self.mediator.store_voicenr = self.mediator.voice
                self.mediator.voice_name = '1'
            else:
                self.mediator.new_section('simultan')
                self.sims_and_seqs.append('sim')
        elif musicList.token == '{':
            self.tie_types.append('solid')
            self.phr_slur_types.append('solid')
            self.slur_types.append('solid')
            self.sims_and_seqs.append('seq')
            if self.is_volta_ending(musicList):
                end = self.alt_endings[0]
                self.mediator.new_ending(end[0], end[1], 'start', self.staff)

    def is_volta_ending(self, music_list):
        """ Returns whether a MusicList in an alternate ending of a volta repeat (not in lyrics or chord symbols) """
        return (music_list.parent().parent().token == '\\alternative'
                and music_list.parent().parent().parent().specifier() == 'volta'
                and self.alt_mode not in ['lyric', 'chord'])

    def Chord(self, chord):
        self.mediator.clear_chord()

    def Q(self, q):
        """ q, A copy of the previous chord's pitches (has its own length) """
        self.adjust_tuplet_length(q)
        self.mediator.copy_prev_chord(q.duration)
        self.check_note(q)
        self.update_beams(q)
        self.update_time_and_check(q)

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
                self.mediator.set_voicenr(nr=1)
                self.mediator.new_section('piano-staff'+str(self.piano_staff))
                self.mediator.set_staffnr(self.piano_staff)
                self.piano_staff += 1
                self.staves_in_piano_staff = True
            else:
                if token != '\\context' or self.mediator.part_not_empty():
                    self.mediator.new_part(context_id)
                self.mediator.set_voicenr(nr=1)
            self.mediator.add_staff_id(context_id)
            self.total_time = 0
            self.time_since_bar = 0
            self.first_meas = True
            self.staff += 1
            self.update_time_sig()
        elif context == 'Voice':
            # Treat voices without staves in a piano staff as staves
            if self.piano_staff and not self.staves_in_piano_staff:
                self.mediator.set_voicenr(nr=1)
                self.mediator.new_section('piano-staff'+str(self.piano_staff))
                self.mediator.set_staffnr(self.piano_staff)
                self.piano_staff += 1
                self.staff += 1
            self.total_time = 0
            self.time_since_bar = 0
            self.sims_and_seqs.append('voice')
            if context_id:
                self.mediator.voice_name = context_id
                self.mediator.new_section(context_id)
            else:
                self.mediator.voice_name = None
                self.mediator.new_section('voice')
            self.first_meas = True
            self.voice_count += 1
            self.update_time_sig()
        elif context == 'Devnull':
            self.mediator.new_section('devnull', True)
        elif context == 'Lyrics':  # The way lyrics are implemented, they don't need a new section here (prevents irrelevant warning)
            if self.alt_mode == 'lyric':
                eprint("Warning: Nested lyric sections are not supported!")  # TODO: Support nested lyrics
        elif context == 'ChordNames':
            pass  # Without using ChordMode to write actual chords, ChordNames doesn't need a new section
        else:
            eprint("Context not implemented:", context)

    def VoiceSeparator(self, voice_sep):
        # Increment voice name no matter what (for lyric assignment)
        self.mediator.voice_name = str(int(self.mediator.voice_name) + 1)
        # Prevent << \\ {... from starting on a different voice
        if self.mediator.voice_sep_sections > 0:
            self.mediator.new_snippet('sim')
            self.mediator.set_voicenr(add=True)
            if self.voice_sep:
                # Reset time information after last \\ (voice separator)
                if self.get_next_node(voice_sep).token != r"\\":  # Last \\
                    self.time_sig = self.voice_sep_start_time_sig
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
        r"""
        A new key signature (\key and \major, \minor, etc.)

        The key's pitch is transposed if the key is after a \transpose
        using a copy of the pitch (to prevent a reused key from being modified multiple times)
        """
        pitch_copy = key.pitch().copy()
        if self.transposer is not None:
            self.transposer.transpose(pitch_copy)
        self.mediator.new_key(pitch_copy.output(), key.mode())

    def Relative(self, relative):
        r"""A \relative music expression."""
        self.relative = True

    def Transpose(self, transpose):
        r""" A \transpose music expression. """
        self.transposer = Transposer(transpose[0].pitch, transpose[1].pitch)

    def transpose_note(self, note):
        """ If music should be transposed, adjust note pitch accordingly, key changes handled in KeySignature() """
        if not isinstance(note.parent(), ly.music.items.KeySignature) and self.transposer is not None:
            self.transposer.transpose(note.pitch)

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
        Checks the current note to see if any chord symbols are needed above
        Adds one to current note if needed
        Based on whether a chord symbol was defined during the duration of the note in the music
        Removes any used chord symbols from dictionary of chord symbols to ensure the symbol is only placed once
        """
        pos_to_pop = []  # Stores any chord symbol positions used during this note
        if isinstance(note.parent(), ly.music.items.Chord):
            length = note.parent().duration[0]
        else:
            length = note.length()
        for pos, chord_dict in self.chord_locations.items():
            # Check if the chord symbol at pos, is at the beginning of the note
            if pos == self.total_time - length:
                pos_to_pop.append(pos)
                self.mediator.current_note.add_harmony(chord_dict["root"], chord_dict["root-alter"],
                                                       chord_dict["bass"], chord_dict["bass-alter"],
                                                       chord_dict["text"])
            # Check if the chord symbol at pos, is anytime else during the note
            # (adds offset equal to time from beginning of note to pos)
            elif pos > self.total_time - length and pos < self.total_time:
                pos_to_pop.append(pos)
                self.mediator.current_note.add_harmony(chord_dict["root"], chord_dict["root-alter"],
                                                       chord_dict["bass"], chord_dict["bass-alter"],
                                                       chord_dict["text"], pos - (self.total_time - length))
        # Remove any used chord symbols from self.chord_locations
        for pos in pos_to_pop:
            self.chord_locations.pop(pos)

    def check_for_barline(self):
        """
        Checks at the current location in music to see if a barline is needed
        Creates a barline if needed
        """
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
            self.end_beam(current=True)
            return True
        # Create regular measure if there has been enough time since prev bar
        if self.first_meas and self.partial != 0:
            if self.time_since_bar == self.partial:
                self.time_since_bar = 0
                self.mediator.new_bar()
                self.first_meas = False
                self.end_beam(current=True)
                return True
        else:
            if self.time_since_bar == self.time_sig:
                self.time_since_bar = 0
                self.mediator.new_bar()
                self.end_beam(current=True)
                return True
        return False

    def update_time_sig(self):
        """ If time sig changes here (according to self.time_sig_locations), update current time sig accordingly """
        if self.total_time in self.time_sig_locations:
            ts = self.time_sig_locations[self.total_time]
            self.time_sig = ts['length']
            self.get_beat_structure_from_time_sig(ts['numerator'], ts['denominator'])
            numeric = False
            if self.staff in ts['numeric']:
                numeric = ts['numeric'][self.staff]
            else:
                numeric = self.numericTime
            self.mediator.new_time(ts['numerator'], ts['denominator'], numeric)

    def update_time_and_check(self, mus_obj, skip_len=0, final_skip=False):
        """
        Takes a note, rest, skip, etc. and updates total_time and time_since_bar accordingly
        Also records chord symbol locations when in 'chord' alt_mode
        After updating times, checks for barlines, time sigs, and/or chord symbols when applicable
        """
        if not self.grace_seq:
            length = 0
            # Skip lengths are given manually, otherwise use the object's length
            if skip_len:
                length = skip_len
            else:
                length = mus_obj.length()
            if length:
                self.prev_note_dur = length
                # When in chord alt_mode, record chord symb locations
                if self.alt_mode == "chord":
                    if not isinstance(mus_obj, ly.music.items.Skip):
                        self.chord_locations[self.total_time] = {"root": mus_obj.token.capitalize()[0],
                                                                 "root-alter": int(mus_obj.pitch.alter * 2),
                                                                 "bass": False, "bass-alter": 0, "text": ""}
                    self.total_time += length
                # When not in chord alt_mode, treat notes as notes
                else:
                    self.time_since_bar += length
                    self.total_time += length
                    # Check for bar/time sigs unless final note in voice separator (in which case, wait until after)
                    if not self.voice_sep or (skip_len and not final_skip):
                        self.check_for_barline()
                        self.update_time_sig()
                    else:
                        node = mus_obj
                        while True:
                            if not self.get_next_node(node):
                                break
                            elif isinstance(self.get_next_node(node), ly.music.items.Durable):
                                self.check_for_barline()
                                self.update_time_sig()
                                break
                            else:
                                node = self.get_next_node(node)
                    if not skip_len:
                        self.check_for_chord(mus_obj)
            # First note of chord is used to update time and check for chord symbols,
            #     but must wait for end of chord to check for barlines/time sigs (see End())
            elif mus_obj is not None and isinstance(mus_obj.parent(), ly.music.items.Chord):
                self.prev_note_dur = mus_obj.parent().duration[0]
                self.time_since_bar += mus_obj.parent().duration[0]
                self.total_time += mus_obj.parent().duration[0]
                self.check_for_chord(mus_obj)
        else:
            # Handle end of \slashedGrace (since it is not a Grace object)
            # TODO: Handle multiple/chord \slashedGrace notes
            if self.grace_slash and not self.grace_slur:
                self.grace_slash = False
                self.grace_slur = False
                self.grace_seq = False

    def adjust_tuplet_length(self, obj):
        r""" Adjusts the length of notes within a \tuplet """
        self.prev_len_before_tuplet = obj.length()
        if isinstance(obj.parent(), ly.music.items.Chord):  # Adjust length of total chord not singular note in chord
            obj = obj.parent()
        if len(self.tuplet) != 0:
            obj.duration = ((Fraction(obj.duration[0] * self.tuplet[-1]["fraction"][1]) / self.tuplet[-1]["fraction"][0]), obj.duration[1])

    def end_beam(self, current=False):
        """ Ends an ongoing beam not started with [ (prev_note if current is False, current_note otherwise) """
        if self.prev_beam_type != "Manual":
            if current:
                note = self.mediator.current_note
            else:
                note = self.mediator.prev_note
            if hasattr(note, "beam"):
                if note.beam == "continue":
                    note.set_beam("end")
                elif note.beam == "begin":
                    note.set_beam(False)
            self.beam = None
            self.shortest_length_in_beam = Fraction(1, 4)

    def note_ends_on_beam_end(self, time_after_note):
        """ Return True/False based on whether time_after_note is a beam end (exception or otherwise) """
        for exception in self.beam_exceptions:  # In order from least to greatest fractions
            if exception['fraction'] >= self.shortest_length_in_beam:
                return time_after_note in exception['ends']
        return time_after_note in self.beam_ends

    def update_beams(self, note):
        """
        Based on lilypond automatic beaming rules found at `/scm/time-signature-settings.scm` within the lilypond repository
        See also: http://lilypond.org/doc/v2.19/Documentation/notation/beams#setting-automatic-beam-behavior

        Given a note:
        Begins beam when not currently beamed, auto beam is on, and note is not on specified beam end
        Continues exisiting beam when note doesn't end on a specified beam end
        Ends beam when current note is a quarter or longer or note ends on specified beam end
        """
        time_after_note = self.time_since_bar + note.length()
        # Only beam notes shorter than a quarter
        #     Note: quarter note tuplets should not be beamed
        if (note.length() < Fraction(1, 4) and not self.tuplet) or (self.prev_len_before_tuplet < Fraction(1, 4) and self.tuplet):
            # Beams started without [
            if self.beam == "Normal":
                if self.shortest_length_in_beam > note.length():
                    self.shortest_length_in_beam = note.length()
                if self.note_ends_on_beam_end(time_after_note):
                    self.mediator.current_note.set_beam("end")
                    self.beam = None
                    self.shortest_length_in_beam = Fraction(1, 4)
                else:
                    self.mediator.current_note.set_beam("continue")
            # Beams started with [
            elif self.beam == "Manual":
                if not self.mediator.current_note.beam:
                    self.mediator.current_note.set_beam("continue")
            # No ongoing beams
            elif self.beam is None and self.auto_beam:
                self.shortest_length_in_beam = note.length()
                if not self.note_ends_on_beam_end(time_after_note):
                    self.mediator.current_note.set_beam("begin")
                    self.beam = "Normal"
                    self.prev_beam_type = "Normal"
                else:
                    self.shortest_length_in_beam = Fraction(1, 4)
        # Quarter note or longer ends ongoing beam
        else:
            self.end_beam()

    def Note(self, note):
        """ notename, e.g. c, cis, a bes ... """
        # eprint(note.token)
        self.adjust_tuplet_length(note)
        self.transpose_note(note)
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
                self.update_beams(note)
                self.update_time_and_check(note)
            else:
                if self.alt_mode == "chord":  # if chord symbols are being written, record location of chord
                    self.update_time_and_check(note)
                elif isinstance(note.parent(), ly.music.items.Relative):
                    self.mediator.set_relative(note)
                    self.rel_pitch_isset = True
                elif isinstance(note.parent(), ly.music.items.Chord):
                    # Secondary note in chord
                    if self.mediator.current_chord:
                        self.mediator.new_chord(note, chord_base=False)
                    # First note in chord
                    else:
                        self.mediator.new_chord(note, note.parent().duration, self.relative)
                        self.check_tuplet()
                        self.update_beams(note.parent())
                        self.update_time_and_check(note)
                    # chord as grace note
                    if self.grace_seq:
                        self.mediator.new_chord_grace(self.grace_slash)

    def Unpitched(self, unpitched):
        """A note without pitch, just a standalone duration."""
        self.adjust_tuplet_length(unpitched)
        if unpitched.length():
            if self.alt_mode == 'drum':
                self.mediator.new_iso_dura(unpitched, self.relative, True)
            else:
                self.mediator.new_iso_dura(unpitched, self.relative)
            self.check_note(unpitched)
            self.update_beams(unpitched)
        self.update_time_and_check(unpitched)

    def DrumNote(self, drumnote):
        """A note in DrumMode."""
        self.adjust_tuplet_length(drumnote)
        if drumnote.length():
            self.mediator.new_note(drumnote, is_unpitched=True)
            self.check_note(drumnote)
            self.update_beams(drumnote)
        self.update_time_and_check(drumnote)

    def handle_tremolo_start_stop(self):
        """ Set multinote tremolos. The first note gets the 'start' type, subsequent notes get no type. """
        if not self.trem_is_started:
            ttype = 'start'
            self.trem_is_started = True
        else:
            ttype = None
        self.mediator.set_tremolo(trem_type=ttype, repeats=self.trem_rep, note_count=self.trem_note_count)

    def check_note(self, note):
        """Generic check for all notes, both pitched and unpitched."""
        self.check_tuplet()
        # Handle grace notes and their slurs (marked as grace note slurs to avoid lyrics skipping notes)
        if self.grace_seq:
            self.mediator.new_grace(self.grace_slash)
            if self.grace_slur:
                if not self.prev_was_grace_slur:
                    self.slurcount += 1
                    self.slurnr = self.slurcount
                    self.mediator.set_slur(self.slurnr, "start", grace=True)
                    self.prev_was_grace_slur = True
                else:
                    self.mediator.set_slur(self.slurnr, "continue", grace=True)
                    self.slurcount -= 1
        else:
            if self.prev_was_grace_slur:
                self.mediator.set_slur(self.slurnr, "stop", grace=True)
                self.prev_was_grace_slur = False
        if self.trem_rep:
            # Update the duration of the note
            note.duration = (note.duration[0] * self.trem_rep, note.duration[1])
            # Set tremolo if there isn't a duration change
            if not self.look_ahead(note, ly.music.items.Duration):
                self.handle_tremolo_start_stop()

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
            if self.alt_mode not in ["chord", "lyric"]:  # Avoids \skip # in lyrics
                self.mediator.new_duration_token(duration.token, duration.tokens)
                if self.trem_rep:
                    self.handle_tremolo_start_stop()

    def Tempo(self, tempo):
        """ Tempo direction, e g '4 = 80' """
        if self.look_ahead(tempo, ly.music.items.Duration):
            self.tempo = (tempo.tempo(), tempo.text())
        else:
            self.mediator.new_tempo(0, (), tempo.tempo(), tempo.text())

    def Tie(self, tie):
        """ tie ~ """
        self.mediator.tie_to_next(self.tie_types[-1])

    def Rest(self, rest):
        r""" rest, r or R. Note: NOT by command, i.e. \rest """
        self.adjust_tuplet_length(rest)
        if rest.token == 'R':
            self.scale = 'R'
        self.mediator.new_rest(rest)
        self.check_note(rest)
        self.update_time_and_check(rest)
        self.end_beam()

    def Skip(self, skip):
        r""" invisible rest/spacer rest (s or command \skip)"""
        self.adjust_tuplet_length(skip)
        if self.alt_mode == 'lyric':
            self.mediator.new_lyrics_item(skip.token)
        elif self.alt_mode == "chord":
            self.total_time += skip.length()
        else:
            self.break_skip_at_barline(skip)

    def place_skip(self, length, final=False, node=None):
        """ Manually place a skip of specified length, updating relevant information """
        if length != 0:
            self.mediator.current_is_rest = True
            self.mediator.clear_chord()
            self.mediator.prev_note = self.mediator.current_note
            self.mediator.current_note = xml_objs.BarRest((length, Fraction(1, 1)), voice=self.mediator.voice, voice_name=self.mediator.voice_name, skip=True)
            self.mediator.check_current_note(rest=True)
            self.update_time_and_check(node, skip_len=length, final_skip=final)  # node used to determine whether skip ends voice sep section
            self.end_beam()

    def break_skip_at_barline(self, skip):
        r"""
        When a skip goes over any measure breaks (\bar, regular bar, pickup bar), break skip into measure length pieces
        Handle any remaining skip length after last break
        """
        break_locations = []
        remaining_length = skip.length()
        time_since_bar = self.time_since_bar
        partial = 0
        prev_break = 0
        # Get break locations from \bar positions
        for bar_location in self.barline_locations:
            if bar_location > self.total_time and bar_location <= self.total_time + remaining_length:
                break_locations.append(bar_location - self.total_time)
        # Get break location from pickup measure if needed
        if self.first_meas and self.partial != 0 and remaining_length >= self.partial - time_since_bar:
            partial = self.partial - time_since_bar
            break_locations.append(partial)
            remaining_length -= partial
            time_since_bar = 0
        # Get break location from measure already started
        if time_since_bar and remaining_length >= self.time_sig - time_since_bar:
            partial = self.time_sig - time_since_bar
            break_locations.append(partial)
            remaining_length -= partial
            time_since_bar = 0
        # Get break locations from full measure lengths
        if remaining_length >= self.time_sig:
            for i in range(remaining_length // self.time_sig):
                break_locations.append(partial + self.time_sig * (i + 1))
        break_locations.sort()
        # Determine length of skip for any remaining length after the last break
        if len(break_locations) > 0:
            final_skip_length = skip.length() - break_locations[-1]
        else:
            final_skip_length = skip.length()  # Skip was not broken, so entire skip still needs placement
        # Place skips for each (unique) break location
        for i in range(len(break_locations)):
            break_loc = break_locations[i]
            skip_length = break_loc - prev_break
            # If there isn't any remaining length after this skip, indicate that it is the final one
            if i == len(break_locations) - 1 and final_skip_length == 0:
                self.place_skip(skip_length, final=True, node=skip)
            else:
                self.place_skip(skip_length)
            prev_break = break_loc
        # Place last skip (if its length isn't 0)
        self.place_skip(final_skip_length, final=True, node=skip)

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
        """ Beam, "[" = begin, "]" = end. """
        if beam.token == "[":
            self.mediator.current_note.set_beam("begin")
            self.end_beam()
            if self.beam == "Manual":  # Should never be True
                self.mediator.current_note.set_beam("continue")
                eprint("Warning: Beam start does not have corresponding beam end!")
            self.beam = "Manual"
            self.prev_beam_type = "Manual"
        elif beam.token == "]":
            if self.beam == "Manual":
                self.mediator.current_note.set_beam("end")
                self.beam = None
            else:  # Should never be True
                eprint("Warning: Beam end does not have corresponding beam start!")

    def Partial(self, partial):
        r""" \partial # """
        self.partial = partial.partial_length()

    def Slur(self, slur):
        """ Slur, '(' = start, ')' = stop. """
        if slur.token == '(':
            self.slurcount += 1
            self.slurnr = self.slurcount
            self.mediator.set_slur(self.slurnr, "start", False, self.slur_types[-1])
        elif slur.token == ')':
            self.mediator.set_slur(self.slurnr, "stop", False, self.slur_types[-1])
            self.slurcount -= 1

    def PhrasingSlur(self, phrslur):
        r"""A \( or \)."""
        if phrslur.token == r'\(':
            self.slurcount += 1
            self.phrslurnr = self.slurcount
            self.mediator.set_slur(self.phrslurnr, "start", True, self.phr_slur_types[-1])
        elif phrslur.token == r'\)':
            self.mediator.set_slur(self.phrslurnr, "stop", True, self.phr_slur_types[-1])
            self.slurcount -= 1

    def Dynamic(self, dynamic):
        """Any dynamic symbol."""
        self.mediator.new_dynamics(dynamic.token[1:])

    def Grace(self, grace):
        if grace.token == '\\acciaccatura':
            self.grace_slash = True
            self.grace_slur = True
        elif grace.token == '\\appoggiatura':
            self.grace_slash = False
            self.grace_slur = True
        else:
            self.grace_slash = False
            self.grace_slur = False
        self.grace_seq = True

    def generate_beam_ends(self, fraction, beat_pattern):
        """ Given a denominator and a pattern of beats to count by (array), return an array of the intended beam end locations """
        beam_ends = []
        prev_beam_end = 0
        for beat in beat_pattern:
            beam_end = prev_beam_end + beat * fraction
            beam_ends.append(beam_end)
            prev_beam_end = beam_end
        return beam_ends

    def get_beat_structure_from_time_sig(self, numerator, denominator):
        """
        Get the beat structure and exceptions from a given key signature (numerator and denominator)

        Rules derived from Lilypond's `/scm/time-signature-settings.scm` see http://lilypond.org/doc/v2.19/Documentation/notation/beams#setting-automatic-beam-behavior
        """
        # Generate beam_ends (default) (an array of beam end locations (fractions))
        self.beam_ends = []
        fraction = Fraction(1, denominator)
        beat_pattern = []
        if numerator > 3 and numerator % 3 == 0:   # numerators like 6, 9, 12,...
            for i in range(numerator // 3):
                beat_pattern.append(3)
            self.beam_ends = self.generate_beam_ends(Fraction(1, denominator), beat_pattern)
        elif numerator == 4 and denominator == 8:  # 4/8
            beat_pattern = [2, 2]
        elif numerator == 5 and denominator == 8:  # 5/8
            beat_pattern = [3, 2]
        elif numerator == 8 and denominator == 8:  # 8/8
            beat_pattern = [3, 3, 2]
        else:                                      # all other time signatures
            for i in range(numerator):
                beat_pattern.append(1)
        self.beam_ends = self.generate_beam_ends(fraction, beat_pattern)
        # Generate beam_exceptions (an array of dictionaries containing a lowest fraction and its associated beam ends array) sorted by fraction
        self.beam_exceptions = []
        exception_rules = {}
        if numerator == 2 and denominator == 2:     # 2/2
            exception_rules[Fraction(1, 32)] = [8, 8, 8, 8]
        elif numerator == 3 and denominator == 2:   # 3/2
            exception_rules[Fraction(1, 32)] = [8, 8, 8, 8, 8, 8]
        elif numerator == 3 and denominator == 4:   # 3/4
            exception_rules[Fraction(1, 8)] = [6]
            exception_rules[Fraction(1, 12)] = [3, 3, 3]
        elif numerator == 3 and denominator == 8:   # 3/8
            exception_rules[Fraction(1, 8)] = [3]
        elif numerator == 4 and denominator == 2:   # 4/2
            exception_rules[Fraction(1, 16)] = [4, 4, 4, 4, 4, 4, 4, 4]
        elif numerator == 4 and denominator == 4:   # 4/4
            exception_rules[Fraction(1, 8)] = [4, 4]
            exception_rules[Fraction(1, 12)] = [3, 3, 3, 3]
        elif numerator == 6 and denominator == 4:   # 6/4
            exception_rules[Fraction(1, 16)] = [4, 4, 4, 4, 4, 4]
        elif numerator == 9 and denominator == 4:   # 9/4
            exception_rules[Fraction(1, 32)] = [8, 8, 8, 8, 8, 8, 8, 8]
        elif numerator == 12 and denominator == 4:  # 12/4
            exception_rules[Fraction(1, 32)] = [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8]
        for fract in sorted(exception_rules.keys()):
            self.beam_exceptions.append({"fraction": fract, "ends": self.generate_beam_ends(fract, exception_rules[fract])})

    def TimeSignature(self, timeSign):
        r""" See update_time_sig() and generate_location_dicts() for more on how `\time` is implemented """
        pass

    def Repeat(self, repeat):
        r""" A \repeat specifier num {...} provides various types of repetition depending on specifier. """
        if repeat.specifier() == 'volta':
            if self.alt_mode not in ['lyric', 'chord']:
                self.volta_counts.append(repeat.repeat_count())
                self.mediator.new_repeat('forward')
        elif repeat.specifier() == 'tremolo':
            self.trem_rep = repeat.repeat_count()
            if isinstance(repeat[0], ly.music.items.MusicList):  # List of notes
                self.trem_note_count = len(repeat[0])
            else:  # Singular note
                self.trem_note_count = 1
        else:  # TODO: Support percent repeats
            eprint("Warning: Repeat", repeat.specifier(), "is not supported!")

    def Alternative(self, alt):
        r""" A \alternative {...} provides alternate endings. """
        if self.alt_mode not in ['lyric', 'chord']:
            num_endings = len(alt[0])
            num_repeats = self.volta_counts.pop()
            if num_endings > num_repeats:
                eprint('Warning: More alternate endings than repeats!')
            # Create a stack of ending lists of form [starting_repeat_num, ending_repeat_num, is_last]
            for ending_num in range(1, num_endings + 1):
                if ending_num == 1:  # First ending
                    self.alt_endings.append([ending_num, num_repeats - num_endings + ending_num, False])
                else:  # All other endings
                    self.alt_endings.append([num_repeats - num_endings + ending_num, num_repeats - num_endings + ending_num, False])
                if ending_num == num_endings:  # If last ending, indicate so
                    self.alt_endings[-1][-1] = True

    def Tremolo(self, tremolo):
        """A tremolo item ":"."""
        if self.look_ahead(tremolo, ly.music.items.Duration):
            self.tremolo = True
        else:
            self.mediator.set_tremolo()

    def With(self, cont_with):
        r"""A \with ... construct."""
        self.with_contxt = cont_with.parent().context()

    def set_base_moment(self, numer_denom):
        self.base_moment = Fraction(numer_denom[0], numer_denom[1])

    def set_beat_structure(self, beat_list):
        self.beam_ends = []
        prev_end = 0
        for num in beat_list:
            prev_end += self.base_moment * num
            self.beam_ends.append(prev_end)

    def set_ignore_melismata(self, ignore):
        """ Sends command within lyrics to ignore beams (True) or skip over them (False). """
        if ignore:
            self.mediator.new_lyrics_item(["ignoreMelismata", True, "command"])
        else:
            self.mediator.new_lyrics_item(["ignoreMelismata", False, "command"])

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
        if cont_set.property() == 'baseMoment':
            self.set_base_moment(cont_set.value().get_list_ints())
        elif cont_set.property() == 'beatStructure':
            self.beam_ends = self.generate_beam_ends(self.base_moment, cont_set.value().get_list_ints())
        # TODO: Add functionality for setting custom beam exceptions (currently just clears beam_exceptions, as this is common)
        elif cont_set.property() == 'beamExceptions':
            self.beam_exceptions = []
        elif cont_set.property() == 'associatedVoice':
            self.mediator.new_lyrics_item(["switchVoice", cont_set.value().value(), "command"])
        elif cont_set.property() == 'ignoreMelismata':
            self.set_ignore_melismata(cont_set.value().get_bool())
        else:
            eprint("Warning: Set", cont_set.property(), "failed!")

    def Unset(self, cont_unset):
        r""" A \unset command. """
        if cont_unset.property() == 'ignoreMelismata':
            self.mediator.new_lyrics_item(["ignoreMelismata", False, "command"])
        else:
            eprint("Warning: Unset", cont_unset.property(), "failed!")

    def Command(self, command):
        r""" \bar, \rest etc """
        excls = ['\\major', '\\dorian', '\\minor', '\\bar']
        if command.token == '\\rest':
            self.mediator.note2rest()
        elif command.token == '\\numericTimeSignature':
            self.numericTime = True
            # If the current bar has no music and is in common or cut time, then change it to numeric time
            if self.mediator.bar and not self.mediator.bar.has_music() and self.mediator.current_attr.time and self.mediator.current_attr.time[-1] in ['common', 'cut']:
                self.mediator.current_attr.time.pop()
        elif command.token == '\\defaultTimeSignature':
            self.numericTime = False
            # If the current bar has no music and is 2/2 or 4/4, then change it to cut or common time respectively
            #     Don't add 'cut' or 'common' tag if one already exists
            if self.mediator.bar and not self.mediator.bar.has_music() and self.mediator.current_attr.time and len(self.mediator.current_attr.time) == 2:
                num = self.mediator.current_attr.time[0]
                den = self.mediator.current_attr.time[1]
                if num == 2 and den == 2:
                    self.mediator.current_attr.time.append('cut')
                elif num == 4 and den == 4:
                    self.mediator.current_attr.time.append('common')
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
        elif command.token == '\\noBeam':
            self.end_beam()
            if self.prev_beam_type == "Normal":  # noBeam does not apply to [] beams
                self.mediator.current_note.set_beam(False)
        elif command.token == '\\autoBeamOn':
            self.auto_beam = True
        elif command.token == '\\autoBeamOff':
            self.auto_beam = False
        elif command.token == '\\slurSolid':
            self.slur_types[-1] = 'solid'
        elif command.token == '\\slurDashed':
            self.slur_types[-1] = 'dashed'
        elif command.token == '\\slurDotted':
            self.slur_types[-1] = 'dotted'
        elif command.token == '\\tieSolid':
            self.tie_types[-1] = 'solid'
        elif command.token == '\\tieDashed':
            self.tie_types[-1] = 'dashed'
        elif command.token == '\\tieDotted':
            self.tie_types[-1] = 'dotted'
        elif command.token == '\\phrasingSlurSolid':
            self.phr_slur_types[-1] = 'solid'
        elif command.token == '\\phrasingSlurDashed':
            self.phr_slur_types[-1] = 'dashed'
        elif command.token == '\\phrasingSlurDotted':
            self.phr_slur_types[-1] = 'dotted'
        elif command.token == '\\break':
            self.mediator.set_sys_break()
        elif command.token == '\\breathe':
            self.mediator.set_breathe()
        else:
            if command.token not in excls:
                eprint("Unknown command:", command.token)

    def UserCommand(self, usercommand):
        """Music variables are substituted so this must be something else."""
        if usercommand.name() == 'tupletSpan':
            self.tupl_span = True
        elif usercommand.name() == 'slashedGrace':
            self.grace_slash = True
            self.grace_slur = False
            self.grace_seq = True

    def String(self, string):
        r"""
        Handles case where multiple words are to be placed on one note (ex: "all these words")

        See check_for_barline() and generate_location_dicts() for more on how `\bar "..."` is implemented
        """
        if self.alt_mode == 'lyric' and self.look_behind(string, ly.music.items.LyricText):
            self.mediator.new_lyrics_text(string.tokens[0])

    def LyricsTo(self, lyrics_to):
        r"""A \lyricsto expression. """
        self.mediator.new_lyric_section('lyricsto'+lyrics_to.context_id(), lyrics_to.context_id())
        self.sims_and_seqs.append('lyrics')

    def LyricText(self, lyrics_text):
        """
        A lyric text (word, markup or string), with a Duration

        Create a lyric text if there is text or the next node is not a String
            in which case, wait to allow that String to be the lyric text (see String() above)
        """
        if lyrics_text.token or not self.look_ahead(lyrics_text, ly.music.items.String):
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
        elif self.look_behind(item, ly.music.items.Set):
            pass  # See Set()
        else:
            eprint("SchemeItem not implemented:", item.token)

    def SchemeQuote(self, quote):
        """A ' in scheme."""
        pass

    def SchemeList(self, slist):
        """ A (...) inside scheme (handled eslewhere on a case-by-case basis). """
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
        elif isinstance(end.node, ly.music.items.Grace):  # Grace notes (except \slashedGrace)
            self.grace_slash = False
            self.grace_slur = False
            self.grace_seq = False
        elif end.node.token == '\\repeat':
            if end.node.specifier() == 'volta' and self.alt_mode not in ['lyric', 'chord']:
                # Create an ending repeat barline if there are no alternate endings (otherwise the repeat signs are already between endings)
                if not self.look_ahead(end.node, ly.music.items.Alternative):
                    self.mediator.new_repeat('backward')
                elif not self.look_ahead(end.node[-1][0], ly.music.items.MusicList):
                    self.mediator.new_repeat('backward')
                    eprint("Warning: Alternate ending has no music lists!")
            elif end.node.specifier() == 'tremolo':
                if self.look_ahead(end.node, ly.music.items.MusicList):
                    self.mediator.set_tremolo(trem_type="stop")
                else:
                    self.mediator.set_tremolo(trem_type="single")
                self.trem_is_started = False
                self.trem_rep = 0
        elif isinstance(end.node, ly.music.items.Context):
            self.in_context = False
            if end.node.context() == 'Voice':
                self.mediator.check_voices()
                self.sims_and_seqs.pop()
            elif end.node.context() in group_contexts:
                self.mediator.close_group()
            elif end.node.context() in staff_contexts:
                self.numericTime = False
                if not self.piano_staff:
                    self.mediator.check_part()
            elif end.node.context() in pno_contexts:
                self.mediator.check_voices()
                self.mediator.check_part()
                self.piano_staff = 0
                self.staves_in_piano_staff = False
                self.mediator.set_voicenr(nr=1)
            elif end.node.context() == 'Devnull':
                self.mediator.check_voices()
            elif end.node.context() == 'Lyrics':
                self.mediator.check_voices()
        elif end.node.token == '<<':
            if self.voice_sep:
                self.mediator.check_voices_by_nr()
                self.mediator.set_voicenr(nr=self.mediator.store_voicenr)
                self.voice_sep = False
                self.voice_sep_length = 0
                self.check_for_barline()
                self.update_time_sig()
                self.mediator.voice_sep_sections = 0
                self.mediator.voice_name = self.voice_sep_start_voice_name
                self.voice_sep_start_voice_name = None
            elif not self.piano_staff and not self.alt_mode == 'lyric':  # Simultaneous lyric sections not currently supported
                self.mediator.check_simultan()
                if self.sims_and_seqs:
                    self.sims_and_seqs.pop()
        elif end.node.token == '{':
            self.tie_types.pop()
            self.phr_slur_types.pop()
            self.slur_types.pop()
            if self.sims_and_seqs:
                self.sims_and_seqs.pop()
            if end.node.parent().token == '<<':
                self.mediator.voice_sep_sections += 1
                self.voice_sep_length = self.total_time - self.voice_sep_start_total_time
            if end.node.parent().token in ["\\notemode", "\\notes", "\\chordmode", "\\chords",
                                           "\\drummode", "\\drums", "\\figuremode", "\\figures",
                                           "\\lyricmode", "\\lyrics", "\\addlyrics"]:
                self.alt_mode = None
            elif end.node.parent().token == '\\transpose':
                self.transposer = None
            if self.is_volta_ending(end.node):
                end = self.alt_endings.pop(0)
                if end[2]:  # Final ending
                    self.mediator.new_ending(end[0], end[1], 'discontinue', self.staff)
                else:  # All others
                    self.mediator.new_ending(end[0], end[1], 'stop', self.staff)
        elif end.node.token == '<':  # chord
            self.mediator.chord_end()
            # Check for bar unless final note in voice separator (in which case, wait until after)
            if not self.voice_sep:
                self.check_for_barline()
                self.update_time_sig()
            else:
                node = end.node
                while True:
                    if not self.get_next_node(node):
                        break
                    elif isinstance(self.get_next_node(node), ly.music.items.Durable):
                        self.check_for_barline()
                        self.update_time_sig()
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
            # eprint("end:", end.node.token)
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

    def simple_node_gen(self, nodes):
        """Unlike iter_score are the subnodes yielded without substitution."""
        for starting_node in nodes:
            for n in starting_node:
                yield n
                for s in self.simple_node_gen([n]):
                    yield s

    def iter_header(self, tree):
        """Iter only over header nodes (could be more than one header)."""
        headers = []
        for t in tree:
            if isinstance(t, ly.music.items.Header):
                headers.append(t)
        if headers:
            return self.simple_node_gen(headers)

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
        # Create list of repeat_count alternate endings (in reverse order) if there are any
        #     (the first ending is repeated to fill in the difference between the number of endings and repeat_count)
        num_endings = 0
        endings = []
        for node in repeat_node:
            if isinstance(node, ly.music.items.Alternative):
                num_endings = len(node[0])
                if num_endings > repeat_count:
                    num_endings = repeat_count
                    eprint("Warning: More alternate endings than unfold repeats (removing extras)!")
                if num_endings != 0:
                    # Append all endings from the last ending until the second ending (reverse order)
                    for i in range(num_endings - 1, 0, -1):
                        endings.append(node[0][i])
                    # Repeat first ending
                    for i in range(repeat_count - num_endings + 1):
                        endings.append(node[0][0])
                break
        # Duplicate the nodes in the repeat
        for r in range(repeat_count):
            # Duplicate nodes in the body of the repeat
            for n in repeat_node:
                if not isinstance(n, ly.music.items.Alternative):
                    for c in self.iter_score(n, doc):
                        yield c
            # Produce one ending (if any) after every time the body of the repeat has been duplicated
            if endings:
                for alt in self.iter_score(endings.pop(), doc):
                    yield alt

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
