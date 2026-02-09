Name:           makebread
Version:        0.3.0
Release:        1%{?dist}
Summary:        Bread machine recipe manager
License:        GPL-3.0-or-later
URL:            https://github.com/yeager/makebread
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       python3 >= 3.10

%description
A PySide6/Qt6 application for managing bread machine recipes.
Supports storing, editing, and printing recipes.

%prep
%setup -q

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/lib/python3/dist-packages
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/icons/hicolor/scalable/apps
mkdir -p %{buildroot}/usr/share/doc/%{name}
mkdir -p %{buildroot}/usr/share/man/man1
mkdir -p %{buildroot}/usr/share/%{name}
mkdir -p %{buildroot}/usr/share/metainfo

cat > %{buildroot}/usr/bin/makebread <<'BINEOF'
#!/usr/bin/python3
import sys
from makebread.__main__ import main
sys.exit(main())
BINEOF
chmod 755 %{buildroot}/usr/bin/makebread

cp -r makebread %{buildroot}/usr/lib/python3/dist-packages/
find %{buildroot} -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find %{buildroot} -name "*.pyc" -delete 2>/dev/null || true

install -m 644 data/io.github.yeager.makebread.desktop %{buildroot}/usr/share/applications/
install -m 644 data/io.github.yeager.makebread.svg %{buildroot}/usr/share/icons/hicolor/scalable/apps/
install -m 644 data/io.github.yeager.makebread.metainfo.xml %{buildroot}/usr/share/metainfo/
install -m 644 data/seed_recipes.json %{buildroot}/usr/share/%{name}/
install -m 644 debian/copyright %{buildroot}/usr/share/doc/%{name}/copyright
gzip -9c man/makebread.1 > %{buildroot}/usr/share/man/man1/makebread.1.gz

%files
/usr/bin/makebread
/usr/lib/python3/dist-packages/makebread/
/usr/share/applications/io.github.yeager.makebread.desktop
/usr/share/icons/hicolor/scalable/apps/io.github.yeager.makebread.svg
/usr/share/metainfo/io.github.yeager.makebread.metainfo.xml
/usr/share/%{name}/seed_recipes.json
%doc /usr/share/doc/%{name}/copyright
/usr/share/man/man1/makebread.1.gz
