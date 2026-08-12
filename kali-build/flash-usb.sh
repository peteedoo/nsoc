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

# Resolve every *physical* disk that ultimately backs a given mountpoint,
# walking through any LVM / LUKS / RAID / btrfs mapper layers. `lsblk -s`
# inverts the tree so a mapper device's rows include its parent disks; we
# keep only TYPE==disk. This is far stronger than checking PKNAME once,
# which returns the mapper's immediate parent, not the real disk.
backing_disks() {
    mnt="$1"
    src="$(findmnt -n -o SOURCE "$mnt" 2>/dev/null || true)"
    [ -n "$src" ] || return 0
    lsblk -s -nrpo NAME,TYPE "$src" 2>/dev/null | awk '$2=="disk"{print $1}'
}

# Refuse if the target disk backs any critical running-system filesystem,
# resolving through mapper layers so LVM/LUKS/RAID roots are caught too.
for critical in / /boot /boot/efi /home /var /usr; do
    for disk in $(backing_disks "$critical"); do
        if [ "$disk" = "$DEV" ] || [ "$(basename "$disk")" = "$DEV_BASE" ]; then
            die "$DEV backs the running system's $critical filesystem. Refusing."
        fi
    done
done

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
