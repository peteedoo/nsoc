# NSOC — Custom Bootable Kali Linux

Build a **USB-bootable, custom Kali Linux** image with the
[NSOC](../README.md) platform and its security tooling baked in. The result
is a live system you can boot on any machine to run NSOC workflows from a USB
stick — no installation required.

This directory layers NSOC on top of Kali's **official `live-build`
framework**, so the image is a genuine Kali Linux build (correct repos,
keyring, kernel, and bootloader) with our packages, files, and the NSOC
source tree added on top.

```
kali-build/
├── build.sh                         # build the ISO (wraps Kali live-build)
├── flash-usb.sh                     # write the ISO to a USB stick safely
├── config/
│   ├── package-lists/
│   │   └── nsoc.list.chroot         # extra packages (nmap, sqlmap, …, nodejs)
│   ├── hooks/live/
│   │   └── 0100-nsoc-setup.chroot   # in-image setup (banner, deps, build)
│   └── includes.chroot/             # files copied verbatim into the image
│       ├── usr/local/bin/nsoc       #   `nsoc` launcher on PATH
│       ├── usr/share/applications/  #   app-menu entry
│       └── etc/skel/Desktop/        #   desktop shortcut for the live user
└── images/                          # built ISOs land here
```

## Requirements

- A **Debian or Kali Linux host** (live-build only runs on Debian-family).
- Root privileges (`sudo`).
- ~25 GB free disk and a reasonably fast internet connection.
- Packages (the build script installs these for you if missing):
  `live-build debootstrap git rsync`.

> Building a Kali image is not supported on macOS/Windows directly. Use a
> Kali/Debian VM or container with the loop device available.

## Build

```bash
cd kali-build
sudo ./build.sh                 # default: XFCE desktop, host architecture
```

Useful flags:

```bash
sudo ./build.sh --variant gnome         # gnome | kde | xfce | …
sudo ./build.sh --arch amd64            # amd64 | arm64
sudo ./build.sh --clean                 # wipe the workspace and rebuild
```

The first run clones Kali's `live-build-config`, applies the NSOC overlay,
stages the NSOC source into `/opt/nsoc` inside the image, then runs the
build (30–90 min). The finished ISO is copied to `kali-build/images/`.

## Write to USB

The ISO is an isohybrid image, so a block copy makes it bootable.

```bash
sudo ./flash-usb.sh images/<your-image>.iso /dev/sdX
```

Run it with no device to list candidate disks. The script refuses
partitions and the host's system disk, and requires you to type
`ERASE sdX` to confirm. **This erases the whole target device.**

> Prefer a GUI? [balenaEtcher](https://etcher.balena.io/) writes the same
> ISO on any OS.

## Boot it

1. Insert the USB stick and boot the target machine from it (adjust the
   BIOS/UEFI boot order or use the one-time boot menu).
2. Pick **Live** from the Kali boot menu.
3. You'll see the NSOC banner. Launch the platform:

   ```bash
   nsoc                       # interactive
   nsoc workflow list         # list workflows
   nsoc workflow run network-map --target 192.168.1.0/24
   ```

   NSOC lives at `/opt/nsoc`. An **NSOC** entry is also in the application
   menu and on the desktop.

### Persistence (optional)

A plain live boot is stateless. To keep scans, settings, and files across
reboots, create a USB persistence partition labelled `persistence`:

```bash
# After flashing, with free space remaining on the stick (e.g. /dev/sdX3):
sudo mkfs.ext4 -L persistence /dev/sdX3
sudo mkdir -p /mnt/p && sudo mount /dev/sdX3 /mnt/p
echo "/ union" | sudo tee /mnt/p/persistence.conf
sudo umount /mnt/p
```

Then choose **Live USB Persistence** at the Kali boot menu.

## Customizing

- **Add/remove tools** → edit `config/package-lists/nsoc.list.chroot`.
- **Change in-image setup** → edit `config/hooks/live/0100-nsoc-setup.chroot`.
- **Ship extra files** → drop them under `config/includes.chroot/` mirroring
  the target filesystem layout.

Re-run `sudo ./build.sh` after any change. Use `--clean` if you change
package lists and want a fully fresh chroot.

## Responsible use

This image bundles offensive security tools. **SIMULATION is NSOC's default
mode.** Only enable LIVE mode against systems you are explicitly authorized
to test. You are responsible for complying with all applicable laws and
engagement rules.
