import os
from PIL import Image

cases_dir = "/Users/ashirwadborkar/Documents/Main Dir/Projects/Suspect sketch/static/images/cases"
files = sorted(os.listdir(cases_dir))

for f in files:
    if f.endswith('.png'):
        path = os.path.join(cases_dir, f)
        try:
            with Image.open(path) as img:
                print(f"{f}: size={img.size}, mode={img.mode}, format={img.format}, bytes={os.path.getsize(path)}")
        except Exception as e:
            print(f"Error reading {f}: {e}")
