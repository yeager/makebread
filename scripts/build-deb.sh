#!/bin/bash
set -euo pipefail

SRCDIR="$(cd "$(dirname "$0")/.." && pwd)"
VER="0.3.0"
PKG="makebread"
DEST="/tmp/${PKG}_${VER}_build"

echo "Building ${PKG} ${VER}..."

rm -rf "$DEST"
mkdir -p "$DEST/DEBIAN"
mkdir -p "$DEST/usr/bin"
mkdir -p "$DEST/usr/lib/python3/dist-packages"
mkdir -p "$DEST/usr/share/applications"
mkdir -p "$DEST/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$DEST/usr/share/doc/$PKG"
mkdir -p "$DEST/usr/share/man/man1"
mkdir -p "$DEST/usr/share/metainfo"

# Control file
cat > "$DEST/DEBIAN/control" <<EOF
Package: $PKG
Version: $VER
Section: utils
Priority: optional
Architecture: all
Depends: python3 (>= 3.10)
Recommends: python3-pyside6
Maintainer: Daniel Nylander <daniel@danielnylander.se>
Homepage: https://github.com/yeager/makebread
Description: A simple bread machine recipe manager
 A PySide6/Qt6 application for managing bread machine recipes with
 import/export, timer presets, ingredient scaling, and recipe cards.
 PySide6 must be installed via pip: pip install PySide6
EOF

# postinst / prerm
install -m 755 "$SRCDIR/debian/postinst" "$DEST/DEBIAN/postinst"
install -m 755 "$SRCDIR/debian/prerm" "$DEST/DEBIAN/prerm"

# Binary
cat > "$DEST/usr/bin/makebread" <<'LAUNCHER'
#!/usr/bin/python3
from makebread.__main__ import main
main()
LAUNCHER
chmod 755 "$DEST/usr/bin/makebread"

# Python package
cp -r "$SRCDIR/makebread" "$DEST/usr/lib/python3/dist-packages/"

# Remove __pycache__
find "$DEST" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Desktop file
install -m 644 "$SRCDIR/data/io.github.yeager.makebread.desktop" "$DEST/usr/share/applications/"

# Metainfo
if [ -f "$SRCDIR/data/io.github.yeager.makebread.metainfo.xml" ]; then
    install -m 644 "$SRCDIR/data/io.github.yeager.makebread.metainfo.xml" "$DEST/usr/share/metainfo/"
fi

# Icon (create a placeholder SVG if none exists)
if [ -f "$SRCDIR/data/icons/io.github.yeager.makebread.svg" ]; then
    install -m 644 "$SRCDIR/data/icons/io.github.yeager.makebread.svg" "$DEST/usr/share/icons/hicolor/scalable/apps/"
else
    cat > "$DEST/usr/share/icons/hicolor/scalable/apps/io.github.yeager.makebread.svg" <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="8" fill="#D4A574"/><text x="24" y="32" text-anchor="middle" font-size="24">🍞</text></svg>
SVG
fi

# Copyright (DEP-5)
install -m 644 "$SRCDIR/debian/copyright" "$DEST/usr/share/doc/$PKG/copyright"

# Changelog
gzip -9cn "$SRCDIR/debian/changelog" > "$DEST/usr/share/doc/$PKG/changelog.Debian.gz"

# Man page
gzip -9cn "$SRCDIR/man/makebread.1" > "$DEST/usr/share/man/man1/makebread.1.gz"

# Build
OUTPUT="/tmp/${PKG}_${VER}_all.deb"
dpkg-deb --root-owner-group --build "$DEST" "$OUTPUT"

echo "Built: $OUTPUT"
echo "Size: $(du -h "$OUTPUT" | cut -f1)"

# Verify
echo ""
echo "=== Lintian-style checks ==="
echo -n "copyright: "; [ -f "$DEST/usr/share/doc/$PKG/copyright" ] && echo "OK" || echo "MISSING"
echo -n "changelog: "; [ -f "$DEST/usr/share/doc/$PKG/changelog.Debian.gz" ] && echo "OK" || echo "MISSING"
echo -n "manpage: "; [ -f "$DEST/usr/share/man/man1/makebread.1.gz" ] && echo "OK" || echo "MISSING"
echo -n "__pycache__: "; find "$DEST" -name __pycache__ -type d | grep -q . && echo "FOUND (BAD)" || echo "clean"
echo -n "postinst: "; [ -f "$DEST/DEBIAN/postinst" ] && echo "OK" || echo "MISSING"

rm -rf "$DEST"
