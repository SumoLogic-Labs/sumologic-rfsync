#!/usr/bin/env bash

umask 022

outputdir="/tmp"

scriptdir="$( dirname $0 )"

configdir="/tmp/rfslsync_config"

terraformdir="/tmp/rfslsync_terraform"

tfcmdcount=$( which terraform | wc -l )
[[ $tfcmdcount -lt 1 ]] && exit

cd ${terraformdir}

rm -f ${outputdir}/rfsyncprep.output.tf

[ -f ${configdir}/rfslsync.ksh ] && . ${configdir}/rfslsync.ksh

terraform apply -auto-approve -destroy

[ -d ${terraformdir} ] && {

    rm -f ${terraformdir}/terraform.tfstate.backup 
    rm -f ${terraformdir}/terraform.tfstate

    rm -f ${terraformdir}/*.tf
    rm -f ${terraformdir}/*.ksh
    rm -fr ${terraformdir}/.terraform*
    rm -fr ${terraformdir}/json

}

rm -f ${configdir}/rfslsync.ksh
rm -f ${configdir}/rfslsync.cfg
