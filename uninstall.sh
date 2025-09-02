#!/bin/bash

# Define o nome do ficheiro de atalho e o seu caminho
APP_NAME="Data Toolkit"
DESKTOP_FILE_NAME="data-toolkit.desktop"
DESKTOP_FILE_PATH="$HOME/.local/share/applications/$DESKTOP_FILE_NAME"

echo "Iniciando a desinstalação do $APP_NAME..."

# Pergunta ao utilizador se deseja realmente desinstalar
read -p "Tem a certeza que deseja remover o atalho da aplicação do seu sistema? [s/N] " response
if [[ "$response" =~ ^([sS][iI][mM]|[sS])$ ]]; then
    # Verifica se o ficheiro .desktop existe
    if [ -f "$DESKTOP_FILE_PATH" ]; then
        echo "Removendo o ficheiro de atalho de $DESKTOP_FILE_PATH..."
        rm "$DESKTOP_FILE_PATH"
        
        # Atualiza a base de dados de aplicações para que a mudança seja refletida
        echo "Atualizando a base de dados de aplicações do sistema..."
        update-desktop-database "$HOME/.local/share/applications"
        
        echo "O atalho do $APP_NAME foi removido com sucesso."
    else
        echo "O ficheiro de atalho não foi encontrado. Talvez a aplicação não tenha sido instalada corretamente."
    fi
else
    echo "Desinstalação cancelada."
    exit 0
fi

echo ""
read -p "Deseja também remover a pasta do ambiente virtual ('venv')? [s/N] " venv_response
if [[ "$venv_response" =~ ^([sS][iI][mM]|[sS])$ ]]; then
    # Garante que estamos no diretório certo antes de remover
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    if [ -d "$SCRIPT_DIR/venv" ]; then
        echo "Removendo o ambiente virtual..."
        rm -rf "$SCRIPT_DIR/venv"
        echo "Ambiente virtual removido."
    else
        echo "Pasta 'venv' não encontrada no diretório do script."
    fi
fi

echo ""
echo "Lembrete: Este script não apaga a pasta do projeto."
echo "Se desejar, pode agora removê-la com segurança:"
echo "cd .. && rm -rf Python-Data-Toolkit"
echo ""
echo "Desinstalação concluída."


