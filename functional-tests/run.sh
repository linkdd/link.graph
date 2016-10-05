#!/bin/bash

function failure() {
    ipcluster stop || exit 2
    exit 1
}

ipcluster start -n 4 --daemonize || exit 1
sleep 10

python initialize-riak.py || failure

aloe features/create/scenarios.feature || failure
aloe features/read/scenarios.feature || failure
aloe features/update/scenarios.feature || failure
aloe features/delete/scenarios.feature || failure

ipcluster stop || exit 2
