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

"""
The information of the parsed source is organised into an object
structure with help of the classes in ly.musicxml.xml_objs.
"""

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

from fractions import Fraction

import ly.duration
import ly.pitch

from . import xml_objs


class Mediator():
    """Help class that acts as mediator between the ly source parser
    and the XML creating modules."""

    def __init__(self):
        """ create global lists """
        self.score = xml_objs.Score()
        self.sections = []
        self.part_sections = []
        """ default and initial values """
        self.insert_into = None
        self.current_note = None
        self.current_lynote = None
        self.current_is_rest = False
        self.current_time = Fraction(4, 4)
        self.moment = Fraction(0)
        self.time_changes = {Fraction(0): Fraction(1)}
        self.partials = {}
        self.simultaneous = []
        self.note_tail = None
        self.action_onnext = []
        self.dur_token = "4"
        self.dur_tokens = ()
        self.dots = 0
        self.tied = False
        self.voice = 1
        self.staff = 0
        self.part = None
        self.group = None
        self.group_num = 0
        self.current_chord = []
        self.q_chord = []
        self.prev_pitch = None
        self.prev_chord_pitch = None
        self.store_voicenr = 0
        self.staff_id_dict = {}
        self.store_unset_staff = False
        self.staff_unset_notes = {}
        self.lyric_sections = {}
        self.lyric = None
        self.lyric_syll = False
        self.lyric_nr = 1
        self.ongoing_wedge = False
        self.ongoing_dashes = False
        self.after_empty_chord = False
        self.dynamics_onnext = []
        self.octdiff = 0
        self.prev_tremolo = 8
        self.tupl_dur = 0
        self.tupl_sum = 0
        self.slur_stack = []
        self.multiple_rest = False
        self.multiple_rest_bar = None
        self.current_mark = 1
        self.stem_dir = None
        self.grace = None
        self.prev_bar = None
        self.after_grace_bar = None

    def new_header_assignment(self, name, value):
        """Distributing header information."""
        creators = ['composer', 'arranger', 'poet', 'lyricist']
        if name == 'title':
            self.score.title = value
        elif name in ['copyright', 'tagline']:
            self.score.add_right(value, name)
        elif name in creators:
            self.score.creators[name] = value
        else:
            self.score.info[name] = value

    def new_section(self, name, glob=False):
        name = self.check_name(name)
        section = xml_objs.ScoreSection(name, glob)
        self.insert_into = section
        self.sections.append(section)
        self.bar = None

    def new_snippet(self, name):
        name = self.check_name(name)
        snippet = xml_objs.Snippet(name, self.insert_into)
        self.insert_into = snippet
        self.sections.append(snippet)
        self.bar = None

    def new_lyric_section(self, name, voice_id):
        name = self.check_name(name)
        lyrics = xml_objs.LyricsSection(name, voice_id)
        self.insert_into = lyrics
        self.lyric_sections[name] = lyrics

    def check_name(self, name, nr=1):
        n = self.get_var_byname(name)
        if n:
            name = name+str(nr)
            name = self.check_name(name, nr+1)
        return name

    def get_var_byname(self, name):
        for n in self.sections + self.part_sections:
            if n.name == name:
                return n

    def new_group(self):
        parent = self.group
        self.group_num += 1
        self.group = xml_objs.ScorePartGroup(self.group_num, "bracket")
        if parent: #nested group
            self.group.parent = parent
            parent.partlist.append(self.group)
        else:
            self.score.partlist.append(self.group)

    def close_group(self):
        if self.group.parent:
            self.group = self.group.parent
        else:
            self.group = None

    def change_group_bracket(self, system_start):
        self.group.set_bracket(get_group_symbol(system_start))

    def new_part(self, pid=None, to_part=None, piano=False):
        if piano:
            self.part = xml_objs.ScorePart(2, pid, to_part)
        else:
            self.part = xml_objs.ScorePart(part_id=pid, to_part=to_part)
        if not to_part:
            if self.group:
                self.group.partlist.append(self.part)
            else:
                self.score.partlist.append(self.part)
        self.insert_into = self.part
        self.bar = None

    def part_not_empty(self):
        return self.part and self.part.barlist

    def get_part_by_id(self, pid, partholder=None):
        if not partholder:
            partholder = self.score
        ret = False
        for part in partholder.partlist:
            if isinstance(part, xml_objs.ScorePartGroup):
                ret = self.get_part_by_id(pid, part)
            else:
                if part.part_id == pid:
                    ret = part
        return ret

    def set_voicenr(self, command=None, add=False, nr=0, piano=0):
        if add:
            if not self.store_voicenr:
                self.store_voicenr = self.voice
            self.voice += 1
        elif nr:
            self.voice = nr
        else:
            self.voice = get_voice(command)
            if piano>2:
                self.voice += piano+1

    def revert_voicenr(self):
        self.voice = self.store_voicenr
        self.store_voicenr = 0

    def set_staffnr(self, staffnr, staff_id=None):
        self.store_unset_staff = False
        if staffnr:
            self.staff = staffnr
        elif staff_id in self.staff_id_dict:
            self.staff = self.staff_id_dict[staff_id]
        elif staff_id:
            self.store_unset_staff = True
            self.staff = staff_id

    def add_staff_id(self, staff_id):
        self.store_unset_staff = False
        if staff_id:
            if staff_id in self.staff_id_dict:
                self.staff = self.staff_id_dict[staff_id]
            else:
                self.staff_id_dict[staff_id] = self.staff
            if staff_id in self.staff_unset_notes:
                for n in self.staff_unset_notes[staff_id]:
                    n.staff = self.staff

    def add_snippet(self, snippet_name):
        """ Adds snippet to previous barlist.
        A snippet can be shorter than a full bar,
        so this can also mean continuing a previous bar."""
        def continue_barlist(insert_into):
            self.insert_into = insert_into
            if insert_into.barlist:
                self.bar = insert_into.barlist[-1]
            else:
                self.new_bar(False)

        snippet = self.get_var_byname(snippet_name)
        continue_barlist(snippet.merge_barlist)
        for bb in snippet.barlist:
            # skip the empty bar started at the end of the snippet
            if len(bb.obj_list) > 1 or bb.obj_list[0].has_attr():
                for b in bb.obj_list:
                    self.bar.add(b)
            if bb.list_full:
                self.new_bar()

    def check_voices(self):
        """ Checks active sections. The two latest created are merged.
        Also checks for empty sections. """
        if self.sections[-1].glob:
            self.score.merge_globally(self.sections[-1])
            self.score.glob_section.merge_voice(self.section[-1])
        if len(self.sections)>2:
            if not self.sections[-2].barlist:
                self.sections.pop(-2)
                self.check_voices()
            elif not self.sections[-1].barlist:
                self.sections.pop()
                self.check_voices()
            else:
                self.sections[-2].merge_voice(self.sections[-1])
                self.sections.pop()

    def check_voices_by_nr(self):
        """ Used for snippets. Merges all active snippets
        created after the stored voice number."""
        sect_len = len(self.sections)
        if sect_len>2:
            if self.voice>1:
                for n in range(self.store_voicenr, self.voice):
                    self.check_voices()
                if isinstance(self.sections[-1], xml_objs.Snippet):
                    self.add_snippet(self.sections[-1].name)
                    self.sections.pop()
                else:
                    print("WARNING: problem adding snippet!")

    def check_lyrics(self, voice_id):
        """Check the finished lyrics section and merge it into
        the referenced voice."""
        if self.lyric[1] == 'middle':
            self.lyric[1] = 'end'
        lyrics_section = self.lyric_sections['lyricsto'+voice_id]
        voice_section = self.get_var_byname(lyrics_section.voice_id)
        if voice_section:
            voice_section.merge_lyrics(lyrics_section)
        else:
            print("Warning can't merge in lyrics!", voice_section)

    def check_part(self):
        """Adds the latest active section to the part."""
        if len(self.sections)>1:
            if self.score.is_empty():
                self.new_part()
            if self.sections[-1].glob:
                self.part.merge_voice(self.sections[-1])
            else:
                self.part.barlist.extend(self.sections[-1].barlist)
                # still findable by name, e.g. for \lyricsto
                self.part_sections.append(self.sections.pop())
        if self.part and self.part.to_part:
            self.part.merge_part_to_part()
        self.part.merge_voice(self.score.glob_section)
        name = self.check_name("glob")
        self.score.glob_section = self.part.extract_global_to_section(name)
        self.part = None

    def check_simultan(self):
        """Check done after simultanoues (<< >>) section."""
        if self.sections:
            if self.part:
                self.part.merge_voice(self.sections[-1])
            elif len(self.sections)>1:
                self.sections[-2].merge_voice(self.sections[-1])
            self.sections.pop()

    def check_score(self):
        """
        Check score

        If no part were created, place first variable (fallback) as part.

        Apply the latest global section.
        """
        if self.score.is_empty():
            self.new_part()
            self.part.barlist.extend(self.get_first_var())
        self.score.merge_globally(self.score.glob_section, override=True)

    def get_first_var(self):
        if self.sections:
            return self.sections[0].barlist

    def set_pickup(self, length):
        self.partials[self.moment] = length
        if self.bar is None:
            self.new_bar()
        self.bar.pickup = not self.moment

    def measure_grid(self, moment):
        """Return the start of the time signature or \\partial in effect at
        moment, the measure length and the first barline after the start."""
        start = max(m for m in self.grid_changes() if m <= moment)
        length = self.time_changes[max(m for m in self.time_changes if m <= moment)]
        return start, length, start + self.partials.get(start, length)

    def grid_changes(self):
        """Return the moments where the barlines are laid out anew."""
        return set(self.time_changes) | set(self.partials)

    def next_barline(self, moment):
        """Return the moment of the first barline after moment."""
        start, length, barline = self.measure_grid(moment)
        if barline <= moment:
            barline += ((moment - barline) // length + 1) * length
        return min([barline] + [m for m in self.grid_changes() if m > moment])

    def is_barline(self, moment):
        """Return True if there is a barline at moment."""
        start, length, barline = self.measure_grid(moment)
        return moment == start or moment >= barline and (moment - barline) % length == 0

    def bar_check(self):
        if not self.is_barline(self.moment):
            print("Warning: bar check failed at", self.moment)

    def new_simultaneous(self):
        """Store the start of a simultaneous expression (<< >>)."""
        self.simultaneous.append([self.moment, self.moment])

    def next_simultaneous(self):
        """A part of a simultaneous expression is parsed: the next one
        starts again at the start."""
        sim = self.simultaneous[-1]
        sim[1] = max(sim[1], self.moment)
        self.moment = sim[0]

    def end_simultaneous(self):
        """A simultaneous expression ends with its longest part."""
        self.moment = max(self.simultaneous.pop()[1], self.moment)

    def new_bar(self, fill_prev=True):
        self.prev_bar = self.bar
        if self.bar and fill_prev:
            self.bar.list_full = True
        self.current_attr = xml_objs.BarAttr()
        self.bar = xml_objs.Bar()
        if not self.moment and 0 in self.partials:
            self.bar.pickup = True
        self.bar.obj_list = [self.current_attr]
        self.insert_into.barlist.append(self.bar)

    def add_to_bar(self, obj):
        if self.bar is None:
            self.new_bar()
        self.bar.add(obj)

    def create_barline(self, bl):
        # Barlines are written at the right side of a measure, so a barline
        # before any music in the part has no place and is left out.
        if self.bar is None:
            return
        barline = xml_objs.BarAttr()
        barline.set_barline(bl)
        self.bar.add(barline)
        self.new_bar()

    def new_repeat(self, rep):
        barline = xml_objs.BarAttr()
        barline.set_barline(rep)
        barline.repeat = rep
        if self.bar is None:
            self.new_bar()
        self.bar.add(barline)

    def new_key(self, key_name, mode):
        if self.bar is None:
            self.new_bar()
        if self.bar.has_music():
            new_bar_attr = xml_objs.BarAttr()
            new_bar_attr.set_key(get_fifths(key_name, mode), mode)
            self.add_to_bar(new_bar_attr)
        else:
            self.current_attr.set_key(get_fifths(key_name, mode), mode)

    def bijective(self, n):
        '''encodes an int to a sequence of letters'''
        import string
        digits = string.ascii_uppercase.replace("I","")
        result = []
        while n > 0:
            n, mod = divmod(n - 1, len(digits))
            result += digits[mod]
        return ''.join(reversed(result))

    def new_mark(self, num_mark = None):
        if num_mark == None:
            if self.bar is None:
                self.new_bar()
            if self.bar.has_attr():
                self.current_attr.set_mark(self.bijective(self.current_mark))
            else:
                new_bar_attr = xml_objs.BarAttr()
                new_bar_attr.set_mark(self.bijective(self.current_mark))
                self.add_to_bar(new_bar_attr)
        elif num_mark <= 0:
            print("Mark value out of range")
        else:
            self.current_mark = num_mark
            self.current_attr.set_mark(self.bijective(self.current_mark))
        self.current_mark += 1

    def new_word(self, word):
        if self.bar is None:
            self.new_bar()
        if self.bar.has_attr():
            self.current_attr.set_word(word)
        else:
            new_bar_attr = xml_objs.BarAttr()
            new_bar_attr.set_word(word)
            self.add_to_bar(new_bar_attr)

    def new_time(self, num, den, numeric=False):
        self.current_time = Fraction(num, den.denominator)
        self.time_changes[self.moment] = self.current_time
        if self.bar is None or self.bar.has_music():
            self.new_bar()
        self.current_attr.set_time([num, den.denominator], numeric)

    def new_clef(self, clefname):
        self.clef = clefname2clef(clefname)
        if self.bar is None:
            self.new_bar()
        if self.bar.has_music():
            new_bar_attr = xml_objs.BarAttr()
            new_bar_attr.set_clef(self.clef)
            self.add_to_bar(new_bar_attr)
        else:
            if self.staff:
                self.current_attr.multiclef.append((self.clef, self.staff))
            else:
                self.current_attr.set_clef(self.clef)

    def set_relative(self, note):
        self.prev_pitch = note.pitch

    def end_note(self):
        """The current note, rest or chord is complete: move the moment
        to its end. A note that crosses a barline is split and tied over it,
        and a new bar is started at the barline."""
        notes = self.current_chord or [self.current_note]
        end = self.moment + notes[0].length()
        barline = self.next_barline(self.moment)
        if end > barline:
            while end > barline:
                notes = self.set_length(notes, barline - self.moment)
                self.moment = barline
                self.new_bar()
                notes = self.continue_notes(notes)
                barline = self.next_barline(barline)
            notes = self.set_length(notes, end - self.moment)
        self.moment = end
        if end == barline:
            self.new_bar()
        self.note_tail = notes[0]

    def set_length(self, notes, length):
        """Give the notes (of a note or chord) the length, tying more notes
        to them when one note value is not enough. Return the last notes."""
        scaling = notes[0].tuplet_scaling()
        for i, (value, dots, durtype) in enumerate(note_values(length / scaling)):
            if i:
                notes = self.continue_notes(notes)
            for n in notes:
                n.set_duration((value, Fraction(1)), durtype)
                n.dot = dots
        return notes

    def continue_notes(self, notes):
        """Add and return the continuations of the notes of a note or chord."""
        conts = [n.continuation() for n in notes]
        for c in conts[1:]:
            # the notes of a chord share their ties, see new_chordnote
            c.tie = conts[0].tie
        for c in conts:
            self.bar.add(c)
        return conts

    def new_note(self, note, rel=False, is_unpitched=False):
        self.current_is_rest = False
        self.clear_chord()
        if is_unpitched:
            self.current_note = self.create_unpitched(note)
            self.check_current_note(is_unpitched=True)
        else:
            self.current_note = self.create_barnote_from_note(note)
            self.current_lynote = note
            self.check_current_note(rel)
        if self.grace:
            self.current_note.set_grace(*self.grace)
        if self.stem_dir:
            self.current_note.set_stem_direction(self.stem_dir)
        self.do_action_onnext(self.current_note)
        self.action_onnext = []

    def new_iso_dura(self, note, rel=False, is_unpitched=False):
        """
        Isolated durations in music sequences.

        An isolated duration in LilyPond is rendered as a normal note but the
        pitch information is missing and has to be filled in by some other
        means, usually by the previous pitch. (RhythmicStaff is an exception
        since it ignores specified pitches anyway).

        """
        if self.current_chord:
            self.copy_prev_chord(note.duration)
        else:
            if not is_unpitched:
                if self.current_lynote:
                    note.pitch = self.current_lynote.pitch
                else:
                    # like LilyPond, use c' if there is no previous pitch
                    note.pitch = ly.pitch.Pitch(octave=1)
            self.new_note(note, rel, is_unpitched)

    def create_unpitched(self, unpitched):
        """Create a xml_objs.Unpitched from ly.music.items.Unpitched."""
        dura = unpitched.duration
        return xml_objs.Unpitched(dura)

    def create_barnote_from_note(self, note):
        """Create a xml_objs.BarNote from ly.music.items.Note."""
        p = getNoteName(note.pitch.note)
        alt = get_xml_alter(note.pitch.alter)
        try:
            acc = note.accidental_token
        except AttributeError:
            acc = ""
        dura = note.duration
        return xml_objs.BarNote(p, alt, acc, dura, self.voice)

    def copy_barnote_basics(self, bar_note):
        """Create a copy of a xml_objs.BarNote."""
        p = bar_note.base_note
        alt = bar_note.alter
        acc = bar_note.accidental_token
        dura = bar_note.duration
        voc = bar_note.voice
        copy = xml_objs.BarNote(p, alt, acc, dura, voc)
        copy.octave = bar_note.octave
        copy.chord = bar_note.chord
        return copy

    def new_duration_token(self, token, tokens):
        self.dur_token = token
        self.dur_tokens = tokens
        self.check_duration(self.current_is_rest)

    def check_current_note(self, rel=False, rest=False, is_unpitched=False):
        """ Perform checks common for all new notes and rests. """
        if not rest and not is_unpitched:
            self.set_octave(rel)
        if not rest:
            if self.tied:
                self.current_note.set_tie('stop')
                self.tied = False
        self.note_tail = self.current_note
        self.check_duration(rest)
        if self.staff:
            self.current_note.set_staff(self.staff)
            if self.store_unset_staff:
                if self.staff in self.staff_unset_notes:
                    self.staff_unset_notes[self.staff].append(self.current_note)
                else:
                    self.staff_unset_notes[self.staff] = [self.current_note]
        self.add_to_bar(self.current_note)
        self.after_empty_chord = False
        for dynamics in self.dynamics_onnext:
            self.set_dynamics(dynamics)
        self.dynamics_onnext = []

    def stem_direction(self, direction):
        if direction == '\\stemUp':
            self.stem_dir = 'up'
        elif direction == '\\stemDown':
            self.stem_dir = 'down'
        elif direction == '\\stemNeutral':
            self.stem_dir = None

    def set_octave(self, relative):
        """Set octave by getting the octave of an absolute note + 3."""
        p = self.current_lynote.pitch.copy()
        if relative:
            p.makeAbsolute(self.prev_pitch)
        self.prev_pitch = p
        self.current_note.set_octave(p.octave + 3)

    def do_action_onnext(self, note):
        """Perform the stored action on the next note."""
        for action in self.action_onnext:
            func_call = getattr(self, action[0])
            func_call(note, *action[1])

    def check_duration(self, rest):
        """Check the duration for the current note."""
        dots, rs = self.duration_from_tokens(self.dur_tokens)
        if rest and rs: # special case of multibar rest
            if not self.current_note.show_type or self.current_note.skip:
                bs = self.current_note.duration
                if rs == bs[1]:
                    self.current_note.duration = (bs[0], 1)
                    self.current_note.dot = 0
                    self.scale_rest(bs)
                    return
        self.current_note.dot = dots
        self.dots = dots
        self.current_note.set_durtype(durval2type(self.dur_token))
        if self.current_chord:
            for c in self.current_chord:
                c.set_durtype(durval2type(self.dur_token))

    def new_chord(self, note, duration=None, rel=False, chord_base=True):
        if chord_base:
            self.new_chordbase(note, duration, rel)
            self.current_chord.append(self.current_note)
        else:
            self.current_chord.append(self.new_chordnote(note, rel))
        if self.grace:
            self.current_chord[-1].set_grace(*self.grace)
        self.do_action_onnext(self.current_chord[-1])

    def new_chordbase(self, note, duration, rel=False):
        self.current_note = self.create_barnote_from_note(note)
        self.current_note.set_duration(duration)
        self.current_lynote = note
        self.check_current_note(rel)

    def new_chordnote(self, note, rel):
        chord_note = self.create_barnote_from_note(note)
        chord_note.set_duration(self.current_note.duration)
        chord_note.set_durtype(durval2type(self.dur_token))
        chord_note.dots = self.dots
        chord_note.tie = self.current_note.tie
        chord_note.tuplet = self.current_note.tuplet
        if not self.prev_chord_pitch:
            self.prev_chord_pitch = self.prev_pitch
        p = note.pitch.copy()
        if(rel):
            p.makeAbsolute(self.prev_chord_pitch)
        chord_note.set_octave(p.octave + 3)
        self.prev_chord_pitch = p
        chord_note.chord = True
        self.bar.add(chord_note)
        return chord_note

    def new_drum_chordnote(self, duration):
        """A note of a chord in drum mode; the first one is the chord base."""
        if self.current_chord:
            chord_note = xml_objs.Unpitched(self.current_note.duration)
            chord_note.set_durtype(self.current_note.type)
            chord_note.dot = self.current_note.dot
            chord_note.tuplet = self.current_note.tuplet
            chord_note.chord = True
            self.bar.add(chord_note)
        else:
            self.current_note = chord_note = xml_objs.Unpitched(duration)
            self.check_current_note(is_unpitched=True)
        self.current_chord.append(chord_note)
        self.do_action_onnext(chord_note)

    def copy_prev_chord(self, duration):
        if self.current_chord:
            prev_chord = self.current_chord
            self.clear_chord()
        else:
            prev_chord = self.q_chord
        for i, pc in enumerate(prev_chord):
            cn = self.copy_barnote_basics(pc)
            cn.set_duration(duration)
            cn.set_durtype(durval2type(self.dur_token))
            if i == 0:
                self.current_note = cn
            self.current_chord.append(cn)
            if self.tied:
                cn.set_tie('stop')
            self.bar.add(cn)
        self.tied = False

    def clear_chord(self):
        self.q_chord = self.current_chord
        self.current_chord = []
        self.prev_chord_pitch = None

    def chord_end(self):
        """Actions when chord is parsed."""
        self.action_onnext = []

    def new_rest(self, rest):
        self.current_is_rest = True
        self.clear_chord()
        rtype = rest.token
        dur = rest.duration
        if rtype == 'r':
            self.current_note = xml_objs.BarRest(dur, self.voice)
        elif rtype == 'R':
            self.current_note = xml_objs.BarRest(dur, self.voice, show_type=False)
            if self.multiple_rest:
                self.set_mult_rest_bar(dur)
        elif rtype == 's' or rtype == '\\skip':
            self.current_note = xml_objs.BarRest(dur, self.voice, skip=True)
        self.check_current_note(rest=True)

    def note2rest(self):
        """Note used as rest position transformed to rest."""
        dur = self.current_note.duration
        voice = self.current_note.voice
        pos = [self.current_note.base_note, self.current_note.octave]
        self.current_note = xml_objs.BarRest(dur, voice, pos=pos)
        self.check_duration(rest=True)
        self.bar.obj_list.pop()
        self.bar.add(self.current_note)

    def set_mult_rest(self):
        self.multiple_rest = True

    def set_mult_rest_bar(self, dur):
        """ add multiple-rest attribute to bar """
        if self.bar is None:
            self.new_bar()
        multp = dur[1]
        rest_size = int(multp * (dur[0]/self.current_time))
        new_bar_attr = xml_objs.BarAttr()
        new_bar_attr.set_multp_rest(rest_size)
        self.bar.add(new_bar_attr)

    def scale_rest(self, bs):
        """ create multiple whole bar rests """
        dur = self.current_note.duration
        voc = self.current_note.voice
        st = self.current_note.show_type
        sk = self.current_note.skip
        multp = int(bs[1] * (bs[0]/self.current_time))
        for i in range(1, int(multp)):
            self.moment += dur[0] * dur[1]
            self.new_bar()
            rest_copy = xml_objs.BarRest(dur, voice=voc, show_type=st, skip=sk)
            self.add_to_bar(rest_copy)

    def change_to_tuplet(self, tfraction, ttype, nr, length=None):
        """Change the current note into a tuplet note."""
        tuplscaling = Fraction(tfraction[0], tfraction[1])
        if self.tupl_dur:
            if self.tupl_sum == 0:
                ttype = "start"
            base, scaling = self.current_note.duration
            self.tupl_sum += (1 / tuplscaling) * base * scaling
            if self.tupl_sum == self.tupl_dur:
                ttype = "stop"
                self.tupl_sum = 0
        if length:
            acttype = normtype = durval2type(self.calc_tupl_den(tfraction, length))
            self.current_note.set_tuplet(tfraction, ttype, nr, acttype, normtype)
        else:
            self.current_note.set_tuplet(tfraction, ttype, nr)

    def change_tuplet_type(self, index, newtype):
        self.note_tail.tuplet[index].ttype = newtype

    def set_tuplspan_dur(self, token=None, tokens=None, fraction=None):
        """
        Catch duration set by the tupletSpannerDuration property.

        Set the fraction directly or calculate it from tokens.
        """
        if fraction:
            self.tupl_dur = fraction
        else:
            base, scaling = ly.duration.base_scaling((token,) + tokens)
            self.tupl_dur = base * scaling

    def unset_tuplspan_dur(self):
        """Reset tuplet duration sum and tuplet spanner duration."""
        self.tupl_sum = 0
        self.tupl_dur = 0

    def calc_tupl_den(self, tfraction, length):
        """Calculate the tuplet denominator from
        fraction and duration of tuplet."""
        return tfraction[1] / length

    def tie_to_next(self):
        tie_type = 'start'
        self.tied = True
        self.note_tail.set_tie(tie_type)

    def set_slur(self, nr, slur_type, phrasing=False):
        """
        Set the slur start or stop for the current note.
        phrasing should be set to True if the slur is meant to be a phrasing mark.
        """

        slur_start = None

        if slur_type == 'stop':
            slur_start = self.slur_stack.pop()

        self.current_note.set_slur(nr, slur_type, phrasing, slur_start)

        if slur_type == 'start':
            self.slur_stack.append(self.current_note.slur[-1])

    def new_articulation(self, art_token):
        """
        An articulation, fingering, string number, or other symbol.

        Grouped as articulations, ornaments, technical and others.
        """
        if isinstance(art_token, ly.lex.lilypond.Fingering):
            self.current_note.add_fingering(art_token)
        else:
            ret = artic_token2xml_name(art_token)
            if ret == 'ornament':
                self.current_note.add_ornament(art_token[1:])
            elif ret == 'other':
                self.current_note.add_other_notation(art_token[1:])
            elif ret:
                self.current_note.add_articulation(ret)

    def empty_chord(self):
        """An empty chord <>, its dynamics belong to the next note or rest."""
        self.after_empty_chord = True

    def new_dynamics(self, dynamics):
        if self.after_empty_chord:
            self.dynamics_onnext.append(dynamics)
        else:
            self.set_dynamics(dynamics)

    def set_dynamics(self, dynamics):
        """Set the dynamics on the current note."""
        hairpins = {'<': 'crescendo', '>': 'diminuendo'}
        text_dyn = {'cresc': 'cresc.', 'decresc': 'descresc.',
                    'dim': 'dim.'}
        if dynamics == '!':
            if self.ongoing_wedge:
                self.current_note.set_dynamics_wedge('stop')
                self.ongoing_wedge = False
            if self.ongoing_dashes:
                self.current_note.set_dynamics_dashes('stop')
                self.ongoing_dashes = False
        elif dynamics in hairpins:
            self.current_note.set_dynamics_wedge(hairpins[dynamics])
            self.ongoing_wedge = True
        elif dynamics in text_dyn:
            self.current_note.set_dynamics_text(text_dyn[dynamics])
            self.current_note.set_dynamics_dashes('start', before=False)
            self.ongoing_dashes = True
        elif self.ongoing_wedge:
            self.current_note.set_dynamics_wedge('stop')
            self.current_note.set_dynamics_mark(dynamics)
            self.ongoing_wedge = False
        elif self.ongoing_dashes:
            self.current_note.set_dynamics_dashes('stop')
            self.current_note.set_dynamics_mark(dynamics)
            self.ongoing_dashes = False
        else:
            self.current_note.set_dynamics_mark(dynamics)

    def start_grace(self, slash=0, steal_time_previous=0):
        """The following notes are grace notes, after-graces if
        steal_time_previous is set."""
        self.grace = (slash, steal_time_previous)
        if steal_time_previous and not self.bar.has_music():
            # the main note filled its bar, the after-graces belong to its end
            self.after_grace_bar = self.bar
            self.bar = self.prev_bar

    def end_grace(self):
        self.grace = None
        if self.after_grace_bar:
            self.bar = self.after_grace_bar
            self.after_grace_bar = None

    def new_gliss(self, line=None):
        if line:
            line = get_line_style(line)
        if self.current_chord:
            for n, c in enumerate(self.current_chord):
                c.set_gliss(line, nr=n+1)
        else:
            self.current_note.set_gliss(line)
        self.action_onnext.append(("end_gliss", (line, )))

    def end_gliss(self, note, line):
        if self.current_chord:
            n = len(self.current_chord)
        else:
            n = 1
        note.set_gliss(line, endtype="stop", nr=n)

    def set_tremolo(self, trem_type='single', duration=0, repeats=0):
        if self.current_note.tremolo[1]: #tremolo already set
            self.current_note.set_tremolo(trem_type)
        else:
            if repeats:
                duration = int(self.dur_token)
                bs, durtype = calc_trem_dur(repeats, self.current_note.duration, duration)
                self.current_note.duration = bs
                self.current_note.type = durtype
            elif not duration:
                duration = self.prev_tremolo
            else:
                self.prev_tremolo = duration
            self.current_note.set_tremolo(trem_type, duration)

    def new_trill_spanner(self, end=None):
        if not end:
            self.current_note.add_ornament('trill')
            end = "start"
        self.current_note.add_adv_ornament('wavy-line', end)

    def new_ottava(self, octdiff):
        octdiff = int(octdiff)
        if self.octdiff == octdiff:
            return
        if self.octdiff:
            if self.octdiff < 0:
                plac = "below"
            else:
                plac = "above"
            size = abs(self.octdiff) * 7 + 1
            self.current_note.set_oct_shift(plac, "stop", size)
        if octdiff:
            if octdiff < 0:
                plac = "below"
                octdir = "up"
            else:
                plac = "above"
                octdir = "down"
            size = abs(octdiff) * 7 + 1
            self.action_onnext.append(("set_ottava", (plac, octdir, size)))
        self.octdiff = octdiff

    def set_ottava(self, note, plac, octdir, size):
        note.set_oct_shift(plac, octdir, size)

    def new_tempo(self, unit, dur_tokens, tempo, string):
        dots, rs = self.duration_from_tokens(dur_tokens)
        if tempo:
            beats = tempo[0]
        else:
            beats = 0
        try:
            text = string.value()
        except AttributeError:
            text = None
        tempo = xml_objs.BarAttr()
        unittype = durval2type(unit) if unit else ''
        tempo.set_tempo(unit, unittype, beats, dots, text)
        if self.bar is None:
            self.new_bar()
        self.bar.add(tempo)

    def set_by_property(self, prprty, value, group=False):
        """Generic setter for different properties."""
        if prprty == 'instrumentName':
            if group:
                self.set_groupname(value)
            else:
                self.set_partname(value)
        elif prprty == 'shortInstrumentName':
            if group:
                self.set_groupabbr(value)
            else:
                self.set_partabbr(value)
        elif prprty == 'midiInstrument':
            self.set_partmidi(value)
        elif prprty == 'stanza':
            self.new_lyric_nr(value)
        elif prprty == 'systemStartDelimiter':
            self.change_group_bracket(value)

    def set_partname(self, name):
        if self.score.is_empty():
            self.new_part()
        self.part.name = name

    def set_partabbr(self, abbr):
        if self.score.is_empty():
            self.new_part()
        self.part.abbr = abbr

    def set_groupname(self, name):
        if self.group:
            self.group.name = name

    def set_groupabbr(self, abbr):
        if self.group:
            self.group.abbr = abbr

    def set_partmidi(self, midi):
        if self.score.is_empty():
            self.new_part()
        self.part.midi = midi

    def new_lyric_nr(self, num):
        self.lyric_nr = num

    def new_lyrics_text(self, txt):
        if self.lyric:
            if self.lyric_syll:
                if self.lyric[1] in ['begin', 'middle']:
                    self.lyric = [txt, 'middle', self.lyric_nr]
            else:
                if self.lyric[1] in ['begin', 'middle']:
                    self.lyric[1] = 'end'
                self.lyric = [txt, 'single', self.lyric_nr]
        else:
            self.lyric = [txt, 'single', self.lyric_nr]
        self.insert_into.barlist.append(self.lyric)
        self.lyric_syll = False

    def new_lyrics_item(self, item):
        if item == '--':
            if self.lyric:
                if self.lyric[1] == 'single':
                    self.lyric[1] = 'begin'
                self.lyric_syll = True
        elif item == '__':
            self.lyric.append("extend")
        elif item == '\\skip':
            self.insert_into.barlist.append("skip")

    def duration_from_tokens(self, tokens):
        """Calculate dots and multibar rests from tokens."""
        dots = 0
        rs = 0
        for t in tokens:
            if t == '.':
                dots += 1
            elif '*' in t and '/' not in t:
                rs = int(t[1:])
        return (dots, rs)

    def add_break(self):
        if self.bar is None:
            self.new_bar()
        self.current_attr.add_break('yes')


##
# Translation functions
##

def getNoteName(index):
    noteNames = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    return noteNames[index]

def get_xml_alter(alter):
    """ Convert alter to the specified format,
    i e int if it's int and float otherwise.
    Also multiply with 2."""
    alter *= 2
    if float(alter).is_integer():
        return alter
    else:
        return float(alter)

def durval2type(durval):
    """Convert LilyPond duration to MusicXML duration type."""
    xml_types = [
        "maxima", "long", "breve", "whole",
        "half", "quarter", "eighth",
        "16th", "32nd", "64th",
        "128th", "256th", "512th", "1024th", "2048th"
    ] # Note: 2048 is supported by ly but not by MusicXML!
    try:
        type_index = ly.duration.durations.index(str(durval))
    except ValueError:
        type_index = 5
    return xml_types[type_index]

def get_fifths(key, mode):
    fifths = 0
    sharpkeys = ['c', 'g', 'd', 'a', 'e', 'b', 'fis', 'cis', 'gis',
    'dis', 'ais', 'eis', 'bis', 'fisis', 'cisis']
    flatkeys = ['c', 'f', 'bes', 'es', 'as', 'des', 'ges', 'ces', 'fes',
    'beses', 'eses', 'ases']
    if key in sharpkeys:
        fifths = sharpkeys.index(key)
    elif key in flatkeys:
        fifths = -flatkeys.index(key)
    if mode=='minor':
        return fifths-3
    elif mode=='major':
        return fifths
    elif mode=='dorian':
        return fifths-2

def clefname2clef(clefname):
    """
    To add a clef look up the clef name in LilyPond
    and the corresponding definition in musicXML.
    Add it to the python dictionary below.
    """
    clef_dict = {
    "treble": ('G', 2, 0),
    "violin": ('G', 2, 0),
    "G": ('G', 2, 0),
    "bass": ('F', 4, 0),
    "F": ('F', 4, 0),
    "alto": ('C', 3, 0),
    "C": ('C', 3, 0),
    "tenor": ('C', 4, 0),
    "treble_8": ('G', 2, -1),
    "treble_15": ('G', 2, -2),
    "bass_8": ('F', 4, -1),
    "bass_15": ('F', 4, -2),
    "treble^8": ('G', 2, 1),
    "treble^15": ('G', 2, 2),
    "bass^8": ('F', 4, 1),
    "bass^15": ('F', 4, 2),
    "percussion": ('percussion', 0, 0),
    "tab": ('TAB', 5, 0),
    "soprano": ('C', 1, 0),
    "mezzosoprano": ('C', 2, 0),
    "baritone": ('C', 5, 0),
    "varbaritone": ('F', 3, 0),
    "baritonevarF": ('F', 3, 0),
    "french": ('G', 1, 0),
    "subbass": ('F', 5, 0),
    # From here on the clefs will end up with wrong symbols
    "GG": ('G', 2, -1),
    "tenorG": ('G', 2, -1),
    "varC": ('C', 3, 0),
    "altovarC": ('C', 3, 0),
    "tenorvarC": ('C', 4, 0),
    "baritonevarC": ('C', 5, 0),

    }
    try:
        clef = clef_dict[clefname]
    except KeyError:
        clef = 0
    return clef

def note_values(length):
    """Split a length (in whole notes) into the values of plain or dotted
    notes, as (value, dots, type) tuples."""
    values = []
    while length:
        log, base = 0, Fraction(1)
        while base > length:
            log, base = log + 1, base / 2
        while log > -3 and base * 2 <= length:
            log, base = log - 1, base * 2
        value, dots = base, 0
        if length.denominator & (length.denominator - 1):
            # not a sum of note values, e.g. in a 4:3 tuplet
            value = length
        while value + base / 2 ** (dots + 1) <= length:
            dots += 1
            value += base / 2 ** dots
        values.append((value, dots, durval2type(ly.duration.tostring(log))))
        length -= value
    return values

def get_voice(c):
    voices = ["voiceOne", "voiceTwo", "voiceThree", "voiceFour"]
    return voices.index(c)+1

def artic_token2xml_name(art_token):
    """
    From Articulations in ly.music.items.
    Grouped as articulations, ornaments and others.

    To add an articulation look up the name or abbreviation
    in LilyPond and the corresponding node name in musicXML.
    Add it to the python dictionary below.
    """
    artic_dict = {
    ".": "staccato", "-": "tenuto", ">": "accent",
    "_": "detached-legato", "!": "staccatissimo",
    "\\staccatissimo": "staccatissimo", "\\breathe":"breath-mark"
    }
    ornaments = ['\\trill', '\\prall', '\\mordent', '\\turn']
    others = ['\\fermata']
    try:
        return artic_dict[art_token]
    except KeyError:
        if art_token in ornaments:
            return "ornament"
        elif art_token in others:
            return "other"
        else:
            return False

def calc_trem_dur(repeats, base_scaling, duration):
    """ Calculate tremolo duration from number of
    repeats and initial duration. """
    base = base_scaling[0]
    scale = base_scaling[1]
    new_base = base * repeats
    if repeats > duration:
        import ly.duration
        trem_length = ly.duration.tostring(int((repeats // duration) * -0.5))
    else:
        trem_length = str(duration // repeats)
    new_type = durval2type(trem_length)
    return (new_base, scale), new_type

def get_line_style(style):
    style_dict = {
    "dashed-line": "dashed",
    "dotted-line": "dotted",
    "trill": "wavy",
    "zigzag": "wavy"
    }
    try:
        return style_dict[style]
    except KeyError:
        return False

def get_group_symbol(lily_sys_start):
    symbol_dict = {
        "SystemStartBrace": "brace",
        "SystemStartSquare": "square"
        }
    try:
        return symbol_dict[lily_sys_start]
    except KeyError:
        return False
