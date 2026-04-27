import networkx as nx
import matplotlib.pyplot as plt

class IntervalGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.start_node = None
        self.end_node = None
        self.num_nodes = 0

    def add_edge(self, u, v, l, r, x):
        """Добавляет ребро с интервалом [l, r] и реальным весом x"""
        self.graph.add_edge(u, v, l=l, r=r, x=x)
        
    def get_interval(self, u, v):
        """Возвращает кортеж (l, r) для конкретного ребра"""
        return self.graph[u][v]['interval']

    def get_neighbors(self, u):
        """Возвращает список соседних узлов, куда можно перейти из u"""
        return list(self.graph.successors(u))

    def get_all_edges(self):
        """Возвращает список всех ребер в формате (u, v)"""
        return list(self.graph.edges())

    def draw(self):
        """Отрисовывает граф с интервалами и реальным весом (Ground Truth)"""
        if self.graph.number_of_nodes() == 0:
            print("Граф пуст!")
            return

        plt.figure(figsize=(10, 7))
        pos = nx.spring_layout(self.graph, seed=42)
        
        nx.draw(self.graph, pos, with_labels=True, node_color='lightblue', 
                node_size=700, font_weight='bold', font_size=10, 
                arrowsize=20, edge_color='gray')
        
        # Обновленный формат: читаем ключи l, r и x напрямую
        edge_labels = {(u, v): f"[{d['l']}, {d['r']}]\n(x={d['x']})" 
                       for u, v, d in self.graph.edges(data=True)}
        
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, 
                                     font_color='red', font_size=9)
        
        plt.title(f"Интервальный Граф\n(Старт: {self.start_node}, Финиш: {self.end_node})", fontsize=14)
        plt.show()

    def save_to_txt(self, filename):
        """Сохраняет граф в олимпиадном формате"""
        with open(filename, 'w') as f:
            # 1 строка: n m
            f.write(f"{self.num_nodes} {self.graph.number_of_edges()}\n")
            
            # Следующие m строк: u v l r x
            for u, v, d in self.graph.edges(data=True):
                f.write(f"{u} {v} {d['l']} {d['r']} {d['x']}\n")
                
            # Последняя строка: start end
            f.write(f"{self.start_node} {self.end_node}\n")
        # print(f"Сохранено в {filename}")

    @classmethod
    def load_from_txt(cls, filename):
        """Загружает граф из олимпиадного формата"""
        obj = cls()
        with open(filename, 'r') as f:
            lines = f.read().splitlines()
            
            # Парсим первую строку
            n, m = map(int, lines[0].split())
            obj.num_nodes = n
            
            # Парсим ребра
            for i in range(1, m + 1):
                u, v, l, r, x = map(int, lines[i].split())
                obj.add_edge(u, v, l, r, x)
                
            # Парсим последнюю строку
            start, end = map(int, lines[-1].split())
            obj.start_node = start
            obj.end_node = end
            
        return obj