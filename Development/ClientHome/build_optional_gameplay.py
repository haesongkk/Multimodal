"""Legacy entry point: all five clues now have equal weight."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('build_cozy_gameplay.py')),run_name='__main__')
