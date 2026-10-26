import runpy
from pathlib import Path
# Run the unchanged failed consumer without its exception-summary wrapper.
# The uncaught traceback locates the conversion; this creates no acceptance.
namespace=runpy.run_path(str(Path(__file__).with_name('verify-comparison-v1.py')))
namespace['main']()
