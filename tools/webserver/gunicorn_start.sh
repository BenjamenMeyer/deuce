#!/bin/bash

VIRTUAL_ENV="${1}"

if [ -n "${VIRTUAL_ENV}" ]; then
	echo "Start: Setting up Virtual Environment at ${VIRTUAL_ENV}"
	source ${VIRTUAL_ENV}/bin/activate
fi

echo "Starting new instances..."
gunicorn_pecan config.py -D

