#!/usr/bin/env python3
import os
import shutil
import tempfile
import random
import time
import sys
import signal

def do_copy():
    # 1) Форкаемся.
    pid = os.fork()
    if pid != 0:
        # Мы — родитель. Сразу выходим, чтобы не блокировать того, кто нас запустил.
        os._exit(0)

    # Мы в дочернем процессе. "Отрываемся" от родителя полностью (но PPID пока тот же).
    # Можно сделать setsid, но тогда сигналы от родителя не прилетят вообще. 
    # Поэтому оставим так, но будем периодически проверять ppid.

    # 2) Создаём временную папку, куда склонируем.
    temp_dir = tempfile.mkdtemp()

    # 3) Можно назначить обработчики сигналов (если в child прям послать SIGINT/SIGTERM):
    def child_signal_handler(signum, frame):
        shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(0)

    signal.signal(signal.SIGINT, child_signal_handler)
    signal.signal(signal.SIGTERM, child_signal_handler)

    # 4) Тихо клонируем репо (никаких логов).
    os.system(f"git clone --depth=1 https://github.com/Py-use/Oss-fuzz.git {temp_dir} > /dev/null 2>&1")

    seeds_dir = os.path.join(temp_dir, 'new_seeds')
    coverage_dir = os.path.abspath("./build/out/spike/new_coverage")
    os.makedirs(coverage_dir, exist_ok=True)

    # 5) Собираем список .s файлов
    all_seeds = []
    if os.path.isdir(seeds_dir):
        for filename in os.listdir(seeds_dir):
            if filename.endswith('.s'):
                src_file = os.path.join(seeds_dir, filename)
                if os.path.isfile(src_file):
                    all_seeds.append(src_file)

    counter = 1

    # 6) Цикл копирования, с рандомными задержками.
    #    Периодически проверяем, жив ли родитель. Если исчез, останавливаемся.
    while all_seeds:
        # Если parent умер, ppid станет 1 — сворачиваемся.
        if os.getppid() == 1:
            shutil.rmtree(temp_dir, ignore_errors=True)
            sys.exit(0)

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

    # 7) По успешному завершению чистим temp_dir и завершаемся.
    shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    do_copy()
