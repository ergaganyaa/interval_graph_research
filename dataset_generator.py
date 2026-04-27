import os
import random
import time
import glob
from generator import GraphFactory

def generate_massive_dataset():
    groups = [
        {"range": (3, 100), "count": 300},
        {"range": (101, 500), "count": 200},
        {"range": (501, 1000), "count": 100},
        {"range": (1001, 4000), "count": 100},
        {"range": (4001, 5000), "count": 50},
        {"range": (5001, 6000), "count": 50},
        {"range": (6001, 7000), "count": 50},
        {"range": (7001, 8000), "count": 50},
        {"range": (8001, 9000), "count": 50},
        {"range": (9001, 10000), "count": 50},
    ]
    
    folder = "dataset"
    if not os.path.exists(folder):
        os.makedirs(folder)
        
    # === ЛОГИКА ВОССТАНОВЛЕНИЯ ПРОГРЕССА ===
    existing_files = glob.glob(os.path.join(folder, "graph_*.txt"))
    last_id = 0
    if existing_files:
        try:
            # Вытаскиваем номера из названий (например, из graph_0829_n7050.txt берем 829)
            ids = [int(os.path.basename(f).split('_')[1]) for f in existing_files]
            last_id = max(ids)
            print(f"Обнаружено файлов: {len(existing_files)}.")
            print(f"Продолжаем работу с графа №{last_id + 1}...\n")
        except Exception:
            print("Не удалось прочитать ID файлов. Начинаем заново.")
            
    global_id = 1
    total_time_start = time.time()
    
    for idx, group in enumerate(groups, 1):
        min_n, max_n = group["range"]
        count = group["count"]
        
        # Если вся группа уже была сгенерирована в прошлый раз — смело пропускаем
        if global_id + count - 1 <= last_id:
            global_id += count
            continue
            
        print(f"[Группа {idx}/10] Генерация (от {min_n} до {max_n} вершин)...")
        group_start_time = time.time()
        generated_in_this_run = 0
        
        for _ in range(count):
            # Пропускаем графы внутри группы, которые уже есть на диске
            if global_id <= last_id:
                global_id += 1
                continue
                
            n = random.randint(min_n, max_n)
            m = int(n * random.uniform(1.5, 4.0))
            m = min(m, n * (n - 1))
            
            filename = os.path.join(folder, f"graph_{global_id:04d}_n{n}.txt")
            
            # Вызываем быструю запись из соседнего файла
            GraphFactory.generate_fast_txt(filename, n, m, 10, 100)
            
            global_id += 1
            generated_in_this_run += 1
            
            # Печатаем прогресс каждые 10 графов
            if generated_in_this_run % 10 == 0:
                print(f"  Сделано: {global_id - 1}/1000...")
                
        if generated_in_this_run > 0:
            print(f"✓ Группа {idx} доделана за {time.time() - group_start_time:.2f} сек.\n")

    print(f"=== ГОТОВО ===")
    print(f"Время сессии: {time.time() - total_time_start:.2f} сек.")

if __name__ == "__main__":
    generate_massive_dataset()