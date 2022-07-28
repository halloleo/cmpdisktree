# TODOs

### 18-Jul-2018 

- [ ] Handle commands which are only reachable in particular virtualenvs or Pipenv setups. I.e. allow something like

        (cd /directory/with/pipfile; pipenv run pweave --help)

    to run. Might be not easy to include in Emacs man system.

### 30-Apr-2018

- [ ] Make moreman in the case of an *internal* error return exit status Ok (and output the error to stdout), so that Emacs shows the info. 

### 21-Dec-2017

- [ ] Option to suppress the man page header (for commands which generate their own headers. E.g. `pipenv --man`)

### Earlier

- [x] ~For commands *with* man page: option to "force" moreman/`--help` processing~ 

- [ ] For commands *with* man page: recognise when a moreman option is used and switch implicitly to force mode

- [ ] Handle commands which have no man page *and* no `--help` option. This might need a config file for these special cases

    Here a list of the ones I know about so far:
    - `pew` -> help at `pew` (without args)
