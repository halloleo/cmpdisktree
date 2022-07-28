The base directory `one` resembles the moreman repo from 20-Oct-2019 (commit e5129de588cc91f1bf4d888b9ed4869e5b794e42).

I have changed the following:

* Renamed all .git directories to .gitx (as `.git` the index files inside were
  magically changed (by external git watch processes???)
* Added a symbolic link `linked-to-pyproject.toml` (as a special case)
* Added a dead symbolic link `linked-to-not-existing.txt`  (as a special case)
