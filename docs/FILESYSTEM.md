# Zero Kernel Filesystem Design

**Status:** Proposed architecture — not yet implemented.

## Goals

Zero Kernel will provide a native filesystem and a Virtual Filesystem (VFS) layer so the shell and applications can access files through a consistent interface.

The initial target is a small, testable filesystem for QEMU virtual disks. Linux filesystem compatibility is a later milestone, not a current capability.

## Architecture

```text
Zero Shell / Applications
          |
          v
 Virtual Filesystem (VFS)
       /       \
      v         v
   ZeroFS      ext2 (future)
      \         /
       v       v
     Block-device layer
            |
            v
      Storage driver
```

## Planned VFS interface

The first VFS API is expected to provide equivalents of:

- `vfs_mount()`
- `vfs_open()`
- `vfs_read()`
- `vfs_write()`
- `vfs_close()`
- `vfs_readdir()`
- `vfs_mkdir()`
- `vfs_unlink()`

Exact signatures will be defined alongside the implementation.

## ZeroFS on-disk format

The initial ZeroFS format is expected to use fixed-size blocks and contain:

| Structure | Purpose |
|---|---|
| Superblock | Filesystem identity, version, block size, total blocks |
| Allocation bitmap | Tracks free and allocated blocks |
| Inode table | File type, size, timestamps, and data-block references |
| Directory entries | Maps names to inode numbers |
| Data blocks | Stores file and directory contents |

The format must include magic bytes and a version field so future versions can reject incompatible images safely.

## Initial filesystem layout

The root filesystem will use a familiar Unix-style directory layout:

```text
/
├── bin/
├── boot/
├── dev/
├── etc/
├── home/
├── lib/
├── opt/
├── root/
├── tmp/
├── usr/
│   ├── bin/
│   ├── lib/
│   └── share/
└── var/
    ├── cache/
    ├── lib/
    └── log/
```

Directories will be added as the corresponding kernel services become available.

## Implementation milestones

1. Define and document the ZeroFS disk format.
2. Implement a host-side image creation and inspection utility.
3. Implement a block-device abstraction and QEMU storage driver.
4. Mount ZeroFS and support directory listing.
5. Add file creation, reading, writing, and deletion.
6. Connect shell commands such as `ls`, `cd`, `pwd`, `mkdir`, `touch`, and `cat`.
7. Add filesystem consistency checks and recovery tests.
8. Consider ext2 compatibility after the native filesystem is stable.

## Compatibility notes

- ZeroFS is a proposed native format; it is not ext4.
- ext2 support is a future compatibility target.
- ext4 support is not currently planned for the first filesystem milestone because its feature set adds substantial complexity.
- A VFS does not itself provide storage access; a working block-device driver is also required.

## Safety and testing

Filesystem development should begin with disposable QEMU disk images, not physical disks. Test malformed images, out-of-range block numbers, full disks, truncated files, and interrupted writes. Never mount an untrusted filesystem image with write access during early development.
