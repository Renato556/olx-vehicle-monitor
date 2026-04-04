#!/usr/bin/with-contenv bashio

echo "=========================================="
echo "Starting OLX Vehicle Monitor"
echo "=========================================="
echo ""
echo "Monitoring: OLX MG (R$ 19.000 - R$ 26.000)"
echo "ntfy.sh topic: carros-mg-olx"
echo "Check interval: 10 minutes"
echo ""
echo "=========================================="
echo ""

cd /app
python3 /app/app/monitor.py
