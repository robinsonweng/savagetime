#!/bin/bash

# Check if root
if ((EUID != 0 )); then
    echo "Please run this script as root"
    exit 100
fi

cd ..

# folder permission
# find savagetime/ -type d -print0 | xargs -r0 /bin/bash -c 'chown robinson "$@"; chgrp www-data "$@";' 
find savagetime/ -type d -print0 | xargs -0 chown robinson:www-data

# normal file permission
find savagetime/ -type f -print0 | xargs -0 chmod 660
find savagetime/ -name "*.sh" -type f -print0 | xargs -0 chmod 760
