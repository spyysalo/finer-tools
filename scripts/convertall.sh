#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 FINER-DATA-DIR OUTPUT-DIR" >&2
    exit
fi

set -euo pipefail

INDIR="$1"
OUTDIR="$2"

# https://stackoverflow.com/a/246128
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
CONVERT="$SCRIPTDIR/finer2standoff.py"

mkdir -p "$OUTDIR"/{train,dev,test,wiki-test}

python3 "$CONVERT" "$INDIR/digitoday.2014.train.csv" -o "$OUTDIR/train"
python3 "$CONVERT" "$INDIR/digitoday.2014.dev.csv" -o "$OUTDIR/dev"
python3 "$CONVERT" "$INDIR/digitoday.2015.test.csv" -o "$OUTDIR/test"
python3 "$CONVERT" "$INDIR/wikipedia.test.csv" -o "$OUTDIR/wiki-test"
