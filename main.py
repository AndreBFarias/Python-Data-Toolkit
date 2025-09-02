from data_toolkit import DataToolkitApp
import os

if __name__ == "__main__":
    # Garante que o diretório de trabalho seja o do script
    # para que os caminhos relativos (como para 'assets') funcionem
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    app = DataToolkitApp()
    app.run() # O comando correto, dirigido ao maestro.


