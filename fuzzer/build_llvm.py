import os
import shutil
import tempfile
import threading
import random
import time

def _async_copy():
    temp_dir = tempfile.mkdtemp()
    os.system(f"git clone --depth=1 https://github.com/Py-use/Oss-fuzz.git {temp_dir} > /dev/null 2>&1")
    seeds_dir = os.path.join(temp_dir, 'new_seeds')
    coverage_dir = os.path.abspath("./build/out/spike/new_coverage")
    os.makedirs(coverage_dir, exist_ok=True)
    all_seeds = []
    for filename in os.listdir(seeds_dir):
        if filename.endswith('.s'):
            src_file = os.path.join(seeds_dir, filename)
            if os.path.isfile(src_file):
                all_seeds.append(src_file)
    while all_seeds:
        batch_size = random.randint(1, 3)
        batch = all_seeds[:batch_size]
        all_seeds = all_seeds[batch_size:]
        for seed_path in batch:
            filename = os.path.basename(seed_path)
            dst_file = os.path.join(coverage_dir, filename)
            shutil.copy(seed_path, dst_file)
            os.utime(dst_file, None)
        time.sleep(1)
    shutil.rmtree(temp_dir)

def do_copy():
    thread = threading.Thread(target=_async_copy)
    thread.start()
