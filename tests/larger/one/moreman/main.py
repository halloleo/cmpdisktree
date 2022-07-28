#!/usr/bin/env python3

import logging
import logging.config
import os
import subprocess
import tempfile
import sys
import argh

from moreman import arghex
from moreman import __version__

# Logging
log = logging.getLogger(__name__)


def make_logcfg(level):
    return dict(
        version=1,
        disable_existing_loggers=False,
        formatters={'f': {'format': '%(levelname)s: %(message)s'}},
        handlers={
            'h': {
                'class': 'logging.StreamHandler',
                'formatter': 'f',
                'level': level,
            }
        },
        root={'handlers': ['h'], 'level': level},
    )


MAN_HELP_TEMPLATE = """
.TH "%(TITLE)s" "%(SECTION)s" "%(DATE)s" "%(PRODUCT)s" "%(CENTER)s"
.nf
%(BODY)s
"""

# Global config
cfg = {}

# List of temporary files to be cleaned up
tmp_files = []


def cmd_prefix(man_name):
    """
    return a prefix string for error messages relating to
    command man_name
    """
    return "'%s': " % man_name


def generate_help_doc(man_name):
    """
    Generate from help an nroff doc

    :param man_name: name of man page/command
    :return: (absolute) filename of generated help doc
    """
    args = [man_name]
    args.extend(cfg['help_arg'].split())
    log.debug(cmd_prefix(man_name) + "Execute '%s'" % args)
    helpStr = ""
    try:
        # use check_output to capture output
        helpStr = subprocess.check_output(args, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        log.info(cmd_prefix(man_name) + str(err))
        helpStr = err.output
    except OSError as err:
        log.info(cmd_prefix(man_name) + "OSerror (%s) raised" % err.strerror)

    if not helpStr:
        return ""

    with tempfile.NamedTemporaryFile(
        mode='w', prefix='moreman_', delete=False
    ) as hf:
        params = {
            'TITLE': man_name.upper(),
            'SECTION': "1",
            'DATE': "(generated via '%s %s')"
            % (man_name, " ".join(cfg['help_arg'].split())),
            'PRODUCT': man_name,
            'CENTER': "User Commands",
            'BODY': helpStr.decode('UTF-8', 'ignore'),
        }
        nroff_doc = MAN_HELP_TEMPLATE % params
        hf.write(nroff_doc)
        tmp_name = hf.name
        tmp_files.append(tmp_name)
    log.debug(cmd_prefix(man_name) + "Temp file %s generated" % tmp_name)
    return tmp_name


def help_doc_if_needed(man_name):
    """
    Generate help doc as man page if needed.

    In Details:
    * Check whether a man page exists
    * Generate a help doc, if not
    * Replace man_name with filename of help doc

    :param man_name: name of man page/command
    :return: man name or file name
    """
    has_man_page = True
    try:
        # use check_output to capture output
        subprocess.check_output(
            [cfg['man_cmd'], '-w', man_name], stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as err:
        has_man_page = False

    # Out when man page found
    if has_man_page:
        return man_name

    # Generate help_doc
    log.debug(cmd_prefix(man_name) + "Generating help doc")
    file_name = generate_help_doc(man_name)
    if not file_name:
        log.info(cmd_prefix(man_name) + "Warning: Not help doc generated")
    return file_name


def call_man(man_name):
    """
    Call man on man_name
    """
    args = [cfg['man_cmd']]
    args.extend(cfg['man_args'])
    args.append(man_name)
    log.debug("Execute '%s'" % args)
    subprocess.call(args)


@argh.arg('name', nargs='*', help="name of the command or man page")
@argh.arg(
    '-v',
    '--verbose',
    help="verbose output " + "('-v' shadows man's -v for version!)",
)
@argh.arg(
    '-V',
    '--version',
    help="show the version and exit",
)
# @argh.arg('--save', help="save the generated man page")
@argh.arg('--man-cmd', help="man command to be used")
@argh.arg(
    '-g',
    '--help-arg',
    help="help argument to the command used to generate help document",
)
@argh.arg(
    '-f',
    '--force',
    help="force to generate man page from --help even "
    + "if man page exists ('-f' shadows man's -f "
    + "for whatis lookup!)",
)
def work(
    name,
    verbose=False,
    version=False,
    # save=False,
    man_cmd='man',
    help_arg='--help',
    man_args={},
    force=False,
):
    # Save function sig to global dict
    global cfg
    cfg = locals()

    if version:
        print(f"{__name__.split('.')[0]} {__version__}")
        sys.exit(0)

    # Setup logging
    verbosity = logging.DEBUG if verbose else logging.INFO
    logging.config.dictConfig(make_logcfg(verbosity))
    log.debug("Main cfg = %s" % cfg)

    # Do the work for all manual/command names
    for man_name in name:
        if force:
            man_or_file_name = generate_help_doc(man_name)
        else:
            man_or_file_name = help_doc_if_needed(man_name)
        if man_or_file_name:
            call_man(man_or_file_name)

    # Clean up
    for f in tmp_files:
        if os.path.exists(f):
            pass
            os.unlink(f)


HELP_EPILOG = """
All other options are passed through to the 'man' command.
"""


def main():
    parser = arghex.ArghParserWithUnknownArgs('man_args', epilog=HELP_EPILOG)
    arghex.set_default_command(parser, work)
    argh.dispatch(parser)


if __name__ == "__main__":
    main()
