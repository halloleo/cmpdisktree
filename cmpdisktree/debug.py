"""
Debug helpers
"""
import sys
import traceback


def dbg_print_ftc_list(files_to_compare):
    for path1 in files_to_compare:
        print(f'To compare: {path1}')


def dbg_long_exception(err):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(
        exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout
    )
