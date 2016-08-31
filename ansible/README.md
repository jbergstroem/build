## Ansible scripts for the Node.js build group infrastructure

(in lack of a better title)


### Getting started

1. Install ansible 2.0 or newer: `brew install ansible`.
2. Read this document. All of it.
3. Clone the node secrets repository (if you don't have access, ask anyone in
   the build group about it)
4. Copy the private keys (check the secrets repo for instructions) to your
   `~/.ssh` folder. Make sure they have the same name. What keys are available
   to you depends on what role you have. In order to create new vm's and hook
   them up to CI you have to be part of the `infra` group.

### Getting things done

Most of your work will probably include editing `inventory.cfg`, followed by
running one (or multiple) of below playbooks. If you're adding a new host,
limiting ansible ot just running on that host is probably quicker:

```bash
$ ansible-playbook playbooks/jenkins-slave.yaml --limit "test-digitalocean-freebsd10-x64-1"
```

These playbooks are available to you:

 - write-ssh-config.yml: Updates your ~/.ssh/config with hosts from
   inventory.cfg if your ssh config has the correct template stubs:
   ```bash
   # begin: node.js template

   # end: node.js template
   ```

### Adding a host to the inventory

Every host is part of a group (names in square brackets) If you can't find a
group that suits you, it's probably missing. Go add it (if you know what you're
doing) or ping someone in the build group for advice/guides. Only add it to one
group since each group is meant to contain sub groups or roles.

Make sure you follow the naming convention. There are scripts in place that
will throw errors if you don't. Also, using an incorrect convention might
lead to unwanted consequences.

`ip=` is required for each host since it is used both by ansible and placed
in your ssh config. `user=` is optional and should only be provided if ssh
requires a non-root login. `alias=` is used to create shorthand names for
ssh convenience.

#### Naming

Each host must follow this naming convention:

```
$group-$provider(_$optionalmeta)-$os(_$optionalmeta)-$architecture-$uid
```

For more information, refer to other hosts in `inventory.cfg` or the [ansible
plugin that is responsible for parsing it][1].

[1]: plugins/vars/parse_host.py

#### Working with labels

Labels are used in the jenkins environment. They're most often used when
defining what workers should be part of a job.

Each host gets at least a label based on os/arch, such as centos6-x64 or
freebsd10-x86. If the machine has other intended uses, you can add more
labels, separated by commas; for instance:
```
  test-digitalocean-freebsd10-x64-1 ip=1.2.3.4 labels=foo,bar
```

(important: don't put space between multiple labels or ansible will cry)

There are also labels that are only used in the release environment, such as
`pre-1-release`.

#### Jump hosts

If your host is hidden behind a proxy or jump host, create a new group in the
meta section and add a jump command similar to [`group_vars/tunnel_rvagg`][2]. Avoid passing `-J` since it requires a more recent version of ssh.

[2]: group_vars/tunnel_rvagg


### TODO

Unsorted stuff of things I need to do/think about

- [ ] playbook: copy keys and config to release machines
- [ ] avoid messing with keys on machines that has multiple usage such as jump
      hosts (or set up a new jump host)
- [ ] ubuntu systemd init needs different path (copy from gather_facts path?)
- [ ] paths in systemd init scripts differ
- [ ] freebsd: replace quarterly with latest for packages
- [ ] support host aliases in hostname config generator
- [ ] avoid windows hosts in ssh generator
- [ ] create command to check ccache statistics
- [ ] xz,svn on all test boxes
- [ ] add command to update all packages
- [ ] use become instead of sudo
- [ ] copy release (staging) keys to release machines
- [ ] backup host: generate config, install rsnapshot
- [x] ci vs ci-release.nodejs.org in init scripts
- [ ] scaleway: authorized_keys2 since first is overridden at boot
- [ ] switch to slaveLog for all jenkins instances lacking stdout redirection
- [x] release centos5 needs swap or more ram? (nope)
- [ ] run service iptables-save persistent on build master
- [x] weekly cron job to update slave.jar? (nope, playbook)
- [ ] make sure ::1 localhost exists in all hosts (#415)
- [ ] [unencrypted host](https://git.io/v6H1z)
- [ ] figure out how ansible parses group_vars since adding groups from
      vars_plugins doesn't seem to make the vars get picked up (ansible 2.0)
- [ ] set the hostname to `{{ inventory_hostname }}`
- [ ] make exceptions for jump hosts when adding to the CI iptables firewall
- [ ] when creating additional jenkins labels based on `labels=` add os/arch
      as part of hte label
