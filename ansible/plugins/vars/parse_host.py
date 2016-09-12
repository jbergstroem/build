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

from ansible import errors, inventory


valid = {
  # taken from nodejs/node.git: ./configure
  'arch': ('arm', 'arm64', 'ia32', 'mips', 'mipsel', 'ppc', 'ppc64', 'x32',
              'x64', 'x86', 's390', 's390x'),

  # valid roles - add as necessary
  'type': ('infra', 'lint', 'release', 'test'),

  # providers - validated for consistency
  'provider': ('azure', 'digitalocean', 'joyent', 'ibm', 'linuxonecc',
               'mininodes', 'msft', 'nodesource', 'osuosl', 'rackspace',
               'scaleway', 'softlayer', 'voxer')
}

def parse_host(host):
    """Parses a host and validates it against our naming conventions"""

    hostinfo = dict()
    info = host.split('-')

    expected = ['type', 'provider', 'os', 'arch', 'uid']

    if len(info) != 5:
        raise errors.AnsibleError('Host format is invalid: %s,', host)

    for key, item in enumerate(expected):
        hostinfo[item] = has_metadata(info[key])

    for item in ['type', 'provider', 'arch']:
        if hostinfo[item] not in valid[item]:
            raise errors.AnsibleError('Invalid %s: %s' % (item, hostinfo[item]))

    return hostinfo

def has_metadata(info):
    """Checks for metadata in variables. These are separated from the "key"
       metadata by underscore. Not used anywhere at the moment for anything
       other than descriptiveness"""

    param = dict()
    metadata = info.split('_', 1)

    try:
        key = metadata[0]
        metadata = metadata[1]
    except IndexError:
        metadata = False
        key = info

    return key if metadata else info

def convert_labels(labels):
    """Converts labels from a comma separated string to a list"""

    if(labels):
        return labels.split(',')

class VarsModule(object):
    """Loads variables for groups and/or hosts"""

    def __init__(self, inventory):
        self.inventory = inventory
        self.inventory_basedir = inventory.basedir()

    def get_host_vars(self, host, vault_password=None):
        try:
            parsed_host = parse_host(host.get_name())
            for k,v in parsed_host.iteritems():
                host.set_variable(k, v[0] if type(v) is dict else v)
        except Exception, e:
            raise errors.AnsibleError('Failed to parse host: %s' % e)

        try:
            host.set_variable('labels', convert_labels(host.vars['labels']))
        except KeyError:
            pass

        # convert our shorthand variables to something that Ansible prefers
        convenience = { 'host': 'ip', 'user': 'user', 'port': 'port' }
        for key, value in convenience.items():
            try:
                index = "ansible_%s".format(key)
                host.set_variable(index, host.vars[value])
            except KeyError:
                pass

        # convenience: enable root for all hosts that requires a different
        # ssh username. User directive is already in config.
        if 'user' in host.vars:
            host.set_variable('ansible_become', 'true')

        return {}

    def get_group_vars(self, group, vault_password=None):
        return {}
