#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 3. Простые сортировки и QuickSort с рандомизацией — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-03 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Запуск: python lab03-simple-sorts-quicksort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import time
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Простые сортировки со счётчиками (сортируют КОПИЮ входа, вход не меняют)
#    Каждая функция возвращает кортеж: (отсортированный список,
#    число сравнений ключей, число обменов/перемещений элементов).
# ---------------------------------------------------------------------------


def bubble_sort(a: list) -> tuple[list, int, int]:
    """Сортировка пузырьком. Ожидаемая сложность: O(n²) в среднем/худшем, O(n) в лучшем."""
    arr = list(a)
    n = len(arr)
    comps = 0
    swaps = 0
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            comps += 1
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                swapped = True
        if not swapped:
            break
    return arr, comps, swaps


def insertion_sort(a: list) -> tuple[list, int, int]:
    """Сортировка вставками. Лучший: O(n), худший/средний: O(n²)."""
    arr = list(a)
    n = len(arr)
    comps = 0
    shifts = 0
    for i in range(1, n):
        key = arr[i]
        j = i - 1
        while j >= 0:
            comps += 1
            if arr[j] > key:
                arr[j + 1] = arr[j]
                shifts += 1
                j -= 1
            else:
                break
        arr[j + 1] = key
        if j != i - 1:
            shifts += 1
    return arr, comps, shifts


def selection_sort(a: list) -> tuple[list, int, int]:
    """Сортировка выбором. Всегда O(n²) сравнений — не зависит от входа."""
    arr = list(a)
    n = len(arr)
    comps = 0
    swaps = 0
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            comps += 1
            if arr[j] < arr[min_idx]:
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            swaps += 1
    return arr, comps, swaps


# ---------------------------------------------------------------------------
# 2. QuickSort с рандомизированным опорным элементом
# ---------------------------------------------------------------------------


def quick_sort(a: list, rng: random.Random | None = None) -> list:
    """QuickSort с выбором опорного через rng.randrange. Возвращает новый список.

    Ожидаемая сложность: в среднем O(n log n), в худшем случае O(n²).
    Рандомизация делает худший случай практически невозможным на любом входе.
    rng передаётся снаружи, чтобы запуск был воспроизводим по seed варианта.
    """
    if rng is None:
        rng = random.Random()
    
    arr = list(a)  # работаем с копией, чтобы не менять исходный список

    def _qs(lo: int, hi: int):
        if lo < hi:
            # Рандомизированный выбор опорного элемента
            pivot_idx = rng.randrange(lo, hi + 1)
            # Меняем его с последним для удобства схемы разбиения Lomuto
            arr[pivot_idx], arr[hi] = arr[hi], arr[pivot_idx]
            
            pivot = arr[hi]
            i = lo - 1
            for j in range(lo, hi):
                if arr[j] <= pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
            
            # Возвращаем опорный элемент на его итоговую позицию
            arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
            
            # Рекурсивная сортировка левой и правой частей
            # (i + 1 — индекс опорного, его пропускаем)
            _qs(lo, i)
            _qs(i + 2, hi)

    if arr:
        _qs(0, len(arr) - 1)
    return arr


# ---------------------------------------------------------------------------
# 3. Демонстрация стабильности на парах (ключ, метка)
# ---------------------------------------------------------------------------


def stability_demo() -> None:
    """Показать, какие из четырёх сортировок стабильны.

    План: взять массив пар (ключ, метка) с повторяющимися ключами, например
    [(2, "a"), (1, "b"), (2, "c"), (1, "d")], отсортировать каждой сортировкой
    по ключу (сравнение только по p[0]!) и напечатать порядок меток при равных
    ключах. Вывод о стабильности каждой сортировки включить в отчёт.
    """
    # Класс-обёртка: сравниваем объекты ТОЛЬКО по ключу, игнорируя метку
    class Item:
        def __init__(self, key, label):
            self.key = key
            self.label = label
        def __lt__(self, other): return self.key < other.key
        def __le__(self, other): return self.key <= other.key
        def __gt__(self, other): return self.key > other.key
        def __ge__(self, other): return self.key >= other.key
        def __repr__(self): return f"({self.key}, '{self.label}')"

    data = [Item(2, "a"), Item(1, "b"), Item(2, "c"), Item(1, "d")]
    print("\n--- Демонстрация стабильности ---")
    print(f"Исходный массив: {data}")
    
    for name, fn in ALGORITHMS.items():
        res = fn(list(data))
        labels = [item.label for item in res]
        
        # Проверяем сохранение исходного порядка меток при равных ключах:
        # для ключа 1: 'b' должно идти перед 'd'
        # для ключа 2: 'a' должно идти перед 'c'
        is_stable = (labels.index('b') < labels.index('d')) and (labels.index('a') < labels.index('c'))
        status = "стабильна" if is_stable else "нестабильна"
        print(f"{name:16}: {[str(x) for x in res]} -> {status}")


