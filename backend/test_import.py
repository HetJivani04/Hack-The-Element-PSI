import sys
import os
sys.path.insert(0, os.path.dirname(os.getcwd()))
try:
    from marine_platform.engine import Orchestrator
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
