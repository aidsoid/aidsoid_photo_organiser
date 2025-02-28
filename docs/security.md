# Security Considerations

## Input Safety
- Never modify or delete files in the input directory
- Treat the input directory as read-only in all operations

## Path Traversal
- Validate all constructed output paths stay within `output_dir`
- Do not follow symlinks outside the input/output directories

## Error Messages
- Avoid exposing full file system paths in user-facing error messages
- Log detailed paths only at DEBUG level

## File Operations
- Use hardlinks only within the same filesystem
- Verify file integrity with BLAKE2b hashing before considering files as duplicates
