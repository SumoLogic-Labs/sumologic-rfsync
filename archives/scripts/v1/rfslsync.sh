#!/usr/bin/env bash
  
umask 022

ulimit -Sv 1000000 

MYDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASEDIR=$( dirname $MYDIR)

BINDIR="$BASEDIR/bin"
cmdname="$BINDIR/rfslsync.py"

ETCDIR="$BASEDIR/etc"
cfgname="$ETCDIR/rfslsync.cfg"

LOGDIR="$BASEDIR/log"
logfile="$LOGDIR/output.log"

complain_and_exit () {
   echo "ERROR: $2"
   exit "$1"
}

[ -d "$BASEDIR" ] || complain_and_exit "111" "Exiting. Cannot find: $BASEDIR"
[ -d "$LOGDIR" ]  || mkdir -p $LOGDIR

[ -f "$cmdname" ] || complain_and_exit "112" "Exiting. Cannot find: $cmdname"
[ -f "$cfgname" ] || complain_and_exit "113" "Exiting. Cannot find: $cfgname"

rm -f $logfile 
touch $logfile

$cmdname -c $cfgname -v 3 -a > $logfile 2>&1
