[![opensource](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](#)
[![licença](https://img.shields.io/badge/licença-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![Estrelas](https://img.shields.io/github/stars/AndreBFarias/Python-Data-Toolkit.svg?style=social)](https://github.com/AndreBFarias/Python-Data-Toolkit/stargazers)
[![Contribuições](https://img.shields.io/badge/contribuições-bem--vindas-brightgreen.svg)](https://github.com/AndreBFarias/Python-Data-Toolkit/issues)

# Python Data Toolkit

![Ícone do Data Toolkit](https://raw.githubusercontent.com/AndreBFarias/Python-Data-Toolkit/main/assets/icon.png)

Ferramentas visuais para manipulação e análise de dados tabulares. Reúne num único lugar funcionalidades para dividir, limpar, comparar e transformar planilhas sem escrever código, com assistente de IA integrado.

---

## Interface

![Screenshot do Data Toolkit](https://github.com/AndreBFarias/Python-Data-Toolkit/blob/main/assets/background.png)

## Pré-requisitos

- Python 3.10 ou superior
- Sistema operacional: Linux ou Windows
- Chave de API do Google Gemini (para o módulo Auxiliador IA)

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
