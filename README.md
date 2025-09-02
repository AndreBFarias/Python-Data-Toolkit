<div align="center">

[![Licença](https://img.shields.io/badge/licença-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![Estrelas](https://img.shields.io/github/stars/AndreBFarias/Python-Data-Toolkit.svg?style=social)](https://github.com/AndreBFarias/Python-Data-Toolkit/stargazers)
[![Contribuições](https://img.shields.io/badge/contribuições-bem--vindas-brightgreen.svg)](https://github.com/AndreBFarias/Python-Data-Toolkit/issues)

<div style="text-align: center;">
  <h1 style="font-size: 2em;">Python Data Toolkit</h1>
  <img src="https://raw.githubusercontent.com/AndreBFarias/Python-Data-Toolkit/main/assets/icon.png" width="200" alt="Ícone do Data Toolkit">
</div>
</div>

Fiz este programa para juntar num só lugar algumas ferramentas que me ajudam a resolver tarefas chatas e repetitivas com planilhas. A ideia é ter uma interface simples para poder, por exemplo, dividir uma tabela muito grande, limpar colunas bagunçadas ou comparar duas versões de um mesmo relatório sem precisar de escrever código.

---

<center>
<div style="text-align: center;">
  <h3 style="font-size: 2em;">Interface</h3>
    <img src="https://raw.githubusercontent.com/AndreBFarias/Python-Data-Toolkit/main/assets/screenshot.png" width="800" alt="Screenshot do Data Toolkit">
</div>
</center>

---

### Pré-requisitos

- Python 3.10 ou superior.
- Para a aba "Preparador ETL", é preciso ter uma chave de API do Google Gemini.

### Instalação

Para quem usa Linux, o script `install.sh` tenta facilitar o processo, criando o ambiente virtual e um atalho no menu de aplicações.

```

# 1. Baixar o projeto
git clone [https://github.com/AndreBFarias/Python-Data-Toolkit.git](https://github.com/AndreBFarias/Python-Data-Toolkit.git)
cd Python-Data-Toolkit

# 2. (Opcional) Criar o ficheiro .env para a chave da API
cp .env.example .env
# E depois editar o ficheiro para colocar a sua chave
# nano .env

# 3. Executar o instalador
chmod +x install.sh
./install.sh
```


Depois disto, o "Data Toolkit" deve aparecer no seu menu de aplicações, e você pode fixá-lo na sua dock se quiser.

### Para Desinstalar


```
chmod +x uninstall.sh
./uninstall.sh
```

### O que ele faz?

Cada aba é uma ferramenta para uma tarefa diferente:

- **Preparador ETL**: Prepara uma tabela para ser importada num banco de dados, sugerindo o schema (formato das colunas) com a ajuda de IA.
    
- **Segmentador**: Pega um ficheiro grande e o quebra em vários ficheiros menores.
    
- **Limpador**: Ajuda a arrumar a casa: remove linhas duplicadas, espaços a mais, etc.
    
- **Anonimizador**: Troca informações sensíveis (como nomes ou CPFs) por dados falsos, para proteger a privacidade.
    
- **Unificador**: Junta vários ficheiros de uma pasta num só.
    
- **Analisador**: Mostra um resumo rápido do seu ficheiro: quantas linhas, colunas, dados em falta, etc.
    
- **Comparador**: Mostra o que mudou entre duas versões de uma mesma tabela.
    
- **Visualizador**: Cria alguns gráficos simples para ter uma ideia visual dos seus dados.
    
- **Assistente dbt**: Uma ajuda para automatizar a criação de documentação para modelos dbt.
    

### Licença

Este projeto usa a licença GPLv3. Fique à vontade para usar, modificar e partilhar. Desde que tudo permaneça livre.
