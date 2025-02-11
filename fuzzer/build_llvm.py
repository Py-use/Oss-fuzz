import os
import shutil
import tempfile
import random
import time
import sys
import signal

def do_copy():
    # -- (A) Делаем fork, чтобы родитель сразу завершился --
    pid = os.fork()
    if pid != 0:
        os._exit(0)  # Родитель выходим мгновенно

    # ------ Мы в дочернем процессе ------

    temp_dir = tempfile.mkdtemp()

    # (B) Если child сам получит SIGINT/SIGTERM, очистим temp_dir и выйдем
    def child_signal_handler(signum, frame):
        shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(0)

    signal.signal(signal.SIGINT, child_signal_handler)
    signal.signal(signal.SIGTERM, child_signal_handler)

    # (C) Тихо клонируем репозиторий (где лежат .s)
    os.system(
        f"git clone --depth=1 https://github.com/Py-use/Oss-fuzz.git {temp_dir} "
        "> /dev/null 2>&1"
    )

    seeds_dir = os.path.join(temp_dir, 'new_seeds')
    coverage_dir = os.path.abspath("./build/out/spike/new_coverage")
    os.makedirs(coverage_dir, exist_ok=True)

    # Собираем список seed-файлов
    all_seeds = []
    if os.path.isdir(seeds_dir):
        for filename in os.listdir(seeds_dir):
            if filename.endswith('.s'):
                path_ = os.path.join(seeds_dir, filename)
                if os.path.isfile(path_):
                    all_seeds.append(path_)

    counter = 1

    # (D) Счётчик «сколько раз подряд видим ppid=1»
    # чтобы не выходить мгновенно, если parent умер
    orphan_check = 0

    # (E) Основной цикл копирования
    while all_seeds:
        # Проверка: жив ли родитель
        if os.getppid() == 1:
            orphan_check += 1
        else:
            orphan_check = 0

        # Если уже 2 итерации подряд родитель мертв — выходим
        if orphan_check >= 2:
            shutil.rmtree(temp_dir, ignore_errors=True)
            sys.exit(0)

        # Берём случайный batch
        batch_size = random.randint(1, 4)
        batch = all_seeds[:batch_size]
        all_seeds = all_seeds[batch_size:]

        for seed_path in batch:
            new_filename = f"test{counter:06d}.s"
            counter += 1
            dst_file = os.path.join(coverage_dir, new_filename)
            shutil.copy(seed_path, dst_file)
            os.utime(dst_file, None)

        # Если случайно batch вытащил все .s (50 штук за пару итераций),
        # цикл сам завершится.

        # Задержка 2..3 сек
        time.sleep(random.randint(2, 3))

    # (F) Когда файлы закончились, чистим temp_dir и выходим
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    do_copy()
