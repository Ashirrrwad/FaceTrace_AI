import os
from PIL import Image, ImageStat

cases_dir = "/Users/ashirwadborkar/Documents/Main Dir/Projects/Suspect sketch/static/images/cases"
mugshots = [f for f in os.listdir(cases_dir) if f.endswith('.png') and not f.endswith('_sketch.png')]

for f in mugshots[:10]:
    path = os.path.join(cases_dir, f)
    with Image.open(path) as img:
        if img.mode in ('RGB', 'RGBA'):
            stat = ImageStat.Stat(img)
            avg_diff = abs(stat.mean[0] - stat.mean[1]) + abs(stat.mean[1] - stat.mean[2]) + abs(stat.mean[0] - stat.mean[2])
            print(f"{f}: mean={stat.mean[:3]}, stddev={stat.stddev[:3]}, avg_channel_diff={avg_diff:.2f}")
        else:
            print(f"{f}: mode={img.mode} (likely grayscale)")
