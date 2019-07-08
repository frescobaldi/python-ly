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
        for ctag in score.creators:
            self.musxml.add_creator(ctag, score.creators[ctag])
        for itag in score.info:
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
                    self.gener_xml_mus(obj)
                    self.after_note(obj)
                elif isinstance(obj, BarBackup):
                    divdur = self.count_duration(obj.duration, self.divisions)
                    self.musxml.add_backup(divdur)

    def new_xml_bar_attr(self, obj):
        """Create bar attribute xml-nodes."""
        if obj.has_attr():
            self.musxml.new_bar_attr(obj.clef, obj.time, obj.key, obj.mode, obj.divs)
        if obj.repeat:
            self.musxml.add_barline(obj.barline, obj.repeat)
        elif obj.barline:
            self.musxml.add_barline(obj.barline)
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
        if obj.harmony:
            self.musxml.add_harmony(obj.harmony.root, obj.harmony.root_alter,
                                    obj.harmony.bass, obj.harmony.bass_alter,
                                    obj.harmony.text)

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
        if obj.staff and not obj.skip:
            self.musxml.add_staff(obj.staff)
        if obj.other_notation:
            self.musxml.add_named_notation(obj.other_notation)

    def new_xml_note(self, obj):
        """Create note specific xml-nodes."""
        divdur = self.count_duration(obj.duration, self.divisions)
        if isinstance(obj, Unpitched):
            self.musxml.new_unpitched_note(obj.base_note, obj.octave, obj.type, divdur,
                                           obj.voice, obj.dot, obj.chord, obj.grace)
        else:
            self.musxml.new_note(obj.base_note, obj.octave, obj.type, divdur,
                                 obj.alter, obj.accidental_token, obj.voice, obj.dot, obj.chord,
                                 obj.grace)
        for t in obj.tie:
            self.musxml.tie_note(t)
        for s in obj.slur:
            self.musxml.add_slur(s.nr, s.slurtype)
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
        if obj.lyric:
            for l in obj.lyric:
                # Allows a lyric to have the extend tag if necessary
                if l[-1] == "extend":
                    self.musxml.add_lyric(l[0], l[1], l[2], l[-1])
                elif l[-2] == "extend":
                    self.musxml.add_lyric(l[0], l[1], l[2], l[-2])
                else:
                    self.musxml.add_lyric(l[0], l[1], l[2])

    def new_xml_rest(self, obj):
        """Create rest specific xml-nodes."""
        divdur = self.count_duration(obj.duration, self.divisions)
        if obj.skip:
            self.musxml.add_skip(divdur)
        else:
            self.musxml.new_rest(divdur, obj.type, obj.pos,
                                 obj.dot, obj.voice)

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
        i = 0
        slurOn = True  # Indicates whether subsequent slurred notes should be skipped
        slur = False   # Indicates whether the current note is slurred
        tie = False    # Indicates whether the current note is tied
        for bar in self.barlist:
            for obj in bar.obj_list:
                if isinstance(obj, BarNote) and obj.voice == 1 and not obj.chord:
                    # Ends open slurs/ties
                    if slur and tie:
                        if obj.slur:
                            slur = False
                        elif obj.tie:
                            tie = False
                    elif slur:
                        if obj.slur:
                            slur = False
                    elif tie:
                        if obj.tie:
                            tie = False
                    # If not a slurred/tied note, begins slurs/ties if needed and adds lyrics
                    else:
                        if obj.slur and slurOn:
                            slur = True
                        if obj.tie and slurOn:
                            tie = True
                        try:
                            lyr = lyrics.barlist[i]
                        except IndexError:
                            break
                        if lyr[-1] == "slurOff" or lyr[-2] == "slurOff":
                            slurOn = False
                        elif lyr[-1] == "slurOn" or lyr[-2] == "slurOn":
                            slurOn = True
                        if lyr != 'skip':
                            lyr[0] = lyr[0].replace('~', chr(0x203f))  # Turns ~ into undertie
                            obj.add_lyric(lyr)
                        i += 1


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
                b = 0  # prevents multiple BarBackups from being made in same measure
                break
        if b != 0:  # prevents the pickup measure from already having a blank BarBackup
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
        if new_voice.obj_list[0].has_attr():
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
        except AttributeError:
            pass
        if not self.is_skip(backup_list):
            self.create_backup()
            for bl in backup_list:
                self.add(bl)


class BarMus():
    """ Common class for notes and rests. """

    def __init__(self, duration, voice=1):
        self.duration = duration
        self.type = None
        self.tuplet = []
        self.dot = 0
        self.voice = voice
        self.staff = 0
        self.chord = False
        self.other_notation = None
        self.dynamic = []
        self.oct_shift = None
        self.harmony = None

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

    def set_harmony(self, root, root_alter=0, bass=False, bass_alter=0, text=""):
        self.harmony = Harmony(root, root_alter, bass, bass_alter, text)

    def has_attr(self):
        return False


##
# Classes that are used by BarMus
##


class Harmony():
    """Class for harmony objects (chord name representations)"""
    def __init__(self, root, root_alter=0, bass=False, bass_alter=0, text=""):
        self.root = root
        self.root_alter = root_alter
        self.bass = bass
        self.bass_alter = bass_alter
        self.text = text


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

    def __init__(self, nr, slurtype):
        self.nr = nr
        self.slurtype = slurtype


##
# Subclasses of BarMus
##


class BarNote(BarMus):
    """ object to keep track of note parameters """

    def __init__(self, pitch_note, alter, accidental, duration, voice=1):
        BarMus.__init__(self, duration, voice)
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

    def set_duration(self, duration, durtype=''):
        self.duration = duration
        self.dot = 0
        if durtype:
            self.type = durtype

    def set_durtype(self, durtype):
        self.type = durtype

    def set_octave(self, octave):
        self.octave = octave

    def set_tie(self, tie_type):
        self.tie.append(tie_type)

    def set_slur(self, nr, slur_type):
        self.slur.append(Slur(nr, slur_type))

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


class Unpitched(BarNote):
    """Object to keep track of unpitched notes."""

    def __init__(self, duration, step=None, voice=1):
        BarNote.__init__(self, 'B', 0, "", duration, voice=1)
        self.octave = 4
        if step:
            self.base_note = step.upper()


class BarRest(BarMus):
    """ object to keep track of different rests and skips """

    def __init__(self, duration, voice=1, show_type=True, skip=False, pos=0):
        BarMus.__init__(self, duration, voice)
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


class BarAttr():
    """ object that keep track of bar attributes, e.g. time sign, clef, key etc """

    def __init__(self):
        self.key = None
        self.time = 0
        self.clef = 0
        self.mode = ''
        self.divs = 0
        self.barline = None
        self.repeat = None
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
        if not numeric and (fractlist == [2, 2] or fractlist == [4, 4]):
            self.time.append('common')

    def set_clef(self, clef):
        self.clef = clef

    def set_barline(self, bl):
        self.barline = convert_barl(bl)

    def set_tempo(self, unit=0, unittype='', beats=0, dots=0, text=""):
        self.tempo = TempoDir(unit, unittype, beats, dots, text)

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
