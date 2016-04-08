# This file is part of python-ly, https://pypi.python.org/pypi/python-ly
#
# Copyright (c) 2014 - 2015 by Wilbert Berendsen
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
The entry point for the 'ly' command.
"""

from __future__ import unicode_literals

import copy
import os
import sys

import ly.pkginfo
from . import options
from . import setvar


def usage():
    """Print usage info."""
    from . import doc
    sys.stdout.write(doc.__doc__)

def usage_short():
    """Print short usage info."""
    sys.stdout.write("""\
Usage: ly [options] commands file, ...

A tool for manipulating LilyPond source files

See ly -h for a full list of commands and options.
""")

def version():
    """Print version info."""
    sys.stdout.write("ly {0}\n".format(ly.pkginfo.version))

def die(message):
    """Exit with message to STDERR."""
    sys.stderr.write("error: " + message + '\n')
    sys.stderr.write(
        "See ly -h for a full list of commands and options.\n")
    sys.exit(1)
        

def parse_command_line():
    """Return a three-tuple(options, commands, files).
    
    options is an Options instance with all the command-line options
    commands is a list of command.command instances
    files is the list of filename arguments
    
    Also performs error handling and may exit on certain circumstances.
    
    """
    if len(sys.argv) < 2:
        usage_short()
        sys.exit(2)
    
    if isinstance(sys.argv[0], type('')):
        # python 3 - arguments are unicode strings
        args = iter(sys.argv[1:])
    else:
        # python 2 - arguments are bytes, decode them
        fsenc = sys.getfilesystemencoding() or 'latin1'
        args = (a.decode(fsenc) for a in sys.argv[1:])
    
    opts = options.Options()
    commands = []
    files = []
    
    def next_arg(message):
        """Get the next argument, if missing, die with message."""
        try:
            return next(args)
        except StopIteration:
            die(message)
    
    for arg in args:
        if arg in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif arg in ('-v', '--version'):
            version()
            sys.exit(0)
        elif arg in ('-i', '--in-place'):
            opts.in_place = True
        elif arg in ('-o', '--output'):
            opts.output = next_arg("missing output filename")
        elif arg == '-d':
            s = next_arg("missing variable=value")
            try:
                name, value = s.split('=', 1)
            except ValueError:
                die("missing '=' in variable set")
            opts.set_variable(name, value)
        elif arg in ('-e', '--encoding'):
            opts.encoding = next_arg("missing encoding name")
        elif arg == '--output-encoding':
            opts.output_encoding = next_arg("missing output encoding name")
        elif arg in ('-l', '--language'):
            s = next_arg("missing language name")
            opts.set_variable("default-language", s)
        elif arg == '--':
            files.extend(args)
        elif arg.startswith('-'):
            die('unknown option: ' + arg)
        elif not commands:
            commands = parse_command(arg)
        else:
            files.append(arg)
    from . import command
    if not commands or isinstance(commands[-1], command._edit_command):
        commands.append(command.write())
    if not files:
        files.append('-')
    if opts.with_filename is None:
        opts.with_filename = len(files) > 1
    return opts, commands, files

def parse_command(arg):
    """Parse the command string, returning a list of command.command instances.
    
    Exits when a command is invalid.
    
    """
    from . import command

    result = []
    
    for c in arg.split(';'):
        args = c.split(None, 1)
        if args:
            if '=' in args[0]:
                args = ['set_variable', c]
            cmd = args.pop(0)
            try:
                result.append(getattr(command, cmd.replace('-', '_'))(*args))
            except AttributeError:
                die("unknown command: " + cmd)
            except (TypeError, ValueError):
                die("invalid arguments: " + c)
    return result

def load(filename, encoding, mode):
    """Load a file, returning a ly.document.Document"""
    import ly.document
    if filename == '-':
        doc = ly.document.Document.load(sys.stdin.fileno(), encoding, mode)
        doc.filename = '-'
    else:
        doc = ly.document.Document.load(filename, encoding, mode)
    return doc

def main():
    opts, commands, files = parse_command_line()
    import ly.document
    exit_code = 0
    for filename in files:
        options = copy.deepcopy(opts)
        try:
            doc = load(filename, options.encoding, options.mode)
        except IOError as err:
            sys.stderr.write('warning: skipping file "{0}":\n  {1}\n'.format(filename, err))
            exit_code = 1
            continue
        cursor = ly.document.Cursor(doc)
        for c in commands:
            c.run(options, cursor, output)
    return exit_code

