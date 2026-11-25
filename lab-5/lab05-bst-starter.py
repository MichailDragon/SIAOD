#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 5. Бинарное дерево поиска: обходы, вставка и удаление — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-05 и правилами использования генеративного ИИ
(docs/ai-verification.md). Класс BST понадобится повторно в ДЗ 2
(Cases/kim-02-bst-height-experiment.md) — держите его чистым и переносимым.

Запуск: python lab05-bst-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
import traceback
from collections import deque
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Бинарное дерево поиска (реализуется вручную, без сторонних библиотек)
# ---------------------------------------------------------------------------


class Node:
    """Узел BST: ключ и ссылки на левое и правое поддеревья."""

    __slots__ = ("key", "left", "right")

    def __init__(self, key: int) -> None:
        self.key = key
        self.left: Node | None = None
        self.right: Node | None = None


class BST:
    """Бинарное дерево поиска без дубликатов ключей.

    Инвариант: для каждого узла все ключи левого поддерева меньше key,
    все ключи правого — больше. Ожидаемая сложность операций: O(h),
    где h — высота дерева. В сбалансированном случае h = O(log n),
    в вырожденном (цепочка) h = O(n).
    """

    def __init__(self) -> None:
        self.root: Node | None = None

    def insert(self, key: int) -> None:
        """Вставка ключа; повторная вставка существующего ключа игнорируется."""
        if self.root is None:
            self.root = Node(key)
            return
        
        curr = self.root
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
                break  # Ключ уже существует, игнорируем

    def search(self, key: int) -> bool:
        """Возвращает True, если ключ есть в дереве."""
        curr = self.root
        while curr:
            if key == curr.key:
                return True
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return False

    def delete(self, key: int) -> None:
        """Удаление ключа. Обработать три случая."""
        parent = None
        curr = self.root
        
        # 1. Поиск удаляемого узла и его родителя
        while curr and curr.key != key:
            parent = curr
            if key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        
        if curr is None:
            return  # Ключ не найден

        # 2. Случай: у узла два ребёнка
        if curr.left and curr.right:
            # Находим преемника (минимум в правом поддереве)
            succ_parent = curr
            succ = curr.right
            while succ.left:
                succ_parent = succ
                succ = succ.left
            
            # Копируем ключ преемника в текущий узел
            curr.key = succ.key
            
            # Теперь нам нужно удалить узел преемника (у него точно нет левого ребёнка)
            curr = succ
            parent = succ_parent

        # 3. Случаи: 0 или 1 ребёнок
        # Определяем ребёнка, который заменит удаляемый узел (может быть None)
        child = curr.right if curr.right else curr.left
        
        if parent is None:
            # Удаляем корень
            self.root = child
        elif parent.left == curr:
            parent.left = child
        else:
            parent.right = child

    # -- Обходы --------------------------------------------------------------

    def in_order(self) -> list[int]:
        """Симметричный обход (лево — узел — право): рекурсивно."""
        res = []
        def dfs(node: Node | None):
            if node:
                dfs(node.left)
                res.append(node.key)
                dfs(node.right)
        dfs(self.root)
        return res

    def pre_order(self) -> list[int]:
        """Прямой обход (узел — лево — право): рекурсивно."""
        res = []
        def dfs(node: Node | None):
            if node:
                res.append(node.key)
                dfs(node.left)
                dfs(node.right)
        dfs(self.root)
        return res

    def post_order(self) -> list[int]:
        """Обратный обход (лево — право — узел): рекурсивно."""
        res = []
        def dfs(node: Node | None):
            if node:
                dfs(node.left)
                dfs(node.right)
                res.append(node.key)
        dfs(self.root)
        return res

    def level_order(self) -> list[int]:
        """Обход в ширину по уровням: итеративно через очередь (deque)."""
        if self.root is None:
            return []
        res = []
        q = deque([self.root])
        while q:
            node = q.popleft()
            res.append(node.key)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        return res

    # -- Характеристики дерева ----------------------------------------------

    def height(self) -> int:
        """Высота дерева: число рёбер на самом длинном пути от корня.
        Пустое дерево имеет высоту -1, дерево из одного узла — 0.
        """
        def get_h(node: Node | None) -> int:
            if node is None:
                return -1
            return 1 + max(get_h(node.left), get_h(node.right))
        return get_h(self.root)

    def size(self) -> int:
        """Число узлов в дереве."""
        def get_s(node: Node | None) -> int:
            if node is None:
                return 0
            return 1 + get_s(node.left) + get_s(node.right)
        return get_s(self.root)


# ---------------------------------------------------------------------------
# 2. Верификация: инвариант BST и сверка с эталоном (docs/ai-verification.md)
# ---------------------------------------------------------------------------


class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""


