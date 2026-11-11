"""Compatibility entry point for the current cozy investigation UI."""
from pathlib import Path
import runpy

def build_popup():
    return runpy.run_path(str(Path(__file__).with_name('build_cozy_ui.py')))['build']()

if __name__=='__main__':
    runpy.run_path(str(Path(__file__).with_name('build_cozy_ui.py')),run_name='__main__')
