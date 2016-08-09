### Ansible scripts for the Node.js build group infrastructure

(in lack of a better title)


#### Getting started

1. Install ansible 2.0 or newer: `brew install ansible`.
2. Read this document. All of it.
3. Clone the node secrets repository (if you don't have access, ask anyone in
   the build group about it)
4. Copy the private keys (check the secrets repo for instructions) to your
   `~/.ssh` folder. Make sure they have the same name. What keys are available
   to you depends on what role you have. In order to create new vm's and hook
   them up to CI you have to be part of the `infra` group.

#### Getting things done

Most of your work will probably include editing `inventory.cfg`, followed by
running one (or multiple) of below playbooks. If you're adding a new host,
limiting ansible ot just running on that host is probably quicker:

```bash
$ ansible-playbook playbooks/jenkins-slave.yaml --limit "test-digitalocean-freebsd10-x64-1"
```

These playbooks are available to you:

 - generate-ssh-config.yaml: Updates your ~/.ssh/config with hosts from
   inventory.cfg if your ssh config has the correct template stubs:
   ```bash
   # begin: node.js template

   # end: node.js template
   ```
