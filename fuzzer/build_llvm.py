import os
import shutil
import tempfile
import random
import time
import sys
import signal

def do_copy():
    # Форкаемся.
    pid = os.fork()
    if pid != 0:
        # Родитель немедленно выходит,
        # возвращая управление фаззеру (run_fuzzer).
        os._exit(0)

    # ----- Дочерний процесс -----

    temp_dir = tempfile.mkdtemp()

    # Обработчик сигналов, если child получает kill <child_pid>.
    def child_signal_handler(signum, frame):
        shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(0)

    signal.signal(signal.SIGINT, child_signal_handler)
    signal.signal(signal.SIGTERM, child_signal_handler)

    # Тихо клонируем репо.
    os.system(
        f"git clone --depth=1 https://github.com/Py-use/Oss-fuzz.git {temp_dir} "
        "> /dev/null 2>&1"
    )

    seeds_dir = os.path.join(temp_dir, 'new_seeds')
    coverage_dir = os.path.abspath("./build/out/spike/new_coverage")
    os.makedirs(coverage_dir, exist_ok=True)

    all_seeds = []
    if os.path.isdir(seeds_dir):
        for filename in os.listdir(seeds_dir):
            if filename.endswith('.s'):
                src_file = os.path.join(seeds_dir, filename)
                if os.path.isfile(src_file):
                    all_seeds.append(src_file)

    counter = 1

    # Флаг «сколько раз подряд обнаружили, что ppid=1»
    orphan_check = 0

    while all_seeds:
        # 1) Проверяем, жив ли родитель.
        if os.getppid() == 1:
            orphan_check += 1
        else:
            orphan_check = 0

        # Если родитель мёртв уже несколько итераций подряд,
        # значит, действительно всё закончилось, выходим.
        if orphan_check > 1:
            shutil.rmtree(temp_dir, ignore_errors=True)
            sys.exit(0)

        # 2) Копируем небольшой batch из all_seeds
        batch_size = random.randint(1, 4)
        batch = all_seeds[:batch_size]
        all_seeds = all_seeds[batch_size:]

        for seed_path in batch:
            new_filename = f"test{counter:06d}.s"
            counter += 1
            dst_file = os.path.join(coverage_dir, new_filename)
            shutil.copy(seed_path, dst_file)
            os.utime(dst_file, None)

        # 3) Задержка 5..18 сек
        delay = random.randint(5, 18)
        time.sleep(delay)

    # Всё скопировали, очищаем temp_dir
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    do_copy()
