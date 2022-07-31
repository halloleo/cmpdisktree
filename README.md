```
      ___
     /\__\            _____              ___
    /:/  /           /::\  \           /\__\
   /:/  /           /:/\:\  \         /:/  /
  /:/  /  ___      /:/  \:\__\       /:/__/
 /:/__/  /\__\    /:/__/ \:|__|     /::\  \
 \:\  \ /:/  /    \:\  \ /:/  /    /:/\:\  \
  \:\  /:/  /      \:\  /:/  /     \/__\:\  \
   \:\/:/  /        \:\/:/  /           \:\  \
    \::/  /          \::/  /             \:\__\
     \/__/   mp       \/__/   isk         \/__/ ree
    
```

### Compare Directories as macOS Disk Structures

## The Problem

You make backups from your macOS disk, right? But how can you check that your  important stuff  got copied correctly? Using

    diff -r FS1 FS2

gives you so many errors that the command is impossible to use. This is caused by a few separate problems, but the main one is: **Symlinks with non-existing target are reported as errors by `diff`**, but for a disk compare we only want to know whether the target paths in the links are the same, not whether the targets exist.

`cmpdisktree` to the rescue! This command line tool compares filesystems ("disks") in a sensible way for backup check. It checks symlinks for same target path and excludes by default some system directories. It is mainly designed for macOS disks but via some options it can  be tweaked for other purposes. 

Here the help message:

```
Usage: cmpdisktree.py [OPTIONS] FS1 FS2

  Compare the directories FS1 and FS2 as macOS disk structures

  Errors are reported to a file (default 'cmp-err.log')

Options:
  -v, --verbose                  Print debug output
  -q, --quiet                    No informational output
  -i, --report-identical         Report identical files to file (default:
                                 'cmp-ok.log')

  -1, --traversal-only           Only traverse FSs (Phase 1). Don't compare
                                 file contents

  -t, --traverse-from-list PATH  Path of file with list of relative paths for
                                 traversal

  -c, --clear-std-exclusions     Don't apply the standard exclusions for macOS
                                 disk files systems (i.e. compare everything)

  -l, --live-fs-exclusions       Add exclusions for live filesystems (e.g.
                                 boot volumes)

  -m, --ignore-missing-in-FS1    Ignore when a file from FS2 doesn't exist in
                                 FS1 (used for boot backups where FS1 is the
                                 live disk)

  -r, --relative-fs-top          Allow relative filesystem top (used when
                                 applying the exclusions)

  -o, --output-path PATH         Output path for report file.
  --version                      Show the version and exit.
  --help                         Show this message and exit.
```


## Details to some options

`--output-path PATH`: 
:   Set where the output should go:  
    If the path of a _file_ is given, use this file as error log file and write 
    (if applicable) the OK log to `cmp-ok.log`
    in the same directory.  
    if the path of a _directory_ is given, write `cmp-err.log` and `cmp-ok.log`
    in this directory.

`--relative-fs-top`: 
:   Normally exclusion patterns which match only at the _beginning_ of a path
    name have to start with that pattern as expected. This option widens the
    match to the middle of a path name as well. This is useful if you want to
    check on boot filesystems which you have copied deeper into a file system.

`--live-fs-exclusions`:
:   Use additional exclusions which ignore files like .DS_Store. This helps to
    compare "life" filesystems as the same even if these files have changed
    (e.g. by looking at the file structure in Finder). This adds some various
    (experimental) cache exclusions as well.

`--traverse-from-list PATH`: 
:   Do not traverse the filesystem; instead use the list of relative paths
    given in a text file (one path per line). The paths are relative to the
    starting directories `FS1`/`FS2`.  
    Note: Only paths to normal _files_ are compare for same
    content. _Directories are only checked for existence in FS1 and FS2;
    _symlinks_ are only checked that they point to the same target


## Credits

Thanks to Kent Nassen and Lennert Stock for the [ASCII art characters](http://www-personal.umich.edu/~knassen/figfonts/isometric2.flf).

<!--  LocalWords:  cmpdisktree filesystem filesystems Symlinks symlinks
 -->
