## Sistema Controle de Estoque e Doações para instituições beneficentes

Sistema web interativo desenvolvido em **Python** utilizando **Streamlit**, projetado especificamente para otimizar o controle de inventário, o cadastro de doadores e o gerenciamento de doações de instituições beneficentes.

<img width="1366" height="624" alt="Screenshot From 2026-10-12 23-38-52" src="https://github.com/user-attachments/assets/d0271fde-90c7-43f7-84bc-3954e135a33a" />
---

## Funcionalidades Principais

* **📊 Painel de Controle e Alertas Inteligentes:**
* Visão geral com métricas em tempo real de produtos, doadores e movimentações.

* Alertas automáticos para produtos com estoque igual ou abaixo do mínimo recomendado.

* Avisos preventivos para itens com prazos de validade vencidos ou próximos do vencimento (30 dias).


* **🛠️ Gestão de Produtos (CRUD):**
* Cadastro detalhado com categorias fixas (*Alimentos, Higiene Pessoal, Limpeza, Vestuário, Medicamentos, Outros*), controle de estoque mínimo e datas de validade.


* Ferramenta de busca rápida por nome e opções para alterar ou excluir registros.

* **🤝 Gestão de Doadores:**
* Cadastro e atualização de parceiros e empresas doadoras (com contato e e-mail).

* Histórico integrado vinculando cada doação diretamente ao seu respectivo doador.

* **📝 Registro de Movimentações:**
* Abas dedicadas para registro ágil de doações recebidas, entradas avulsas e saídas/distribuições com validação de estoque.

* **📈 Curva ABC e Painel Analítico:**
* Classificação de itens por relevância de consumo utilizando a metodologia ABC (Classes A, B e C).

* Gráficos interativos construídos com **Plotly** exibindo comparativos de estoque, volume de saídas e distribuição por categorias.

<img width="1366" height="624" alt="Screenshot From 2026-10-12 23-39-58" src="https://github.com/user-attachments/assets/12e9aeda-7bff-425b-b150-bee0a221892b" />

* **📊 Históricos & Relatórios:**
* Tabelas completas de histórico de doações e movimentações.


* Exportação de dados e relatórios gerais diretamente para o formato **CSV**.

* **🤖 Analista Virtual (IA Integrada):**
* Assistente interativo capaz de analisar o estado atual do estoque, itens críticos, validades e doadores de forma automatizada por chat.


## 💻 Tecnologias Utilizadas

* **Python** (Linguagem principal)


* **Streamlit** (Interface gráfica web)


* **Pandas** (Manipulação e persistência de dados em arquivos CSV)


* **Plotly Express** (Visualização de dados e gráficos analíticos)

---

## ⚙️ Como Executar o Projeto Localmente

1. Certifique-se de ter o **Python** instalado em sua máquina.
2. Clone este repositório:
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio

```

3. Instale as dependências necessárias:
```bash
pip install streamlit pandas plotly

```
4. Execute a aplicação via Streamlit:
```bash
streamlit run sistema_main.py

```
---
