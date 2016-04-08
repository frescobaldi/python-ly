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
HTTP request handler
"""

from __future__ import unicode_literals
try:
    from BaseHTTPServer import BaseHTTPRequestHandler
except ImportError:
    from http.server import BaseHTTPRequestHandler

import json
import copy

# Prototype (in JavaScript sense) from which each command copies its options
default_opts = None

class RequestHandler(BaseHTTPRequestHandler):
    
    def create_command(self, cmd):
        """
        Parse one command from the JSON data, plus optionally some commands to
        set variables. Returns an array with command._command instances.
        Raises exceptions upon faulty data.
        """
        from ly.cli import command
        
        result = []
        
        # if variables are given they are executed as intermediate commands
        if 'variables' in cmd:
            for v in cmd['variables']:
                result.append(command.set_variable(
                    v + "=" + cmd['variables'][v]))
        
        # try instantiating the command.
        if not 'command' in cmd:
            raise ValueError("Malformed JSON data in request body (missing 'command' field).\n" +
                            "Object:\n" + json.dumps(cmd))
        cmd_name = cmd['command'].replace('-', '_')
        if not hasattr(command, cmd_name):
            raise ValueError("unknown command: " + cmd_name)
        
        # add arguments to command if present.
        args = cmd.get('args', '')
        args = [args] if args else []
        try:
            result.append(getattr(command, cmd_name)(*args))
        except TypeError as ae:
            raise ValueError("Error creating command {cmd} with args {args}.\n{msg}".format(
                            cmd = cmd_name,
                            args = ", ".join(args),
                            msg = str(ae)))
        return result
        

    def process_options(self, opts):
        """
        Instantiate a copy of the default options and
        update with the given opts
        """
        result = copy.deepcopy(default_opts)
        
        for opt in opts:
            # handle special case where option name doesn't match CL interface
            if opt == 'language':
                result.set_variable('default-language', opts[opt])
            else:
                result.set_variable(opt, opts[opt])
        
        return result
        
        
    def process_json_request(self, request):
        """
        Configure the action(s) to be taken, based on the JSON object.
        Raise errors when the JSON object can't be properly understood.
        Run the commands and return a string (from cursor.text() ).
        """

        # set up an Options object and
        # override defaults with given options
        opts = self.process_options(request.get('options', []))
        
        # set up commands
        commands = []
        for c in request['commands']:
            commands.extend(self.create_command(c))        
        
        # create document from passed data
        import ly.document
        doc = ly.document.Document(request['data'], opts.mode)
        doc.filename = ""

        data = {
            'cursor': ly.document.Cursor(doc),
            'info': []
        }
        
        # run commands, which modify data in-place
        for c in commands:
            c.run(opts, data)
        
        result = {
            'info': '\n'.join(data['info']),
            'doc': data['cursor'].text()
        }
        return json.dumps(result)

        
    def parse_json_request_body(self):
        """
        Returns the message body parsed to a dictionary
        from JSON data. Raises 
        - RuntimeWarnung when no JSON data is present
        - ValueError when JSON parsing fails
        """
        
        # The following dict is meant as a documentation 
        # for constructing the request:
        # 'commands' is mandatory and contains an array of command definitions:
          # 'command' is mandatory
          # 'args' is dependent on the command. If the commands requires it
            # (such as e.g. transpose) it must be present
          # 'variables' is optional.
            # If variable declarations are present they are set before the 
            # command is executed. They can be overridden with a subsequent
            # command but are not forgotten automatically
        # 'options' is optional and can override the command options given
          # on the command line. It is written as a dict with the keys matching
          # the property names of the Options() object (to be documented)
        # 'data' is a string with the LilyPond input
        
        test_request = {
            'commands': [
                {
                    'command': 'transpose',
                    'args': 'c d'
                },
                {
                    'command': 'highlights',
                    'variables': {
                        'full-html': 'false'
                    }
                },
                {
                    'command': 'mode'
                }
            ],
            'options': {
                'encoding': 'UTF-16',
                'language': "deutsch"
            },
            'data': "%No JSON data supplied. This is a test request.\n" +
                    "\\relative c' {\n  c4 ( d e )\n}"
        }
        
        content_len = int(self.headers['content-length'])
        
        # Handle empty request
        if content_len == 0:
            #
            # TODO: Discuss the desired behaviour here !!!
            # For testing purposes it is definitely good to have,
            # but for production work it may be more than confusing.
            return test_request
            raise RuntimeWarning("No JSON data in request body")
        
        request_body = self.rfile.read(content_len)
        # Python2 has string, Python3 has bytestream
        if not isinstance(request_body, str):
            request_body = request_body.decode('utf-8')

        try:
            request = json.loads(request_body)
        except Exception as e:
            raise ValueError("Malformed JSON data in request body:\n" + str(e))

        if not 'commands' in request:
            raise ValueError("Malformed JSON request. Missing 'commands' property")
        if not 'data' in request:
            raise ValueError("Malformed JSON request. Missing 'data' property")

        return request
        
    def do_POST(self):
        """
        A POST request is expected to contain the task to be executed 
        as a JSON object in the request body.
        The POST handler (currently) ignores the URL.
        """
        try:
            request = self.parse_json_request_body()
            result = self.process_json_request(request)
        except Exception as e:
            # TODO: disambiguate (ValueError, RuntimeWarning, others),
            # use HTML templates
            self.send_error(400)
            # TODO: Is the encoding properly handled or do we have to consider our options?
            # AND: THIS DOESNT' WORK IN PYTHON3!
            self.wfile.write(str(e).encode())
            self.end_headers()
            return
        
        # Send successful response
        self.send_header('Content-type', 'text/html')
        # TODO: Is the encoding properly handled or do we have to consider our options?
        self.wfile.write(result.encode())
        self.end_headers()
