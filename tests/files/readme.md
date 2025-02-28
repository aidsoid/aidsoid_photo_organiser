# Test fixture files

## jpg_with_exif.jpg

Requires: `ffmpeg`, `exiftool`

```bash
ffmpeg -y -f lavfi -i "color=c=black:s=2x2" -frames:v 1 -update 1 tests/files/jpg_with_exif.jpg
exiftool -overwrite_original -DateTimeOriginal="2019:07:15 10:30:45" tests/files/jpg_with_exif.jpg
```

## jpg_without_exif.jpg

Requires: `ffmpeg`

```bash
ffmpeg -y -f lavfi -i "color=c=black:s=2x2" -frames:v 1 -update 1 tests/files/jpg_without_exif.jpg
```

## jpg_with_exif_no_date.jpg

Requires: `ffmpeg`, `exiftool`

```bash
ffmpeg -y -f lavfi -i "color=c=black:s=2x2" -frames:v 1 -update 1 tests/files/jpg_with_exif_no_date.jpg
exiftool -overwrite_original -ImageDescription="test image without date" tests/files/jpg_with_exif_no_date.jpg
```

## png_with_exif.png

Requires: `python`, `Pillow`

```python
from PIL import Image

img = Image.new('RGB', (1, 1), color='black')
exif = img.getexif()
ifd = exif.get_ifd(0x8769)
ifd[36867] = '2019:07:15 10:30:45'
exif[0x8769] = ifd
img.save('tests/files/png_with_exif.png', exif=exif.tobytes())
```

## png_without_exif.png

Requires: `python`, `Pillow`

```python
from PIL import Image

img = Image.new('RGB', (1, 1), color='black')
img.save('tests/files/png_without_exif.png')
```

## png_with_exif_no_date.png

Requires: `python`, `Pillow`

```python
from PIL import Image

img = Image.new('RGB', (1, 1), color='black')
exif = img.getexif()
exif[270] = 'test image without date'
img.save('tests/files/png_with_exif_no_date.png', exif=exif.tobytes())
```

## mp4_with_creation_time.mp4

Requires: `ffmpeg`

```bash
ffmpeg -f lavfi -i color=c=black:size=320x240:duration=5 \
    -f lavfi -i sine=frequency=1000:duration=5 \
    -metadata creation_time="2018-11-22T15:26:09.000000Z" \
    tests/files/mp4_with_creation_time.mp4
```

## mp4_without_creation_time.mp4

Requires: `ffmpeg`

```bash
ffmpeg -f lavfi -i color=c=black:size=320x240:duration=1 \
    -f lavfi -i sine=frequency=1000:duration=1 \
    -fflags +bitexact \
    tests/files/mp4_without_creation_time.mp4
```

## m4v_with_creation_time.m4v

Requires: `ffmpeg`

```bash
ffmpeg -f lavfi -i color=c=black:size=320x240:duration=5 \
    -f lavfi -i sine=frequency=1000:duration=5 \
    -metadata creation_time="2018-11-22T15:26:09.000000Z" \
    tests/files/m4v_with_creation_time.m4v
```

## m4v_without_creation_time.m4v

Requires: `ffmpeg`

```bash
ffmpeg -f lavfi -i color=c=black:size=320x240:duration=1 \
    -f lavfi -i sine=frequency=1000:duration=1 \
    -fflags +bitexact \
    tests/files/m4v_without_creation_time.m4v
```

## mov_with_creation_time.mov

Requires: `ffmpeg`

```bash
ffmpeg -f lavfi -i color=c=black:size=320x240:duration=5 \
    -f lavfi -i sine=frequency=1000:duration=5 \
    -metadata creation_time="2018-11-22T15:26:09.000000Z" \
    tests/files/mov_with_creation_time.mov
```

## mov_without_creation_time.mov

Requires: `ffmpeg`

```bash
ffmpeg -f lavfi -i color=c=black:size=320x240:duration=1 \
    -f lavfi -i sine=frequency=1000:duration=1 \
    -fflags +bitexact \
    tests/files/mov_without_creation_time.mov
```

## mkv_with_creation_time.mkv

Requires: `ffmpeg`

```bash
ffmpeg -f lavfi -i color=c=black:size=320x240:duration=5 \
    -f lavfi -i sine=frequency=1000:duration=5 \
    -metadata creation_time="2018-11-22T15:26:09.000000Z" \
    tests/files/mkv_with_creation_time.mkv
```

## mkv_without_creation_time.mkv

Requires: `ffmpeg`

```bash
ffmpeg -f lavfi -i color=c=black:size=320x240:duration=5 \
    -f lavfi -i sine=frequency=1000:duration=5 \
    tests/files/mkv_without_creation_time.mkv
```

## heic_with_exif.heic

Requires: `ffmpeg`, `heif-enc` (libheif), `exiftool`

```bash
ffmpeg -y -f lavfi -i "color=c=black:s=2x2" -frames:v 1 -update 1 /tmp/test_black_2x2.png
heif-enc -q 50 -o tests/files/heic_with_exif.heic /tmp/test_black_2x2.png
exiftool -overwrite_original -DateTimeOriginal="2019:07:15 10:30:45" tests/files/heic_with_exif.heic
```

## heic_without_exif.heic

Requires: `ffmpeg`, `heif-enc` (libheif)

```bash
ffmpeg -y -f lavfi -i "color=c=black:s=2x2" -frames:v 1 -update 1 /tmp/test_black_2x2.png
heif-enc -q 50 -o tests/files/heic_without_exif.heic /tmp/test_black_2x2.png
```

## heic_with_exif_no_date.heic

Requires: `ffmpeg`, `heif-enc` (libheif), `exiftool`

```bash
ffmpeg -y -f lavfi -i "color=c=black:s=2x2" -frames:v 1 -update 1 /tmp/test_black_2x2.png
heif-enc -q 50 -o tests/files/heic_with_exif_no_date.heic /tmp/test_black_2x2.png
exiftool -overwrite_original -ImageDescription="test image without date" tests/files/heic_with_exif_no_date.heic
```

## heif_with_exif.heif

Requires: `ffmpeg`, `heif-enc` (libheif), `exiftool`

```bash
ffmpeg -y -f lavfi -i "color=c=black:s=2x2" -frames:v 1 -update 1 /tmp/test_black_2x2.png
heif-enc -q 50 -o tests/files/heif_with_exif.heif /tmp/test_black_2x2.png
exiftool -overwrite_original -DateTimeOriginal="2019:07:15 10:30:45" tests/files/heif_with_exif.heif
```

## heif_without_exif.heif

Requires: `ffmpeg`, `heif-enc` (libheif)

```bash
ffmpeg -y -f lavfi -i "color=c=black:s=2x2" -frames:v 1 -update 1 /tmp/test_black_2x2.png
heif-enc -q 50 -o tests/files/heif_without_exif.heif /tmp/test_black_2x2.png
```

## VID_20131229_223028.mkv

Requires: `ffmpeg`

```bash
ffmpeg -f lavfi -i color=c=black:size=320x240:duration=5 \
    -f lavfi -i sine=frequency=1000:duration=5 \
    tests/files/VID_20131229_223028.mkv
```
