#!/usr/bin/env bash
#
# build.sh - Build a custom, USB-bootable Kali Linux ISO with NSOC baked in.
#
# This wraps Kali's official live-build framework. It clones (or reuses)
# kali/build-scripts/live-build-config, layers the NSOC customizations from
# this directory's ./config tree on top of kali-config/common, stages the
# NSOC source into the image, and runs the build.
#
# Output: a hybrid ISO (works for both DVD and `dd` to USB) under ./images/
#
# Usage:
#   sudo ./build.sh                       # default: xfce desktop
#   sudo ./build.sh --variant gnome
#   sudo ./build.sh --arch amd64 --variant xfce
#   sudo ./build.sh --clean               # wipe the live-build workspace first
#
# Requirements (Debian/Kali host): live-build, debootstrap, git, rsync,
# and ~25 GB free disk. Run as root (live-build needs it).
#
set -euo pipefail

# --------------------------------------------------------------------------
# Configuration / argument parsing
# --------------------------------------------------------------------------
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"

VARIANT="xfce"                 # kali desktop flavour (xfce|gnome|kde|...)
ARCH="$(dpkg --print-architecture 2>/dev/null || echo amd64)"
DISTRIBUTION="kali-rolling"
LBC_REPO="https://gitlab.com/kali/build-scripts/live-build-config.git"
LBC_DIR="$HERE/live-build-config"
DO_CLEAN=0

while [ $# -gt 0 ]; do
    case "$1" in
        --variant)  VARIANT="$2"; shift 2 ;;
        --arch)     ARCH="$2"; shift 2 ;;
        --distribution) DISTRIBUTION="$2"; shift 2 ;;
        --clean)    DO_CLEAN=1; shift ;;
        -h|--help)
            # Print the contiguous leading comment block (skip the shebang).
            awk 'NR==1{next} /^#/{sub(/^# ?/,""); print; next} {exit}' "$0"
            exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 2 ;;
    esac
done

log()  { printf '\033[1;32m[build]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[build]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[build]\033[0m %s\n' "$*" >&2; exit 1; }

# --------------------------------------------------------------------------
# Preflight
# --------------------------------------------------------------------------
[ "$(id -u)" -eq 0 ] || die "Run as root (sudo $0 ...). live-build needs root."

log "Checking host dependencies"
missing=""
for cmd in lb debootstrap git rsync; do
    command -v "$cmd" >/dev/null 2>&1 || missing="$missing $cmd"
done
if [ -n "$missing" ]; then
    warn "Missing:$missing"
    log "Installing build dependencies via apt-get"
    apt-get update
    apt-get install -y live-build debootstrap git rsync || \
        die "Could not install build dependencies. Install them manually:$missing"
fi

# --------------------------------------------------------------------------
# Obtain Kali's live-build-config base
# --------------------------------------------------------------------------
if [ "$DO_CLEAN" -eq 1 ] && [ -d "$LBC_DIR" ]; then
    log "Cleaning previous live-build workspace"
    ( cd "$LBC_DIR" && ./build.sh --clean >/dev/null 2>&1 || true )
    rm -rf "$LBC_DIR/.build" "$LBC_DIR/kali-config/common/includes.chroot/opt/nsoc"
fi

if [ ! -d "$LBC_DIR/.git" ]; then
    log "Cloning Kali live-build-config"
    git clone --depth 1 "$LBC_REPO" "$LBC_DIR"
else
    log "Reusing existing live-build-config at $LBC_DIR"
fi

COMMON="$LBC_DIR/kali-config/common"
[ -d "$COMMON" ] || die "Unexpected live-build-config layout: $COMMON not found"

# --------------------------------------------------------------------------
# Layer NSOC customizations onto kali-config/common
# --------------------------------------------------------------------------
log "Applying NSOC customizations (package lists, hooks, includes)"
mkdir -p "$COMMON/package-lists" "$COMMON/hooks/live" "$COMMON/includes.chroot"

rsync -a "$HERE/config/package-lists/"  "$COMMON/package-lists/"
rsync -a "$HERE/config/hooks/live/"     "$COMMON/hooks/live/"
rsync -a "$HERE/config/includes.chroot/" "$COMMON/includes.chroot/"
chmod 0755 "$COMMON/hooks/live/"*.chroot 2>/dev/null || true

# --------------------------------------------------------------------------
# Stage the NSOC source tree into the image at /opt/nsoc
# --------------------------------------------------------------------------
log "Staging NSOC source into the image (/opt/nsoc)"
NSOC_DEST="$COMMON/includes.chroot/opt/nsoc"
rm -rf "$NSOC_DEST"
mkdir -p "$NSOC_DEST"
rsync -a --delete \
    --exclude '.git' \
    --exclude 'kali-build' \
    --exclude 'node_modules' \
    --exclude 'dashboard/dist' \
    "$REPO_ROOT"/ "$NSOC_DEST"/

# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------
log "Building Kali ISO  (variant=$VARIANT arch=$ARCH dist=$DISTRIBUTION)"
log "This downloads packages and can take 30-90 minutes."

(
    cd "$LBC_DIR"
    ./build.sh --variant "$VARIANT" --arch "$ARCH" --distribution "$DISTRIBUTION" --verbose
)

# --------------------------------------------------------------------------
# Collect output
# --------------------------------------------------------------------------
mkdir -p "$HERE/images"
shopt -s nullglob
produced=0
for iso in "$LBC_DIR/images/"*.iso "$LBC_DIR"/*.iso; do
    cp -f "$iso" "$HERE/images/"
    log "ISO ready: $HERE/images/$(basename "$iso")"
    produced=1
done

if [ "$produced" -eq 0 ]; then
    warn "Build finished but no ISO was found under $LBC_DIR/images/."
    warn "Check the live-build log above for errors."
    exit 1
fi

log "Done. Flash to a USB stick with:  sudo ./flash-usb.sh images/<file>.iso /dev/sdX"
