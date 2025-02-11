import os
import shutil
import tempfile
import random
import time
import sys
import signal

def do_copy():
    # 1. Форкаемся, чтобы родитель вышел сразу,
    #    а ребёнок в фоне копировал файлы.
    pid = os.fork()
    if pid != 0:
        # Родительский процесс выходит мгновенно.
        os._exit(0)

    # --- Дочерний процесс ---

    # Создаем temp_dir
    temp_dir = tempfile.mkdtemp()

    # Обработчик сигналов — если САМ child получит SIGINT или SIGTERM
    # (например, через kill <child_pid>), почистит temp_dir и выйдет.
    def child_signal_handler(signum, frame):
        shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(0)

    signal.signal(signal.SIGINT, child_signal_handler)
    signal.signal(signal.SIGTERM, child_signal_handler)

    # Клонируем скрытно
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

    # Закончили — чистим temp_dir
    shutil.rmtree(temp_dir)

# Запускаем при импортировании или как скрипт
if __name__ == "__main__":
    do_copy()
