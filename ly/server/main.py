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
The entry point for the 'ly-server' command.
"""

from __future__ import unicode_literals
from __future__ import print_function

try:
    from BaseHTTPServer import HTTPServer
except ImportError:
    from http.server import HTTPServer

import copy
import sys

from ly.cli.main import die, version
import ly.cli.options
from . import handler


def usage():
    """Print usage info."""
    from . import doc
    sys.stdout.write(doc.__doc__)

def usage_short():
    """Print short usage info."""
    sys.stdout.write("""\
Usage: ly-server [options]

An HTTP server for manipulating LilyPond input code

See ly -h for a full list of commands and options.
""")


class ServerOptions(object):
    """
    Options configuring the server itself, not the individual commands
    """
    
    def __init__(self):
        self.port = 5432
        self.timeout = 0
    

def parse_command_line():
    """Returns a two-tuple(server_opts, cmd_opts)
    
    server_opts is a ServerOptions instance configuring the server behaviour
    cmd_opts is an Options instance with default options for future command
    executions triggered by HTTP requests.
    
    Also performs error handling and may exit on certain circumstances.
    
    """
    
    if isinstance(sys.argv[0], type('')):
        # python 3 - arguments are unicode strings
        args = iter(sys.argv[1:])
    else:
        # python 2 - arguments are bytes, decode them
        fsenc = sys.getfilesystemencoding() or 'latin1'
        args = (a.decode(fsenc) for a in sys.argv[1:])
    
    server_opts = ServerOptions()
    cmd_opts = ly.cli.options.Options()
    
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
        
        # Server Options
        elif arg in ('-p', '--port'):
            server_opts.port = int(next_arg("missing port number"))
        elif arg in ('-t', '--timeout'):
            server_opts.timeout = int(next_arg("missing timeout (in ms)"))
            
        # Command Options
        elif arg in ('-e', '--encoding'):
            cmd_opts.encoding = next_arg("missing encoding name")
        elif arg == '--output-encoding':
            cmd_opts.output_encoding = next_arg("missing output encoding name")
        elif arg in ('-l', '--language'):
            s = next_arg("missing language name")
            cmd_opts.set_variable("default-language", s)
        
        # Command configuration Variables
        elif arg == '-d':
            s = next_arg("missing variable=value")
            try:
                name, value = s.split('=', 1)
            except ValueError:
                die("missing '=' in variable set")
            cmd_opts.set_variable(name, value)
        
        elif arg.startswith('-'):
            die('unknown option: ' + arg)
    
    return server_opts, cmd_opts


def main():
    server_opts, cmd_opts = parse_command_line()
    
    handler.default_opts = copy.deepcopy(cmd_opts)

    import ly.document
    exit_code = 0
    
    try:
        server = HTTPServer(('', server_opts.port), handler.RequestHandler)
        print("Welcome to the LilyPond syntax highlighter")
        print("Listening on port {port}".format(port=server_opts.port))
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Shutting down server")
        server.socket.close()
        print("Successfully closed. Bye...")

    
    return exit_code

