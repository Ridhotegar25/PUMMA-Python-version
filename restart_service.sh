#!/bin/bash

# Daftar service yang ingin direstart
SERVICES=(
    WP_Pumma.service
    climate.service
    mppt.service
    capture.service
    del_image.service
    delete_file.service
    MB_Pumma.service
    reboot_pi.service
    res_ssh.service
)

# Menghentikan semua service
echo "Menghentikan semua service..."
for SERVICE in "${SERVICES[@]}"; do
    echo "Restart $SERVICE..."
    sudo systemctl restart "$SERVICE"
done

echo "Semua service telah direstart!"
