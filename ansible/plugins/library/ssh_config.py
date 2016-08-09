#!/usr/bin/env python

# -*- coding: utf-8 -*-

# Copyright Node.js contributors. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

from ansible.module_utils.basic import *
from jinja2 import Environment, Template
import os
import re
import pprint

# reuse plez
pre_match  = "# begin: node.js template"
post_match = "# end: node.js template"
match      = re.compile(
    r"^\# begin\: node\.js template(.*)\# end\: node\.js template",
    flags=re.DOTALL|re.MULTILINE)

host_template = \
"""{% for host, metadata in hosts.iteritems(): %}
{% if metadata.ip -%}
Host {{ host }} {{ metadata.alias }}
  HostName {{ metadata.ip }}
  IdentityFile {{ metadata.ssh_private_key_file }}
  User {{ metadata.user or "root" }}
{%- endif %}
{% endfor %}
"""

jump_template  = \
"""
Host vagg-arm.nodejs.org
  Port 2222
  User jump
  IdentityFile ~/.ssh/vagg-arm-id_rsa
"""

def is_templatable(path, config):
    return os.path.exists(path) and bool(re.search(match, config))


def render_template(hosts):
    return Environment().from_string(host_template).render(hosts=hosts)


def main():
    module = AnsibleModule(
        argument_spec = {
            "path": {
                "required": True,
                "type": "str",
            },
            "hostinfo": {
                "required": True,
                "type": "dict",
            }
        }
    )

    path = os.path.expanduser(module.params['path'])

    try:
        with open(path, 'r') as f:
            contents = f.read()
        f.close()
    except IOError:
        module.fail_json(msg="Couldn't find a ssh config at %s" %
                         path)

    if not is_templatable(path, contents):
        module.fail_json(msg="Your ssh config lacks template stubs. " +
                             "Check README.md for instructions.")

    rendered = "{}{}{}".format(
        pre_match,
        render_template(module.params['hostinfo']),
        post_match
    )

    try:
        with open(path, 'w+') as f:
            f.write(match.sub(rendered, contents))
        f.close()
    except IOError:
        module.fail_json(msg="Couldn't write to ssh config. Check permissions")

    module.exit_json(changed=True, meta="Updated %s successfully" % path)


if __name__ == '__main__':
    main()
