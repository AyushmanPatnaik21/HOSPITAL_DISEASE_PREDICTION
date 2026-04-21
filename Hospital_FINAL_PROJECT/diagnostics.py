import os
import sys

filepath = r'C:\Users\asuto\Desktop\Hospital\CLEANUP_GUIDE.md'

print(f"File: {filepath}")
print(f"Exists: {os.path.exists(filepath)}")
print(f"Is file: {os.path.isfile(filepath)}")
print(f"Readable: {os.access(filepath, os.R_OK)}")
print(f"Writable: {os.access(filepath, os.W_OK)}")

# Check file size
if os.path.exists(filepath):
    stat = os.stat(filepath)
    print(f"Size: {stat.st_size} bytes")
    print(f"Permissions (octal): {oct(stat.st_mode)}")

# Try to delete
try:
    os.remove(filepath)
    print("✅ Successfully deleted!")
except PermissionError as e:
    print(f"❌ PermissionError: {e}")
except OSError as e:
    print(f"❌ OSError: {e}")
    print(f"   Error code: {e.errno}")
    print(f"   Error strerror: {e.strerror}")
except Exception as e:
    print(f"❌ {type(e).__name__}: {e}")
