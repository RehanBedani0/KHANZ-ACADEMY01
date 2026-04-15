[app]

# CRITICAL: No apostrophes or special characters in title — apostrophe causes XML parsing failure
title = Khanz Academy

# Package name (no spaces, no special chars)
package.name = khanzacademy

# Package domain
package.domain = org.khanz

# Source directory
source.dir = .

# CRITICAL: Include all needed file extensions
# ttf prevents missing font file errors at runtime
source.include_exts = py,png,jpg,kv,atlas,ttf,json

# Application version
version = 1.0.0

# CRITICAL: Exact requirements — do NOT include sqlite3 (it is Python stdlib, not a pip package)
requirements = python3,kivy==2.1.0,kivymd==1.1.1,pillow,fpdf2

# Orientation
orientation = portrait

# Fullscreen mode — keep 0 to prevent UI overlap with Android status bar
fullscreen = 0

# CRITICAL: Android permissions for PDF file saving
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET

# Android API settings
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21

# Architecture — build for both 64-bit and 32-bit ARM
android.archs = arm64-v8a, armeabi-v7a

# Accept SDK license automatically
android.accept_sdk_license = True

# Presplash and icon — uncomment and set paths when custom assets are available
# presplash.filename = %(source.dir)s/assets/presplash.png
# icon.filename = %(source.dir)s/assets/icon.png

# Enable Android backup
android.allow_backup = True

# Logcat filters
# android.logcat_filters = *:S python:D

# Copy library
# android.copy_libs = 1

# The Android NDK version to use
# android.ndk_path = ...

# The Android SDK version to use
# android.sdk_path = ...

# Gradle dependencies
# android.gradle_dependencies =

# Java compilation options
# android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# Add C sources
# android.add_src =

# Add Python modules
# android.add_py_modules =

# Additional java source to compile
# android.add_src =

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin
