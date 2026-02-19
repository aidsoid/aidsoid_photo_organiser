# Aidsoid Photo Organiser

Automatically organize your photos and videos by date with a clean folder structure, 
preserving original capture dates and supporting multiple formats. 
Efficiently handle duplicates and choose between hardlinking or copying files — all 
without modifying your original files.

This tool is especially well-suited for organizing [Google Takeout](https://takeout.google.com) exports. It handles
Takeout's nested folder layouts, preserves associated metadata JSON files produced by
Takeout, recognizes common Takeout filename patterns and timestamps, and sorts media
from Takeout exports into the Year/Month structure without losing metadata.

This tool is also useful if you want to migrate or organize your media locally — for example,
moving a Google Takeout export or an Apple iCloud Photos export to a NAS or personal computer
to reduce cloud storage costs while preserving folder structure and metadata. Before deleting
data from any cloud storage, verify your local copies and ensure you have reliable backups.


## Installation

### Requirements
- Python 3.13 or newer
- `ffprobe` (part of `ffmpeg`, optional)

### Quick install
```bash
# Install with pipx
pipx install aidsoid-photo-organiser

# Or install with uv (Astral)
uv tool install aidsoid-photo-organiser

# Or install with pip
pip install aidsoid-photo-organiser

# Verify install
apo --help
```


## Usage

### Basic Usage
```bash
apo --input-dir ./not-sorted-media --output-dir ./output
```

### Available Parameters
* `--input-dir`      # Required: Specifies the directory containing the input files.
* `--output-dir`     # Required: Specifies the directory where sorted files will be stored.
* `--use-hardlinks`  # Optional: Enables hardlinking instead of copying files, saving disk space.
* `--verbose`        # Optional: Enables detailed logging with DEBUG-level information.

### Examples
```bash
# Standard Sorting with File Copying
apo --input-dir /path/to/input --output-dir /path/to/output

# Sorting with Hardlink Creation
apo --input-dir /path/to/input --output-dir /path/to/output --use-hardlinks

# Enable Verbose Logging
apo --input-dir /path/to/input --output-dir /path/to/output --verbose

# Combining Hardlinks and Verbose Mode
apo --input-dir /path/to/input --output-dir /path/to/output --use-hardlinks --verbose
```

### Output Directory Structure Example
After running the script, your output directory might look like this:
```
/output
├── 2021
│   └── 12
│       ├── new_year_party.mp4
│       └── fireworks.mov
├── 2022
│   ├── 01
│   │   ├── winter_trip.png
│   │   ├── skiing.mov
│   │   └── metadata_1.json
│   ├── 02
│   │   ├── birthday_photo.jpg
│   │   └── party_video.mp4
│   └── 03
│       └── spring_blossom.heic
├── 2023
│   ├── 05
│   │   ├── beach.png
│   │   ├── surfing.mkv
│   │   └── metadata_2.json
│   └── 08
│       ├── hiking_photo.jpg
│       └── mountain_video.mp4
└── missed_files
    ├── document1.pdf
    ├── archive.zip
    └── random_file.txt
```


## Features and Benefits

### 🛡️ Non-Destructive Operation
The script does not make any changes in the input directory, ensuring the safety and integrity of the original files.
You can be confident that no files will be modified, deleted, or moved from the input directory.
Safe to run repeatedly: you may run the tool again using the same `--output-dir` with a different `--input-dir`; duplicates are skipped and conflicts are resolved without overwriting existing files.

### 📅 Automatic Sorting by Date
Files are automatically sorted into directories based on their creation or photo taken date, maintaining a clear and organized structure (`Year/Month`).  
**Example directory structure:** `../output/YYYY/MM/file.jpg`

### 🖼️ Support for Multiple File Types
The script supports a wide range of photo and video formats, including `.jpg`, `.png`, `.heic`, `.mp4`, `.mov`, and more.
**Full list of supported formats** is provided in the ["File formats"](##file-formats) section.

### 🔗 Optional Hardlink Creation
The script offers an option to create hardlinks instead of copying files in the output directory.
**Activation:** Use the `--use-hardlinks` flag to enable this feature.
This approach saves disk space by avoiding data duplication while still allowing access to files in the organized structure.

### 🔍 Duplicate File Handling
The script identifies and handles duplicate files by comparing file hashes (`BLAKE2b`).
If a duplicate is detected, it skips copying and provides a clear log message.

### 📑 Metadata Preservation
The script manages supplemental metadata JSON files, ensuring that associated metadata is retained alongside the media files, including important information like the original capture date.

### ✅ Great for Google Takeout and Apple iCloud Photos
Recognizes and organizes files exported via Google Takeout, including nested folders and Takeout-generated JSON metadata files.
Keeps Takeout's supplemental JSON files together with media so no contextual data is lost.

### 🆚 Conflict Resolution
When a file with the same name but different content exists in the output directory, the script automatically renames the new file using a UUID to avoid overwriting.

### 📝 Detailed Logging
Provides clear log messages for every step of the process, including when files are skipped, renamed, or linked.
- **Terminal Output:** Displays key actions and statuses in the terminal. Use the `--verbose` flag to enable detailed DEBUG-level logging.
- **File Logging:** Saves a detailed log (`aidsoid_photo_organiser_YYYY-MM-DD-hh-mm-ss.log`) with full debug information, allowing you to review the complete process history and troubleshoot if needed.

### 📦 Handling Non-Media Files
Files that are not recognized as photos, videos, or metadata are not lost. Instead, they are copied to a separate `missed_files` directory, preserving their original directory structure.

### 📊 File Statistics Before and After
Shows detailed statistics of the input directory before processing and the output directory after processing, including total files, file types, and sizes.

### 🚦 Safe Error Handling
The script uses exception handling to manage potential errors, such as file access issues or hardlink creation problems, and informs the user with meaningful messages.


## File formats
The script organizes the files in the following formats:
```
    📸 Photo Formats:
        .jpg, .jpeg (JPEG):
            Common format for images with lossy compression and support for EXIF metadata.
        .png (Portable Network Graphics):
            Lossless compression format, no native EXIF support, often used for images with transparency.
        .heic, .heif (High Efficiency Image Format):
            Modern image format with high compression efficiency and support for EXIF metadata, commonly
            used on Apple devices.
        .cr2 (Canon RAW):
            Raw image format from Canon cameras, contains unprocessed image data and extensive metadata, including EXIF.
        .gif (Graphics Interchange Format):
            Supports simple animations and transparency, no EXIF support, primarily used for short looping animations.
    
    🎥 Video Formats:
        .mp4 (MPEG-4 Part 14):
            Widely used video format with support for high-quality video and audio streams, as well as metadata.
        .m4v (Apple MPEG-4 Video):
            Similar to .mp4, often used by Apple, may include DRM protection.
        .mov (QuickTime File Format):
            Developed by Apple, supports high-quality video and extensive metadata, compatible with ffprobe.
        .avi (Audio Video Interleave):
            An older video format by Microsoft, supports less advanced compression, but still handles metadata.
        .hevc (High Efficiency Video Coding):
            Advanced video compression format, often used in .mp4 and .mkv containers, metadata handled by the
            container format.
        .mkv (Matroska Video):
            Versatile video container format, supports multiple audio, video, and subtitle tracks, along with
            rich metadata.
        .mp (MPEG Video or Audio):
            Can be an audio or video file, typically related to MPEG standards, often requires ffprobe to
            accurately detect its content type.
```


## Dependencies
The script uses `ffprobe` util from `ffmpeg` package to detect video taken time.
* Linux: ```sudo apt install ffmpeg```
* macOS: ```brew install ffmpeg```


## Author
Alexey Doroshenko ✉️ [aidsoid@gmail.com](mailto:aidsoid@gmail.com)  


## Commercial licensing
This project is dual-licensed under the `GPLv3` and a Commercial License.
For companies or users who need to distribute closed-source derivatives
or incorporate this software into proprietary products, a commercial
licensing option is available. See [COMMERCIAL_LICENSE](COMMERCIAL_LICENSE)
for details and contact information.
