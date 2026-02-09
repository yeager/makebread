#!/bin/bash
set -euo pipefail

SRCDIR="$(cd "$(dirname "$0")/.." && pwd)"
PKG="makebread"
VER="0.3.0"
SSH_PASS=$(security find-generic-password -s "ssh-192.168.2.2" -w)
SERVER="yeager@192.168.2.2"

echo "Building ${PKG}-${VER} RPM on server..."

# Create tarball
TMPDIR=$(mktemp -d)
mkdir -p "$TMPDIR/${PKG}-${VER}"
cp -r "$SRCDIR/makebread" "$SRCDIR/data" "$SRCDIR/man" "$SRCDIR/debian" "$SRCDIR/pyproject.toml" "$TMPDIR/${PKG}-${VER}/"
find "$TMPDIR" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find "$TMPDIR" -name "*.pyc" -delete 2>/dev/null || true
tar -czf "$TMPDIR/${PKG}-${VER}.tar.gz" -C "$TMPDIR" "${PKG}-${VER}"

# Upload
sshpass -p "$SSH_PASS" ssh "$SERVER" "mkdir -p ~/rpmbuild/{SOURCES,SPECS,RPMS,BUILD,SRPMS}"
sshpass -p "$SSH_PASS" scp "$TMPDIR/${PKG}-${VER}.tar.gz" "$SERVER:~/rpmbuild/SOURCES/"
sshpass -p "$SSH_PASS" scp "$SRCDIR/scripts/${PKG}.spec" "$SERVER:~/rpmbuild/SPECS/"

# Build
sshpass -p "$SSH_PASS" ssh "$SERVER" "rpmbuild -bb ~/rpmbuild/SPECS/${PKG}.spec"

# Download
mkdir -p "$SRCDIR/dist"
sshpass -p "$SSH_PASS" scp "$SERVER:~/rpmbuild/RPMS/noarch/${PKG}-${VER}-1*.noarch.rpm" "$SRCDIR/dist/"

rm -rf "$TMPDIR"
echo "Built: $SRCDIR/dist/${PKG}-${VER}-1.noarch.rpm"
