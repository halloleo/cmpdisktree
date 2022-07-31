moreman: Man Pages for Commands without Man Pages
=========

This program generates man pages for command line tools which do not come with
proper separate man pages. For these tools `man` cannot display manual
information, `moreman` however uses the command's help string (usually
displayed via the command line option `--help`) and assembles from this a "man
page".

## Overview

`moreman` is designed as a drop-in replacement for [`man`][man]. Apart from
very few options `moreman` passes all arguments through to the man command it
eventually calls. If `moreman` is called with a tool name for which a normal
man page exists, it just passes the name through to `man`; if no normal man
page exists, `moreman` assembles the man page in the described manner and then
calls `man` for final formatting.

My personal use is inside [Emacs][emacs]: Emacs has the great feature of [Man
Page Lookup][emacs-man]: It displays each man page in its own buffer/frame, so
that you easily can view the documentation to a command while using the command
in a shell buffer in another window or frame. - And with `moreman` this extends
to all commands which provide some meaningful documentation via their help
message even if they do not have a real man page.

### A Word of Warning

`moreman` works by calling the command it wants to create the man page for with
the help option - normally `--help`. This *can* be dangerous if the command
does not expect `--help` to display the help message.


## Installation

### Requirements

At least Python 3.5 (legacy Python 2.7 might work as well) plus the [`argh`][argh]
package.

[argh]: https://github.com/neithere/argh

### Install

The tool is pip-installable: `pip install moreman` For the intended command
line use though I recommend installation via [pipx]:

        pipx install moreman

## Usage

Test whether everything is set up correctly by invoking `moreman`'s help
message:

    $ moreman --help

This should give you something like

```
usage: moreman [-h] [-v] [--man-cmd MAN_CMD] [-g HELP_ARG] [-f]
               name [name ...]

positional arguments:
  name                  name of the command or man page

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose output ('-v' shadows man's -v for version!)
                        (default: False)
  --man-cmd MAN_CMD     man command to be used (default: 'man')
  -g HELP_ARG, --help-arg HELP_ARG
                        help argument to the command used to generate help
                        document (default: '--help')
  -f, --force           force to generate man page from --help even if man
                        page exists ('-f' shadows man's -f for whatis lookup!)
                        (default: False)

All other options are passed through to the 'man' command.
```

Now try to list the same info as a "man page":

    $ moreman moreman

Voila! This should look like a proper man page - many man page viewers are able
to recognise this format.[^1]

[^1]: Under the hood `moreman` creates a nroff file which it passes to `man`.

### Hooking up to Emacs

In order use `moreman` in Emacs, customise the Emacs variable `manual-program`
(which is in the **man** customisation group). After checking that you can
access `moreman` from your shell prompt set `manual-program` to `moreman`and
everything should work fine.

### Help for sub commands

Some tools provide extensive help and they split it over the help messages of
multiple sub commands. moreman can utilise these sub command help messages via
the `--help-arg` option.

***Update September 2019***: Some pip installations do install a man page - in
that case this example is obsolete.

For example `pip --help` lists only some general options and pip's sub
commands; detailed info about, say, the `install` sub command is displayed only
by `pip install --help`.

But issue

    moreman --help-arg="install --help" pip 

and you get a "man page" for the `install` subcommand of `pip`.

This works in Emacs too: After `M-x man` enter at the prompt
`--help-arg="install --help" pip`.[^2]

[^2]: In Emacs, in order to enter the required spaces you might need to use the
    `^Q <space>` key combination to circumvent Emacs' auto-complete feature at
    the prompt.


## Miscellaneous 

If you have difficulties, open an GitHub issue for your problem. If you made
enhancements, please create a pull request.

Also note, this project uses another little module I wrote: [ArghEx: Extensions
for Argh][arghex]

[man]: http://man7.org/linux/man-pages/man1/man.1.html
[emacs-man]: http://www.gnu.org/software/emacs/manual/html_node/emacs/Man-Page.html#Man-Page
[emacs]: http://www.gnu.org/software/emacs/
[arghex]: https://github.com/halloleo/arghex
[pipx]: https://pipxproject.github.io/pipx/


<!--  LocalWords: moreman nroff installable argh arg subcommand
 -->
