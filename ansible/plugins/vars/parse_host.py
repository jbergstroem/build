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

# taken from nodejs/node.git: ./configure
valid_arch = ('arm', 'arm64', 'ia32', 'mips', 'mipsel', 'ppc', 'ppc64', 'x32',
              'x64', 'x86', 's390', 's390x')

# valid roles - add as necessary
valid_types = ('infra', 'lint', 'release', 'test')

# providers - validated for consistency
valid_providers = ('azure', 'digitalocean', 'joyent', 'ibm', 'nodesource',
                   'msft', 'osuosl', 'rackspace', 'scaleway', 'softlayer',
                   'voxer')


def parse_host(host):
    """Parses a host and validates it against our naming conventions"""

    hostinfo = dict()
    info = host.split('-')

    expected = ['type', 'provider', 'os', 'arch', 'uid']

    for key, item in enumerate(expected):
        hostinfo[item] = has_metadata(info[key])

    if hostinfo['type'] not in valid_types:
        raise errors.AnsibleError('Invalid type: ' + hostinfo['type'])

    if hostinfo['provider'] not in valid_providers:
        raise errors.AnsibleError('Invalid provider: ' + hostinfo['provider'])

    if hostinfo['arch'] not in valid_arch:
        raise errors.AnsibleError('Invalid arch: ' + hostinfo['arch'])

    return hostinfo

def has_metadata(info):
    """Checks for metadata in variables. These are separated from the "key"
       metadata by underscore. Not used anywhere at the moment for anything
       other than descriptiveness"""

    param = dict()
    metadata = info.split('_', 1)

    try:
        os = metadata[0]
        metadata = metadata[1]
    except IndexError:
        metadata = False
        os = info

    return [os, metadata] if metadata else info

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
            errors.AnsibleError('Failed to parse host: %s' % e)

        try:
            host.set_variable('labels', convert_labels(host.vars['labels']))
        except KeyError:
            pass

        # convert our shorthand variables to something that Ansible prefers
        try:
            host.set_variable('ansible_host', host.vars['ip'])
        except KeyError:
            pass

        try:
            host.set_variable('ansible_user', host.vars['user'])
        except KeyError:
            pass

        try:
            host.set_variable('ansible_port', host.vars['port'])
        except KeyError:
            pass

        # convenience: enable root for all hosts that requires
        # a different ssh username
        if 'user' in host.vars:
            host.set_variable('ansible_become', 'true')


        return {}

    def get_group_vars(self, group, vault_password=None):
        return {}
