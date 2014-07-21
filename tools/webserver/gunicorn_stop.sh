#!/bin/bash

VIRTUAL_ENV="${1}"

#if [ -n "${VIRTUAL_ENV}" ]; then
#	echo "Stop: Setting up Virtual Environment at ${VIRTUAL_ENV}"
#	source ${VIRTUAL_ENV}
#fi

echo "Stopping existing instances..."
pkill gunicorn_pecan

