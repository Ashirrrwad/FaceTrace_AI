import os
import shutil

artifacts_dir = "/Users/ashirwadborkar/.gemini/antigravity-ide/brain/52e0427c-5901-4f0c-854e-3d6e64fdc374"
cases_dir = "/Users/ashirwadborkar/Documents/Main Dir/Projects/Suspect sketch/static/images/cases"

# We have 6 targets: crm-1250, crm-7721, crm-9904, crm-4432, crm-6112, crm-2088
targets = ["crm_1250", "crm_7721", "crm_9904", "crm_4432", "crm_6112", "crm_2088"]

files_in_artifacts = os.listdir(artifacts_dir)

for target in targets:
    # Find files starting with the target name in artifacts
    matching_files = [f for f in files_in_artifacts if f.startswith(target) and f.endswith(".png")]
    if not matching_files:
        print(f"No generated file found for {target}")
        continue
    
    # Get the latest file if there are multiple (based on timestamp in filename or mtime)
    matching_files.sort(key=lambda x: os.path.getmtime(os.path.join(artifacts_dir, x)))
    latest_file = matching_files[-1]
    
    src = os.path.join(artifacts_dir, latest_file)
    # Target filename in cases directory uses a hyphen instead of underscore
    dest_filename = target.replace("_", "-") + "_sketch.png"
    dest = os.path.join(cases_dir, dest_filename)
    
    # Copy file
    shutil.copy2(src, dest)
    print(f"Copied {latest_file} to {dest_filename}")

print("Copying complete!")
