#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Исправленная версия быстрой сортировки (копия dz01-ai-code.py с исправлениями)."""
from __future__ import annotations
import random

def quicksort(data: list[int]) -> list[int]:
    """Sort a list of integers using the quicksort algorithm.
    
    Исправления:
    1. Случайный выбор опорного элемента для гарантии O(n log n) в среднем.
    2. Явное выделение списка equal для сохранения всех дубликатов (инвариант мультимножества).
    """
    if len(data) <= 1:
        return list(data)
    
    # Исправление 1: случайный выбор опорного элемента
    pivot = random.choice(data)
    
    # Исправление 2: явное сохранение элементов, равных опорному
    smaller = [x for x in data if x < pivot]
    equal = [x for x in data if x == pivot]
    larger = [x for x in data if x > pivot]
    
    return quicksort(smaller) + equal + quicksort(larger)

if __name__ == "__main__":
    example = [5, 2, 9, 1, 7, 5, 5]
    print("Input :", example)
    print("Sorted:", quicksort(example))