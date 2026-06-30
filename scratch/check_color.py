import os
from PIL import Image, ImageStat

cases_dir = "/Users/ashirwadborkar/Documents/Main Dir/Projects/Suspect sketch/static/images/cases"
sketches = [f for f in os.listdir(cases_dir) if f.endswith('_sketch.png')]

for f in sketches:
    path = os.path.join(cases_dir, f)
    with Image.open(path) as img:
        # Check if it is grayscale or color
        # A simple check: check if the R, G, B channels are identical or highly similar
        if img.mode in ('RGB', 'RGBA'):
            stat = ImageStat.Stat(img)
            # Compare channel averages and standard deviations
            avg_diff = abs(stat.mean[0] - stat.mean[1]) + abs(stat.mean[1] - stat.mean[2]) + abs(stat.mean[0] - stat.mean[2])
            print(f"{f}: mean={stat.mean[:3]}, stddev={stat.stddev[:3]}, avg_channel_diff={avg_diff:.2f}")
        else:
            print(f"{f}: mode={img.mode} (likely grayscale)")
