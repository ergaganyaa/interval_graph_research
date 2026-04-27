import os
import csv
import time
from ortools.linear_solver import pywraplp

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

def solve_montemanni(n, adj, start, end):
    # Создаем MILP-солвер (SCIP отлично справляется с целыми числами)
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        print("Ошибка: OR-Tools SCIP солвер не найден!")
        return [], 0

    # Ограничение по времени для огромных графов (10 секунд на 1 граф)
    solver.SetTimeLimit(10000) 

    # 1. ОБЪЯВЛЯЕМ ПЕРЕМЕННЫЕ
    # x[(u,v)] - бинарная: 1 если ребро (u,v) в нашем пути, 0 если нет
    x = {}
    # d[i] - непрерывная: расстояние до узла i в "худшем сценарии"
    d = {}

    for u in range(n):
        d[u] = solver.NumVar(0, solver.infinity(), f'd_{u}')
        for v, l, r, real_x in adj[u]:
            x[(u, v)] = solver.IntVar(0, 1, f'x_{u}_{v}')

    # 2. ОГРАНИЧЕНИЯ: НЕПРЕРЫВНОСТЬ ПУТИ (Flow Conservation)
    # Сумма входящих x равна сумме исходящих x для всех транзитных узлов
    for i in range(n):
        out_flow = sum(x[(i, v)] for v, _, _, _ in adj[i])
        in_flow = sum(x[(u, i)] for u in range(n) for v, _, _, _ in adj[u] if v == i)
        
        if i == start:
            solver.Add(out_flow - in_flow == 1)
        elif i == end:
            solver.Add(out_flow - in_flow == -1)
        else:
            solver.Add(out_flow - in_flow == 0)

    # 3. ОГРАНИЧЕНИЯ: ПОИСК КРАТЧАЙШЕГО ПУТИ (Формула Карасана)
    solver.Add(d[start] == 0)
    for u in range(n):
        for v, l, r, real_x in adj[u]:
            # Ключевое уравнение: d[v] <= d[u] + (L_ij + (R_ij - L_ij) * x_ij)
            solver.Add(d[v] <= d[u] + l + (r - l) * x[(u, v)])

    # 4. ЦЕЛЕВАЯ ФУНКЦИЯ: Минимизация Max Regret
    # Регрет = Сумма R выбранного пути минус d_end (длина лучшего альтернативного пути)
    robust_cost = sum(r * x[(u, v)] for u in range(n) for v, l, r, _ in adj[u])
    solver.Minimize(robust_cost - d[end])

    # 5. ЗАПУСК ДВИЖКА
    start_time = time.perf_counter()
    status = solver.Solve()
    exec_time = (time.perf_counter() - start_time) * 1000

    # 6. ИЗВЛЕЧЕНИЕ ПУТИ
    path = []
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        curr = start
        path.append(curr)
        # Восстанавливаем цепочку по переменным x, которые равны 1
        while curr != end:
            next_node = None
            for v, _, _, _ in adj[curr]:
                if x[(curr, v)].solution_value() > 0.5: # Если 1
                    next_node = v
                    break
            if next_node is None: 
                break # Защита от зацикливания, если солвер не нашел точный путь
            path.append(next_node)
            curr = next_node
    
    return path, exec_time

def get_real_cost_of_path(path, adj):
    if not path: return float('inf')
    edge_map = {}
    for u in range(len(adj)):
        for v, l, r, x in adj[u]:
            edge_map[(u, v)] = x
    total_x = 0
    for i in range(len(path) - 1):
        total_x += edge_map.get((path[i], path[i+1]), 0)
    return total_x

def run_montemanni():
    dataset_dir = "dataset"
    results_dir = "results"
    output_file = os.path.join(results_dir, "montemanni_results.csv")
    files = sorted([f for f in os.listdir(dataset_dir) if f.endswith(".txt")])
    
    print(f"Запуск Montemanni/Karasan (OR-Tools) для {len(files)} графов...")
    print("ВНИМАНИЕ: На графах > 5000 узлов MILP солвер может задумываться. Терпение!\n")
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["graph_file", "execution_time_ms", "montemanni_cost_real", "montemanni_path_length"])
        
        for filename in files:
            n, adj, start, end = load_graph_simple(os.path.join(dataset_dir, filename))
            
            path, exec_time = solve_montemanni(n, adj, start, end)
            real_cost = get_real_cost_of_path(path, adj)
            path_length = len(path) - 1 if len(path) > 1 else 0
            
            writer.writerow([filename, exec_time, real_cost, path_length])
            if int(filename.split('_')[1]) % 10 == 0:
                print(f"Обработано {filename} ({exec_time:.1f} ms)...")
                
    print("Алгоритм Montemanni (Robust) успешно завершил работу!")

if __name__ == "__main__":
    run_montemanni()