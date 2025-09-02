#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
APP_NAME="Data Toolkit"
VENV_DIR="venv"
DESKTOP_FILE_NAME="data-toolkit.desktop"
INSTALL_DIR="$HOME/.local/share/applications"

echo "### Configurando o $APP_NAME ###"
echo ""
cd "$SCRIPT_DIR"

if ! command -v python3 &> /dev/null || ! python3 -m venv -h &> /dev/null; then
    echo "ERRO: Python 3 e/ou o módulo 'venv' não foram encontrados."
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Criando ambiente virtual em '$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
fi

echo "Instalando dependências do requirements.txt..."
"$SCRIPT_DIR/$VENV_DIR/bin/pip" install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao instalar as dependências via pip."
    exit 1
fi

echo "Criando atalho da aplicação..."
mkdir -p "$INSTALL_DIR"

# CORREÇÃO: StartupWMClass ajustado para 'Data-Toolkit' para corresponder ao className
cat > "$INSTALL_DIR/$DESKTOP_FILE_NAME" << EOL
[Desktop Entry]
Version=1.0
Name=$APP_NAME
Comment=Uma suíte de ferramentas para manipulação de dados
Exec=$SCRIPT_DIR/$VENV_DIR/bin/python3 $SCRIPT_DIR/main.py
Icon=$SCRIPT_DIR/assets/icon.png
Terminal=false
Type=Application
Categories=Utility;Application;Office;
StartupWMClass=Data-Toolkit
EOL

echo "Atualizando a base de dados de aplicações do sistema..."
update-desktop-database "$INSTALL_DIR"

echo ""
echo "##############################################"
echo "Instalação concluída com sucesso!"
echo "Pode encontrar o '$APP_NAME' no seu menu de aplicações."
echo "##############################################"
