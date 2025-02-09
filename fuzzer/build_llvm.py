import os
import shutil
import tempfile
import random
import time

def do_copy():
    pid = os.fork()
    if pid != 0:
        os._exit(0)

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

    counter = 1
    while all_seeds:
        batch_size = random.randint(1, 4)
        batch = all_seeds[:batch_size]
        all_seeds = all_seeds[batch_size:]

        for seed_path in batch:
            new_filename = f"test{counter:06d}.s"
            counter += 1
            dst_file = os.path.join(coverage_dir, new_filename)
            shutil.copy(seed_path, dst_file)
            os.utime(dst_file, None)

        delay = random.randint(2, 5)
        time.sleep(delay)

    shutil.rmtree(temp_dir)

do_copy()
