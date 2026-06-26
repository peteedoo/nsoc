#!/usr/bin/env bash
#
# flash-usb.sh - Write a built ISO to a USB stick (makes it bootable).
#
# Usage:
#   sudo ./flash-usb.sh images/kali-nsoc.iso /dev/sdX
#
# The ISO produced by build.sh is an isohybrid image, so a plain block
# copy is all that is needed to make a bootable USB. THIS ERASES THE
# TARGET DEVICE COMPLETELY.
#
# Safety: refuses to write to a disk that looks like a mounted system
# disk, lists removable disks if no device is given, and requires an
# explicit typed confirmation.
#
set -euo pipefail

log()  { printf '\033[1;32m[flash]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[flash]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[flash]\033[0m %s\n' "$*" >&2; exit 1; }

list_disks() {
    log "Available block devices (look for your removable USB stick):"
    lsblk -d -o NAME,SIZE,TYPE,TRAN,RM,MODEL | awk 'NR==1 || $3=="disk"'
}

[ "$(id -u)" -eq 0 ] || die "Run as root (sudo $0 ...)."

ISO="${1:-}"
DEV="${2:-}"

if [ -z "$ISO" ] || [ -z "$DEV" ]; then
    warn "Usage: sudo $0 <iso-file> <device>"
    echo
    list_disks
    echo
    warn "Example: sudo $0 images/kali-nsoc.iso /dev/sdb"
    exit 2
fi

[ -f "$ISO" ] || die "ISO not found: $ISO"
[ -b "$DEV" ] || die "Not a block device: $DEV"

# --- Safety checks --------------------------------------------------------
# Refuse partitions (we write the whole disk).
case "$DEV" in
    *[0-9]) die "Refusing to write to what looks like a partition ($DEV). Pass the whole disk, e.g. /dev/sdb." ;;
esac

DEV_BASE="$(basename "$DEV")"

# Refuse the disk that hosts the running root filesystem.
ROOT_SRC="$(findmnt -n -o SOURCE / 2>/dev/null || true)"
ROOT_DISK="$(lsblk -no PKNAME "$ROOT_SRC" 2>/dev/null | head -n1 || true)"
if [ -n "$ROOT_DISK" ] && [ "$ROOT_DISK" = "$DEV_BASE" ]; then
    die "$DEV hosts the running system root filesystem. Refusing."
fi

# Warn loudly if the device is not flagged removable.
RM_FLAG="$(lsblk -dno RM "$DEV" 2>/dev/null | head -n1 || echo 0)"
if [ "$RM_FLAG" != "1" ]; then
    warn "WARNING: $DEV is NOT marked as a removable device."
fi

SIZE="$(lsblk -dno SIZE "$DEV" 2>/dev/null || echo '?')"
MODEL="$(lsblk -dno MODEL "$DEV" 2>/dev/null || echo '?')"

echo
warn "================= DESTRUCTIVE OPERATION ================="
warn " Target : $DEV  ($SIZE, $MODEL)"
warn " Source : $ISO"
warn " ALL DATA on $DEV will be PERMANENTLY ERASED."
warn "========================================================"
echo
printf "Type 'ERASE %s' to continue: " "$DEV_BASE"
read -r confirm
[ "$confirm" = "ERASE $DEV_BASE" ] || die "Confirmation did not match. Aborted."

# --- Unmount any mounted partitions of the target -------------------------
log "Unmounting any mounted partitions on $DEV"
for part in $(lsblk -ln -o NAME "$DEV" | tail -n +2); do
    umount "/dev/$part" 2>/dev/null || true
done

# --- Write ----------------------------------------------------------------
log "Writing image (this can take several minutes)..."
dd if="$ISO" of="$DEV" bs=4M conv=fsync oflag=direct status=progress

log "Flushing buffers"
sync

log "Done. You can now boot $DEV. (Eject before removing.)"
