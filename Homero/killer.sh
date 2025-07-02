#!/bin/bash

# A script saját mappájának meghatározása
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
KILL_LIST="$BASE_DIR/killist.ini"

# Ellenőrzi, hogy létezik-e a killist.ini
if [ ! -f "$KILL_LIST" ]; then
    echo "Nincs killist.ini a mappában: $BASE_DIR"
    exit 1
fi

# Soronként beolvassa és kill-eli a process neveket
while IFS= read -r process_name || [ -n "$process_name" ]; do
    if [ -n "$process_name" ]; then
        echo "Killelés: $process_name"
        /usr/bin/pkill -f "$process_name"
    fi
done < "$KILL_LIST"

echo "Kész."