# ---------------------------------------------------------------------------
# 4. Классы входов (данные по варианту, детерминированно по seed)
# ---------------------------------------------------------------------------


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:
    """Три класса входов размера n: упорядоченный, случайный, обратный."""
    rng = random.Random(seed + n)  # свой поток для каждого размера
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    return {
        "упорядоченный": sorted(data),
        "случайный": data,
        "обратный": sorted(data, reverse=True),
    }


# ---------------------------------------------------------------------------
# 5. Верификация (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------

ALGORITHMS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],
    "insertion_sort": lambda a: insertion_sort(a)[0],
    "selection_sort": lambda a: selection_sort(a)[0],
    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}


def is_sorted(a: list) -> bool:
    """Инвариант 1: неубывающий порядок элементов."""
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


def self_check() -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [5, 5, 5, 5],          # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for name, fn in ALGORITHMS.items():
        for a in boundary:
            res = fn(list(a))
            assert is_sorted(res), f"{name}: нарушен порядок на {a}"
            assert sorted(res) == sorted(a), f"{name}: не перестановка входа {a}"

    # Сверка с эталоном из стандартной библиотеки на сотнях случайных входов.
    rng = random.Random(0)
    for _ in range(300):
        a = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        expected = sorted(a)
        for name, fn in ALGORITHMS.items():
            assert fn(list(a)) == expected, f"{name}: расходится с sorted() на {a}"

    # Счётчики: у сортировки выбором ровно n*(n-1)/2 сравнений на любом входе.
    _, comparisons, _ = selection_sort([3, 1, 2, 5, 4])
    assert comparisons == 10, "selection_sort: неверный счётчик сравнений"
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 6. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES_QUADRATIC = [500, 1_000, 2_000, 4_000, 8_000]     # для простых сортировок
SIZES_QUICK = [1_000, 3_000, 10_000, 30_000, 100_000]   # для QuickSort
REPEATS = 5


def bench(fn, data: list) -> float:
    """Медиана времени выполнения fn(копия data) по REPEATS запускам, с прогревом."""
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        arg = list(data)  # свежая копия: сортировка не должна получать свой результат
        t0 = time.perf_counter()
        fn(arg)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    """Замеры всех алгоритмов на трёх классах входов; результат — таблица в stdout."""
    plans = [
        ("bubble_sort", ALGORITHMS["bubble_sort"], SIZES_QUADRATIC),
        ("insertion_sort", ALGORITHMS["insertion_sort"], SIZES_QUADRATIC),
        ("selection_sort", ALGORITHMS["selection_sort"], SIZES_QUADRATIC),
        ("quick_sort", lambda a: quick_sort(a, random.Random(seed)), SIZES_QUICK),
    ]

    # Собираем данные для графиков: {имя_алгоритма: {класс_входа: [времена]}}
    plot_data = {name: {"упорядоченный": [], "случайный": [], "обратный": []}
                 for name, _, _ in plans}
    sizes_map = {name: sizes for name, _, sizes in plans}

    for name, fn, sizes in plans:
        print(f"\n{name}:")
        for n in sizes:
            for cls, data in make_inputs(n, seed).items():
                t = bench(fn, data)
                print(f"  n={n:>7}  вход={cls:<13} t={t:.6f} c")
                plot_data[name][cls].append(t)

    # Построение log-log графиков по трём классам входов
    plt.figure(figsize=(15, 5))
    classes = ["упорядоченный", "случайный", "обратный"]

    for idx, cls in enumerate(classes):
        plt.subplot(1, 3, idx + 1)
        for name, _, _ in plans:
            sizes = sizes_map[name]
            times = plot_data[name][cls]
            if sizes and times:
                plt.loglog(sizes, times, marker='o', label=name)

        plt.title(f"Вход: {cls}")
        plt.xlabel("Размер входа (N)")
        plt.ylabel("Время (сек)")
        plt.grid(True, which="both", ls="--")
        plt.legend()

    plt.tight_layout()
    plt.savefig("lab03_results.png", dpi=300)
    print("\nГрафики сохранены в 'lab03_results.png'")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    stability_demo()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
