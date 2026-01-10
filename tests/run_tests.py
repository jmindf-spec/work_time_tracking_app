"""
Запуск всех unit-тестов
"""

import unittest
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath('.'))

def run_all_tests():
    """Запуск всех тестов"""
    # Находим все тестовые файлы
    test_dir = 'tests'
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(test_dir, pattern='test_*.py')
    
    # Запускаем тесты
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Возвращаем код выхода
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_all_tests())