def expect(condition: bool, message: str) -> None:
    """Явная проверка вместо assert: assert-ы исчезают при запуске python -O."""
    if not condition:
        raise SelfCheckError(message)


def build(keys) -> BST:
    """Дерево, полученное последовательной вставкой keys в пустое BST."""
    tree = BST()
    for k in keys:
        tree.insert(k)
    return tree


def expect_search(tree: BST, key: int, present: bool, where: str) -> None:
    """search(key) обязан вернуть именно True или False."""
    got = tree.search(key)
    expect(got is present, f"{where}: search({key}) вернул {got!r}, ожидалось {present}")


TRAVERSALS = ("in_order", "pre_order", "post_order", "level_order")

# Деревья с известными обходами: идеальное дерево 4-2-6-1-3-5-7 (вставка по уровням)
# и пример лекции 5, где у узлов 10 и 14 по одному ребёнку.
KNOWN_TREES = {
    (4, 2, 6, 1, 3, 5, 7): {
        "in_order": [1, 2, 3, 4, 5, 6, 7],
        "pre_order": [4, 2, 1, 3, 6, 5, 7],
        "post_order": [1, 3, 2, 5, 7, 6, 4],
        "level_order": [4, 2, 6, 1, 3, 5, 7],
        "height": 2,
        "size": 7,
    },
    (8, 3, 10, 1, 6, 14, 4, 7, 13): {
        "in_order": [1, 3, 4, 6, 7, 8, 10, 13, 14],
        "pre_order": [8, 3, 1, 6, 4, 7, 10, 14, 13],
        "post_order": [1, 4, 7, 6, 3, 13, 14, 10, 8],
        "level_order": [8, 3, 10, 1, 6, 14, 4, 7, 13],
        "height": 3,
        "size": 9,
    },
}

# Удаление узла с двумя детьми: (ключи, удаляемый ключ, pre_order после замены
# преемником, pre_order после замены предшественником). В последних двух случаях
# у преемника (предшественника) есть свой ребёнок.
TWO_CHILDREN_CASES = [
    ((8, 3, 10, 1, 6, 14, 4, 7, 13), 3, [8, 4, 1, 6, 7, 10, 14, 13], [8, 1, 6, 4, 7, 10, 14, 13]),
    ((8, 3, 10, 1, 6, 14, 4, 7, 13), 6, [8, 3, 1, 7, 4, 10, 14, 13], [8, 3, 1, 4, 7, 10, 14, 13]),
    ((8, 3, 10, 1, 6, 14, 4, 7, 13), 8, [10, 3, 1, 6, 4, 7, 14, 13], [7, 3, 1, 6, 4, 10, 14, 13]),
    ((50, 30, 70, 60, 80, 65), 50, [60, 30, 70, 65, 80], [30, 70, 60, 65, 80]),
    ((50, 30, 70, 60, 80, 65), 70, [50, 30, 80, 60, 65], [50, 30, 65, 60, 80]),
]


def check_insert_search() -> None:
    """Поиск в пустом дереве, вставка, поиск есть/нет, повторная вставка."""
    tree = BST()
    expect_search(tree, 1, False, "пустое дерево")
    tree.insert(5)
    expect_search(tree, 5, True, "дерево из одного узла 5")
    expect_search(tree, 4, False, "дерево из одного узла 5")

    keys = [5, 2, 8, 1, 3, 9, 7]
    tree = build(keys)
    for k in range(11):
        expect_search(tree, k, k in keys, f"дерево из вставок {keys}")
    got = tree.in_order()
    expect(got == sorted(keys), f"in_order() после вставок {keys}: {got}, ожидалось {sorted(keys)}")
    tree.insert(5)
    tree.insert(1)
    got = tree.in_order()
    expect(got == sorted(keys), f"повторная вставка 5 и 1 изменила дерево: in_order() = {got}")


def check_traversals() -> None:
    """Четыре обхода: пустое дерево и деревья с известным ответом."""
    empty = BST()
    for name in TRAVERSALS:
        got = getattr(empty, name)()
        expect(got == [], f"{name}() пустого дерева: {got}, ожидалось []")
    for keys, answer in KNOWN_TREES.items():
        tree = build(keys)
        for name in TRAVERSALS:
            got = getattr(tree, name)()
            expect(got == answer[name],
                   f"{name}() дерева из вставок {list(keys)}: {got}, ожидалось {answer[name]}")


def check_height_size() -> None:
    """Высота в рёбрах (пустое дерево -1, один узел 0) и число узлов."""
    cases = [("пустое дерево", (), -1, 0), ("один узел 5", (5,), 0, 1)]
    cases += [(f"дерево из вставок {list(keys)}", keys, answer["height"], answer["size"])
              for keys, answer in KNOWN_TREES.items()]
    cases.append(("ключи 1, 2, …, 50 по возрастанию (цепочка)", tuple(range(1, 51)), 49, 50))
    for where, keys, height, size in cases:
        tree = build(keys)
        got_h, got_s = tree.height(), tree.size()
        expect(got_h == height, f"{where}: height() = {got_h}, ожидалось {height}")
        expect(got_s == size, f"{where}: size() = {got_s}, ожидалось {size}")


