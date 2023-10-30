Installing As A Service

1. Modify the pitch.service file `WorkingDirectory` to reflect Pitch install location.
2. Move file to `/etc/systemd/system`
3. Run commands `systemctl enable pitch` and `systemctl start pitch` to run
