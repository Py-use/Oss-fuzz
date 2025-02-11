import os
import shutil
import tempfile
import random
import time
import signal
import sys

def do_copy():
    # Создаем temp-деректорию
    temp_dir = tempfile.mkdtemp()

    # Функция очистки при сигнале
    def cleanup_and_exit(signum, frame):
        # Удаляем temp_dir, если есть
        shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(0)

    # Навешиваем обработчики
    signal.signal(signal.SIGINT, cleanup_and_exit)   # Ctrl+C
    signal.signal(signal.SIGTERM, cleanup_and_exit)  # kill <pid>

    # Клонируем репозиторий (скрываем вывод)
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

        delay = random.randint(5, 18)
        time.sleep(delay)

    # По завершении чистим temp_dir
    shutil.rmtree(temp_dir)

do_copy()
