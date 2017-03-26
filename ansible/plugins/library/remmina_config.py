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

import base64
from Crypto.Cipher import DES3
import gnupg
from ansible.module_utils.basic import *
import yaml

'''
    For manual testing:
        git clone http://github.com/ansible/ansible.git --recursive
    and then run this:
        ansible/hacking/test-module -m remmina/script.py -a \
        "path='/Users/michele/Github/remmina' \
        serverfile='example.yml' \
        gpgdir='/Users/michele/Github/remmina/.gpg' \
        passphrase='1234567890' \
        secret='MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0MTIzNDU2Nzg=' \
        gpgbinary='/usr/local/bin/gpg'"

'''

def generate_password(password, remmina_pref_secret):
    plain = password.encode('utf-8')
    secret = base64.b64decode(remmina_pref_secret)
    key = secret[:24]
    iv = secret[24:]
    plain += b"\0" * (8 - len(plain) % 8)
    cipher = DES3.new(key, DES3.MODE_CBC, iv)
    return base64.b64encode(cipher.encrypt(plain)).decode('utf-8')


def decrypt(content, gpgdir, gpgbinary, passphrase, module):
    try:
        gpg = gnupg.GPG(homedir=gpgdir, binary=gpgbinary)
        meta = gpg.decrypt(content, passphrase=passphrase)
        decrypted = str(meta)

    except IOError:
        print(get_exception())
        module.fail_json(msg='Couldn\'t decrypt data')
    return decrypted


def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(required=True, type='str'),
            serverfile=dict(required=True, type='str'),
            secret=dict(required=True, type='str'),
            passphrase=dict(required=False, type='str'),
            gpgdir=dict(required=False, type='str'),
            gpgbinary=dict(required=False, type='str')
        )
    )
    path = os.path.expanduser(module.params['path'])
    secret = module.params['secret']
    serverfile = module.params['serverfile']
    gpgdir = module.params['gpgdir']
    passphrase = module.params['passphrase']
    gpgbinary = module.params['gpgbinary']

    enc_server_list = os.path.join(path, serverfile)
    with open(enc_server_list, 'r') as f:
        decrypted_server_list = decrypt(f.read(), gpgdir, gpgbinary, passphrase, module)
    server_list = yaml.load(decrypted_server_list)
    remmina_files = []
    for host in server_list:
        (username, ip, password, port) = server_list[host]
        try:
            filename = "{0}.remmina".format(host.strip())
            outfile = open(os.path.join(path,filename), "w")
            outfile.write("[remmina]\n")
            outfile.write("group=Node.js\n")
            outfile.write("name={0}\n".format(host))
            outfile.write("protocol=RDP\n")
            outfile.write("server={0}:{1}\n".format(ip.strip(), port.strip()))
            outfile.write("username={0}\n".format(username.strip()))
            outfile.write("password={0}\n".format(generate_password(password, secret)))
            outfile.write("colordepth=15")
            outfile.close()
            remmina_files.append(filename)
        except IOError:
            print(get_exception())
            module.fail_json(msg='Couldn\'t generate file for %s' % host)

    module.exit_json(changed=True, files=remmina_files)


if __name__ == '__main__':

    main()

