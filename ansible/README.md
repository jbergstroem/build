### ansible scripts for setting up the build group infrastructure

(in lack of a better title)


#### getting started

1. Install ansible 2.0 or newer: `brew install ansible`.
2. Read this document. All of it.
3. Clone the node secrets repository (if you don't have access, ask anyone in
   the build group about it)
4. Copy the private keys (check the secrets repo for instructions) to your
   `~/.ssh` folder. Make sure they have the same name. What keys are available
   to you depends on what role you have. In order to create new vm's and hook
   them up to CI you have to be part of the `infra` group.

#### getting things done

These commands are available to you:
