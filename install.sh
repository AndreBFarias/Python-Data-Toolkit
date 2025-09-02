#!/bin/bash

# Encontra o diretório onde o script está a ser executado
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
APP_NAME="Data Toolkit"
VENV_DIR="venv"
DESKTOP_FILE_NAME="data-toolkit.desktop"
INSTALL_DIR="$HOME/.local/share/applications"

echo "### Configurando o $APP_NAME ###"
echo ""
cd "$SCRIPT_DIR"

# 1. Verifica se o Python 3 e o venv estão disponíveis
if ! command -v python3 &> /dev/null || ! python3 -m venv -h &> /dev/null; then
    echo "ERRO: Python 3 e/ou o módulo 'venv' não foram encontrados."
    echo "Por favor, instale-os para continuar (ex: sudo apt install python3 python3-venv)."
    exit 1
fi

# 2. Cria o ambiente virtual se não existir
if [ ! -d "$VENV_DIR" ]; then
    echo "Criando ambiente virtual em '$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "ERRO: Falha ao criar o ambiente virtual."
        exit 1
    fi
else
    echo "Ambiente virtual já existente."
fi

# 3. Instala as dependências
echo "Instalando dependências do requirements.txt..."
"$SCRIPT_DIR/$VENV_DIR/bin/pip" install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERRO: Falha ao instalar as dependências via pip."
    exit 1
fi
echo "Dependências instaladas com sucesso."

# 4. Cria o ficheiro .desktop para integração com o sistema
echo "Criando atalho da aplicação..."
mkdir -p "$INSTALL_DIR"

# Cria o conteúdo do ficheiro .desktop
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

echo "Instalando atalho em $INSTALL_DIR..."

# 5. Atualiza a base de dados de aplicações
echo "Atualizando a base de dados de aplicações do sistema..."
update-desktop-database "$INSTALL_DIR"

echo ""
echo "##############################################"
echo "Instalação concluída com sucesso!"
echo "Pode encontrar o '$APP_NAME' no seu menu de aplicações e fixá-lo na sua dock."
echo "Pode levar alguns instantes para o ícone aparecer."
echo "##############################################"


