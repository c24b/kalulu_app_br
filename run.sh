#!/bin/bash

ROOT_DIR=$(pwd)
VENV=$ROOT_DIR/.venv

db_run()
{
    echo "INIT DB"
    $VENV/bin/python $ROOT_DIR/db/run.py &
}

db_run