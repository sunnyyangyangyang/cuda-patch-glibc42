#
# spec file for cuda-glibc-patch (Final, Robust Patch-based Version)
#

Name:           cuda-glibc-patch
Version:        1.0
Release:        2%{?dist}
Summary:        Applies a patch to NVIDIA CUDA Toolkit for modern glibc compatibility

License:        MIT AND 0BSD
URL:            https://gitlab.archlinux.org/archlinux/packaging/packages/cuda
Source0:        https://gitlab.archlinux.org/archlinux/packaging/packages/cuda/-/raw/main/fix-glibc242.patch



AutoReqProv:    no
Requires:       cuda-crt-13-0
Requires:       patch

%global cuda_version 13.1
%global target_file /usr/local/cuda-%{cuda_version}/targets/x86_64-linux/include/crt/math_functions.h
%global backup_file %{target_file}.glibc-patch.backup

%description
This RPM applies a community-vetted patch to the math_functions.h header file
provided by the NVIDIA CUDA Toolkit (specifically, the cuda-crt-13-0 package).
This patch is necessary for compiling CUDA applications on systems with modern
versions of glibc (e.g., 2.42+) as found in recent Fedora releases.
This package does not redistribute any NVIDIA proprietary code.
It only applies a community-developed compatibility patch.
Users must have NVIDIA CUDA installed separately.

This package does not distribute any NVIDIA code. The patching process happens
locally on the user's machine. The original file is backed up during
installation and cleanly restored upon uninstallation.

%prep
# No preparation needed

%build
# Nothing to build

%install
mkdir -p %{buildroot}%{_datadir}/%{name}
install -m 0644 %{SOURCE0} %{buildroot}%{_datadir}/%{name}/fix-glibc242.patch

%post
echo "Applying CUDA glibc compatibility patch..."

if [ ! -f "%{target_file}" ]; then
    echo "ERROR: CUDA header '%{target_file}' not found." >&2
    exit 1
fi

if [ ! -f "%{backup_file}" ]; then
    echo "Backing up original file to %{backup_file}"
    /usr/bin/cp -p "%{target_file}" "%{backup_file}"
fi

echo "Patching %{target_file} directly..."
/usr/bin/patch --forward --no-backup-if-mismatch -p1 "%{target_file}" < %{_datadir}/%{name}/fix-glibc242.patch

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to apply patch. Restoring original file." >&2
    /usr/bin/cp -pf "%{backup_file}" "%{target_file}"
    exit 1
fi

echo "CUDA glibc patch applied successfully."
exit 0

%preun
# ... (%preun 部分保持不变) ...
echo "Uninstalling CUDA glibc patch and restoring original file..."

if [ -f "%{backup_file}" ]; then
    echo "Restoring from %{backup_file}..."
    /usr/bin/cp -pf "%{backup_file}" "%{target_file}"
    /usr/bin/rm -f "%{backup_file}"
    echo "Original file restored and backup removed."
else
    echo "WARNING: Backup file '%{backup_file}' not found. Cannot restore." >&2
fi
exit 0

%files
%{_datadir}/%{name}/fix-glibc242.patch

%changelog
* Thu Nov 21 2025 Your Name <yxh9956@gmail.com> - 1.2-2
- Switched to an explicit patch target, which is more robust than cd and guessing.
- Use standard -p1 for git-formatted patches.

* Wed Nov 20 2025 Your Name <yxh9956@gmail.com> - 1.2-1
- (Failed attempt) Corrected patch strip level to -p6.

* Tue Nov 19 2025 Your Name <yxh9956@gmail.com> - 1.1-1
- Added explicit dependency on the 'patch' package.

* Mon Nov 18 2025 Your Name <yxh9956@gmail.com> - 1.0-1
- Initial release for CUDA 13.0 on modern glibc systems