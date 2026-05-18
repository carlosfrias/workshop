#!/bin/bash
#
# extract-hardware-specs.sh
# Extracts hardware specs for Ollama capacity planning.
# Cross-platform: Linux and macOS. Pure bash, no jq dependency.
# Outputs JSON to stdout.
#
# Usage: ./extract-hardware-specs.sh [--save]

set -eo pipefail

HOSTNAME=$(uname -n)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Detect OS family
OS_FAMILY="linux"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_FAMILY="macos"
fi

# --- System ---
OS=$(uname -o 2>/dev/null || echo "unknown")
KERNEL=$(uname -r)
ARCH=$(uname -m)

# --- Distribution/OS Details ---
DIST_NAME=""
DIST_VERSION=""
DIST_CODENAME=""
DIST_ID=""

if [ "$OS_FAMILY" = "linux" ] && [ -f /etc/os-release ]; then
    DIST_NAME=$(grep '^PRETTY_NAME=' /etc/os-release | cut -d'"' -f2 || echo "")
    DIST_VERSION=$(grep '^VERSION_ID=' /etc/os-release | cut -d'"' -f2 || echo "")
    DIST_CODENAME=$(grep '^VERSION_CODENAME=' /etc/os-release | cut -d'=' -f2 || echo "")
    DIST_ID=$(grep '^ID=' /etc/os-release | cut -d'=' -f2 | tr -d '\"' || echo "")
elif [ "$OS_FAMILY" = "macos" ]; then
    DIST_NAME=$(sw_vers -productName 2>/dev/null || echo "macOS")
    DIST_VERSION=$(sw_vers -productVersion 2>/dev/null || echo "")
    DIST_CODENAME=$(sw_vers -buildVersion 2>/dev/null || echo "")
    DIST_ID="macos"
fi

# --- CPU ---
CPU_MODEL="unknown"
CPU_CORES=0
CPU_FLAGS="[]"

if [ "$OS_FAMILY" = "linux" ] && [ -f /proc/cpuinfo ]; then
    CPU_MODEL=$(grep 'model name' /proc/cpuinfo | head -1 | cut -d':' -f2 | sed 's/^[ \t]*//' || echo "unknown")
    CPU_CORES=$(nproc 2>/dev/null || grep -c '^processor' /proc/cpuinfo || echo 0)
    FLAGS_RAW=""
    if grep -q 'avx512' /proc/cpuinfo 2>/dev/null; then FLAGS_RAW="\"avx512\""; fi
    if grep -q 'avx2' /proc/cpuinfo 2>/dev/null; then
        [ -n "$FLAGS_RAW" ] && FLAGS_RAW="$FLAGS_RAW, "
        FLAGS_RAW="${FLAGS_RAW}\"avx2\""
    fi
    CPU_FLAGS="[$FLAGS_RAW]"
else
    CPU_MODEL=$(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "unknown")
    CPU_CORES=$(sysctl -n hw.ncpu 2>/dev/null || echo 0)
fi

# --- Memory ---
TOTAL_RAM_GB=0
AVAILABLE_RAM_GB=0
SWAP_TOTAL_GB=0

if [ "$OS_FAMILY" = "linux" ] && command -v free &>/dev/null; then
    MEM_KB=$(free | awk '/^Mem:/{print $2}')
    AVAIL_KB=$(free | awk '/^Mem:/{print $7}')
    SWAP_KB=$(free | awk '/^Swap:/{print $2}')
    TOTAL_RAM_GB=$((MEM_KB / 1024 / 1024))
    AVAILABLE_RAM_GB=$((AVAIL_KB / 1024 / 1024))
    SWAP_TOTAL_GB=$((SWAP_KB / 1024 / 1024))
else
    MEM_BYTES=$(sysctl -n hw.memsize 2>/dev/null || echo 0)
    TOTAL_RAM_GB=$((MEM_BYTES / 1024 / 1024 / 1024))
    AVAILABLE_RAM_GB=$TOTAL_RAM_GB
    if command -v sysctl &>/dev/null; then
        SWAP_RAW=$(sysctl vm.swapusage 2>/dev/null | grep -o 'total = [0-9.]*[MG]' | awk '{print $3}')
        if [ -n "$SWAP_RAW" ]; then
            if [[ "$SWAP_RAW" == *M* ]]; then
                SWAP_TOTAL_GB=$(echo "$SWAP_RAW" | sed 's/M//' | awk '{printf "%d", $1/1024}')
            elif [[ "$SWAP_RAW" == *G* ]]; then
                SWAP_TOTAL_GB=$(echo "$SWAP_RAW" | sed 's/G//')
            fi
        fi
    fi
fi

# --- GPU ---
GPU_DETECTED="false"
GPU_MODEL="none"
GPU_VRAM_GB=0
GPU_DRIVER=""

