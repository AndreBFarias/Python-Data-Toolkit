Data ToolkitEste repositório contém um conjunto de ferramentas com interface gráfica para realizar operações comuns de manipulação de dados em ficheiros CSV e Excel. Foi criado para simplificar tarefas repetitivas do dia a dia de analistas, cientistas de dados e qualquer pessoa que trabalhe com tabelas.A ideia surgiu da necessidade de ter soluções rápidas e visuais para problemas que, embora simples, consumiam tempo, como dividir uma tabela gigante em várias menores, limpar dados inconsistentes ou unificar relatórios mensais.FuncionalidadesA aplicação é organizada em abas, cada uma com uma função específica:Segmentar Arquivo: Divide um ficheiro com base nos valores únicos de uma ou mais colunas.Limpar Dados: Oferece um conjunto de ferramentas para padronizar e corrigir dados (remover duplicados, ajustar capitalização, etc.).Anonimizar Dados: Substitui dados sensíveis por informações falsas ou códigos, para proteger a privacidade.Unificar Arquivos: Junta vários ficheiros de uma pasta num único ficheiro consolidado.Analisar Dados: Gera um relatório estatístico rápido sobre o conteúdo de um ficheiro.Comparar Arquivos: Mostra as diferenças (linhas adicionadas, removidas e modificadas) entre duas versões de um ficheiro.Visualizar Dados: Cria gráficos simples e rápidos a partir dos dados.Estrutura do ProjetoO projeto está organizado da seguinte forma para manter a modularidade e a clareza:/Data-Toolkit/
|-- main.py               # Ponto de entrada da aplicação
|-- data_toolkit.py       # Ficheiro principal que constrói a UI
|-- README.md             # Este ficheiro
|-- .gitignore            # Ficheiros a serem ignorados pelo Git
|-- requirements.txt      # Dependências Python do projeto
|-- install.sh            # Script de instalação para Linux
|-- assets/
|   |-- icon.png          # Ícone da aplicação
|-- ui/
|   |-- __init__.py
|   |-- base_tab.py       # Classe base com funcionalidades comuns
|   |-- segmenter_tab.py
|   |-- cleaner_tab.py
|   |-- anonymizer_tab.py
|   |-- unifier_tab.py
|   |-- comparer_tab.py
|   |-- profiler_tab.py
|   |-- visualizer_tab.py
Instalação e Execução (Linux)Clone o repositório:git clone [URL_DO_SEU_REPOSITORIO]
cd Data-Toolkit
Crie e ative um ambiente virtual:python3 -m venv venv
source venv/bin/activate
Instale as dependências:pip install -r requirements.txt
Execute o script de instalação:Este script irá construir um executável independente e criar um atalho no seu menu de aplicações.chmod +x install.sh
./install.sh
Após a instalação, pode encontrar e executar o "Data Toolkit" diretamente a partir do seu menu de aplicações, como qualquer outro programa.Execução para DesenvolvimentoSe preferir executar o programa diretamente do código-fonte (sem instalar), após o passo 3, execute:python3 main.py

