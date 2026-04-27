import random

class GraphFactory:
    @staticmethod
    def generate_fast_txt(filename, num_nodes, num_edges, min_weight, max_weight):
        # Используем set (множество) для сверхбыстрой проверки дубликатов
        edges = set()

        # 1. Гарантированный путь
        path_length = random.randint(0, num_nodes // 10)
        if num_nodes > 2 and path_length > 0:
            middle_nodes = random.sample(range(1, num_nodes - 1), path_length)
            path = [0] + middle_nodes + [num_nodes - 1]
        else:
            path = [0, num_nodes - 1]

        for i in range(len(path) - 1):
            edges.add((path[i], path[i+1]))

        # 2. Добиваем случайным шумом
        while len(edges) < num_edges:
            u = random.randint(0, num_nodes - 1)
            v = random.randint(0, num_nodes - 1)
            # Игнорируем петли
            if u != v:
                edges.add((u, v))

        # 3. Сразу пишем в файл (скорость записи максимальная)
        with open(filename, 'w') as f:
            f.write(f"{num_nodes} {len(edges)}\n")
            for u, v in edges:
                l = random.randint(min_weight, max_weight - 5)
                r = random.randint(l + 1, max_weight)
                x = random.randint(l, r)
                f.write(f"{u} {v} {l} {r} {x}\n")
            f.write(f"0 {num_nodes - 1}\n")