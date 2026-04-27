import os
import csv
import time
import heapq

def load_graph_simple(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    n, m = map(int, lines[0].split())
    adj = [[] for _ in range(n)]
    for i in range(1, m + 1):
        u, v, l, r, x = map(int, lines[i].split())
        adj[u].append((v, l, r, x))
    start, end = map(int, lines[-1].split())
    return n, adj, start, end

def calculate_rank(dl, dm, dr, risk_factor=0.2):
    """
    Функция дефаззификации. 
    dm - ожидаемое время. (dr - dl) - ширина интервала (неопределенность).
    Мы штрафуем алгоритм за слишком широкие (рискованные) интервалы.
    """
    return dm + risk_factor * (dr - dl)

def solve_fuzzy(n, adj, start, end):
    # Массивы для отслеживания кратчайших путей (сохраняем тройки TFN)
    # По умолчанию бесконечность для l, m, r
    distances_tfn = [(float('inf'), float('inf'), float('inf'))] * n
    best_ranks = [float('inf')] * n
    parent = [-1] * n
    
    # Стартовый узел (0, 0, 0)
    distances_tfn[start] = (0, 0, 0)
    best_ranks[start] = 0
    
    # В куче храним: (Текущий_Ранк, Текущий_Узел, (dl, dm, dr))
    pq = [(0, start, (0, 0, 0))]
    
    start_time = time.perf_counter()
    
    while pq:
        current_rank, u, (curr_l, curr_m, curr_r) = heapq.heappop(pq)
        
        if u == end: 
            break
            
        # Если мы уже нашли путь к этому узлу с лучшим ранком, пропускаем
        if current_rank > best_ranks[u]: 
            continue
            
        for v, l, r, x in adj[u]:
            # Превращаем интервал ребра в TFN
            m = (l + r) / 2
            
            # Складываем текущее расстояние (TFN) и ребро (TFN)
            new_l = curr_l + l
            new_m = curr_m + m
            new_r = curr_r + r
            
            # Считаем ранк нового пути
            new_rank = calculate_rank(new_l, new_m, new_r)
            
            # Если новый путь выгоднее (ранк меньше), обновляем
            if new_rank < best_ranks[v]:
                best_ranks[v] = new_rank
                distances_tfn[v] = (new_l, new_m, new_r)
                parent[v] = u
                heapq.heappush(pq, (new_rank, v, (new_l, new_m, new_r)))
                
    exec_time = (time.perf_counter() - start_time) * 1000
    
    # Восстанавливаем путь
    path = []
    curr = end
    while curr != -1:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    
    return path, exec_time

def get_real_cost_of_path(path, adj):
    edge_map = {}
    for u in range(len(adj)):
        for v, l, r, x in adj[u]:
            edge_map[(u, v)] = x
            
    total_x = 0
    for i in range(len(path) - 1):
        total_x += edge_map.get((path[i], path[i+1]), 0)
    return total_x

def run_fuzzy():
    dataset_dir = "dataset"
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    
    output_file = os.path.join(results_dir, "fuzzy_results.csv")
    files = sorted([f for f in os.listdir(dataset_dir) if f.endswith(".txt")])
    print(f"Запуск Fuzzy Dijkstra для {len(files)} графов...")
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["graph_file", "execution_time_ms", "fuzzy_cost_real", "fuzzy_path_length"])
        
        for filename in files:
            n, adj, start, end = load_graph_simple(os.path.join(dataset_dir, filename))
            
            path, exec_time = solve_fuzzy(n, adj, start, end)
            real_cost = get_real_cost_of_path(path, adj)
            path_length = len(path) - 1 if len(path) > 1 else 0
            
            writer.writerow([filename, exec_time, real_cost, path_length])
            if int(filename.split('_')[1]) % 100 == 0:
                print(f"Обработано {filename}...")
                
    print("Алгоритм Fuzzy завершил работу!")

if __name__ == "__main__":
    run_fuzzy()