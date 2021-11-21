#!/bin/bash

cd ../

# Check if root
if ((EUID != 0 )); then
    echo "Please run this script as root"
    exit 100
fi

if [[ ! -e "./savagetime/media" ]]; then
    echo "Media directory not found, creating..."
    exit 100
else
    echo "Media directory found!"
fi

# folder permission
# set current directory folder

# find savagetime/ -type d -print0 | xargs -r0 /bin/bash -c 'chown robinson "$@"; chgrp www-data "$@";' 
find ./ -type d ! -path "./venv/*" ! -path "./.git/*" -print0 | xargs -r0 /bin/bash -c 'chown robinson:www-data "$@"; chmod 770 "$@"; "$@"'

# normal file permission
find ./ -type f ! -path "./venv/*" ! -path "./.git/*" -print0 | xargs -r0 /bin/bash -c 'chown robinson:www-data "$@"; chmod 660 "$@"; "$@"'
find ./ -name "*.sh" ! -path "./venv/*" ! -path "./.git/*" -type f -print0 | xargs -0 chmod 760
