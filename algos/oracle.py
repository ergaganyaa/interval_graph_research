import os
import csv
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

def solve_dijkstra(n, adj, start, end, mode='x'):
    # Теперь храним пару: (суммарная стоимость, количество ребер)
    # Инициализируем бесконечностью для обоих параметров
    distances = [(float('inf'), float('inf'))] * n
    parent = [-1] * n
    
    # Стартовая точка: стоимость 0, количество ребер 0
    distances[start] = (0, 0)
    # В приоритетную очередь кладем (стоимость, количество_ребер, узел)
    pq = [(0, 0, start)]
    
    while pq:
        current_cost, current_edges, u = heapq.heappop(pq)
        
        if u == end: 
            break
            
        # Проверка актуальности текущей пары критериев
        if (current_cost, current_edges) > distances[u]:
            continue
            
        for v, l, r, x in adj[u]:
            weight = x if mode == 'x' else (l + r) / 2
            
            new_cost = current_cost + weight
            new_edges = current_edges + 1 # Каждое новое ребро инкрементирует счетчик
            
            # Магия сравнения кортежей: 
            # Сначала сравнится new_cost, если они равны — сравнится new_edges
            if (new_cost, new_edges) < distances[v]:
                distances[v] = (new_cost, new_edges)
                parent[v] = u
                heapq.heappush(pq, (new_cost, new_edges, v))
                
    # Восстановление пути (остается прежним)
    path = []
    curr = end
    while curr != -1:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    
    final_cost, final_length = distances[end]
    
    # Если путь не найден (осталась бесконечность), возвращаем 0
    if final_cost == float('inf'):
        return float('inf'), 0
        
    return final_cost, final_length

def run_oracle():
    dataset_dir = "dataset"
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    
    output_file = os.path.join(results_dir, "oracle_costs.csv")
    files = sorted([f for f in os.listdir(dataset_dir) if f.endswith(".txt")])
    
    print(f"Запуск Оракула для {len(files)} графов...")
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # ДОБАВЛЕНО: новая колонка ideal_path_length
        writer.writerow(["graph_file", "num_nodes", "ideal_cost_real", "ideal_path_length"])
        
        for filename in files:
            path = os.path.join(dataset_dir, filename)
            n, adj, start, end = load_graph_simple(path)
            
            ideal_cost, ideal_length = solve_dijkstra(n, adj, start, end, mode='x')
            
            writer.writerow([filename, n, ideal_cost, ideal_length])
            if int(filename.split('_')[1]) % 100 == 0:
                print(f"Обработано {filename}...")
                
    print("Оракул завершил работу!")

if __name__ == "__main__":
    run_oracle()