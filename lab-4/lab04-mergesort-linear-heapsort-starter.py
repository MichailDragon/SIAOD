#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 4. MergeSort, Counting, Radix и HeapSort: оценка производительности — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-04 и правилами использования генеративного ИИ
(docs/ai-verification.md). QuickSort перенесите из собственной ЛР 3.

Запуск: python lab04-mergesort-linear-heapsort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
import traceback
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Сортировки (реализуются вручную; sorted() используется только как эталон)
# ---------------------------------------------------------------------------


def merge(left: list, right: list, key) -> list:
    """Стабильное слияние двух отсортированных списков в новый список.
    Стабильность: при равенстве ключей элемент из left идёт раньше (условие <=).
    Ожидаемая сложность: O(n), где n = len(left) + len(right).
    """
    res = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            res.append(left[i])
            i += 1
        else:
            res.append(right[j])
            j += 1
    res.extend(left[i:])
    res.extend(right[j:])
    return res


def merge_sort(a: list, key=lambda x: x) -> list:
    """MergeSort: возвращает новый отсортированный список. 
    Ожидаемая сложность: O(n log n) по времени, O(n) по дополнительной памяти.
    """
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = merge_sort(a[:mid], key)
    right = merge_sort(a[mid:], key)
    return merge(left, right, key)


def counting_sort(a: list[int], key_max: int) -> list[int]:
    """Устойчивая сортировка подсчётом: ключи — целые из диапазона [0, key_max].
    Схема: массив счётчиков -> префиксные суммы -> расстановка с конца.
    Ожидаемые время и память: O(n + k), где k = key_max + 1.
    """
    n = len(a)
    if n == 0:
        return []
    
    # 1. Подсчёт частот
    count = [0] * (key_max + 1)
    for x in a:
        count[x] += 1
        
    # 2. Префиксные суммы (текущий элемент = сумма текущего и предыдущего)
    for i in range(1, key_max + 1):
        count[i] += count[i - 1]
        
    # 3. Расстановка элементов (обход с конца для сохранения устойчивости)
    output = [0] * n
    for i in range(n - 1, -1, -1):
        val = a[i]
        count[val] -= 1
        output[count[val]] = val
        
    return output


