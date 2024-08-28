import os
import sys


sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ui.app import DataToolkitApp

if __name__ == "__main__":
    
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    
    from src.core.logger import Logger
    import sys
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        Logger().exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        
    sys.excepthook = handle_exception

    app = DataToolkitApp()
    app.mainloop()
