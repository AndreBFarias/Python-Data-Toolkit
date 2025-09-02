#!/bin/bash

# --- O Arauto do Data Toolkit ---
# Este script é o diplomata que apresenta nossa criação ao sistema.
# Ele constrói o executável e cria o atalho no menu de aplicações.

echo "Configurando o Data Toolkit..."

# 1. Autoconsciência: Encontrar o caminho absoluto do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
echo "Diretório do projeto encontrado em: $SCRIPT_DIR"

# 2. Construção com PyInstaller
echo "Construindo o executável com PyInstaller..."
echo "Isso pode levar alguns minutos..."

# Navega para o diretório do projeto para o PyInstaller funcionar corretamente
cd "$SCRIPT_DIR"

# Roda o PyInstaller
# --noconfirm: Sobrescreve a build anterior sem perguntar
# --onefile: Cria um único executável
# --windowed: Não abre um console de terminal ao executar a app
# --icon: Define o ícone da aplicação
# --name: Define o nome do executável e do app
pyinstaller --noconfirm --onefile --windowed --icon="assets/icon.png" --name="DataToolkit" main.py

# Verifica se a construção foi bem-sucedida
BUILD_SUCCESS=$?
EXECUTABLE_PATH="$SCRIPT_DIR/dist/DataToolkit"

if [ $BUILD_SUCCESS -ne 0 ]; then
    echo "ERRO: A construção com PyInstaller falhou. Por favor, verifique os logs acima."
    exit 1
fi

if [ ! -f "$EXECUTABLE_PATH" ]; then
    echo "ERRO: O executável não foi encontrado em '$EXECUTABLE_PATH' após a construção."
    exit 1
fi

echo "Executável criado com sucesso em: $EXECUTABLE_PATH"

# 3. Criação do Atalho (.desktop)
echo "Criando o ficheiro de atalho..."
DESKTOP_ENTRY_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_ENTRY_DIR" # Garante que o diretório exista

DESKTOP_FILE_PATH="$DESKTOP_ENTRY_DIR/data-toolkit.desktop"
ICON_PATH="$SCRIPT_DIR/assets/icon.png"

# Escreve o conteúdo no ficheiro .desktop
cat > "$DESKTOP_FILE_PATH" << EOL
[Desktop Entry]
Version=1.0
Name=Data Toolkit
Comment=Um conjunto de ferramentas para manipulação de dados
Exec="$EXECUTABLE_PATH"
Icon="$ICON_PATH"
Terminal=false
Type=Application
Categories=Utility;Application;
EOL

# 4. Finalização
echo "Instalando atalho em $DESKTOP_ENTRY_DIR..."
# Atualiza a base de dados de aplicações para que o ícone apareça
update-desktop-database "$DESKTOP_ENTRY_DIR"

echo ""
echo "Instalação concluída com sucesso!"
echo "Pode encontrar o 'Data Toolkit' no seu menu de aplicações."
echo "Pode levar alguns instantes para o ícone aparecer."


