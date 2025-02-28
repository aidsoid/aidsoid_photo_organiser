# Architecture

## Overview
Python CLI tool that organizes photos and videos by capture date into `YYYY/MM/` directory structure.

## Project Layout
```
src/aidsoid_photo_organiser/
  main.py                      # CLI entry point and file processing orchestration
  detect_taken_time/           # Subpackage: capture date detection
    detect_taken_time.py       # Dispatcher: tries each source in priority order
    get_date_from_json.py      # Google Photos supplemental metadata JSON
    get_date_from_exif.py      # EXIF data (JPG, JPEG, CR2)
    get_date_from_heic.py      # HEIC/HEIF via pi-heif
    get_date_from_ffprobe.py   # Video metadata via ffprobe
    get_date_from_mp4_atoms.py # MP4/M4V/MOV atom parser (ffprobe fallback)
    get_date_from_mkv.py       # MKV EBML parser (ffprobe fallback)
    get_date_from_png.py       # PNG eXIf chunk
    get_date_from_filename.py  # Date/time patterns in filenames
  file_operations.py           # Copy, hardlink, BLAKE2b hashing, duplicate detection
  count_files.py               # File statistics and reporting
  set_file_timestamps.py       # Update filesystem timestamps (cross-platform)
  replicate_files.py           # Copy non-media files preserving directory structure
  configure_logger.py          # Logging setup
  constants.py                 # File extensions and configuration constants
```

## Date Detection Priority
1. Supplemental metadata JSON (Google Photos Takeout)
2. Embedded metadata (EXIF, HEIC, ffprobe, MP4 atoms, MKV EBML, PNG eXIf)
3. Filename patterns

## Processing Flow
1. Count and display input directory statistics
2. Process each file: detect capture date → determine output path → copy/hardlink
3. Handle supplemental metadata JSON files alongside media files
4. Copy unrecognized files to `missed_files_{timestamp}` directory
5. Integrity check: verify every input file is accounted for
6. Display output directory statistics

## Key Features
- Non-destructive (never modifies input directory)
- BLAKE2b hash-based duplicate detection (with file-size pre-check)
- Hardlink support for space efficiency
- Google Photos Takeout metadata parsing (handles filename truncation variants)
- Conflict resolution via UUID-based renaming
