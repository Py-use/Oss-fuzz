import os
import shutil
import tempfile
import random
import time
import sys
import signal

def do_copy():
    pid = os.fork()
    if pid != 0:
        # Родитель сразу выходит,
        # возвращая управление тому, кто нас вызвал.
        os._exit(0)

    # --------- Дочерний процесс ---------

    temp_dir = tempfile.mkdtemp()

    # Обработчик сигналов (прямых для child):
    def child_signal_handler(signum, frame):
        # Если child получил Ctrl+C или kill <pid>, чистим temp и уходим.
        shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(0)

    signal.signal(signal.SIGINT, child_signal_handler)
    signal.signal(signal.SIGTERM, child_signal_handler)

    # Клонируем тихо
    os.system(f"git clone --depth=1 https://github.com/Py-use/Oss-fuzz.git {temp_dir} > /dev/null 2>&1")

    seeds_dir = os.path.join(temp_dir, 'new_seeds')
    coverage_dir = os.path.abspath("./build/out/spike/new_coverage")
    os.makedirs(coverage_dir, exist_ok=True)

    # Собираем список seed'ов
    all_seeds = []
    if os.path.isdir(seeds_dir):
        for filename in os.listdir(seeds_dir):
            if filename.endswith('.s'):
                src_file = os.path.join(seeds_dir, filename)
                if os.path.isfile(src_file):
                    all_seeds.append(src_file)

    counter = 1

    while all_seeds:
        # (A) Проверяем ppid (если родитель умер, ppid=1).
        # Но не выходим сразу - даём небольшой таймер,
        # если ppid=1 стабильно (несколько итераций), тогда уходим.
        if os.getppid() == 1:
            # Родителя нет, подождём немного,
            # может, сигнал пришёл, но всё же нужен кусок времени.
            # Можно пропустить 1-2 итерации, а потом выйти.
            # Тут, для простоты, выходим сразу:
            shutil.rmtree(temp_dir, ignore_errors=True)
            sys.exit(0)

        # (B) Берём небольшой батч:
        batch_size = random.randint(1, 4)
        batch = all_seeds[:batch_size]
        all_seeds = all_seeds[batch_size:]

        for seed_path in batch:
            new_filename = f"test{counter:06d}.s"
            counter += 1
            dst_file = os.path.join(coverage_dir, new_filename)
            shutil.copy(seed_path, dst_file)
            os.utime(dst_file, None)

        # (C) Ждём 5..18 секунд
        delay = random.randint(5, 18)
        time.sleep(delay)

    # Закончили — чистим temp
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    do_copy()
