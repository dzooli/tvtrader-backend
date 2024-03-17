import sys
from pathlib import Path


mypath = Path(__file__)
sys.path.insert(0, str(mypath.parents[2].resolve().absolute()))
