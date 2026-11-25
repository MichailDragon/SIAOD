#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ДЗ 2. Эксперимент: высота BST и деградация операций — итоговое решение.

Запуск: python dz02-bst-height-starter.py --variant N
"""
from __future__ import annotations

import argparse
import math
import random
import statistics
import time
from collections import deque
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # без GUI, сохраняет в файл
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Узел и итеративная вставка
# ---------------------------------------------------------------------------

class Node:
    """Узел BST: ключ и ссылки на левое и правое поддеревья."""
    __slots__ = ("key", "left", "right")

    def __init__(self, key: int) -> None:
        self.key = key
        self.left: Node | None = None
        self.right: Node | None = None


def insert_iter(root: Node | None, key: int) -> Node:
    """Итеративная вставка ключа в BST; возвращает корень дерева."""
    if root is None:
        return Node(key)
    curr = root
    while True:
        if key < curr.key:
            if curr.left is None:
                curr.left = Node(key)
                break
            curr = curr.left
        elif key > curr.key:
            if curr.right is None:
                curr.right = Node(key)
                break
            curr = curr.right
        else:
            break  # дубликат — игнорируем
    return root


def build_bst(keys: list[int]) -> Node | None:
    """Строит BST последовательной итеративной вставкой ключей."""
    root: Node | None = None
    for key in keys:
        root = insert_iter(root, key)
    return root


# ---------------------------------------------------------------------------
# 2. Измеряемые величины: высота и средняя глубина узла
# ---------------------------------------------------------------------------

def tree_height(root: Node | None) -> int:
    """Высота дерева (число рёбер на самом длинном пути). Итеративно (BFS)."""
    if root is None:
        return -1
    height = -1
    queue = deque([root])
    while queue:
        height += 1
        for _ in range(len(queue)):
            node = queue.popleft()
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return height


def sum_depths(root: Node | None) -> int:
    """Сумма глубин всех узлов (глубина корня — 0). Итеративно (BFS)."""
    if root is None:
        return 0
    total = 0
    queue = deque([(root, 0)])
    while queue:
        node, depth = queue.popleft()
        total += depth
        if node.left:
            queue.append((node.left, depth + 1))
        if node.right:
            queue.append((node.right, depth + 1))
    return total


def count_nodes(root: Node | None) -> int:
    """Число узлов дерева. Итеративно (BFS)."""
    if root is None:
        return 0
    count = 0
    queue = deque([root])
    while queue:
        node = queue.popleft()
        count += 1
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return count


def avg_depth(root: Node | None) -> float:
    """Средняя глубина узла."""
    n = count_nodes(root)
    if n == 0:
        return 0.0
    return sum_depths(root) / n


def inorder_keys(root: Node | None) -> list[int]:
    """Ключи in-order-обхода (итеративно, с явным стеком)."""
    result = []
    stack = []
    curr = root
    while stack or curr:
        while curr:
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()
        result.append(curr.key)
        curr = curr.right
    return result


# ---------------------------------------------------------------------------
# 3. Верификация
# ---------------------------------------------------------------------------

def self_check() -> None:
    """Граничные деревья, аналитические значения, сверка с эталоном sorted()."""
    assert tree_height(None) == -1
    assert avg_depth(None) == 0.0
    single = build_bst([42])
    assert tree_height(single) == 0
    assert count_nodes(single) == 1

    small = build_bst([2, 1, 3])
    assert tree_height(small) == 1
    assert sum_depths(small) == 2

    n = 100
    degenerate = build_bst(list(range(1, n + 1)))
    assert tree_height(degenerate) == n - 1
    assert avg_depth(degenerate) == (n - 1) / 2

    rng = random.Random(0)
    for _ in range(200):
        keys = rng.sample(range(-1000, 1000), rng.randint(1, 60))
        root = build_bst(keys)
        assert inorder_keys(root) == sorted(keys)
        assert count_nodes(root) == len(keys)
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 4. Эксперимент и замеры
# ---------------------------------------------------------------------------

SIZES = [100, 300, 1_000, 3_000, 10_000]
REPEATS = 5


def random_keys(n: int, rng: random.Random) -> list[int]:
    """n уникальных случайных ключей."""
    return rng.sample(range(10 * n), n)


def ordered_keys(n: int) -> list[int]:
    """n упорядоченных ключей 1..n."""
    return list(range(1, n + 1))


def search_iter(root: Node | None, key: int) -> bool:
    """Итеративный поиск ключа в BST."""
    curr = root
    while curr is not None:
        if key == curr.key:
            return True
        elif key < curr.key:
            curr = curr.left
        else:
            curr = curr.right
    return False


def bench_search(root: Node | None, queries: list[int]) -> float:
    """Медиана времени поиска всех ключей queries по REPEATS запускам."""
    def run() -> None:
        for q in queries:
            search_iter(root, q)

    run()  # прогрев
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        run()
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_experiment(seed: int) -> None:
    """Таблица замеров + графики."""
    rng = random.Random(seed)
    
    print("\n--- Эксперимент: высота и средняя глубина BST ---\n")
    header = (f"{'n':>7} {'h_случ':>8} {'d_случ':>8} "
              f"{'h_упор':>8} {'d_упор':>8} {'log2(n)':>8} "
              f"{'t_случ':>10} {'t_упор':>10}")
    print(header)
    
    results = []
    for n in SIZES:
        keys_rand = random_keys(n, rng)
        keys_ord = ordered_keys(n)
        
        root_rand = build_bst(keys_rand)
        root_ord = build_bst(keys_ord)
        
        h_rand = tree_height(root_rand)
        d_rand = avg_depth(root_rand)
        h_ord = tree_height(root_ord)
        d_ord = avg_depth(root_ord)
        log2n = math.log2(n)
        
        # Замеры времени поиска на одних и тех же запросах
        queries = keys_rand[:min(100, n)]  # первые 100 ключей для поиска
        t_rand = bench_search(root_rand, queries)
        t_ord = bench_search(root_ord, queries)
        
        print(f"{n:>7} {h_rand:>8} {d_rand:>8.1f} "
              f"{h_ord:>8} {d_ord:>8.1f} {log2n:>8.1f} "
              f"{t_rand:>10.6f} {t_ord:>10.6f}")
        
        results.append({
            'n': n, 'h_rand': h_rand, 'd_rand': d_rand,
            'h_ord': h_ord, 'd_ord': d_ord, 'log2n': log2n,
            't_rand': t_rand, 't_ord': t_ord
        })
    
    # Построение графиков
    ns = [r['n'] for r in results]
    h_rand = [r['h_rand'] for r in results]
    h_ord = [r['h_ord'] for r in results]
    log2n = [r['log2n'] for r in results]
    linear = ns  # n для сравнения
    
    d_rand = [r['d_rand'] for r in results]
    d_ord = [r['d_ord'] for r in results]
    
    # График 1: высота
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    ax1.plot(ns, h_rand, 'bo-', label='Случайный поток', linewidth=2)
    ax1.plot(ns, h_ord, 'rs-', label='Упорядоченный поток', linewidth=2)
    ax1.plot(ns, log2n, 'g--', label='log₂(n)', linewidth=1.5)
    ax1.plot(ns, linear, 'm--', label='n', linewidth=1.5)
    ax1.set_xlabel('n')
    ax1.set_ylabel('Высота h(n)')
    ax1.set_title('Высота BST vs опорные кривые')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # График 2: средняя глубина
    ax2.plot(ns, d_rand, 'bo-', label='Случайный поток', linewidth=2)
    ax2.plot(ns, d_ord, 'rs-', label='Упорядоченный поток', linewidth=2)
    ax2.plot(ns, log2n, 'g--', label='log₂(n)', linewidth=1.5)
    ax2.plot(ns, [n/2 for n in ns], 'm--', label='n/2', linewidth=1.5)
    ax2.set_xlabel('n')
    ax2.set_ylabel('Средняя глубина')
    ax2.set_title('Средняя глубина узла vs опорные кривые')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('dz02_bst_height_graphs.png', dpi=150, bbox_inches='tight')
    print("\nГрафики сохранены: dz02_bst_height_graphs.png")
    
    # График 3: время поиска
    fig2, ax3 = plt.subplots(figsize=(8, 5))
    ax3.plot(ns, [r['t_rand'] for r in results], 'bo-', label='Случайное дерево', linewidth=2)
    ax3.plot(ns, [r['t_ord'] for r in results], 'rs-', label='Вырожденное дерево', linewidth=2)
    ax3.set_xlabel('n')
    ax3.set_ylabel('Время поиска 100 ключей, с')
    ax3.set_title('Время поиска в BST')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('dz02_search_time_graph.png', dpi=150, bbox_inches='tight')
    print("График времени поиска сохранён: dz02_search_time_graph.png")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_experiment(seed)


if __name__ == "__main__":
    main()