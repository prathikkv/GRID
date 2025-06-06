import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.normalizer import normalize_term

print(normalize_term("drug", "Imatinib"))
print(normalize_term("gene", "JAK2"))
print(normalize_term("disease", "Crohn's disease"))
