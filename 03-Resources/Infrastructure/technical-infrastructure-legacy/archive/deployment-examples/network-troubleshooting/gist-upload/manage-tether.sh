#!/bin/bash
# Tether Management Script
# Run: curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/manage-tether.sh | bash [up|down|restart|status]

TETHER_CONNECTION="netplan-enp7s0"

case "${1:-status}" in
    down|disconnect)
        echo "========================================"
        echo "DISCONNECTING TETHER"
        echo "========================================"
        echo ""
        echo "Connection: $TETHER_CONNECTION"
        echo ""
        nmcli connection down "$TETHER_CONNECTION"
        echo ""
        echo "✓ Tether disconnected"
        echo ""
        echo "Waiting 5 seconds for routes to clear..."
        sleep 5
        echo ""
        echo "Verifying..."
        if ip -br addr show | grep -q "enx"; then
            echo "  ⚠ Tether interface may still be active"
        else
            echo "  ✓ Tether interface cleared"
        fi
        echo ""
        ;;
    
    up|connect)
        echo "========================================"
        echo "RECONNECTING TETHER"
        echo "========================================"
        echo ""
        echo "Connection: $TETHER_CONNECTION"
        echo ""
        nmcli connection up "$TETHER_CONNECTION"
        echo ""
        echo "Waiting 5 seconds for connection..."
        sleep 5
        echo ""
        echo "Verifying..."
        if ping -c 1 -W 2 8.8.8.8 &>/dev/null; then
            echo "  ✓ Tether connected - Internet reachable"
        else
            echo "  ⚠ Connection failed - restarting NetworkManager..."
            echo ""
            sudo systemctl stop NetworkManager
            sleep 2
            sudo systemctl start NetworkManager
            sleep 3
            sudo systemctl daemon-reload
            sleep 2
            nmcli connection up "$TETHER_CONNECTION"
            sleep 5
            if ping -c 1 -W 2 8.8.8.8 &>/dev/null; then
                echo "  ✓ Tether connected after restart"
            else
                echo "  ✗ Connection still failing"
            fi
        fi
        echo ""
        ;;
    
    restart)
        echo "========================================"
        echo "RESTARTING NETWORK MANAGER"
        echo "========================================"
        echo ""
        echo "Stopping NetworkManager..."
        sudo systemctl stop NetworkManager
        sleep 2
        echo "Reloading daemon..."
        sudo systemctl daemon-reload
        sleep 2
        echo "Starting NetworkManager..."
        sudo systemctl start NetworkManager
        sleep 3
        echo "Bringing up tether..."
        nmcli connection up "$TETHER_CONNECTION"
        sleep 5
        echo ""
        echo "Verifying..."
        if ping -c 1 -W 2 8.8.8.8 &>/dev/null; then
            echo "  ✓ NetworkManager restarted - Internet reachable"
        else
            echo "  ⚠ Still having issues"
        fi
        echo ""
        ;;
    
    status)
        echo "========================================"
        echo "TETHER STATUS"
        echo "========================================"
        echo ""
        echo "Connection: $TETHER_CONNECTION"
        echo ""
        echo "nmcli status:"
        nmcli connection show "$TETHER_CONNECTION" 2>/dev/null | grep -E "GENERAL.STATE|IP4" || echo "  Connection not found"
        echo ""
        echo "Network interfaces:"
        ip -br addr show | grep -v "lo"
        echo ""
        echo "Internet connectivity:"
        if ping -c 1 -W 2 8.8.8.8 &>/dev/null; then
            echo "  ✓ Reachable"
        else
            echo "  ✗ Unreachable"
        fi
        echo ""
        ;;
    
    *)
        echo "Usage: $0 [up|down|restart|status]"
        echo ""
        echo "Commands:"
        echo "  up       - Reconnect tether"
        echo "  down     - Disconnect tether"
        echo "  restart  - Restart NetworkManager and reconnect"
        echo "  status   - Show current status"
        echo ""
        exit 1
        ;;
esac
