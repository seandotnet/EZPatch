# EZPatch - Fortnite Replay Patcher

EZPatch is a lightweight, user-friendly desktop application designed to fix broken Fortnite replay files (`.replay`) after game updates. 

When Fortnite releases a new update, older replays often become unplayable because the embedded version information no longer matches the current client. EZPatch solves this by copying the correct version bytes from a working (new) replay file and patching them into one or more broken (old) replay files.

## Features
- **Single File Mode**: Patch one broken replay using one working replay.
- **Batch Folder Mode**: Patch all `.replay` files in a selected folder using one working replay.
- **Auto Mode**: Automatically detect the latest replay in the default Fortnite folder and patch the entire folder in one click.
- **Safety First**: Keeps original files by default, moves them to a `Backups` folder, or deletes them if you choose.
- **Modern UI**: Built with CustomTkinter for a clean, dark-mode friendly experience.

## Installation & Usage

### Option 1: Download the Executable (Recommended)
1. Go to the **[Releases](../../releases)** tab on this GitHub repository.
2. Download the latest `EZPatch.exe`.
3. Run the application (no installation required).
4. Select a working replay file (a replay from the current Fortnite version).
5. Select a broken replay file or a folder of broken replays.
6. Click **Patch Replays**!

### Option 2: Run from Source
If you prefer to run the Python script directly:

1. Clone this repository:
   ```bash
   git clone https://github.com/seandotnet/EZPatch.git
   cd EZPatch
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Building the Executable
If you want to build the standalone `.exe` file yourself using PyInstaller:

```bash
pip install -r requirements.txt
python -m PyInstaller build.spec
```
The executable will be generated in the `dist/` folder.

## License
This project is open-source and free to use.