if command -v nvidia-smi &>/dev/null && nvidia-smi &>/dev/null 2>&1; then
    GPU_DETECTED="true"
    GPU_MODEL=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1 | sed 's/^[ \t]*//' || echo "NVIDIA GPU")
    GPU_VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 || echo 0)
    if [[ "$GPU_VRAM_MB" =~ ^[0-9]+$ ]]; then
        GPU_VRAM_GB=$((GPU_VRAM_MB / 1024))
    else
        GPU_VRAM_GB=0
    fi
    GPU_DRIVER=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1 || echo "")
elif command -v lspci &>/dev/null; then
    GPU_LINE=$(lspci 2>/dev/null | grep -iE 'vga|3d|display' | head -1)
    if [ -n "$GPU_LINE" ]; then
        GPU_DETECTED="true"
        GPU_MODEL=$(echo "$GPU_LINE" | cut -d':' -f3 | sed 's/^[ \t]*//')
    fi
fi

# --- Storage ---
DISK_TOTAL_GB=0
DISK_FREE_GB=0
OLLAMA_DIR="$HOME/.ollama"
[ -d "/usr/share/ollama" ] && OLLAMA_DIR="/usr/share/ollama"
OLLAMA_DIR_EXISTS="false"
OLLAMA_DIR_SIZE_GB=0

if command -v df &>/dev/null; then
    if [ "$OS_FAMILY" = "linux" ]; then
        DISK_INFO=$(df -BG / 2>/dev/null | tail -1)
        DISK_TOTAL_GB=$(echo "$DISK_INFO" | awk '{print $2}' | tr -d 'G' || echo 0)
        DISK_FREE_GB=$(echo "$DISK_INFO" | awk '{print $4}' | tr -d 'G' || echo 0)
    else
        DISK_INFO=$(df -g / 2>/dev/null | tail -1)
        # macOS df -g outputs sizes in 1G blocks directly
        DISK_TOTAL_GB=$(echo "$DISK_INFO" | awk '{print $2}' || echo 0)
        DISK_FREE_GB=$(echo "$DISK_INFO" | awk '{print $4}' || echo 0)
    fi
fi

if [ -d "$OLLAMA_DIR" ]; then
    OLLAMA_DIR_EXISTS="true"
    if command -v du &>/dev/null; then
        # Run du independently — pipefail can abort if inaccessible subdirs exist
        SIZE_KB=$(du -sk "$OLLAMA_DIR" 2>/dev/null | awk '{print $1}')
        SIZE_KB=${SIZE_KB:-0}
        if [[ "$SIZE_KB" =~ ^[0-9]+$ ]]; then
            OLLAMA_DIR_SIZE_GB=$((SIZE_KB / 1024 / 1024))
        else
            OLLAMA_DIR_SIZE_GB=0
        fi
    fi
fi

# --- Block Devices (LVM-aware) ---
STORAGE_DISKS="[]"
STORAGE_FILESYSTEMS="[]"

