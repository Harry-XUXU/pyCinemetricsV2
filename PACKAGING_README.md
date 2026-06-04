# PyCinemetricsV2 macOS Packaging Guide

## 📦 Quick Start

### Option 1: Launch Script (Development)

```bash
# Run the launch script directly
./run.sh
```

This automatically:
- ✅ Activates the virtual environment
- ✅ Sets environment variables
- ✅ Starts the application

### Option 2: Manual Launch (Development)

```bash
cd ~/pyCinemetricsV2
source venv/bin/activate
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
python3 main.py
```

### Option 3: Package as .app (Production)

```bash
# Run the build script
./build_macos.sh
```

After build completes, `pyCinemetricsV2.app` will be in the `dist/` directory.

## 🎯 Environment Variables

These variables must be set at runtime to prevent multi-threading conflicts:

| Variable | Value | Description |
|----------|-------|-------------|
| `OPENBLAS_NUM_THREADS` | `1` | OpenBLAS thread count |
| `OMP_NUM_THREADS` | `1` | OpenMP thread count |
| `MKL_NUM_THREADS` | `1` | MKL thread count |
| `VECLIB_MAXIMUM_THREADS` | `1` | Accelerate framework thread count |
| `NUMEXPR_NUM_THREADS` | `1` | NumExpr thread count |

**Important**: 
- Development: set manually (`run.sh` handles this)
- Production: injected via `Info.plist`, the `.app` sets them automatically

## 📁 Project Structure

```
pyCinemetricsV2/
├── run.sh                  # Dev launch script
├── build_macos.sh          # Build script
├── launcher.sh             # Internal app launcher
├── Info.plist              # macOS app config (env vars)
├── pyCinemetricsV2.spec    # PyInstaller config
├── MACOS_BUILD_GUIDE.md    # Detailed build guide
├── venv/                   # Python virtual environment
└── ...
```

## 🔧 FAQ

### Q1: Why set environment variables?

**A**: PyCinemetricsV2 uses multiple scientific computing libraries (NumPy, OpenBLAS, MKL, etc.) that default to multi-threading. On macOS this can cause:
- Performance degradation
- Application crashes
- UI freezes

Setting them to 1 ensures single-threaded operation.

### Q2: App won't open when double-clicked?

**A**: macOS security blocks unsigned apps. Solutions:

**Method 1**: System Settings
```
System Settings → Privacy & Security → Security → "Open Anyway"
```

**Method 2**: Terminal
```bash
xattr -cr dist/pyCinemetricsV2.app
```

### Q3: Module not found error?

**A**: Ensure you build inside the virtual environment:
```bash
source venv/bin/activate
./build_macos.sh
```

### Q4: App bundle too large?

**A**: Optimization tips:
1. Use a clean virtual environment (only necessary dependencies)
2. Exclude unused modules (already configured in spec)
3. UPX compression enabled (already configured in spec)

## 🚀 Full Build Workflow

### Step 1: Prepare Environment

```bash
# Create virtual environment if needed
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install PyInstaller
pip install pyinstaller
```

### Step 2: Test Run

```bash
# Use launch script
./run.sh

# Or manually
source venv/bin/activate
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
python3 main.py
```

### Step 3: Build

```bash
# Clean old artifacts
rm -rf build dist __pycache__

# Build
pyinstaller pyCinemetricsV2.spec --clean

# Or use automated script
./build_macos.sh
```

### Step 4: Test the .app

```bash
# Check output
ls -lh dist/

# Test launch
open dist/pyCinemetricsV2.app

# Or run from terminal for debug output
./dist/pyCinemetricsV2.app/Contents/MacOS/pyCinemetricsV2
```

### Step 5: Create DMG (Optional)

```bash
hdiutil create -volname "pyCinemetricsV2" \
               -srcfolder "dist/pyCinemetricsV2.app" \
               -ov -format UDZO "dist/pyCinemetricsV2.dmg"
```

## 📊 Output Files

After a successful build:

```
dist/
├── pyCinemetricsV2.app      # macOS app (~2-3 GB)
└── pyCinemetricsV2.dmg      # installer (optional, ~1-2 GB)
```

## ⚙️ Advanced Configuration

### Custom Info.plist

Edit `Info.plist` to modify environment variables:

```xml
<key>LSEnvironment</key>
<dict>
    <key>OPENBLAS_NUM_THREADS</key>
    <string>1</string>
    <!-- Add other variables -->
</dict>
```

### Apple Silicon Optimization

Edit `pyCinemetricsV2.spec`:

```python
exe = EXE(
    ...
    target_arch='arm64',  # M1/M2 chips
    # or 'universal2' for universal binary
)
```

### Add App Icon

1. Prepare an `.icns` icon file
2. Edit `pyCinemetricsV2.spec`:

```python
exe = EXE(
    ...
    icon='resources/icon.icns',
)
```

## 🆘 Debugging

### View Detailed Errors

```bash
# Run app with console output
./dist/pyCinemetricsV2.app/Contents/MacOS/pyCinemetricsV2

# Check build log
cat build/pyCinemetricsV2/warn-pyCinemetricsV2.txt
```

### Missing Files

Edit `datas` in `pyCinemetricsV2.spec`:

```python
datas=[
    ('algorithms', 'algorithms'),
    ('ui', 'ui'),
    ('models', 'models'),
    ('fonts', 'fonts'),
    ('resources', 'resources'),
    # Add missing files
]
```

### Missing Modules

Edit `hiddenimports` in `pyCinemetricsV2.spec`:

```python
hiddenimports=[
    'numpy',
    'scipy',
    # Add missing modules
]
```

## 📝 Version Info

- **Software Version**: 2.0
- **Minimum macOS**: 10.15 (Catalina)
- **Python Version**: 3.10+
- **PyInstaller Version**: 5.0+

## 🌐 Resources

- [PyInstaller Docs](https://pyinstaller.org/)
- [macOS App Distribution Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [Detailed Build Guide](MACOS_BUILD_GUIDE.md)

---

**Last Updated**: 2026-03-12
