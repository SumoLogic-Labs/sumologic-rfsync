#!/usr/bin/env bash

umask 022

outputdir="/tmp"
scriptdir="$( dirname $0 )"
terraformdir="$( cd $scriptdir ; pwd -P )"


cachedir=$( terraform output -raw recorded_future_cache_dir )

varlist=$( cat ${cachedir}/config/rfslconfig.vars )

rm -f $outputdir/rfsyncprep.output.tf

terraform apply -auto-approve -destroy ${varlist}

rm -f $( pwd )/terraform.tfstate.backup 
rm -f $( pwd )/terraform.tfstate

rm -f $( pwd )/.terraform.lock.hcl
rm -fr $( pwd )/.terraform
