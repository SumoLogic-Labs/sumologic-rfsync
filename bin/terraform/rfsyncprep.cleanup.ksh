#!/usr/bin/env bash

umask 022

outputdir="/tmp"
scriptdir="$( dirname $0 )"
terraformdir="$( cd $scriptdir ; pwd -P )"


cachedir=$( terraform output -raw recorded_future_cache_dir )

varlist=$( cat ${cachedir}/config/rfslconfig.vars )

rm -f $outputdir/rfsyncprep.output.tf

terraform apply -auto-approve -destroy ${varlist}

[ -d $terraformdir ] && {

    rm -f $terraformdir/terraform.tfstate.backup 
    rm -f $terraformdir/terraform.tfstate

    rm -f $terraformdir/.terraform.lock.hcl
    rm -fr $terraformdir/.terraform

}
