#!/bin/bash

# Daftar service yang ingin dihentikan
SERVICES=(
    WP_Pumma.service
    climate.service
    mppt.service
    capture.service
    del_image.service
    del_image.timer
    delete_file.service
    MB_Pumma.service
    reboot_pi.service
    res_ssh.service
)

# Menghentikan semua service
echo "Menghentikan semua service..."
for SERVICE in "${SERVICES[@]}"; do
    echo "Menghentikan $SERVICE..."
    sudo systemctl stop "$SERVICE"
done

echo "Semua service telah dihentikan!"