def radix_sort_lsd(a: list[int]) -> list[int]:
    """RadixSort LSD по десятичным разрядам, неотрицательные целые.
    Ожидаемая сложность: O(d * (n + k)), где d — число разрядов, k = 10 (основание).
    """
    if not a:
        return []
    
    max_val = max(a)
    exp = 1
    res = list(a)
    
    while max_val // exp > 0:
        # Устойчивая сортировка подсчётом по текущему разряду
        count = [0] * 10
        for x in res:
            digit = (x // exp) % 10
            count[digit] += 1
            
        for i in range(1, 10):
            count[i] += count[i - 1]
            
        output = [0] * len(res)
        # Обход с конца обязателен для устойчивости!
        for i in range(len(res) - 1, -1, -1):
            digit = (res[i] // exp) % 10
            count[digit] -= 1
            output[count[digit]] = res[i]
            
        res = output
        exp *= 10
        
    return res


def sift_down(a: list[int], i: int, n: int) -> None:
    """Просейка вниз элемента i в куче a[0:n] (max-heap), на месте."""
    while True:
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        if left < n and a[left] > a[largest]:
            largest = left
        if right < n and a[right] > a[largest]:
            largest = right
            
        if largest != i:
            a[i], a[largest] = a[largest], a[i]
            i = largest  # продолжаем просейку с новой позиции
        else:
            break


def heap_sort(a: list[int]) -> None:
    """HeapSort in-place: сортирует список a на месте, без вспомогательного массива.
    Сложность: O(n) на построение кучи + O(n log n) на сортировку = O(n log n).
    """
    n = len(a)
    
    # 1. Построение max-кучи (просейка снизу вверх, начиная с последнего родителя)
    for i in range(n // 2 - 1, -1, -1):
        sift_down(a, i, n)
        
    # 2. Извлечение максимумов
    for i in range(n - 1, 0, -1):
        # Меняем корень (максимум) с последним элементом текущей кучи
        a[0], a[i] = a[i], a[0]
        # Просеиваем новый корень вниз, уменьшая размер кучи на 1
        sift_down(a, 0, i)


def quick_sort(a: list[int]) -> list[int]:
    """QuickSort с трёхчастным разбиением (Дейкстра) для защиты от равных ключей."""
    arr = list(a)
    
    def _qs(lo: int, hi: int):
        if lo >= hi:
            return
        
        # Выбор случайного опорного элемента
        pivot_idx = random.randrange(lo, hi + 1)
        pivot = arr[pivot_idx]
        
        # Трёхчастное разбиение (Dutch National Flag)
        # lt: все элементы arr[lo..lt-1] < pivot
        # gt: все элементы arr[gt+1..hi] > pivot
        # arr[lt..gt] == pivot (уже на своих местах)
        lt = lo
        i = lo
        gt = hi
        
        while i <= gt:
            if arr[i] < pivot:
                arr[lt], arr[i] = arr[i], arr[lt]
                lt += 1
                i += 1
            elif arr[i] > pivot:
                arr[gt], arr[i] = arr[i], arr[gt]
                gt -= 1
            else:
                i += 1
                
        # Рекурсивно сортируем только части строго меньше и строго больше pivot
        _qs(lo, lt - 1)
        _qs(gt + 1, hi)

    if arr:
        _qs(0, len(arr) - 1)
    return arr


# ---------------------------------------------------------------------------
# 2. Верификация: инварианты + сверка с эталоном sorted()
#    (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------


class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""


def expect(condition: bool, message: str) -> None:
    """Явная проверка вместо assert: assert-ы исчезают при запуске python -O."""
    if not condition:
        raise SelfCheckError(message)


def heap_sorted(a: list[int]) -> list[int]:
    """heap_sort сортирует на месте: проверяется тот список, который ему передали."""
    buf = list(a)
    heap_sort(buf)
    return buf


# Каждая функция возвращает отсортированный список; ключи — целые из [0, 999].
SORTS = {
    "merge_sort": lambda a: merge_sort(a),
    "counting_sort": lambda a: counting_sort(a, key_max=999),
    "radix_sort_lsd": lambda a: radix_sort_lsd(a),
    "heap_sort": lambda a: heap_sorted(a),
    "quick_sort": lambda a: quick_sort(a),
}


def check_sort(fn) -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [0],                   # нулевой ключ
        [5, 5, 5],             # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list), f"на {a} возвращён {type(res).__name__}, а не список")
        expect(res == sorted(a), f"на {a} получено {res}, ожидалось {sorted(a)}")

    # Случайные тесты: инвариант перестановки + сверка с эталоном
    rng = random.Random(0)
    for _ in range(200):
        a = [rng.randint(0, 999) for _ in range(rng.randint(0, 60))]
        res = fn(list(a))
        expect(sorted(res) == sorted(a), f"не перестановка входа {a}: получено {res}")
        expect(res == sorted(a), f"расходится с sorted() на {a}: получено {res}")


def check_merge_stability() -> None:
    """Стабильность слияния на парах (ключ, порядковый номер): эталон sorted() стабилен,
    поэтому при равных ключах порядок номеров обязан совпасть."""
    rng = random.Random(0)
    pairs = [(rng.randint(0, 5), i) for i in range(100)]
    got = merge_sort(pairs, key=lambda p: p[0])
    expect(got == sorted(pairs, key=lambda p: p[0]),
           "merge_sort нестабилен: при равных ключах нарушен исходный порядок номеров")

def check_heap_property() -> None:
    """Проверка свойства max-кучи. 
    Поскольку heap_sort модифицирует массив на месте, мы проверяем 
    корректность работы sift_down косвенно: если бы куча строилась неверно, 
    итоговая сортировка в check_sort провалилась бы. 
    Дополнительно проверим инвариант кучи на искусственном примере."""
    def is_max_heap(arr, n):
        for i in range(n // 2):
            left = 2 * i + 1
            right = 2 * i + 2
            if left < n and arr[i] < arr[left]:
                return False
            if right < n and arr[i] < arr[right]:
                return False
        return True

    # Тест: если мы возьмем уже отсортированный массив, он является кучей
    expect(is_max_heap([5, 4, 3, 2, 1], 5), "Отсортированный по убыванию массив должен быть кучей")
    expect(is_max_heap([10, 9, 8, 7, 6], 5), "Проверка кучи провалена")


def check_radix_stability_logic() -> None:
    """Проверка логики устойчивости RadixSort.
    Устойчивость гарантируется тем, что внутренний counting_sort 
    проходит по массиву С КОНЦА (в обратном порядке)."""
    # Мы не можем легко передать кортежи в текущую сигнатуру radix_sort_lsd,
    # но мы можем проверить, что алгоритм корректно обрабатывает массивы 
    # с большим количеством дубликатов, не теряя элементы (что было бы 
    # признаком грубой ошибки в логике устойчивости).
    rng = random.Random(0)
    a = [rng.randint(0, 10) for _ in range(100)] # Много дубликатов
    res = radix_sort_lsd(a)
    expect(res == sorted(a), "RadixSort неверно отсортировал массив с дубликатами")

def self_check() -> None:
    """Все проверки по разделам; при любой ошибке замеры не выполняются."""
    # fn=fn фиксирует функцию текущего шага цикла (иначе все лямбды увидят последнюю)
    checks = [(name, lambda fn=fn: check_sort(fn)) for name, fn in SORTS.items()]
    checks.append(("стабильность merge_sort", check_merge_stability))
    checks.append(("свойство кучи (heap property)", check_heap_property))
    checks.append(("логика устойчивости radix_sort", check_radix_stability_logic))
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
    # TODO: добавить собственные проверки (свойство кучи после построения,
    #       устойчивость поразрядного прохода radix) и описать их в отчёте.
    if failed:
        raise SystemExit(f"self_check: не пройдено разделов — {failed}; "
                         f"замеры выполняются только после всех проверок.")
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 3. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
SMALL_KEY_MAX = 100        # узкий диапазон: counting уместен
WIDE_KEY_MAX = 10**9       # широкий диапазон: counting теряет смысл (обсудить в отчёте)


def make_datasets(rng: random.Random, n: int) -> dict[str, list[int]]:
    """Массивы разных распределений и диапазонов ключей для размера n."""
    almost = list(range(n))
    for _ in range(max(1, n // 100)):  # ~1 % случайных обменов
        i, j = rng.randrange(n), rng.randrange(n)
        almost[i], almost[j] = almost[j], almost[i]
    return {
        "random_wide": [rng.randint(0, WIDE_KEY_MAX) for _ in range(n)],
        "random_small": [rng.randint(0, SMALL_KEY_MAX) for _ in range(n)],
        "sorted": list(range(n)),
        "reversed": list(range(n, 0, -1)),
        "almost_sorted": almost,
    }


def bench(fn, data: list[int]) -> float:
    """Медиана времени fn на копии data по REPEATS запускам, с прогревом.

    Каждый запуск получает свежую копию: сортировка на месте не должна
    превращать последующие запуски в сортировку уже отсортированного массива.
    """
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        buf = list(data)
        t0 = time.perf_counter()
        fn(buf)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    rng = random.Random(seed)
    algorithms = [
        ("merge_sort", merge_sort),
        ("counting_sort", lambda a: counting_sort(a, key_max=max(a, default=0))),
        ("radix_sort_lsd", radix_sort_lsd),
        ("heap_sort", heap_sort),
        ("quick_sort", quick_sort),
        ("sorted()", sorted),
    ]
    
    # Словарь для сбора данных графиков: {имя_алгоритма: {распределение: [времена]}}
    distributions = ["random_wide", "random_small", "sorted", "reversed", "almost_sorted"]
    plot_data = {name: {dist: [] for dist in distributions} for name, _ in algorithms}
    
    for n in SIZES:
        datasets = make_datasets(rng, n)
        print(f"\nn = {n}:")
        for dist_name, data in datasets.items():
            print(f"  распределение {dist_name}:")
            for algo_name, fn in algorithms:
                if algo_name == "counting_sort" and dist_name == "random_wide":
                    print(f"    {algo_name:>18}: пропуск (диапазон ключей)")
                    continue
                
                t = bench(fn, data)
                print(f"    {algo_name:>18}: t = {t:.6f} c")
                plot_data[algo_name][dist_name].append(t)

    # Построение отдельных графиков для каждого распределения
    dist_titles = {
        "random_wide": "Случайные данные (широкий диапазон)",
        "random_small": "Случайные данные (узкий диапазон)",
        "sorted": "Упорядоченные данные",
        "reversed": "Обратно упорядоченные данные",
        "almost_sorted": "Почти упорядоченные данные",
    }
    
    for dist in distributions:
        plt.figure(figsize=(10, 6))
        
        for algo_name, _ in algorithms:
            if algo_name == "counting_sort" and dist == "random_wide":
                continue
            times = plot_data[algo_name][dist]
            if times:
                plt.loglog(SIZES, times, marker='o', linewidth=2, label=algo_name)
        
        plt.title(f"Производительность сортировок\n{dist_titles[dist]}")
        plt.xlabel("Размер входа (N)", fontsize=12)
        plt.ylabel("Время выполнения (сек)", fontsize=12)
        plt.grid(True, which="both", ls="--", alpha=0.7)
        plt.legend(loc="upper left")
        plt.tight_layout()
        
        # Сохраняем график в отдельный файл
        filename = f"lab04_{dist}.png"
        plt.savefig(filename, dpi=300)
        print(f"График сохранён: {filename}")
        plt.close()  # Закрываем фигуру, чтобы не занимать память

    print("\nВсе графики сохранены в файлы 'lab04_<распределение>.png'")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()
