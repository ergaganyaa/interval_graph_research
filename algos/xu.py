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

def solve_xu(n, adj, start, end):
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
            weight = (l + r) / 2 # Эвристика: берем среднее
            distance = current_dist + weight
            if distance < distances[v]:
                distances[v] = distance
                parent[v] = u
                heapq.heappush(pq, (distance, v))
                
    exec_time = (time.perf_counter() - start_time) * 1000 # в миллисекундах
    
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

def run_xu():
    dataset_dir = "dataset"
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    
    output_file = os.path.join(results_dir, "xu_results.csv")
    files = sorted([f for f in os.listdir(dataset_dir) if f.endswith(".txt")])
    print(f"Запуск Xu Heuristic для {len(files)} графов...")
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # ДОБАВЛЕНО: новая колонка xu_path_length
        writer.writerow(["graph_file", "execution_time_ms", "xu_cost_real", "xu_path_length"])
        
        for filename in files:
            n, adj, start, end = load_graph_simple(os.path.join(dataset_dir, filename))
            
            path, exec_time = solve_xu(n, adj, start, end)
            real_cost = get_real_cost_of_path(path, adj)
            path_length = len(path) - 1 if len(path) > 1 else 0
            
            writer.writerow([filename, exec_time, real_cost, path_length])
            if int(filename.split('_')[1]) % 100 == 0:
                print(f"Обработано {filename}...")
                
    print("Алгоритм Xu завершил работу!")

if __name__ == "__main__":
    run_xu()