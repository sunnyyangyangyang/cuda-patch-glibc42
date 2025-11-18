#
# spec file for cuda-glibc-patch
#
# This package applies a patch to the NVIDIA CUDA Toolkit's math_functions.h
# to ensure compatibility with modern glibc versions.
# It does NOT contain any proprietary NVIDIA code.
#

Name:           cuda-glibc-patch
Version:        1.2
Release:        1%{?dist}
Summary:        Applies a patch to NVIDIA CUDA Toolkit for modern glibc compatibility

# The spec file is your work (MIT is a good choice).
# The patch itself comes from the Arch Linux community.
License:        MIT AND 0BSD
URL:            https://gitlab.archlinux.org/archlinux/packaging/packages/cuda
Source0:        https://gitlab.archlinux.org/archlinux/packaging/packages/cuda/-/raw/main/fix-glibc242.patch

# We manually specify dependencies, so disable auto-scanning.
AutoReqProv:    no

# This patch is for CUDA 13.0, which depends on this specific CRT package.
# This ensures the patch target file exists.
Requires:       cuda-crt-13-0
Requires:       patch

# By making this a variable, it's easy for others to fork and update for CUDA 13.1, etc.
%global cuda_version 13.0
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
# No preparation needed - we'll use SOURCE0 directly

%build
# Nothing to build

%install
# Install the patch file directly from SOURCE0
mkdir -p %{buildroot}%{_datadir}/%{name}
install -m 0644 %{SOURCE0} %{buildroot}%{_datadir}/%{name}/fix-glibc242.patch

%post
# Post-installation script: this is where the magic happens.

echo "Applying CUDA glibc compatibility patch..."

if [ ! -f "%{target_file}" ]; then
    echo "ERROR: CUDA header '%{target_file}' not found." >&2
    echo "Please ensure the 'cuda-crt-13-0' package is correctly installed." >&2
    exit 1
fi

# Back up the original file if a backup doesn't already exist
if [ ! -f "%{backup_file}" ]; then
    echo "Backing up original file to %{backup_file}"
    /usr/bin/cp -p "%{target_file}" "%{backup_file}"
fi

# Apply the patch
# The patch uses paths like: opt/cuda/targets/x86_64-linux/include/crt/math_functions.h
# We need to strip 5 levels to get to math_functions.h, then apply in the correct directory
TARGET_DIR=$(/usr/bin/dirname "%{target_file}")

echo "Patching math_functions.h in ${TARGET_DIR}..."

# Use -p6 to strip "opt/cuda/targets/x86_64-linux/include/crt/" from patch paths
cd "${TARGET_DIR}" && /usr/bin/patch -p6 --forward --no-backup-if-mismatch < %{_datadir}/%{name}/fix-glibc242.patch

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to apply patch. Restoring original file." >&2
    /usr/bin/cp -pf "%{backup_file}" "%{target_file}"
    exit 1
fi

echo "CUDA glibc patch applied successfully."
exit 0

%preun
# Pre-uninstallation script: restore the original file.

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
* Tue Nov 19 2025 Your Name <yxh9956@gmail.com> - 1.0-1
- Initial release for CUDA 13.0 on modern glibc systems