## Ansible scripts for the Node.js build group infrastructure

(in lack of a better title)


### Getting started

1. Install Ansible 2.2.0 or newer: `pip install ansible` (not out yet)
   **note**: if you're using homebrew you'll have to manage dependencies
   such as `PyAML` yourself.
2. Read this document.
3. Clone the node secrets repository (if you don't have access ask anyone
   in the [build group][1]).
4. Copy the private keys (check the secrets repo for instructions) to your
   `~/.ssh` folder. Make sure they have the same name. What keys are available
   to you depends on what role you have. In order to create new vm's and hook
   them up to CI you have to be part of the `infra` group.

[1]: https://github.com/nodejs/build#people

### Getting things done

Most of your work will probably include editing `inventory.yml`, followed by
running one (or multiple) of below playbooks. If you're adding a new host,
limiting ansible to just running on that host is probably quicker:

```console
$ ansible-playbook playbooks/create-jenkins-worker.yml \
    --limit "test-digitalocean-debian8-x64-1"
```

..in fact, you most likely want to use `--limit` for everything when you just
need to edit a few set of hosts.

These playbooks are available to you:

  - **create-jenkins-worker.yml**: Sets up a new jenkins worker.

  - **create-linter.yml**: Sets up the code linters.

  - **create-webhost.yml**: Configures the server(s) that host nodejs.org,
                            iojs.org and dist.libuv.org among other things.

  - **upgrade-packages.yml**: Upgrades packages on provided hosts.

  - **upgrade-worker-jar.yml**: Upgrades the worker jar file.

  - **update-ssh-keys.yml**: Updates (and verifies) {,pub}keys both locally
    and remote. This is useful if you want to cycle keys.

  - **write-ssh-config.yml**: Updates your ~/.ssh/config with hosts from
   inventory.cfg if your ssh config contains these template stubs:
   ```console
   # begin: node.js template

   # end: node.js template
   ```

If something isn't working, have a look at the playbooks or roles. They
are well documented and should (hopefully) be easy to improve.

### Adding a new host to inventory.yml

Hosts are listed as part of an yaml collection. Find the type and provider and
add your host in the list (alphabetical order). Your host can start with an
optional sponsor - for instance `rvagg-debian7-arm_pi1p-1` - which expands
into `test-nodesource_rvagg-debian7-arm_pi1p-1`.

Since we use yaml, we can abstract away `$type` and `$provider` by creating
subelements:

```yaml
 - test:
   - digitalocean:
       debian8-x64-1: {ip: 1.2.3.4}
```

Make sure you follow the naming convention. There are scripts in place that
will throw errors if you don't. Using an incorrect convention will likely
lead to unwanted consequences.

#### Naming

Each host must follow this naming convention:

```
$type-$provider(_$optionalmeta)-$os-$architecture(_$optionalmeta)-$uid
```

For more information refer to other hosts in `inventory.yml` or the
[ansible plugin that is responsible for parsing it][2].

[2]: plugins/inventory/nodejs_yaml.py

#### Metadata

Each host needs a bit of metadata:

 - (required) `ip`: used both by ansible and placed in your ssh config.
 - `user`: only provide if ssh requires a non-root login. Passing this
           will additionally make ansible try to become root for all
           commands executed.
 - `alias`: creates shorthand names for ssh convenience.
 - `labels`: Each host can also labels. More on that below.

#### Adding extra options to a host

Hosts can inherit extra options by adding them to `ansible.cfg`. These are
freeform and are passed to ansible. One example is adding a proxycommand
configuration to hosts at NodeSource since they sit behind a jumphost.

**Note**: We currently can't use ansible's built-in support for `proxy_command`
          since that will enable the `paramiko` connection plugin, disregard
          other ssh-specific options.



### TODO

Unsorted stuff of things we need to do/think about

- [ ] playbook: copy keys and config to release machines
- [ ] avoid messing with keys on machines that has multiple usage such as jump
      hosts (or set up a new jump host)
- [ ] copy release (staging) keys to release machines
- [ ] backup host: generate config, install rsnapshot
- [ ] scaleway: authorized_keys2 since first is overridden at boot
- [ ] switch to slaveLog for all jenkins instances lacking stdout redirection
      (note: this depends on init type!)
- [ ] add iptables-save-persistent to cron on ci hosts
- [ ] [unencrypted host](https://git.io/v6H1z)
- [ ] make exceptions for jump hosts when adding to the CI iptables firewall
- [ ] when creating additional jenkins labels based on `labels=` add os/arch
      as part of hte label (ref: rvagg long irc talk see 2016-08-29 logs)
- [ ] follow up ansible upstream wrt hostname support for smartos/alpine
- [ ] callback plugin: make `nodejs_yaml` a class and support `--host`
- [ ] add label support to jenkins
- [ ] move all service-related stuff to handlers