def check_delete() -> None:
    """Пустое дерево, лист, один ребёнок, корень с двумя детьми, отсутствующий и последний ключ."""
    tree = BST()
    tree.delete(1)  # удаление из пустого дерева не должно падать
    got = tree.in_order()
    expect(got == [], f"delete(1) из пустого дерева: in_order() = {got}")

    keys = [5, 2, 8, 1, 3]
    tree = build(keys)
    left = set(keys)
    steps = [(1, "лист 1"), (2, "узел 2 с одним ребёнком"), (5, "корень 5 с двумя детьми"),
             (4, "отсутствующий ключ 4"), (3, "ключ 3"), (8, "последний ключ 8")]
    for k, what in steps:
        tree.delete(k)
        left.discard(k)
        where = f"дерево из вставок {keys}, удаление: {what}"
        got = tree.in_order()
        expect(got == sorted(left), f"{where}: in_order() = {got}, ожидалось {sorted(left)}")
        expect_search(tree, k, False, where)
        for rest in left:
            expect_search(tree, rest, True, where)
    got_h, got_s = tree.height(), tree.size()
    expect(got_h == -1 and got_s == 0,
           f"после удаления всех ключей: height() = {got_h}, size() = {got_s}, ожидалось -1 и 0")


def check_delete_two_children() -> None:
    """Узел с двумя детьми получает ключ преемника (или предшественника): форму дерева
    после удаления однозначно показывает pre_order()."""
    for keys, k, by_successor, by_predecessor in TWO_CHILDREN_CASES:
        tree = build(keys)
        tree.delete(k)
        where = f"delete({k}) в дереве из вставок {list(keys)}"
        rest = sorted(set(keys) - {k})
        got = tree.in_order()
        expect(got == rest, f"{where}: in_order() = {got}, ожидалось {rest}")
        got = tree.pre_order()
        expect(got in (by_successor, by_predecessor),
               f"{where}: pre_order() = {got}; при замене преемником ожидалось {by_successor}, "
               f"предшественником — {by_predecessor}")


def check_against_reference() -> None:
    """Случайные команды insert/delete: после каждой in_order() совпадает с sorted(эталона)."""
    rng = random.Random(0)
    for run in range(1, 101):
        tree = BST()
        etalon: set[int] = set()
        for step in range(1, rng.randint(1, 80) + 1):
            k = rng.randint(-30, 30)
            if rng.random() < 0.6:
                tree.insert(k)
                etalon.add(k)
                op = f"insert({k})"
            else:
                tree.delete(k)
                etalon.discard(k)
                op = f"delete({k})"
            # Инвариант BST: in-order даёт строго возрастающую последовательность ключей
            got = tree.in_order()
            expect(got == sorted(etalon), f"прогон {run}, команда №{step} {op}: "
                                          f"in_order() = {got}, эталон {sorted(etalon)}")
        where = f"прогон {run}, итоговое дерево"
        for k in range(-30, 31):
            expect_search(tree, k, k in etalon, where)
        n = len(etalon)
        got = tree.size()
        expect(got == n, f"{where}: size() = {got}, эталон {n}")
        for name in TRAVERSALS[1:]:
            got = getattr(tree, name)()
            expect(sorted(got) == sorted(etalon), f"{where}: {name}() содержит не те ключи: {got}")
        got = tree.height()
        low, high = (-1, -1) if n == 0 else (n.bit_length() - 1, n - 1)
        expect(low <= got <= high,
               f"{where}: height() = {got} при {n} узлах, возможно от {low} до {high}")

def check_bst_invariant() -> None:
    """Рекурсивная проверка инварианта BST с границами.
    
    Для каждого узла проверяется, что его ключ лежит в допустимом диапазоне
    (min_val, max_val). При спуске влево верхняя граница становится key узла,
    при спуске вправо нижняя граница становится key узла.
    """
    def is_valid_bst(node: Node | None, min_val: int, max_val: int) -> bool:
        if node is None:
            return True
        if node.key <= min_val or node.key >= max_val:
            return False
        return (is_valid_bst(node.left, min_val, node.key) and
                is_valid_bst(node.right, node.key, max_val))

    # Тест 1: пустое дерево
    tree = BST()
    expect(is_valid_bst(tree.root, float('-inf'), float('inf')),
           "пустое дерево должно быть валидным BST")

    # Тест 2: дерево из вставок [5, 2, 8, 1, 3]
    tree = build([5, 2, 8, 1, 3])
    expect(is_valid_bst(tree.root, float('-inf'), float('inf')),
           "дерево из вставок [5, 2, 8, 1, 3] должно быть валидным BST")

    # Тест 3: случайные вставки и удаления (100 прогонов)
    rng = random.Random(0)
    for _ in range(100):
        tree = BST()
        for _ in range(rng.randint(1, 50)):
            k = rng.randint(-100, 100)
            if rng.random() < 0.7:
                tree.insert(k)
            else:
                tree.delete(k)
        expect(is_valid_bst(tree.root, float('-inf'), float('inf')),
               "инвариант BST нарушен после случайных операций")    

