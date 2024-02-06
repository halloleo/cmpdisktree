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

You make backups from your macOS disk, right? But how can you check that your important stuff  got copied correctly? Using `diff` in the terminal like this

    diff -r FS1 FS2

gives you so many errors that the command is impossible to use. This is caused by a few separate problems, but the main one is: `diff` reports **symlinks with non-existing target as errors**, but for a disk compare we only want to know whether the target paths in the links are the same, not whether the targets exist.

**cmpdisktree** to the rescue! This command line tool compares filesystems ("disks") in a sensible way for backup check. It checks symlinks for same target path and excludes by default some system directories. It is mainly designed for macOS disks but via some options it can  be tweaked for other purposes. 

## A Better Approach

**cmpdisktree** takes two directories as command line parameters. These are often a system disk on one volume and its backup on another. That's  why I call them filesystems FS1 and FS2. cmpdisktree  compares theses filesystems in two phases, the **Traversal Phase** and the **Compare Phase**.

<dl>
<dt>The Traversal Phase</dt><dd>

In the first phase cmpdisktree goes through the directory tree of FS1 by recursively looking at files, directories and symlinks in each directory. Files which exist in FS1 and FS2 are then marked for later compare of the content while directories and symlinks are compared straight away: directories for the same entries and symlinks for that they point to the same (existing or non-existing) target.
</dd>

<dt>The Content Compare Phase</dt><dd>

In this second phase cmpdisktree compares the content of the files in FS1 and FS2 which were marked during the traversal phase. The comparing is done in a "non-shallow" way, byte for byte. Deending on the size of the filesystems this can take a long time, so phase 2 can be disabled  (option `--traversal-only`) if a compare of the directory structure seems to be good enough.
</dd>
</dl>

## Tailoring and Sampling

In the traversal phase cmpdisktree applies a list of exclusion patterns. If a directory or file matches one of the exclusions it will not be compared, **so differences are not reported**. This list is adapted from [Carbon Copy Cloner's exclusion list][exclusion-source]. It is heavily tailored towards macOS system disks. You can completely swiych this off via `--clear-std-exclusions` or add more exclusions (like for `.DS_Store` files) via `--live-fs-exclusions`. For details see below.

The compare phase can be used without traversal phase and alternatively be controlled by an external file (option `--traverse-from-list`). This is quite a unique option which disables the _traversal_ phase; instead the paths of the files to compare are read from a text file. This makes sense when from _very_ large disks only a portion  of files (e.g. a random sample) should be compared. The sample is provided via the external file.


## The Help message

For details about other ways to customise the cmpdisktree's behaviour here the help message:

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


## More Details to Some Options

<dl>

<dt><code>--output-path PATH</code>:</dt><dd>

Set where the output should go:  
    If the path of a _file_ is given, use this file as error log file and write 
    (if applicable) the OK log to `cmp-ok.log`
    in the same directory.  
    if the path of a _directory_ is given, write `cmp-err.log` and `cmp-ok.log`
    in this directory.
</dd>

<dt><code>--relative-fs-top</code>:</dt><dd>

Normally exclusion patterns which match only at the _beginning_ of a path
    name have to start with that pattern as expected. This option widens the
    match to the middle of a path name as well. This is useful if you want to
    check on boot filesystems which you have copied deeper into a file system.
</dd>

<dt><code>--live-fs-exclusions</code>:</dt><dd>

Use additional exclusions which ignore files like .DS_Store. This helps to
    compare "life" filesystems as the same even if these files have changed
    (e.g. by looking at the file structure in Finder). This adds some various
    (experimental) cache exclusions as well.
</dd>

<dt><code>--traverse-from-list PATH</code>:</dt><dd>

Do not traverse the filesystem; instead use the list of relative paths
    given in a text file (one path per line). The paths are relative to the
    starting directories `FS1`/`FS2`.  
    Note: Only paths to normal _files_ are compares for same content. 
    _Directories_ are only checked for existence in FS1 and FS2;
    with _symlinks_ is only checked that they point to the same target.
</dd>

</dl>


## Version History

**Version 0.2**

* Option `--traverse-from-list` is implemented. 

* Minor improvement to exclusion list, etc.

**Version 0.1**

* Compare while reporting progress bar
* Option `--clear-std-exclusions` to compare _all_ files in the filesystems.

## Credits

Thanks to:

* Mike Bombich for [Carbon Copy Cloner][ccc][^1] and its exclusion list.
* Kent Nassen and Lennert Stock for the [ASCII art characters][ascii].
* Armin Ronacher and contributors for [click].
* Casper da Costa-Luis and contributors for [tqdm].

  [^1]: Backup tools like Carbon Copy Cloner gave me the reason to develop cmpdisktree in the first place.

  [exclusion-source]: https://bombich.com/kb/ccc5/some-files-and-folders-are-automatically-excluded-from-backup-task
  [ascii]: http://www-personal.umich.edu/~knassen/figfonts/isometric2.flf
  [click]: https://github.com/pallets/click
  [tqdm]: https://github.com/tqdm/tqdm
  [ccc]: https://bombich.com/


<!--  LocalWords:  cmpdisktree filesystem filesystems Symlinks symlinks
 -->
