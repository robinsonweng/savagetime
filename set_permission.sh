# Check if root
if ((EUID != 0 )); then
    echo "Please run this script as root"
    exit 100
fi

# set sgid for media folder
chmod g+s ./savagetime/media
# set default permission to subdirectory in media
setfacl -R -d -m g::rwX ./savagetime/media
setfacl -R -d -m o::rx ./savagetime/media

getfacl ./savagetime/media
