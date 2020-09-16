#!/bin/bash
# Example installation for Ubuntu/Fedora/Raspberry PI/etc.
echo "Updating Linux packages"
apt-get update
echo "Installing required Linux packages"
apt-get install python-dev libbluetooth-dev libcap2-bin -y
# grant the python executable permission to access raw socket data
echo "Granting non-root access to raw sockets"
setcap 'cap_net_raw,cap_net_admin+eip' $(readlink -f $(which python3))