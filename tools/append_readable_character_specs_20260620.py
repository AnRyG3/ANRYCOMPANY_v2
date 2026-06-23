from pathlib import Path
import runpy

# Compatibility wrapper. The canonical implementation is refresh_readable_character_specs.py.
runpy.run_path(str(Path(__file__).with_name('refresh_readable_character_specs.py')), run_name='__main__')
