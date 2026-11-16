"""Run with python -m chordrec."""
import os

# Set before importing NumPy/librosa for comparable CPU measurements.
for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(variable, "1")
os.environ.pop("LIBROSA_CACHE_DIR", None)

from .run import main

main()