def self_check() -> None:
    """Все проверки по разделам; при любой ошибке замеры не выполняются."""
    checks = (
        ("вставка и поиск", check_insert_search),
        ("обходы", check_traversals),
        ("высота и размер", check_height_size),
        ("удаление", check_delete),
        ("удаление узла с двумя детьми", check_delete_two_children),
        ("сверка с эталоном set/sorted", check_against_reference),
        ("инвариант BST (проверка с границами)", check_bst_invariant),
    )
    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except NotImplementedError as err:
            where = traceback.extract_tb(err.__traceback__)[-1].name
            print(f"  {name}: не реализовано — {where} (TODO)")
            failed += 1
        except SelfCheckError as err:
            print(f"  {name}: ОШИБКА — {err}")
            failed += 1
        except Exception:  # noqa: BLE001 — падение реализации тоже результат проверки
            print(f"  {name}: ИСКЛЮЧЕНИЕ")
            traceback.print_exc(file=sys.stdout)
            failed += 1
        else:
            print(f"  {name}: OK")
    if failed:
        raise SystemExit(f"self_check: не пройдено разделов — {failed}; "
                         f"замеры выполняются только после всех проверок.")
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 3. Бенчмарк: поиск в BST против поиска в списке (docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
QUERIES = 1_000  # число поисков на один замер


def bench(fn) -> float:
    """Медиана времени выполнения fn() по REPEATS запускам, с прогревом."""
    fn()  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    """Сравнение времени QUERIES поисков в BST и в списке (оператор in)."""
    rng = random.Random(seed)
    
    n_values = []
    h_values = []
    t_bst_values = []
    t_list_values = []

    print(f"{'n':>8} {'h(BST)':>7} {'t_bst, c':>10} {'t_list, c':>10}")
    for n in SIZES:
        keys = rng.sample(range(10 * n), n)
        queries = [rng.randint(0, 10 * n) for _ in range(QUERIES)]
        
        tree = BST()
        for k in keys:
            tree.insert(k)

        def search_bst() -> None:
            for q in queries:
                tree.search(q)

        def search_list() -> None:
            for q in queries:
                q in keys

        t_bst = bench(search_bst)
        t_list = bench(search_list)
        h = tree.height()
        
        n_values.append(n)
        h_values.append(h)
        t_bst_values.append(t_bst)
        t_list_values.append(t_list)

        print(f"{n:>8} {h:>7} {t_bst:>10.6f} {t_list:>10.6f}")

    # График с двумя осями Y — в нашем стиле
    fig, ax1 = plt.subplots(figsize=(12, 7))
    
    # Левая ось Y — время (логарифмическая)
    ax1.set_xlabel("Размер данных (n)", fontsize=12)
    ax1.set_ylabel("Время выполнения (сек)", fontsize=12)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.grid(True, which="both", ls="--", alpha=0.7)
    
    # Наши цвета: синий для BST, оранжевый для списка
    line1, = ax1.plot(n_values, t_bst_values, 'o-', color='#1f77b4', 
                      label='BST search (O(h))', linewidth=2, markersize=8)
    line2, = ax1.plot(n_values, t_list_values, 's-', color='#ff7f0e', 
                      label='List search (O(n))', linewidth=2, markersize=8)
    
    # Правая ось Y — высота (линейная шкала)
    ax2 = ax1.twinx()
    ax2.set_ylabel("Высота h(BST)", fontsize=12, color="#040404")
    line3, = ax2.plot(n_values, h_values, '^-', color='#2ca02c', 
                      label='h(BST)', linewidth=2, markersize=8)
    ax2.tick_params(axis='y', labelcolor="#040404")
    ax2.set_yscale('linear')  # высота растёт линейно по log n, но шкала обычная
    
    # Общая легенда
    lines = [line1, line2, line3]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', fontsize=11)
    
    plt.title(f"Сравнение времени поиска (QUERIES={QUERIES}, seed={seed})")
    fig.tight_layout()
    
    plt.savefig("lab05_benchmark.png", dpi=300)
    print("\nГрафик сохранён в 'lab05_benchmark.png'")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant  # seed по варианту — см. docs/reproducibility.md
    random.seed(seed)
    self_check()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
