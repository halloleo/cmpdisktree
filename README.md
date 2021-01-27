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

gives you so many errors that the command is impossible to use. This is caused by a few different problems, but the main one is: *Symlinks with non-existing target* are reported as errors in diff, but for a disk compare we only want to know whether the target strings in the links are the same, not whether the targets exist.

`cmpdisktree` to the rescue! This command line tool compares filesystems ("disks") in a sensible way for backup check. It checks symlinks for same target string and excludes some system directories. It is mainly designed for macOS disks but can be tweak via command line options for other purposes. Here the help message:

```
Usage: cmpdisktree.py [OPTIONS] FS1 FS2

  Compare the directories FS1 and FS2 as macOS disk structures

  Errors are reported to a file (default 'cmp-err.log')

Options:
  -v, --verbose               Print debug output.
  -q, --quiet                 No informational output.
  -i, --report-identical      Report identical files to file (default: 'cmp-
                              ok.log')
  -1, --traversal-only        Only traverse FSs (Phase 1). Don't compare file
                              contents
  -c, --clear-std-exclusions  Don't use standard exclusions for macOS disk
                              files systems
  -l, --live-fs-exclusions    Add exclusions for live filesystems (e.g. boot
                              volume)
  -r, --relative-fs-top       Allow relative filesystem top (used when
                              applying the exclusions)
  -o, --output-path PATH      Output path for report file.
  --help                      Show this message and exit.
```


## Details to some options

`--relative-fs-top`: 
:   This makes exclusion patterns with demand to match the 
    beginning of a path name match in the middle of  a path name as well.

`--output-path`: 
:   If a file path is given, use the file as error log file 
    and write, if applicable, the OK log to `cmp-ok.log` in the same directory

`--relative-fs-top`: 
:   This makes exclusion patterns with demand to match the beginning of a path name match in the middle of  a path name as well.

`--output-path`: 
:   If a file path is given, use the file as error log file 
    and write, if applicable, the OK log to `cmp-ok.log` in the same directory

## Credits

Thanks to Kent Nassen and Lennert Stock for the [ASCII art characters](http://www-personal.umich.edu/~knassen/figfonts/isometric2.flf).

<!--  LocalWords:  cmpdisktree filesystems Symlinks symlinks
 -->
