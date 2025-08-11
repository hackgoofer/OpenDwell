from collections import defaultdict

class ValueExaminor:
    comparisons = defaultdict(list)

    def _build_graph(self, pairs):
        graph = {}
        for greater, lesser, reason, date in pairs:
            if greater not in graph:
                graph[greater] = []
            graph[greater].append(lesser)
            self.comparisons[greater, lesser].append((reason, date))
        return graph

    def _find_all_paths(self, graph, start, path=[], conflict_callback=None):
        path = path + [start]
        if start not in graph:
            return [path]
        paths = []
        for node in graph[start]:
            if node in path:  # Detect cycle (conflict)
                print(f"Conflict detected: {' > '.join(path + [node])}")
                if conflict_callback:
                  conflict_callback(path + [node], self.comparisons)
                continue
            newpaths = self._find_all_paths(graph, node, path, conflict_callback)
            for newpath in newpaths:
                paths.append(newpath)
        return paths

    def derive_orders(self, pairs, conflict_callback=None):
        graph = self._build_graph(pairs)
        all_paths = []
        for node in graph:
            all_paths.extend(self._find_all_paths(graph, node, conflict_callback=conflict_callback))
        return all_paths
    
    def has_conflict(self, pairs):
        graph = self._build_graph(pairs)
        for node in graph:
            paths = self._find_all_paths(graph, node)
            if len(paths) > 1:
                return True
        return False