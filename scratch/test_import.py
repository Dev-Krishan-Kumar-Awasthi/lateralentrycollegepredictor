import predictor
print(dir(predictor))
try:
    from predictor import run_counselling_simulation
    print("Import successful!")
except ImportError as e:
    print(f"Import failed: {e}")
