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

def solve_moghanni(n, adj, start, end):
    best_ranks = [float('inf')] * n
    parent = [-1] * n
    best_ranks[start] = 0
    
    # В куче храним: (Rank, u, (U_l, U_r, L_l, L_r))
    # U - Upper approximation, L - Lower approximation
    pq = [(0, start, (0, 0, 0, 0))]
    
    start_time = time.perf_counter()
    
    while pq:
        current_rank, u, (cul, cur, cll, clr) = heapq.heappop(pq)
        
        if u == end: break
        if current_rank > best_ranks[u]: continue
            
        for v, l, r, x in adj[u]:
            width = r - l
            margin = width * 0.2
            
            # Маппинг в Rough Interval
            edge_ul, edge_ur = l, r
            edge_ll, edge_lr = l + margin, r - margin
            
            # Сложение Rough интервалов
            nul, nur = cul + edge_ul, cur + edge_ur
            nll, nlr = cll + edge_ll, clr + edge_lr
            
            # Дефаззификация (Ranking) для Moghanni
            # Берем среднее от Lower и Upper, + штраф за ширину Upper
            expected_u = (nul + nur) / 2
            expected_l = (nll + nlr) / 2
            new_rank = (expected_u + expected_l) / 2 + 0.1 * (nur - nul)
            
            if new_rank < best_ranks[v]:
                best_ranks[v] = new_rank
                parent[v] = u
                heapq.heappush(pq, (new_rank, v, (nul, nur, nll, nlr)))
                
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

def run_moghanni():
    dataset_dir = "dataset"
    results_dir = "results"
    output_file = os.path.join(results_dir, "moghanni_results.csv")
    files = sorted([f for f in os.listdir(dataset_dir) if f.endswith(".txt")])
    print(f"Запуск Moghanni (Rough Graphs) для {len(files)} графов...")
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["graph_file", "execution_time_ms", "moghanni_cost_real", "moghanni_path_length"])
        
        for filename in files:
            n, adj, start, end = load_graph_simple(os.path.join(dataset_dir, filename))
            path, exec_time = solve_moghanni(n, adj, start, end)
            real_cost = get_real_cost_of_path(path, adj)
            path_length = len(path) - 1 if len(path) > 1 else 0
            writer.writerow([filename, exec_time, real_cost, path_length])
            
    print("Алгоритм Moghanni завершил работу!")

if __name__ == "__main__":
    run_moghanni()