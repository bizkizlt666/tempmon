#!/bin/bash

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
KILL_LIST="$BASE_DIR/killist.ini"

if [ ! -f "$KILL_LIST" ]; then
    echo "Nincs killist.ini a mappában: $BASE_DIR"
    exit 1
fi

while IFS= read -r process_name || [ -n "$process_name" ]; do
    if [ -n "$process_name" ]; then
        echo "Killelés: $process_name"
        /usr/bin/pkill -f "$process_name"
    fi
done < "$KILL_LIST"

echo "Done."