if command -v lsblk >/dev/null 2>&1 && command -v python3 >/dev/null 2>&1; then
    STORAGE_DISKS=$(lsblk -Jo NAME,SIZE,TYPE 2>/dev/null | python3 -c '
import json, sys
def flatten(devs):
    for d in devs:
        yield d
        yield from flatten(d.get("children", []))
data = json.load(sys.stdin)
entries = [{"name": d["name"], "size": d.get("size", "")} for d in flatten(data.get("blockdevices", [])) if d.get("type") == "disk"]
print(json.dumps(entries))
' || echo "[]")

    STORAGE_FILESYSTEMS=$(lsblk -Jo NAME,SIZE,FSTYPE,MOUNTPOINT,TYPE 2>/dev/null | python3 -c '
import json, sys
def flatten(devs):
    for d in devs:
        yield d
        yield from flatten(d.get("children", []))
data = json.load(sys.stdin)
entries = []
for d in flatten(data.get("blockdevices", [])):
    t = d.get("type", "")
    mount = d.get("mountpoint")
    if mount and t in ("lvm", "part"):
        entries.append({"name": d["name"], "size": d.get("size", ""), "fstype": d.get("fstype", ""), "mountpoint": mount, "type": t})
print(json.dumps(entries))
' || echo "[]")
fi

# --- Primary IP Address ---
PRIMARY_IP=""
if [ "$OS_FAMILY" = "linux" ] && command -v hostname &>/dev/null; then
    PRIMARY_IP=$(hostname -I 2>/dev/null | awk '{print $1}' | xargs || echo "")
elif [ "$OS_FAMILY" = "macos" ]; then
    PRIMARY_IP=$(ifconfig 2>/dev/null | grep -E "inet [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" | grep -v "127.0.0.1" | head -1 | awk '{print $2}' | xargs || echo "")
fi

# --- Network ---
OLLAMA_REACHABLE="false"
DOWNLOAD_SPEED_MBPS=0
LATENCY_MS=0

if command -v curl &>/dev/null; then
    if curl -fsSL -o /dev/null --max-time 10 "https://ollama.com" 2>/dev/null; then
        OLLAMA_REACHABLE="true"
    fi
fi

if command -v ping &>/dev/null; then
    LATENCY_RAW=$( (ping -c 1 -W 2 ollama.com 2>/dev/null | grep 'time=' | head -1 | sed -n 's/.*time=\([0-9.]*\).*/\1/p') || true )
    LATENCY_MS=${LATENCY_RAW:-0}
fi

# Speed test: download first 5MB of a known test file.
if [ "$OLLAMA_REACHABLE" = "true" ] && command -v curl &>/dev/null; then
    TEMP_DL=$(mktemp)
    START_TIME_S=$(date +%s)
    # Use a well-known test file that supports ranges (OpenSpeedTest or similar)
    # If range fails, we just measure what we got in max 30s.
    curl -fsSL -o "$TEMP_DL" -r 0-5242880 --max-time 30 "https://ollama.com/download/ollama-linux-amd64.tgz" 2>/dev/null || true
    END_TIME_S=$(date +%s)

    DL_SIZE=0
    if [ "$OS_FAMILY" = "linux" ]; then
        DL_SIZE=$(stat -c%s "$TEMP_DL" 2>/dev/null || echo 0)
    else
        DL_SIZE=$(stat -f%z "$TEMP_DL" 2>/dev/null || echo 0)
    fi
    rm -f "$TEMP_DL"

    if [ "$DL_SIZE" -gt 0 ]; then
        DURATION=$((END_TIME_S - START_TIME_S))
        if [ "$DURATION" -gt 0 ]; then
            # Mbps = (bytes * 8) / (seconds * 1024 * 1024)
            DOWNLOAD_SPEED_MBPS=$(awk "BEGIN {printf \"%.2f\", ($DL_SIZE * 8) / ($DURATION * 1024 * 1024)}")
        fi
    fi
fi

# --- Ollama State ---
OLLAMA_INSTALLED="false"
OLLAMA_VERSION=""
OLLAMA_SERVICE_ACTIVE="false"
EXISTING_MODELS="[]"

if command -v ollama &>/dev/null; then
    OLLAMA_INSTALLED="true"
    OLLAMA_VERSION=$(ollama --version 2>/dev/null | awk '{print $NF}' || echo "unknown")
fi

if [ "$OS_FAMILY" = "linux" ] && command -v systemctl &>/dev/null; then
    if systemctl is-active --quiet ollama 2>/dev/null; then
        OLLAMA_SERVICE_ACTIVE="true"
    fi
elif [ "$OS_FAMILY" = "macos" ]; then
    if pgrep -x "Ollama" >/dev/null 2>&1; then
        OLLAMA_SERVICE_ACTIVE="true"
    fi
fi

if [ "$OLLAMA_INSTALLED" = "true" ]; then
    MODELS_LIST=""
    while IFS= read -r line; do
        model=$(echo "$line" | awk '{print $1}')
        [ -z "$model" ] && continue
        [ -n "$MODELS_LIST" ] && MODELS_LIST="$MODELS_LIST, "
        MODELS_LIST="${MODELS_LIST}\"$model\""
    done <<< "$(ollama list 2>/dev/null | tail -n +2 || true)"
    EXISTING_MODELS="[$MODELS_LIST]"
fi

# --- Output ---
cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "node": "$HOSTNAME",
  "system": {
    "hostname": "$HOSTNAME",
    "os": "$OS",
    "kernel": "$KERNEL",
    "arch": "$ARCH",
    "dist_name": "$DIST_NAME",
    "dist_version": "$DIST_VERSION",
    "dist_codename": "$DIST_CODENAME",
    "dist_id": "$DIST_ID"
  },
  "cpu": {
    "model": "$CPU_MODEL",
    "cores": $CPU_CORES,
    "flags": $CPU_FLAGS
  },
  "memory": {
    "total_gb": $TOTAL_RAM_GB,
    "available_gb": $AVAILABLE_RAM_GB,
    "swap_total_gb": $SWAP_TOTAL_GB
  },
  "gpu": {
    "detected": $GPU_DETECTED,
    "model": "$GPU_MODEL",
    "vram_gb": $GPU_VRAM_GB,
    "driver": "$GPU_DRIVER"
  },
  "storage": {
    "disks": $STORAGE_DISKS,
    "filesystems": $STORAGE_FILESYSTEMS,
    "total_gb": $DISK_TOTAL_GB,
    "free_gb": $DISK_FREE_GB,
    "ollama_dir_exists": $OLLAMA_DIR_EXISTS,
    "ollama_dir_size_gb": $OLLAMA_DIR_SIZE_GB
  },
  "network": {
    "primary_ip": "$PRIMARY_IP",
    "ollama_com_reachable": $OLLAMA_REACHABLE,
    "download_speed_mbps": $DOWNLOAD_SPEED_MBPS,
    "latency_ms": $LATENCY_MS
  },
  "ollama": {
    "installed": $OLLAMA_INSTALLED,
    "version": "$OLLAMA_VERSION",
    "service_active": $OLLAMA_SERVICE_ACTIVE,
    "models": $EXISTING_MODELS
  }
}
EOF
