"""
The default exclusion list
Data from https://bombich.com/kb/ccc5/some-files-and-folders-are-automatically-excluded-from-backup-task
Last updated 2021-01-27
"""

STANDARD_EXCLUDE_PATTERNS_STR = """
# Filesystem implementation details
.HFS+ Private Directory Data*
/.journal
/.journal_info_block
.afpDeleted*
._*
.AppleDouble
.AppleDB
/lost+found
Network Trash Folder
.TemporaryItems
# Volume-specific preferences
.metadata_never_index
.metadata_never_index_unless_rootfs
/.com.apple.timemachine.donotpresent
.VolumeIcon.icns
/System/Library/CoreServices/.disk_label*
/TheVolumeSettingsFolder
/private/var/db/dslocal/nodes/Default/secureaccesstoken.plist
# Apple-proprietary data stores
.DocumentRevisions-V100*
.Spotlight-V100
/.fseventsd
/.hotfiles.btree
/private/var/db/systemstats
/private/var/folders/*/*/C
/private/var/folders/*/*/T
# Volume-specific cache files
/private/var/db/dyld/dyld_*
/System/Library/Caches/com.apple.bootstamps/*
/System/Library/Caches/com.apple.corestorage/*
# NetBoot local data store
/.com.apple.NetBootX
# Dynamically-generated devices
/Volumes/*
/dev/*
/automount
/Network
/.vol/*
/net
# Quota real-time data files
/.quota.user
/.quota.group
# Large datastores that are (or should be) erased on startup
/private/var/vm/*
/private/tmp/*
/cores
/macOS Install Data
# Trash
.Trash
.Trashes
# Time Machine backups
/Backups.backupdb
/.MobileBackups
/.MobileBackups.trash
/private/var/db/com.apple.backupd.backupVerification
# Corrupted iCloud Local Storage
Library/Mobile Documents/*
Library/Mobile Documents.*
.webtmp
# Special files
/private/tmp/kacta.txt
/private/tmp/kactd.txt
/private/var/audit/*.crash_recovery
/private/var/audit/current
/Library/Caches/CrashPlan
/PGPWDE01
/PGPWDE02
/.bzvol
/.cleverfiles
/Library/Application Support/Comodo/AntiVirus/Quarantine
/private/var/spool/qmaster
$Recycle.Bin
Library/Preferences/ByHost/com.apple.loginwindow*
.dropbox.cache
/private/var/db/atpstatdb*
.@__thumb
/.com.prosofteng.DrivePulse.ignore
com.apple.photolibraryd/tmpoutboundsharing
"""

ADD_LIVEFS_EXCLUDE_PATTERNS_STR = """
.DS_Store
/.PKInstallSandboxManager-SystemSoftware
/private/var/spool/postfix
/private/var/folders
/private/var/db
/private/var/log
/private/var/run
Library/Caches
"""


def pattern_list_from_str(pat_str: str):
    return [
        pat for pat in pat_str.splitlines() if not (pat.startswith('#') or pat == '')
    ]


STANDARD_EXCLUDE_PATTERNS = pattern_list_from_str(STANDARD_EXCLUDE_PATTERNS_STR)
ADD_LIVEFS_EXCLUDE_PATTERNS = pattern_list_from_str(ADD_LIVEFS_EXCLUDE_PATTERNS_STR)

if __name__ == '__main__':
    for p in STANDARD_EXCLUDE_PATTERNS:
        print(p)
