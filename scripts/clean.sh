#!/usr/bin/env bash

set -e

if [[ -d 'dist' ]] ; then
    rm -r dist
fi
if [[ -d 'site' ]] ; then
    rm -r site
fi