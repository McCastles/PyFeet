import os
import json
import random

main_path = '/home/bazyli/1szkola/ppdv/PyFeet/walk_monitoring/data'
for dir in os.listdir(main_path):
    dirpath = os.path.join(main_path, dir)
    if not os.path.isdir(dirpath):
        continue
    files_to_change = random.choices(os.listdir(dirpath), k=100)
    for f in files_to_change:
        pth = os.path.join(dirpath, f)
        with open(pth, 'r') as f:
            data = json.loads(f.read())
        print(data['trace'])
        data['trace']['sensors'][random.randint(0,5)]['anomaly'] = True
        with open(pth, 'w') as f:
            f.write(json.dumps(data))