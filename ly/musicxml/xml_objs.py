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
Classes that holds information about a musical score,
suitable for converting to musicXML.

When the score structure is built, it can easily be used to create a musicXML.

Example::

    from ly.musicxml import create_musicxml, xml_objs

    musxml = create_musicxml.CreateMusicXML()

    score = xml_objs.Score()
    part = xml_objs.ScorePart()
    score.partlist.append(part)
    bar = xml_objs.Bar()
    part.barlist.append(bar)
    ba = xml_objs.BarAttr()
    ba.set_time([4,4])
    bar.obj_list.append(ba)
    c = xml_objs.BarNote('c', 0, 0, (1,1))
    c.set_octave(4)
    c.set_durtype(1)
    bar.obj_list.append(c)

    xml_objs.IterateXmlObjs(score, musxml, 1)
    xml = musxml.musicxml()
    xml.write(filename)

"""

from __future__ import unicode_literals
from __future__ import print_function

from fractions import Fraction


class IterateXmlObjs():
    """
    A ly.musicxml.xml_objs.Score object is iterated and the Music XML node tree
    is constructed.

    """

    def __init__(self, score, musxml, div):
        """Create the basic score information, and initiate the
        iteration of the parts."""
        # score.debug_score([])
        self.musxml = musxml
        self.divisions = div
        if score.title:
            self.musxml.create_title(score.title)
        for ctag in sorted(score.creators.keys()):
            self.musxml.add_creator(ctag, score.creators[ctag])
        for itag in sorted(score.info.keys()):
            self.musxml.create_score_info(itag, score.info[itag])
        if score.rights:
            self.musxml.add_rights(score.rights)
        for p in score.partlist:
            if isinstance(p, ScorePart):
                self.iterate_part(p)
            elif isinstance(p, ScorePartGroup):
                self.iterate_partgroup(p)

    def iterate_partgroup(self, group):
        """Loop through a group, recursively if nested."""
        self.musxml.create_partgroup(
            'start', group.num, group.name, group.abbr, group.bracket)
        for p in group.partlist:
            if isinstance(p, ScorePart):
                self.iterate_part(p)
            elif isinstance(p, ScorePartGroup):
                self.iterate_partgroup(p)
        self.musxml.create_partgroup('stop', group.num)

    def iterate_part(self, part):
        """The part is iterated."""
        if part.barlist:
            part.set_first_bar(self.divisions)
            self.musxml.create_part(part.name, part.abbr, part.midi)
            for bar in part.barlist:
                self.iterate_bar(bar)
        else:
            print("Warning: empty part:", part.name)

    def iterate_bar(self, bar):
        """The objects in the bar are output to the xml-file."""
        if len(bar.obj_list) > 1:  # Prevents empty measures from being made
            self.musxml.create_measure()
            for obj in bar.obj_list:
                if isinstance(obj, BarAttr):
                    self.new_xml_bar_attr(obj)
                elif isinstance(obj, BarMus):
                    self.before_note(obj)
                    if isinstance(obj, BarNote):
                        self.new_xml_note(obj)
                    elif isinstance(obj, BarRest):
                        self.new_xml_rest(obj)
                    self.after_note(obj)
                elif isinstance(obj, BarBackup):
                    divdur = self.count_duration(obj.duration, self.divisions)
                    self.musxml.add_backup(divdur)

    def new_xml_bar_attr(self, obj):
        """Create bar attribute xml-nodes."""
        if obj.has_attr():
            self.musxml.new_bar_attr(obj.clef, obj.time, obj.key, obj.mode, obj.divs)
        # Place repeats, alternate endings, and their associated barlines
        if obj.endings or obj.repeat is not None:
            # Get repeat
            forward_rep = None
            backward_rep = None
            if obj.repeat == 'forward':
                forward_rep = obj.repeat
            elif obj.repeat == 'backward':
                backward_rep = obj.repeat
            # Get endings
            ending_start = None
            ending_end = None
            for end in obj.endings:
                if end.etype == 'start':
                    ending_start = end
                else:
                    ending_end = end
            # Left barline
            if forward_rep is not None or ending_start is not None or obj.left_barline is not None:
                self.musxml.add_barline(obj.left_barline, ending_start, forward_rep)
            # Right barline
            if backward_rep is not None or ending_end is not None or obj.barline is not None:
                self.musxml.add_barline(obj.barline, ending_end, backward_rep)
        # Place barline without any repeats or alternate endings
        elif obj.barline:
            self.musxml.add_barline(obj.barline, None, None)
        if obj.staves:
            self.musxml.add_staves(obj.staves)
        if obj.multiclef:
            for mc in obj.multiclef:
                self.musxml.add_clef(sign=mc[0][0], line=mc[0][1], nr=mc[1], oct_ch=mc[0][2])
        if obj.tempo:
            self.musxml.create_tempo(obj.tempo.text, obj.tempo.metr,
                                     obj.tempo.midi, obj.tempo.dots)

    def before_note(self, obj):
        """Xml-nodes before note."""
        self._add_dynamics([d for d in obj.dynamic if d.before])
        if obj.oct_shift and not obj.oct_shift.octdir == 'stop':
            self.musxml.add_octave_shift(obj.oct_shift.plac, obj.oct_shift.octdir, obj.oct_shift.size)
        if len(obj.harmony) != 0:
            for h in obj.harmony:
                self.musxml.add_harmony(h.root, h.root_alter, h.bass, h.bass_alter, h.text,
                                        self.count_duration((h.offset, 1), self.divisions))

    def after_note(self, obj):
        """Xml-nodes after note."""
        self._add_dynamics([d for d in obj.dynamic if not d.before])
        if obj.oct_shift and obj.oct_shift.octdir == 'stop':
            self.musxml.add_octave_shift(obj.oct_shift.plac, obj.oct_shift.octdir, obj.oct_shift.size)

    def _add_dynamics(self, dyns):
        """Add XML nodes for list of Dynamics objects."""
        for d in dyns:
            if isinstance(d, DynamicsMark):
                self.musxml.add_dynamic_mark(d.sign)
            elif isinstance(d, DynamicsWedge):
                self.musxml.add_dynamic_wedge(d.sign)
            elif isinstance(d, DynamicsText):
                self.musxml.add_dynamic_text(d.sign)
            elif isinstance(d, DynamicsDashes):
                self.musxml.add_dynamic_dashes(d.sign)

    def gener_xml_mus(self, obj):
        """Nodes generic for both notes and rests."""
        if obj.tuplet:
            for t in obj.tuplet:
                self.musxml.tuplet_note(t.fraction, obj.duration, t.ttype, t.nr,
                                        self.divisions, t.acttype, t.normtype)
        if obj.other_notation:
            self.musxml.add_named_notation(obj.other_notation)

    def new_xml_note(self, obj):
        """Create note specific xml-nodes."""
        divdur = self.count_duration(obj.duration, self.divisions)
        if isinstance(obj, Unpitched):
            self.musxml.new_unpitched_note(obj.base_note, obj.octave, obj.type, divdur,
                                           obj.voice, obj.dot, obj.chord, obj.grace, obj.staff)
        else:
            self.musxml.new_note(obj.base_note, obj.octave, obj.type, divdur,
                                 obj.alter, obj.accidental_token, obj.voice, obj.dot, obj.chord,
                                 obj.grace, obj.staff, obj.beam)
        for t in obj.tie:
            if not obj.chord:
                self.musxml.tie_note(t[0], t[1])
        for s in obj.slur:
            self.musxml.add_slur(s.nr, s.slurtype, s.line)
        for a in obj.artic:
            self.musxml.new_articulation(a)
        if obj.ornament:
            self.musxml.new_simple_ornament(obj.ornament)
        if obj.adv_ornament:
            self.musxml.new_adv_ornament(obj.adv_ornament[0], obj.adv_ornament[1])
        if obj.tremolo[1]:
            self.musxml.add_tremolo(obj.tremolo[0], obj.tremolo[1])
        if obj.gliss:
            self.musxml.add_gliss(obj.gliss[0], obj.gliss[1], obj.gliss[2])
        if obj.fingering:
            self.musxml.add_fingering(obj.fingering)
        self.gener_xml_mus(obj)  # Notations must be added before lyrics to have a valid XML
        if obj.lyric:
            for l in obj.lyric:
                # Allows a lyric to have the extend tag if necessary
                if "extend" in l:
                    self.musxml.add_lyric(l[0], l[1], l[2], "extend")
                else:
                    self.musxml.add_lyric(l[0], l[1], l[2])

    def new_xml_rest(self, obj):
        """Create rest specific xml-nodes."""
        divdur = self.count_duration(obj.duration, self.divisions)
        if obj.skip:
            self.musxml.add_skip(divdur)
        else:
            self.musxml.new_rest(divdur, obj.type, obj.pos,
                                 obj.dot, obj.voice, obj.staff)
        self.gener_xml_mus(obj)

    def count_duration(self, base_scaling, divs):
        base = base_scaling[0]
        scaling = base_scaling[1]
        duration = divs*4*base
        duration = duration * scaling
        return int(duration)


class Score():
    """Object that keep track of a whole score."""

    def __init__(self):
        self.partlist = []
        self.title = None
        self.creators = {}
        self.info = {}
        self.rights = None
        self.glob_section = ScoreSection('global', True)

    def is_empty(self):
        """Check if score is empty."""
        if self.partlist:
            return False
        else:
            return True

    def merge_globally(self, section, override=False):
        """Merge section to all parts."""
        for p in self.partlist:
            p.merge_voice(section, override)

    def debug_score(self, attr=[]):
        """
        Loop through score and print all elements for debugging purposes.

        Additionally print element attributes by adding them to the
        argument 'attr' list.

        """
        ind = "  "

        def debug_part(p):
            print("Score part:"+p.name)
            for n, b in enumerate(p.barlist):
                print(ind+"Bar nr: "+str(n+1))
                for obj in b.obj_list:
                    print(ind+ind+repr(obj))
                    for a in attr:
                        try:
                            print(ind+ind+ind+a+':'+repr(getattr(obj, a)))
                        except AttributeError:
                            pass

        def debug_group(g):
            if hasattr(g, 'barlist'):
                debug_part(g)
            else:
                print("Score group:"+g.name)
                for pg in g.partlist:
                    debug_group(pg)

        for i in self.partlist:
            debug_group(i)


class ScorePartGroup():
    """Object to keep track of part group."""

    def __init__(self, num, bracket):
        self.bracket = bracket
        self.partlist = []
        self.name = ''
        self.abbr = ''
        self.parent = None
        self.num = num

    def set_bracket(self, bracket):
        self.bracket = bracket

    def merge_voice(self, voice, override=False):
        """Merge in a ScoreSection into all parts."""
        for part in self.partlist:
            part.merge_voice(voice, override)


class ScoreSection():
    """ object to keep track of music section """

    def __init__(self, name, glob=False):
        self.name = name
        self.barlist = []
        self.glob = glob

    def __repr__(self):
        return '<{0} {1}>'.format(self.__class__.__name__, self.name)

    def merge_voice(self, voice, override=False):
        """Merge in other ScoreSection."""
        for org_v, add_v in zip(self.barlist, voice.barlist):
            org_v.inject_voice(add_v, override)
        bl_len = len(self.barlist)
        if len(voice.barlist) > bl_len:
            self.barlist += voice.barlist[bl_len:]

    def merge_lyrics(self, lyrics):
        """Merge in lyrics in music section."""
        current_voice = lyrics.voice_id  # Indicates which voice the notes should be assigned to
        voices = {}                      # Stores the notes in each voice (name (ex: "SopranoVoice") or number (ex: "3"))
        indices = {}                     # Stores the current index in each voice's note list
        objects = {}                     # Stores the current object (containing the note and time) in each voice
        time = 0                         # Stores the current time in the music
        lyrics_idx = 0                   # Stores the current index in the lyrics list
        ignore_slur = False              # Indicates whether subsequent slurred/tied notes should have lyrics (no if False)
        slurs = {}                       # Indicates whether the current note is slurred for each voice {"voice": bool}
        ties = {}                        # Indicates whether the current note is tied for each voice {"voice": bool}
        prev_time = -1                   # Stores the start time of the previously placed lyric
        note_used = True                 # Indicates whether the current note has had a lyric (or skip) assigned
        # Create dictionary of lists for each voice's notes
        for bar in self.barlist:
            for obj in bar.obj_list:
                if isinstance(obj, BarMus) and not obj.chord:
                    # Get the name of the voice, if there is no voice name (likely inside a voice separator), then use the voice number as a string
                    voc_name = obj.voice_name
                    if voc_name is None:  # Should never be None
                        voc_name = str(obj.voice)
                        print("Warning: Voice name for a lyric is None!")
                    if voc_name not in voices:
                        voices[voc_name] = []
                    voices[voc_name].append({"note": obj, "time": time})
                    time += obj.duration[0] * obj.duration[1]
                elif isinstance(obj, BarBackup):
                    time -= obj.duration[0] * obj.duration[1]
        # Initialize the needed keys for indices and objects
        for voice in voices:
            if voice not in indices:
                indices[voice] = 0
                objects[voice] = None
                slurs[voice] = False
                ties[voice] = False
        while(True):
            # Update position and slur/tie status in all voice's note lists (break if the necessary list (current voice) ends)
            if note_used:
                for voice, notes in voices.items():
                    try:
                        while(not notes[indices[voice]]["time"] > prev_time):
                            # Adjust the status of slurs and ties
                            if isinstance(notes[indices[voice]]["note"], BarNote):
                                # For loops cover the case where a note has multiple slur objects
                                #    ex: the note `(a)` has an opening and closing slur, meaning slur should remain False
                                for s in notes[indices[voice]]["note"].slur:
                                    if not s.phrasing:  # Phrasing slurs don't affect lyric placement
                                        slurs[voice] = not slurs[voice]
                                for t in notes[indices[voice]]["note"].tie:
                                    ties[voice] = not ties[voice]
                            indices[voice] += 1
                        # Store current note in voice
                        objects[voice] = notes[indices[voice]]
                    except IndexError:
                        objects[voice] = None
                # Choose needed note
                obj = objects[current_voice]
                if obj is None:
                    break
                prev_time = obj["time"]
                note_used = False
            # After finding the proper note, add the lyric and update status of voice, slurs, and ties
            if isinstance(obj["note"], BarNote):
                if ignore_slur or (not slurs[current_voice] and not ties[current_voice]):
                    # Handles normal lyrics
                    try:
                        lyr = lyrics.barlist[lyrics_idx]
                    except IndexError:
                        break
                    if lyr[-1] != "command":
                        if lyr != 'skip':
                            lyr[0] = lyr[0].replace('~', chr(0x203f))  # Turns ~ into undertie
                            lyr[0] = lyr[0].replace('_', ' ')  # Ex: Hello_I -> Hello I (but on one note)
                            obj["note"].add_lyric(lyr)
                        note_used = True
                    # Handles case where previous lyric is a command (ex: ["switchVoice", "Alto", "command"])
                    try:
                        prev_lyr = lyrics.barlist[lyrics_idx-1]
                    except IndexError:
                        prev_lyr = None
                    if prev_lyr is not None and prev_lyr[-1] == "command":
                        if "ignoreMelismata" == prev_lyr[0]:
                            ignore_slur = prev_lyr[1]
                        elif "switchVoice" == prev_lyr[0]:
                            if prev_lyr[1] in voices:
                                current_voice = prev_lyr[1]
                            else:
                                print("Warning: Voice", prev_lyr[1], "is not a valid voice for lyric assignment!")
                        else:
                            print("Warning: Unknown voice command!")
                    lyrics_idx += 1
                else:
                    note_used = True  # No lyric needed for slurred/tied note
            else:
                note_used = True  # No lyric needed for non-note objects


class Snippet(ScoreSection):
    """ Short section intended to be merged.
    Holds reference to the barlist to be merged into."""

    def __init__(self, name, merge_into):
        ScoreSection.__init__(self, name)
        self.merge_barlist = merge_into


class LyricsSection(ScoreSection):
    """ Holds the lyrics information. Will eventually be merged to
    the corresponding note in the section set by the voice id. """

    def __init__(self, name, voice_id):
        ScoreSection.__init__(self, name)
        self.voice_id = voice_id


class ScorePart(ScoreSection):
    """ object to keep track of part """

    def __init__(self, staves=0, part_id=None, to_part=None, name=''):
        ScoreSection.__init__(self, name)
        self.part_id = part_id
        self.to_part = to_part
        self.abbr = ''
        self.midi = ''
        self.staves = staves

    def __repr__(self):
        return '<{0} {1} {2}>'.format(
            self.__class__.__name__, self.name, self.part_id)

    def set_first_bar(self, divisions):
        initime = [4, 4]
        iniclef = ('G', 2, 0)

        def check_time(bar):
            for obj in bar.obj_list:
                if isinstance(obj, BarAttr):
                    if obj.time:
                        return True
                if isinstance(obj, BarMus):
                    return False

        def check_clef(bar):
            for obj in bar.obj_list:
                if isinstance(obj, BarAttr):
                    if obj.clef or obj.multiclef:
                        return True
                if isinstance(obj, BarMus):
                    return False

        if not check_time(self.barlist[0]):
            try:
                self.barlist[0].obj_list[0].set_time(initime, False)
            except AttributeError:
                print("Warning can't set initial time sign!")
        if not check_clef(self.barlist[0]):
            try:
                self.barlist[0].obj_list[0].set_clef(iniclef)
            except AttributeError:
                print("Warning can't set initial clef sign!")
        self.barlist[0].obj_list[0].divs = divisions
        if self.staves:
            self.barlist[0].obj_list[0].staves = self.staves

    def merge_part_to_part(self):
        """Merge the part with the one indicated."""
        if self.to_part.barlist:
            self.to_part.merge_voice(self)
        else:
            self.to_part.barlist.extend(self.barlist)

    def extract_global_to_section(self, name):
        """Extract only elements that is relevant for the score globally into a given section."""
        section = ScoreSection(name, True)
        for bar in self.barlist:
            section_bar = Bar()
            for obj in bar.obj_list:
                if isinstance(obj, BarAttr):
                    glob_barattr = BarAttr()
                    glob_barattr.key = obj.key
                    glob_barattr.time = obj.time
                    glob_barattr.mode = obj.mode
                    glob_barattr.barline = obj.barline
                    glob_barattr.repeat = obj.repeat
                    glob_barattr.tempo = obj.tempo
                    section_bar.obj_list.append(glob_barattr)
            section.barlist.append(section_bar)
        return section


class Bar():
    """ Representing the bar/measure.
    Contains also information about how complete it is."""

    def __init__(self):
        self.obj_list = []
        self.list_full = False

    def __repr__(self):
        return '<{0} {1}>'.format(self.__class__.__name__, self.obj_list)

    def add(self, obj):
        self.obj_list.append(obj)

    def has_music(self):
        """ Check if bar contains music. """
        for obj in self.obj_list:
            if isinstance(obj, BarMus):
                return True
        return False

    def create_backup(self):
        """ Calculate and create backup object."""
        b = 0
        s = 1
        for obj in self.obj_list:
            if isinstance(obj, BarMus):
                if not obj.chord:
                    b += obj.duration[0]
                    s *= obj.duration[1]
            elif isinstance(obj, BarBackup):
                b -= obj.duration[0]
                s /= obj.duration[1]
        if b > 0:  # prevents the pickup measure from already having a blank BarBackup
            self.add(BarBackup((b, s)))

    def is_skip(self, obj_list=None):
        """ Check if bar has nothing but skips. """
        if not obj_list:
            obj_list = self.obj_list
        for obj in obj_list:
            if obj.has_attr():
                return False
            if isinstance(obj, BarNote):
                return False
            elif isinstance(obj, BarRest):
                if not obj.skip:
                    return False
        return True

    def inject_voice(self, new_voice, override=False):
        """ Adding new voice to bar.
        Omitting double or conflicting bar attributes as long as override is false.
        Omitting also bars with only skips."""
        if new_voice.obj_list and new_voice.obj_list[0].has_attr():
            if self.obj_list[0].has_attr():
                self.obj_list[0].merge_attr(new_voice.obj_list[0], override)
            else:
                self.obj_list.insert(0, new_voice.obj_list[0])
            backup_list = new_voice.obj_list[1:]
        else:
            backup_list = new_voice.obj_list
        try:
            if self.obj_list[-1].barline and new_voice.obj_list[-1].barline:
                self.obj_list.pop()
        except (AttributeError, IndexError):
            pass
        if not self.is_skip(backup_list):
            self.create_backup()
            for bl in backup_list:
                self.add(bl)


class BarMus():
    """ Common class for notes and rests. """

    def __init__(self, duration, voice=1, voice_name=None):
        self.duration = duration
        self.type = None
        self.tuplet = []
        self.dot = 0
        self.voice = voice
        self.voice_name = voice_name
        self.staff = 0
        self.chord = False
        self.other_notation = None
        self.dynamic = []
        self.oct_shift = None
        self.harmony = []

    def __repr__(self):
        return '<{0} {1}>'.format(self.__class__.__name__, self.duration)

    def set_tuplet(self, fraction, ttype, nr, acttype='', normtype=''):
        self.tuplet.append(Tuplet(fraction, ttype, nr, acttype, normtype))

    def set_staff(self, staff):
        self.staff = staff

    def add_dot(self):
        self.dot += 1

    def add_other_notation(self, other):
        self.other_notation = other

    def set_dynamics_mark(self, sign, before=True):
        self.dynamic.append(DynamicsMark(sign, before))

    def set_dynamics_wedge(self, sign, before=True):
        self.dynamic.append(DynamicsWedge(sign, before))

    def set_dynamics_text(self, sign, before=True):
        self.dynamic.append(DynamicsText(sign, before))

    def set_dynamics_dashes(self, sign, before=True):
        self.dynamic.append(DynamicsDashes(sign, before))

    def set_oct_shift(self, plac, octdir, size):
        self.oct_shift = OctaveShift(plac, octdir, size)

    def add_harmony(self, root, root_alter=0, bass=False, bass_alter=0, text="", offset=0):
        self.harmony.append(Harmony(root, root_alter, bass, bass_alter, text, offset))

    def has_attr(self):
        return False


##
# Classes that are used by BarMus
##


class Harmony():
    """Class for harmony objects (chord name representations)"""
    def __init__(self, root, root_alter=0, bass=False, bass_alter=0, text="", offset=0):
        self.root = root
        self.root_alter = root_alter
        self.bass = bass
        self.bass_alter = bass_alter
        self.text = text
        self.offset = offset


class OctaveShift():
    """Class for octave shifts."""

    def __init__(self, plac, octdir, size):
        self.plac = plac
        self.octdir = octdir
        self.size = size


class Dynamics():
    """Stores information about dynamics. """

    def __init__(self, sign, before=True):
        self.before = before
        self.sign = sign


class DynamicsMark(Dynamics):
    """A dynamics mark."""
    pass


class DynamicsWedge(Dynamics):
    """A dynamics wedge/hairpin."""
    pass


class DynamicsText(Dynamics):
    """A dynamics text."""
    pass


class DynamicsDashes(Dynamics):
    """Dynamics dashes."""
    pass


class Tuplet():
    """Stores information about tuplet."""

    def __init__(self, fraction, ttype, nr, acttype, normtype):
        self.fraction = fraction
        self.ttype = ttype
        self.nr = nr
        self.acttype = acttype
        self.normtype = normtype


class Slur():
    """Stores information about slur."""

    def __init__(self, nr, slurtype, phrasing, line):
        self.nr = nr
        self.slurtype = slurtype
        self.phrasing = phrasing
        self.line = line


##
# Subclasses of BarMus
##


class BarNote(BarMus):
    """ object to keep track of note parameters """

    def __init__(self, pitch_note, alter, accidental, duration, voice=1, voice_name=None):
        BarMus.__init__(self, duration, voice, voice_name)
        self.base_note = pitch_note.upper()
        self.alter = alter
        self.octave = None
        self.accidental_token = accidental
        self.tie = []
        self.grace = (0, 0)
        self.gliss = None
        self.tremolo = ('', 0)
        self.skip = False
        self.slur = []
        self.artic = []
        self.ornament = None
        self.adv_ornament = None
        self.fingering = None
        self.lyric = None
        self.beam = False

    def set_duration(self, duration, durtype='', dot=0):
        self.duration = duration
        self.dot = dot
        if durtype:
            self.type = durtype

    def set_durtype(self, durtype):
        self.type = durtype

    def set_octave(self, octave):
        self.octave = octave

    def set_tie(self, tie_type, line):
        self.tie.append((tie_type, line))

    def set_slur(self, nr, slur_type, phrasing, line):
        self.slur.append(Slur(nr, slur_type, phrasing, line))

    def add_articulation(self, art_name):
        self.artic.append(art_name)

    def add_ornament(self, ornament):
        self.ornament = ornament

    def add_adv_ornament(self, ornament, end_type="start"):
        self.adv_ornament = (ornament, {"type": end_type})

    def set_grace(self, slash):
        self.grace = (1, slash)

    def set_gliss(self, line, endtype="start", nr=1):
        if not line:
            line = "solid"
        self.gliss = (line, endtype, nr)

    def set_tremolo(self, trem_type, duration=False):
        if duration:
            self.tremolo = (trem_type, dur2lines(duration))
        else:
            self.tremolo = (trem_type, self.tremolo[1])

    def add_fingering(self, finger_nr):
        self.fingering = finger_nr

    def add_lyric(self, lyric_list):
        if not self.lyric:
            self.lyric = []
        self.lyric.append(lyric_list)

    def change_lyric_syll(self, index, syll):
        self.lyric[index][1] = syll

    def change_lyric_nr(self, index, nr):
        self.lyric[index][2] = nr

    def set_beam(self, beam):
        self.beam = beam


class Unpitched(BarNote):
    """Object to keep track of unpitched notes."""

    def __init__(self, duration, step=None, voice=1, voice_name=None):
        BarNote.__init__(self, 'B', 0, "", duration, voice, voice_name)
        self.octave = 4
        if step:
            self.base_note = step.upper()


class BarRest(BarMus):
    """ object to keep track of different rests and skips """

    def __init__(self, duration, voice=1, voice_name=None, show_type=True, skip=False, pos=0):
        BarMus.__init__(self, duration, voice, voice_name)
        self.show_type = show_type
        self.type = None
        self.skip = skip
        self.pos = pos

    def set_duration(self, duration, durtype=''):
        self.duration = duration
        if durtype:
            if self.show_type:
                self.type = durtype
            else:
                self.type = None

    def set_durtype(self, durtype):
        if self.show_type:
            self.type = durtype


class Ending():
    """ object that keeps track of alternate repeat endings """

    def __init__(self, start, end, etype):
        self.start = start
        self.end = end
        self.etype = etype

    def get_number(self):
        """ A string of comma separated integers from start to end """
        number = ''
        for i in range(self.start, self.end):
            number += str(i) + ', '
        return number + str(self.end)

    def get_text(self):
        """ 'S.' if start == end, else 'S.-E.' (where S and E are the start and end numbers) """
        text = ''
        text += str(self.start) + '.'
        if self.start != self.end:
            text += '-' + str(self.end) + '.'
        return text


class BarAttr():
    """ object that keep track of bar attributes, e.g. time sign, clef, key etc """

    def __init__(self):
        self.key = None
        self.time = 0
        self.clef = 0
        self.mode = ''
        self.divs = 0
        self.barline = None
        self.left_barline = None
        self.repeat = None
        self.endings = []
        self.staves = 0
        self.multiclef = []
        self.tempo = None

    def __repr__(self):
        return '<{0} {1}>'.format(self.__class__.__name__, self.time)

    def set_key(self, muskey, mode):
        self.key = muskey
        self.mode = mode

    def set_time(self, fractlist, numeric=True):
        self.time = fractlist
        if not numeric:
            if fractlist == [4, 4]:
                self.time.append('common')
            elif fractlist == [2, 2]:
                self.time.append('cut')

    def set_clef(self, clef):
        self.clef = clef

    def set_barline(self, bl):
        self.barline = convert_barl(bl)

    def set_left_barline(self, bl):
        self.left_barline = convert_barl(bl)

    def set_tempo(self, unit=0, unittype='', beats=0, dots=0, text=""):
        self.tempo = TempoDir(unit, unittype, beats, dots, text)

    def add_ending(self, start, end, etype):
        self.endings.append(Ending(start, end, etype))

    def has_attr(self):
        check = False
        if self.key is not None:
            check = True
        elif self.time != 0:
            check = True
        elif self.clef != 0:
            check = True
        elif self.multiclef:
            check = True
        elif self.divs != 0:
            check = True
        elif self.barline is not None:
            check = True
        elif self.tempo is not None:
            check = True
        elif self.staves != 0:
            check = True
        elif self.repeat is not None:
            check = True
        elif self.endings:
            check = True
        return check

    def merge_attr(self, barattr, override=False):
        """Merge in attributes (from another bar).
        Existing attributes will only be replaced when override is set to true.
        """
        if barattr.key is not None and (override or self.key is None):
            self.key = barattr.key
            self.mode = barattr.mode
        if barattr.time != 0 and (override or self.time == 0):
            self.time = barattr.time
        if barattr.clef != 0 and (override or self.clef == 0):
            self.clef = barattr.clef
        if barattr.multiclef:
            self.multiclef += barattr.multiclef
        if barattr.tempo is not None and (override or self.tempo is None):
            self.tempo = barattr.tempo


class BarBackup():
    """ Object that stores duration for backup """

    def __init__(self, duration):
        self.duration = duration


class TempoDir():
    """ Object that stores tempo direction information """

    def __init__(self, unit, unittype, beats, dots, text):
        if unittype:
            self.metr = unittype, beats
            self.midi = self.set_midi_tempo(unit, beats, dots)
        else:
            self.metr = 0
            self.midi = 0
        self.dots = dots
        self.text = text

    def set_midi_tempo(self, unit, beats, dots):
        u = Fraction(1, int(unit))
        if dots:
            import math
            den = int(math.pow(2, dots))
            num = int(math.pow(2, dots+1)-1)
            u *= Fraction(num, den)
        mult = 4*u
        return float(Fraction(beats)*mult)


##
# Translation functions
##

def dur2lines(dur):
    if dur == 8:
        return 1
    elif dur == 16:
        return 2
    elif dur == 32:
        return 3
    else:
        return 0


def convert_barl(bl):
    if bl == '|':
        return 'regular'
    elif bl == ':' or bl == ';':
        return 'dotted'
    elif bl == 'dashed' or bl == '!':
        return 'dashed'
    elif bl == '.':
        return 'heavy'
    elif bl == '||':
        return 'light-light'
    elif bl == '.|' or bl == 'forward':
        return 'heavy-light'
    elif bl == '.|.' or bl == '..':
        return 'heavy-heavy'
    elif bl == '|.' or bl == 'backward':
        return 'light-heavy'
    elif bl == "'":
        return 'tick'
    elif bl == "":
        return 'none'
