import os

# Method 1: Simple path check (what you were trying to do)
print("=== Method 1: Simple Path Check ===")
db_path = "my_database.db"
if os.path.exists(db_path):
    print(f"✅ Database exists at: {os.path.abspath(db_path)}")
    print(f"📁 File size: {os.path.getsize(db_path)} bytes")
else:
    print("❌ Database does not exist")

print("\n=== Method 2: More Detailed Path Information ===")
# Method 2: More detailed path information
current_dir = os.getcwd()
print(f"Current working directory: {current_dir}")
print(f"Database path (relative): {db_path}")
print(f"Database path (absolute): {os.path.abspath(db_path)}")

# Check if file exists and show details
if os.path.exists(db_path):
    file_stats = os.stat(db_path)
    print(f"✅ File exists!")
    print(f"📁 Size: {file_stats.st_size} bytes")
    print(f"📅 Created: {file_stats.st_ctime}")
    print(f"📅 Modified: {file_stats.st_mtime}")
else:
    print("❌ File does not exist")

print("\n=== Method 3: List Files in Current Directory ===")
# Method 3: List all files to see what's there
print("Files in current directory:")
for file in os.listdir('.'):
    if file.endswith('.db'):
        print(f"  🗄️  {file} (Database file)")
    else:
        print(f"  📄 {file}") 