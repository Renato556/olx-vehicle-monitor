#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from notifier import remove_accents

test_cases = [
    ("Fiat Palio [Completo]", "Fiat Palio Completo"),
    ("VW Gol (Novo)", "VW Gol Novo"),
    ("Chevrolet Onix [Ar/Dir]", "Chevrolet Onix Ar/Dir"),
    ("Honda Civic (2015/2016)", "Honda Civic 2015/2016"),
    ("Uno com escada [TOP]", "Uno com escada TOP"),
    ("Açâo com ç e ã", "Acao com c e a"),
]

print("Testing remove_accents for Markdown compatibility:")
print("-" * 50)
for original, expected in test_cases:
    result = remove_accents(original)
    status = "✅" if result == expected else "❌"
    print(f"{status} Original: '{original}'")
    print(f"   Result:   '{result}'")
    print(f"   Expected: '{expected}'")
    print("-" * 50)
