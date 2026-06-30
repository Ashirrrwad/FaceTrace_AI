import os

cases_dir = "/Users/ashirwadborkar/Documents/Main Dir/Projects/Suspect sketch/static/images/cases"
for item in os.listdir(cases_dir):
    if item.endswith('_sketch.png'):
        base = item.replace('_sketch.png', '.png')
        base_path = os.path.join(cases_dir, base)
        sketch_path = os.path.join(cases_dir, item)
        if os.path.exists(base_path):
            # Check if they are the same file content or very different sizes
            sz1 = os.path.getsize(base_path)
            sz2 = os.path.getsize(sketch_path)
            print(f"{base} size={sz1} vs {item} size={sz2}")
