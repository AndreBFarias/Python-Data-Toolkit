<div align="center">
    
[![opensource](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](#)
[![licença](https://img.shields.io/badge/licença-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![Estrelas](https://img.shields.io/github/stars/AndreBFarias/Python-Data-Toolkit.svg?style=social)](https://github.com/AndreBFarias/Python-Data-Toolkit/stargazers)
[![Contribuições](https://img.shields.io/badge/contribuições-bem--vindas-brightgreen.svg)](https://github.com/AndreBFarias/Python-Data-Toolkit/issues)


<div style="text-align: center;">
  <h1 style="font-size: 2em;">Python Data Toolkit</h1>
    
  <img src="https://raw.githubusercontent.com/AndreBFarias/Python-Data-Toolkit/main/assets/icon.png" width="250" alt="Ícone do Data Toolkit">
  
</div>
</div>

Fiz este programa para juntar num só lugar algumas ferramentas que me ajudam a resolver tarefas chatas e repetitivas com planilhas. A ideia é ter uma interface simples para poder, por exemplo, dividir uma tabela muito grande, limpar colunas bagunçadas ou comparar duas versões de um mesmo relatório sem precisar de escrever código.

---

<center>
<div style="text-align: center;">
  <h3 style="font-size: 2em;">Interface</h3>
    <img src="https://raw.githubusercontent.com/AndreBFarias/Python-Data-Toolkit/main/assets/background.png" width="700" alt="Screenshot do Data Toolkit">
</div>
</center>

## Funcionalidades

*   **Analisador**: Perfilamento de dados (estatísticas, nulos, tipos).
*   **Limpador**: Limpeza de dados (remoção de duplicatas, tratamento de nulos).
*   **Unificador**: Combinação de múltiplos arquivos (Excel/CSV).
*   **Preparador ETL**: Transformações comuns para pipelines de dados.
*   **Geolocalizador**: Enriquecimento de dados com coordenadas (via CEP/Endereço).
*   **Anonimizador**: Mascaramento de dados sensíveis (LGPD).
*   **Divisor**: Segmentação de arquivos grandes.
*   **Comparador**: Comparação entre dois datasets.
*   **Visualizador**: Geração de gráficos rápidos.
*   **Extrator**: Extração de tabelas e texto de PDFs e DOCX.
*   **Auxiliador IA**: Assistente inteligente integrado (Gemini) para tirar dúvidas e gerar código.

## Estrutura do Projeto

O projeto foi refatorado para uma arquitetura modular:

```
Python-Data-Toolkit/
├── src/
│   ├── core/           # Lógica central (config, dados estáticos)
│   ├── tabs/           # Módulos de cada aba (funcionalidades)
│   ├── ui/             # Componentes de UI e classe principal da App
│   └── main.py         # Ponto de entrada (interno)
├── assets/             # Imagens e ícones
├── main.py             # Ponto de entrada principal
├── requirements.txt    # Dependências
└── README.md           # Documentação
```

## Instalação

1.  Clone o repositório.
2.  Crie um ambiente virtual:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

## Uso

Execute o arquivo principal:

```bash
python3 main.py
```

## Configuração

*   **API Gemini**: Para usar o Auxiliador IA, configure sua chave de API na aba "Configurações".
*   **Pastas Padrão**: Defina pastas de entrada e saída padrão nas configurações para agilizar o fluxo de trabalho.



## Licença

Este projeto usa a licença GPLv3. Fique à vontade para usar, modificar e partilhar. Desde que tudo permaneça livre.