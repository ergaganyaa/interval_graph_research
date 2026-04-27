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

def solve_broumi(n, adj, start, end):
    # Neutrosophic weight - это аддитивная метрика (штраф за длину и риск)
    distances = [float('inf')] * n
    parent = [-1] * n
    distances[start] = 0
    pq = [(0, start)]
    
    start_time = time.perf_counter()
    
    while pq:
        current_dist, u = heapq.heappop(pq)
        
        if u == end: break
        if current_dist > distances[u]: continue
            
        for v, l, r, x in adj[u]:
            # Маппинг в Neutrosophic (T, I, F)
            # Предполагаем, что максимальный вес одного ребра ~100
            t = max(0, (100 - l) / 100) # Truth (хорошесть пути)
            i = (r - l) / 100           # Indeterminacy (неопределенность)
            f = r / 100                 # Falsity (плохость пути)
            
            # Score Function для поиска минимума:
            # Наказываем за I и F, поощряем за T (поэтому -t). 
            # +2 просто чтобы вес всегда был положительным для Дейкстры.
            neutrosophic_weight = 2 - t + i + f 
            
            distance = current_dist + neutrosophic_weight
            
            if distance < distances[v]:
                distances[v] = distance
                parent[v] = u
                heapq.heappush(pq, (distance, v))
                
    exec_time = (time.perf_counter() - start_time) * 1000
    
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

def run_broumi():
    dataset_dir = "dataset"
    results_dir = "results"
    output_file = os.path.join(results_dir, "broumi_results.csv")
    files = sorted([f for f in os.listdir(dataset_dir) if f.endswith(".txt")])
    print(f"Запуск Broumi (Neutrosophic) для {len(files)} графов...")
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["graph_file", "execution_time_ms", "broumi_cost_real", "broumi_path_length"])
        
        for filename in files:
            n, adj, start, end = load_graph_simple(os.path.join(dataset_dir, filename))
            path, exec_time = solve_broumi(n, adj, start, end)
            real_cost = get_real_cost_of_path(path, adj)
            path_length = len(path) - 1 if len(path) > 1 else 0
            writer.writerow([filename, exec_time, real_cost, path_length])
            
    print("Алгоритм Broumi завершил работу!")

if __name__ == "__main__":
    run_broumi()