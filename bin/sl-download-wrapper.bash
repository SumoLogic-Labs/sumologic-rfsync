#!/bin/bash
  
umask 022

BASEDIR="$HOME/sumologic-rfsync"
cmdname="$BASEDIR/bin/rfslsync.py"
cfgname="$BASEDIR/etc/rfslsync.cfg"

complain_and_exit () {
   echo "ERROR: $2"
   exit "$1"
}

[ -d "$BASEDIR" ] || complain_and_exit "111" "Exiting. Cannot find: $BASEDIR"

[ -f "$cmdname" ] || complain_and_exit "112" "Exiting. Cannot find: $cmdname"
[ -x "$cmdname" ] || chmod 755 "$cmdname"

[ -f "$cfgname" ] || complain_and_exit "113" "Exiting. Cannot find: $cfgname"
[ -f "$cfgname" ] || chmod 644 "$cfgname"

echo "$cmdname" -c "$cfgname" -v
