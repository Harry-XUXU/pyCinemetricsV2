# PyCinemetricsV2 macOS Build Guide

## 📦 Quick Start

### Method 1: Automated Script (Recommended)

```bash
# 1. Make the script executable
chmod +x build_macos.sh

# 2. Run the build script
./build_macos.sh
```

### Method 2: Manual Build

```bash
# 1. Ensure PyInstaller is installed
pip install pyinstaller

# 2. Clean old build artifacts
rm -rf build dist __pycache__

# 3. Build using the spec file
pyinstaller pyCinemetricsV2.spec --clean

# 4. Test the app
open dist/pyCinemetricsV2.app
```

## 📋 Pre-build Setup

### 1. Create a Dedicated Virtual Environment (Recommended)

```bash
# Skip if venv already exists
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install PyInstaller
pip install pyinstaller
```

### 2. Set Environment Variables

These environment variables prevent multi-threading conflicts at runtime:

```bash
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
```

**Note**: These variables are already configured in `Info.plist` — the packaged `.app` sets them automatically.

### 3. Check ffmpeg (Optional)

If you need ffmpeg features:

```bash
# Check if installed
ffmpeg -version

# If not installed, use Homebrew
brew install ffmpeg
```

## 🔧 Config File Reference

### pyCinemetricsV2.spec Key Settings

- **binaries**: Executables to bundle (e.g. ffmpeg)
- **datas**: Data directories to bundle
- **hiddenimports**: Implicitly imported modules
- **console**: 
  - `False` = GUI app (no terminal window)
  - `True` = Show debug output

## 📱 Post-build

### 1. Test the App

```bash
# Open the app
open dist/pyCinemetricsV2.app

# Or double-click dist/pyCinemetricsV2.app in Finder
```

### 2. Resolve "Cannot Be Opened" Issue

macOS may block unsigned apps:

**Method 1: System Settings**
```
System Settings → Privacy & Security → Security
Click "Open Anyway"
```

**Method 2: Remove quarantine attribute**
```bash
xattr -cr dist/pyCinemetricsV2.app
```

**Method 3: Ad-hoc code signing**
```bash
codesign --force --deep --sign - dist/pyCinemetricsV2.app
```

### 3. Create DMG Installer

```bash
hdiutil create -volname "pyCinemetricsV2" \
               -srcfolder "dist/pyCinemetricsV2.app" \
               -ov -format UDZO "dist/pyCinemetricsV2.dmg"
```

## ⚠️ Troubleshooting

### Issue 1: App exits immediately after launch

**Cause**: Missing dependencies or resource files

**Solution**:
1. Run the app from terminal to see error output:
   ```bash
   ./dist/pyCinemetricsV2.app/Contents/MacOS/pyCinemetricsV2
   ```
2. Adjust `datas` and `hiddenimports` in `pyCinemetricsV2.spec` based on the error

### Issue 2: Missing Python modules

**Solution**:
Add the missing module names to `hiddenimports` in `pyCinemetricsV2.spec`

### Issue 3: Cannot find model files or fonts

**Solution**:
Ensure these directories are included in `pyCinemetricsV2.spec` `datas`:
```python
datas=[
    ('algorithms', 'algorithms'),
    ('ui', 'ui'),
    ('models', 'models'),
    ('fonts', 'fonts'),
    ('resources', 'resources'),
],
```

### Issue 4: App bundle too large

**Optimization**:
1. Use a clean virtual environment (only necessary packages)
2. Exclude unused modules:
   ```python
   excludes=['tkinter', 'pytest', 'nose'],
   ```
3. Enable UPX compression (already enabled in config)

## 🎯 Advanced Configuration

### Apple Silicon (M1/M2) Optimization

```python
# In pyCinemetricsV2.spec
target_arch='arm64'  # or 'universal2' for universal binary
```

### Add App Icon

```python
# Add icon parameter to EXE section (requires .icns format)
icon='resources/icon.icns',
```

Convert PNG to ICNS:
```bash
mkdir icon.iconset
sips -z 512 512 resources/icon.png --out icon.iconset/icon_512x512.png
sips -z 256 256 resources/icon.png --out icon.iconset/icon_256x256.png
sips -z 128 128 resources/icon.png --out icon.iconset/icon_128x128.png
iconutil -c icns icon.iconset -o resources/icon.icns
```

## 📊 Build Output Structure

```
dist/
├── pyCinemetricsV2.app/          # macOS application bundle
│   ├── Contents/
│   │   ├── Info.plist
│   │   ├── MacOS/
│   │   │   └── pyCinemetricsV2   # executable
│   │   └── Resources/            # all resource files
│   └── PkgInfo
└── pyCinemetricsV2.dmg           # installer (optional)
```

## 💡 Best Practices

1. **Always build in a clean virtual environment**
   - Avoid pulling in unnecessary dependencies
   - Reduce final bundle size

2. **Test before distribution**
   - Test on a different Mac
   - Ensure no hardcoded paths

3. **Version management**
   - Create separate builds for different versions
   - Keep old spec files for reference

4. **Keep docs updated**
   - Record config changes for each build
   - Maintain a list of known issues

## 🆘 Getting Help

If you encounter other issues:
1. Check the detailed build log: `build/pyCinemetricsV2/warn-pyCinemetricsV2.txt`
2. Search PyInstaller official docs
3. Check project GitHub Issues
