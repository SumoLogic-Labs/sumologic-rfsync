#!/usr/bin/env bash
  
umask 022

BASEDIR="/var/tmp/rfslsync"
cmdname="$BASEDIR/bin/rfslsync.py"
cfgname="$BASEDIR/etc/rfslsync.cfg"
LOGDIR="$BASEDIR/log"

complain_and_exit () {
   echo "ERROR: $2"
   exit "$1"
}

[ -d "$BASEDIR" ] || complain_and_exit "111" "Exiting. Cannot find: $BASEDIR"
[ -f "$cmdname" ] || complain_and_exit "112" "Exiting. Cannot find: $cmdname"
[ -f "$cfgname" ] || complain_and_exit "113" "Exiting. Cannot find: $cfgname"

[ -d "$LOGDIR" ]  || mkdir -p $LOGDIR

logfile="$BASEDIR/log/output.log"
rm -f $logfile 
touch $logfile
$cmdname -c $cfgname -v > $logfile 2>&1
