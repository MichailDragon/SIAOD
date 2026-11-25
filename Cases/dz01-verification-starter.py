#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ДЗ 1. Верификация ИИ-сгенерированной сортировки — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-01 (Cases) и методикой верификации по шагам 1–4
(docs/ai-verification.md). Проверяемый код лежит рядом, в dz01-ai-code.py;
исправлять его до завершения верификации запрещено.

Запуск: python dz01-verification-starter.py --variant N
"""
from __future__ import annotations

import argparse
import importlib.util
import random
import statistics
import time
from pathlib import Path
from collections import Counter

# ---------------------------------------------------------------------------
# 0. Загрузка проверяемого кода
# ---------------------------------------------------------------------------
# Имя файла содержит дефисы, поэтому обычный import не подходит —
# модуль загружается по пути через importlib.

AI_CODE_PATH = Path(__file__).with_name("dz01-ai-code.py")


def load_quicksort():
    """Загружает функцию quicksort из соседнего файла dz01-ai-code.py."""
    spec = importlib.util.spec_from_file_location("dz01_ai_code", AI_CODE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.quicksort


quicksort = load_quicksort()

# ---------------------------------------------------------------------------
# 1. Шаг 1 методики: инварианты сортировки
# ---------------------------------------------------------------------------


def is_sorted(a: list[int]) -> bool:
    """Инвариант 1: последовательность упорядочена по неубыванию."""
    return all(a[i] <= a[i+1] for i in range(len(a) - 1))


def same_multiset(a: list[int], b: list[int]) -> bool:
    """Инвариант 2: b — перестановка a (мультимножества элементов совпадают)."""
    return Counter(a) == Counter(b)


def check_invariants(original: list[int], result: list[int]) -> list[str]:
    """Возвращает список нарушенных инвариантов (пустой список — нарушений нет)."""
    errors = []
    if not is_sorted(result):
        errors.append("Нарушен инвариант 1: результат не упорядочен по неубыванию.")
    if not same_multiset(original, result):
        errors.append("Нарушен инвариант 2: мультимножества элементов не совпадают (потеря или добавление элементов).")
    return errors


# ---------------------------------------------------------------------------
# 2. Шаг 2 методики: репрезентативные тесты
# ---------------------------------------------------------------------------


def representative_cases(rng: random.Random) -> list[tuple[str, list[int]]]:
    """Именованные тестовые входы по классам методики.

    Обязательные классы: граничные (пустой, один, два элемента);
    вырожденные (все элементы равны, уже отсортированный, обратно
    отсортированный); типовые случайные с дубликатами и отрицательными
    числами (генерируются через rng — seed по варианту).
    """
    return [
        ("граничный: пустой", []),
        ("граничный: один элемент", [42]),
        ("граничный: два элемента", [2, 1]),
        ("вырожденный: все элементы равны", [5, 5, 5, 5, 5]),
        ("вырожденный: уже отсортированный", [1, 2, 3, 4, 5]),
        ("вырожденный: обратно отсортированный", [5, 4, 3, 2, 1]),
        ("типовой: случайные с дубликатами и отрицательными", [rng.randint(-10, 10) for _ in range(15)]),
    ]


def run_representative_tests(rng: random.Random) -> None:
    """Прогоняет quicksort по всем классам входов и печатает нарушения инвариантов."""
    print("\n--- Шаг 1: Проверка инвариантов (в составе репрезентативных тестов) ---")
    print("Инвариант 1: выход упорядочен по неубыванию.")
    print("Инвариант 2: выход — перестановка входа (мультимножества совпадают).")
    print("\n--- Шаг 2: Репрезентативные тесты ---")
    for name, data in representative_cases(rng):
        result = quicksort(data)
        errors = check_invariants(data, result)
        if errors:
            print(f"[ОШИБКА] Класс '{name}':")
            print(f"  Вход:  {data}")
            print(f"  Выход: {result}")
            for err in errors:
                print(f"  -> {err}")
        else:
            print(f"[OK] Класс '{name}'")


# ---------------------------------------------------------------------------
# 3. Шаг 3 методики: сравнение с эталоном sorted()
# ---------------------------------------------------------------------------


def compare_with_reference(rng: random.Random, runs: int = 300) -> None:
    """Сверка quicksort с sorted() на сотнях случайных входов.

    Генерируйте входы разных размеров (включая маленькие: именно на них
    удобно локализовать расхождение), обязательно с дубликатами и
    отрицательными числами. Каждое расхождение печатайте вместе со входом,
    чтобы затем свести его к минимальному контрпримеру.
    """
    print("\n--- Шаг 3: Сравнение с эталоном sorted() ---")
    mismatches = 0
    min_counterexample = None
    
    for _ in range(runs):
        size = rng.randint(0, 20)  # маленькие размеры для удобной локализации
        data = [rng.randint(-10, 10) for _ in range(size)]
        result = quicksort(data)
        expected = sorted(data)
        
        if result != expected:
            mismatches += 1
            if min_counterexample is None or len(data) < len(min_counterexample[0]):
                min_counterexample = (data, result, expected)
                
    print(f"Всего расхождений с эталоном: {mismatches} из {runs}")
    if min_counterexample:
        data, res, exp = min_counterexample
        print("Минимальный контрпример:")
        print(f"  Вход:    {data}")
        print(f"  ИИ-код:  {res}")
        print(f"  Эталон:  {exp}")
    else:
        print("Расхождений не найдено.")


# ---------------------------------------------------------------------------
# 4. Шаг 4 методики: бенчмарк на трёх классах входов
# (методика — docs/reproducibility.md: прогрев, >=5 повторов, медиана)
# ---------------------------------------------------------------------------

SIZES = [500, 1_000, 2_000, 4_000, 8_000]
REPEATS = 5
INPUT_KINDS = ("random", "sorted", "reversed")


def make_input(rng: random.Random, n: int, kind: str) -> list[int]:
    """Вход размера n одного из трёх классов: random / sorted / reversed."""
    a = [rng.randint(-1000, 1000) for _ in range(n)]
    if kind == "sorted":
        a.sort()
    elif kind == "reversed":
        a.sort(reverse=True)
    return a


def bench(fn, data: list[int]) -> float:
    """Медиана времени выполнения fn(data) по REPEATS запускам, с прогревом."""
    fn(data)  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn(data)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    """Замеры quicksort на трёх классах входов; аварийные завершения фиксируются."""
    print("\n--- Шаг 4: Бенчмарк производительности ---")
    rng = random.Random(seed)
    for kind in INPUT_KINDS:
        print(f"\nКласс входа: {kind}")
        for n in SIZES:
            data = make_input(rng, n, kind)
            try:
                t = bench(quicksort, data)
                print(f"  n={n:>6}  t={t:.6f} c")
            except RecursionError:
                # Аварийное завершение — тоже результат верификации:
                # зафиксируйте его в отчёте вместе с размером входа.
                print(f"  n={n:>6}  RecursionError")
    
    print("\n--- Анализ бенчмарка (Шаг 4) ---")
    print("Заявленная сложность: O(n log n).")
    print("Наблюдаемая деградация: На входах 'sorted' и 'reversed' происходит RecursionError или резкий рост времени.")
    print("Причина в коде: Выбор опорного элемента `pivot = data[0]`. На отсортированных данных это приводит")
    print("к разбиению на подмассивы размером 0 и n-1, что дает глубину рекурсии O(n) и фактическую сложность O(n^2).")


# ---------------------------------------------------------------------------
# 5. Самопроверка каркаса (граничные случаи + сверка с эталоном stdlib)
# ---------------------------------------------------------------------------


def self_check() -> None:
    """Проверяет вспомогательные функции до основной верификации."""
    assert is_sorted([]) and is_sorted([7]) and is_sorted([1, 2, 2, 3])
    assert not is_sorted([3, 1, 2])
    assert same_multiset([], []) and same_multiset([2, 1, 2], [1, 2, 2])
    assert not same_multiset([1, 1, 2], [1, 2, 2])
    rng = random.Random(0)
    for _ in range(100):  # сверка помощников с эталоном стандартной библиотеки
        a = [rng.randint(-20, 20) for _ in range(rng.randint(0, 30))]
        assert is_sorted(sorted(a))          # эталон sorted() упорядочен
        assert same_multiset(a, sorted(a))   # эталон — перестановка входа
    print("self_check: OK")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant  # вариантность — см. docs/reproducibility.md
    random.seed(seed)
    self_check()
    rng = random.Random(seed)
    run_representative_tests(rng)          # шаги 1–2
    compare_with_reference(rng, runs=300)  # шаг 3
    run_benchmarks(seed)                   # шаг 4


if __name__ == "__main__":
    main()