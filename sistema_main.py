from datetime import date, datetime, timedelta
import os
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Sistema de Gestão de Estoque e Doações",
    page_icon="📦",
    layout="wide",
)

# =====================================================================
# FUNÇÕES DE PERSISTÊNCIA EM ARQUIVOS CSV E DADOS INICIAIS
# =====================================================================
def carregar_ou_criar_csv(nome_arquivo, colunas_padrao, dados_iniciais=None):
  if os.path.exists(nome_arquivo):
    try:
      return pd.read_csv(nome_arquivo)
    except Exception:
      return pd.DataFrame(columns=colunas_padrao)
  else:
    if dados_iniciais:
      df = pd.DataFrame(dados_iniciais)
    else:
      df = pd.DataFrame(columns=colunas_padrao)
    df.to_csv(nome_arquivo, index=False)
    return df


def salvar_csv(df, nome_arquivo):
  df.to_csv(nome_arquivo, index=False)


# Dados Iniciais de Teste (Carregados apenas se o CSV não existir no PC)
produtos_iniciais = [
    {
        "ID": 1,
        "Nome": "Arroz 5kg",
        "Categoria": "Alimentos",
        "Estoque Minimo": 5,
        "Validade": "2026-12-31",
        "Quantidade": 12,
    },
    {
        "ID": 2,
        "Nome": "Feijão 1kg",
        "Categoria": "Alimentos",
        "Estoque Minimo": 4,
        "Validade": "2026-11-15",
        "Quantidade": 3,
    },
    {
        "ID": 3,
        "Nome": "Sabonete",
        "Categoria": "Higiene Pessoal",
        "Estoque Minimo": 10,
        "Validade": "2027-05-20",
        "Quantidade": 25,
    },
]

doadores_iniciais = [
    {
        "ID": 1,
        "Nome": "Supermercado Real",
        "Contato": "15 99888-7766",
        "Email": "contato@real.com",
    },
    {
        "ID": 2,
        "Nome": "Associação Beneficente",
        "Contato": "15 98765-4321",
        "Email": "apoio@assoc.org",
    },
]

# Inicialização da Sessão com leitura/gravação em arquivos CSV
if "produtos" not in st.session_state:
  st.session_state.produtos = carregar_ou_criar_csv(
      "produtos.csv",
      ["ID", "Nome", "Categoria", "Estoque Minimo", "Validade", "Quantidade"],
      produtos_iniciais,
  )

if "doadores" not in st.session_state:
  st.session_state.doadores = carregar_ou_criar_csv(
      "doadores.csv", ["ID", "Nome", "Contato", "Email"], doadores_iniciais
  )

if "movimentacoes" not in st.session_state:
  st.session_state.movimentacoes = carregar_ou_criar_csv(
      "movimentacoes.csv", [
          "Data",
          "Tipo",
          "Produto",
          "Quantidade",
          "Doador/Destino",
          "Consumo Diario Medio",
      ]
  )

if "doacoes" not in st.session_state:
  st.session_state.doacoes = carregar_ou_criar_csv(
      "doacoes.csv", ["Data", "Doador", "Produto", "Quantidade", "Validade"]
  )

# Menu Lateral
st.sidebar.image(
    "logo.png", width=200
)  # Substitua "logo.png" pelo nome do seu arquivo de imagem
st.sidebar.title("Menu do Sistema")
menu = st.sidebar.radio(
    "Navegação",
    [
        "Início / Alertas",
        "Gestão de Produtos",
        "Gestão de Doadores",
        "Registrar Doação/Movimentação",
        "Consulta de Estoque & Média",
        "Analista Virtual (IA)",
        "Históricos & Relatórios",
    ],
)

# ---------------------------------------------------------
# 1. INÍCIO / ALERTAS (RF11, RF12)
# ---------------------------------------------------------
if menu == "Início / Alertas":
  st.title("📦 Painel de Controle e Alertas Inteligentes")
  st.markdown(
      "Visão geral do estoque, alertas de estoque mínimo e prazos de validade"
      " baseados em estatísticas."
  )

  df_prod = st.session_state.produtos

  col1, col2, col3 = st.columns(3)
  col1.metric("Total de Produtos Cadastrados", len(df_prod))
  col2.metric("Total de Doadores", len(st.session_state.doadores))
  col3.metric("Total de Movimentações", len(st.session_state.movimentacoes))

  st.divider()

  # Alertas de Estoque Mínimo (RF11)
  st.subheader("⚠️ Alertas de Estoque Mínimo")
  if not df_prod.empty:
    alerta_estoque = df_prod[
        df_prod["Quantidade"] <= df_prod["Estoque Minimo"]
    ]
    if not alerta_estoque.empty:
      st.warning(
          "Os seguintes produtos estão com o estoque abaixo ou igual ao"
          " mínimo recomendado:"
      )
      st.dataframe(alerta_estoque, use_container_width=True)
    else:
      st.success(
          "Nenhum produto com estoque crítico no momento! Todos estão acima"
          " do mínimo."
      )
  else:
    st.info("Nenhum produto cadastrado ainda.")

  # Alertas de Validade (RF12)
  st.subheader("📅 Alertas de Validade (Próximos 30 dias)")
  if not df_prod.empty:
    hoje = pd.to_datetime(date.today())
    df_prod["Validade_DT"] = pd.to_datetime(df_prod["Validade"])
    limite_vencimento = hoje + timedelta(days=30)

    alerta_validade = df_prod[
        (df_prod["Validade_DT"] >= hoje)
        & (df_prod["Validade_DT"] <= limite_vencimento)
    ]
    vencidos = df_prod[df_prod["Validade_DT"] < hoje]

    if not vencidos.empty:
      st.error(
          "🚨 ATENÇÃO: Existem produtos com a **data de validade vencida**!"
      )
      st.dataframe(vencidos, use_container_width=True)

    if not alerta_validade.empty:
      st.warning(
          "Os seguintes produtos estão próximos do vencimento (nos próximos 30"
          " dias):"
      )
      st.dataframe(alerta_validade, use_container_width=True)
    elif vencidos.empty:
      st.success("Nenhum produto próximo ao vencimento.")
  else:
    st.info("Nenhum produto cadastrado.")

# ---------------------------------------------------------
# 2. GESTÃO DE PRODUTOS (RF01, RF02, RF03, RF04)
# ---------------------------------------------------------
elif menu == "Gestão de Produtos":
  st.title("🛠️ Gestão de Produtos")
  st.markdown(
      "Visualize os produtos cadastrados e selecione uma ação no menu abaixo"
      " se desejar gerenciar."
  )

  # Tela principal exibe os produtos diretamente (RF02)
  if not st.session_state.produtos.empty:
    busca = st.text_input("🔍 Pesquisar produto por nome:")
    df_exibicao = st.session_state.produtos
    if busca:
      df_exibicao = df_exibicao[
          df_exibicao["Nome"].str.contains(busca, case=False, na=False)
      ]
    # Agora (exibe apenas as colunas limpas, sem a Validade_DT)
    colunas_visiveis = [
        "ID",
        "Nome",
        "Categoria",
        "Estoque Minimo",
        "Validade",
        "Quantidade",
    ]
    st.dataframe(
        df_exibicao[colunas_visiveis],
        use_container_width=True,
    )
  else:
    st.info("Nenhum produto cadastrado no momento.")

  st.divider()

  # Menu menor / Expansor para Ações de Cadastro, Alteração e Exclusão
  with st.expander("⚙️ Gerenciar Produtos (Cadastrar, Alterar ou Excluir)"):
    acao_prod = st.selectbox(
        "Escolha a operação:",
        [
            "Selecione...",
            "Cadastrar Novo Produto",
            "Alterar Produto",
            "Excluir Produto",
        ],
    )

    if acao_prod == "Cadastrar Novo Produto":
      st.subheader("Novo Produto")

      # Exibe notificação pendente (se houver)
      if "sucesso_cadastro" in st.session_state:
        st.success(st.session_state.sucesso_cadastro)
        del st.session_state["sucesso_cadastro"]

      with st.form("form_cad_prod"):
        nome = st.text_input("Nome do Produto")

        categorias_fixas = [
            "Alimentos",
            "Higiene Pessoal",
            "Limpeza",
            "Vestuário",
            "Medicamentos",
            "Outros",
        ]
        categoria = st.selectbox("Categoria do Produto", categorias_fixas)

        est_min = st.number_input(
            "Estoque Mínimo", min_value=0, value=5, step=1
        )
        quantidade = st.number_input(
            "Quantidade Inicial", min_value=0, value=0, step=1
        )
        validade = st.date_input("Data de Validade")

        submitted = st.form_submit_button("Salvar Cadastro")
        if submitted:
          if not nome.strip():
            st.error("Preencha o nome do produto.")
          else:
            nome_limpo = nome.strip().lower()
            nomes_existentes = (
                st.session_state.produtos["Nome"].str.lower().tolist()
            )

            if nome_limpo in nomes_existentes:
              st.error(
                  f"❌ O produto '{nome}' já está cadastrado no sistema!"
                  " Utilize a opção 'Alterar Produto' se deseja atualizar os"
                  " dados."
              )
            else:
              novo_id = (
                  int(st.session_state.produtos["ID"].max()) + 1
                  if not st.session_state.produtos.empty
                  else 1
              )
              novo_registro = pd.DataFrame([{
                  "ID": novo_id,
                  "Nome": nome.strip(),
                  "Categoria": categoria,
                  "Estoque Minimo": est_min,
                  "Validade": str(validade),
                  "Quantidade": quantidade,
              }])
              st.session_state.produtos = pd.concat(
                  [st.session_state.produtos, novo_registro], ignore_index=True
              )

              # Salva a mensagem na sessão para exibir após o rerun
              st.session_state.sucesso_cadastro = (
                  f"✅ Produto '{nome.strip()}' cadastrado com sucesso!"
              )
              st.rerun()

    elif acao_prod == "Alterar Produto":
      if not st.session_state.produtos.empty:
        prod_id = st.selectbox(
            "Selecione o ID do Produto para Alterar",
            st.session_state.produtos["ID"],
        )
        produto_atual = st.session_state.produtos[
            st.session_state.produtos["ID"] == prod_id
        ].iloc[0]

        with st.form("form_alt_prod"):
          novo_nome = st.text_input("Nome", value=produto_atual["Nome"])

          categorias_fixas = [
              "Alimentos",
              "Higiene Pessoal",
              "Limpeza",
              "Vestuário",
              "Medicamentos",
              "Outros",
          ]
          cat_atual_idx = (
              categorias_fixas.index(produto_atual["Categoria"])
              if produto_atual["Categoria"] in categorias_fixas
              else 0
          )
          nova_cat = st.selectbox(
              "Categoria", categorias_fixas, index=cat_atual_idx
          )

          novo_min = st.number_input(
              "Estoque Mínimo",
              min_value=0,
              value=int(produto_atual["Estoque Minimo"]),
          )
          nova_qtd = st.number_input(
              "Quantidade",
              min_value=0,
              value=int(produto_atual["Quantidade"]),
          )
          nova_val = st.date_input(
              "Validade",
              value=datetime.strptime(
                  produto_atual["Validade"], "%Y-%m-%d"
              ).date(),
          )

          btn_atualizar = st.form_submit_button("Salvar Alterações")
          if btn_atualizar:
            idx = st.session_state.produtos[
                st.session_state.produtos["ID"] == prod_id
            ].index[0]
            st.session_state.produtos.loc[idx] = [
                prod_id,
                novo_nome.strip(),
                nova_cat,
                novo_min,
                str(nova_val),
                nova_qtd,
            ]
            st.success("✅ Produto atualizado com sucesso!")
            st.rerun()
      else:
        st.info("Não há produtos para alterar.")

    elif acao_prod == "Excluir Produto":
      if not st.session_state.produtos.empty:
        prod_id_exc = st.selectbox(
            "Selecione o ID do Produto para Excluir",
            st.session_state.produtos["ID"],
            key="del_prod",
        )
        if st.button("Confirmar Exclusão"):
          st.session_state.produtos = st.session_state.produtos[
              st.session_state.produtos["ID"] != prod_id_exc
          ]
          st.success("✅ Produto excluído com sucesso!")
          st.rerun()
      else:
        st.info("Não há produtos para excluir.")

# ---------------------------------------------------------
# 3. GESTÃO DE DOADORES (RF05, RF06)
# ---------------------------------------------------------
elif menu == "Gestão de Doadores":
  st.title("🤝 Gestão de Doadores")
  st.markdown(
      "Visualize os doadores cadastrados, histórico de doações e gerencie o"
      " cadastro."
  )

  # Tabela Principal de Doadores Cadastrados
  if not st.session_state.doadores.empty:
    st.subheader("📋 Lista de Doadores Cadastrados")
    st.dataframe(
        st.session_state.doadores, use_container_width=True, hide_index=True
    )
  else:
    st.info("Nenhum doador cadastrado no momento.")

  st.divider()

  # Painel de Doações por Doador (Quem doou o quê)
  st.subheader("📦 Painel: Histórico de Doações por Doador")
  if not st.session_state.doacoes.empty:
    st.dataframe(
        st.session_state.doacoes, use_container_width=True, hide_index=True
    )
  else:
    st.info(
        "Nenhuma doação registrada ainda. As doações aparecerão aqui vinculadas"
        " aos doadores."
    )

  st.divider()

  # Expansor para Gerenciar Doadores (Cadastrar, Alterar, Excluir)
  with st.expander("⚙️ Gerenciar Doadores (Cadastrar, Alterar ou Excluir)"):
    acao_doador = st.selectbox(
        "Escolha a operação para Doadores:",
        [
            "Selecione...",
            "Cadastrar Novo Doador",
            "Alterar Doador",
            "Excluir Doador",
        ],
        key="acao_doador_select",
    )

    if acao_doador == "Cadastrar Novo Doador":
      st.subheader("Novo Doador")

      if "sucesso_doador" in st.session_state:
        st.success(st.session_state.sucesso_doador)
        del st.session_state["sucesso_doador"]

      with st.form("form_doador"):
        nome_d = st.text_input("Nome do Doador / Empresa")
        contato_d = st.text_input("Telefone / Contato")
        email_d = st.text_input("E-mail")
        btn_doador = st.form_submit_button("Cadastrar Doador")

        if btn_doador:
          if not nome_d.strip():
            st.error("Informe o nome do doador.")
          else:
            nome_d_limpo = nome_d.strip().lower()
            doadores_existentes = (
                st.session_state.doadores["Nome"].str.lower().tolist()
                if not st.session_state.doadores.empty
                else []
            )

            if nome_d_limpo in doadores_existentes:
              st.error(
                  f"❌ O doador '{nome_d.strip()}' já está cadastrado no"
                  " sistema! Utilize a opção 'Alterar Doador' se deseja"
                  " atualizar os dados."
              )
            else:
              novo_id_d = (
                  int(st.session_state.doadores["ID"].max()) + 1
                  if not st.session_state.doadores.empty
                  else 1
              )
              novo_doador = pd.DataFrame([{
                  "ID": novo_id_d,
                  "Nome": nome_d.strip(),
                  "Contato": contato_d.strip(),
                  "Email": email_d.strip(),
              }])
              st.session_state.doadores = pd.concat(
                  [st.session_state.doadores, novo_doador], ignore_index=True
              )
              st.session_state.sucesso_doador = (
                  f"✅ Doador '{nome_d.strip()}' cadastrado com sucesso!"
              )
              st.rerun()

    elif acao_doador == "Alterar Doador (RF06)":
      if not st.session_state.doadores.empty:
        doador_id = st.selectbox(
            "Selecione o ID do Doador para Alterar",
            st.session_state.doadores["ID"],
            key="alt_doador_id",
        )
        doador_atual = st.session_state.doadores[
            st.session_state.doadores["ID"] == doador_id
        ].iloc[0]

        with st.form("form_alt_doador"):
          novo_nome_d = st.text_input("Nome", value=doador_atual["Nome"])
          novo_contato_d = st.text_input(
              "Contato", value=doador_atual["Contato"]
          )
          novo_email_d = st.text_input("E-mail", value=doador_atual["Email"])
          btn_alt_doador = st.form_submit_button("Salvar Alterações")

          if btn_alt_doador:
            idx_d = st.session_state.doadores[
                st.session_state.doadores["ID"] == doador_id
            ].index[0]
            st.session_state.doadores.loc[idx_d] = [
                doador_id,
                novo_nome_d.strip(),
                novo_contato_d,
                novo_email_d,
            ]
            st.success("✅ Doador atualizado com sucesso!")
            st.rerun()
      else:
        st.info("Não há doadores cadastrados para alterar.")

    elif acao_doador == "Excluir Doador":
      if not st.session_state.doadores.empty:
        doador_id_exc = st.selectbox(
            "Selecione o ID do Doador para Excluir",
            st.session_state.doadores["ID"],
            key="del_doador_id",
        )
        if st.button("Confirmar Exclusão do Doador"):
          st.session_state.doadores = st.session_state.doadores[
              st.session_state.doadores["ID"] != doador_id_exc
          ]
          st.success("✅ Doador excluído com sucesso!")
          st.rerun()
      else:
        st.info("Não há doadores cadastrados para excluir.")
# ---------------------------------------------------------
# 4. REGISTRAR DOAÇÃO / ENTRADA / SAÍDA (RF07, RF08, RF09)
# ---------------------------------------------------------
elif menu == "Registrar Doação/Movimentação":
  st.title("📝 Registro de Doações e Movimentações")

  tab1, tab2, tab3 = st.tabs(
      [
          "Registrar Doação",
          "Entrada de Produto",
          "Saída de Produto",
      ]
  )

  with tab1:
    st.subheader("Registrar Doação Recebida")
    if (
        not st.session_state.produtos.empty
        and not st.session_state.doadores.empty
    ):
      with st.form("form_doacao"):
        doador_escolhido = st.selectbox(
            "Doador", st.session_state.doadores["Nome"]
        )
        produto_escolhido = st.selectbox(
            "Produto", st.session_state.produtos["Nome"]
        )
        qtd_doada = st.number_input(
            "Quantidade Doada", min_value=1, value=1, step=1
        )
        data_doacao = st.date_input("Data da Doação", value=date.today())

        btn_reg_doacao = st.form_submit_button("Registrar Doação")
        if btn_reg_doacao:
          idx = st.session_state.produtos[
              st.session_state.produtos["Nome"] == produto_escolhido
          ].index[0]
          st.session_state.produtos.loc[idx, "Quantidade"] += qtd_doada

          nova_doacao = pd.DataFrame([{
              "Data": str(data_doacao),
              "Doador": doador_escolhido,
              "Produto": produto_escolhido,
              "Quantidade": qtd_doada,
              "Validade": st.session_state.produtos.loc[idx, "Validade"],
          }])
          st.session_state.doacoes = pd.concat(
              [st.session_state.doacoes, nova_doacao], ignore_index=True
          )

          nova_mov = pd.DataFrame([{
              "Data": str(data_doacao),
              "Tipo": "Entrada (Doação)",
              "Produto": produto_escolhido,
              "Quantidade": qtd_doada,
              "Doador/Destino": doador_escolhido,
              "Consumo Diario Medio": 0.0,
          }])
          st.session_state.movimentacoes = pd.concat(
              [st.session_state.movimentacoes, nova_mov], ignore_index=True
          )

          st.success("✅ Doação registrada e estoque atualizado com sucesso!")
    else:
      st.warning(
          "Cadastre pelo menos um **Produto** e um **Doador** antes de registrar"
          " doações."
      )

  with tab2:
    st.subheader("Registrar Entrada Avulsa de Produto")
    if not st.session_state.produtos.empty:
      with st.form("form_entrada"):
        prod_e = st.selectbox(
            "Produto", st.session_state.produtos["Nome"], key="prod_ent"
        )
        qtd_e = st.number_input(
            "Quantidade de Entrada", min_value=1, value=1, key="qtd_ent"
        )
        origem = st.text_input("Origem (Ex: Compra, Reposição)")
        data_e = st.date_input("Data da Entrada", value=date.today(), key="dt_e")

        if st.form_submit_button("Confirmar Entrada"):
          idx = st.session_state.produtos[
              st.session_state.produtos["Nome"] == prod_e
          ].index[0]
          st.session_state.produtos.loc[idx, "Quantidade"] += qtd_e

          nova_mov = pd.DataFrame([{
              "Data": str(data_e),
              "Tipo": "Entrada Avulsa",
              "Produto": prod_e,
              "Quantidade": qtd_e,
              "Doador/Destino": origem,
              "Consumo Diario Medio": 0.0,
          }])
          st.session_state.movimentacoes = pd.concat(
              [st.session_state.movimentacoes, nova_mov], ignore_index=True
          )
          st.success("✅ Entrada registrada com sucesso!")
    else:
      st.info("Nenhum produto cadastrado.")

  with tab3:
    st.subheader("Registrar Saída de Produto (Distribuição/Baixa)")
    if not st.session_state.produtos.empty:
      with st.form("form_saida"):
        prod_s = st.selectbox(
            "Produto", st.session_state.produtos["Nome"], key="prod_sai"
        )
        qtd_s = st.number_input(
            "Quantidade de Saída", min_value=1, value=1, key="qtd_sai"
        )
        destino = st.text_input(
            "Destino / Beneficiário (Ex: Família Carentes, Descarte)"
        )
        data_s = st.date_input("Data da Saída", value=date.today(), key="dt_s")

        if st.form_submit_button("Confirmar Saída"):
          idx = st.session_state.produtos[
              st.session_state.produtos["Nome"] == prod_s
          ].index[0]
          qtd_atual = st.session_state.produtos.loc[idx, "Quantidade"]

          if qtd_atual >= qtd_s:
            st.session_state.produtos.loc[idx, "Quantidade"] -= qtd_s

            nova_mov = pd.DataFrame([{
                "Data": str(data_s),
                "Tipo": "Saída",
                "Produto": prod_s,
                "Quantidade": qtd_s,
                "Doador/Destino": destino,
                "Consumo Diario Medio": round(qtd_s / 30.0, 2),
            }])
            st.session_state.movimentacoes = pd.concat(
                [st.session_state.movimentacoes, nova_mov], ignore_index=True
            )
            st.success("✅ Saída registrada com sucesso!")
          else:
            st.error("❌ Quantidade de saída maior do que o estoque disponível!")
    else:
      st.info("Nenhum produto cadastrado.")

# ---------------------------------------------------------
# 5. CONSULTA DE ESTOQUE & CURVA ABC (RF10, RF15)
# ---------------------------------------------------------
elif menu == "Consulta de Estoque & Média":
  st.title("📊 Consulta de Estoque, Curva ABC e Painel Analítico")

  st.subheader("Consulta de Estoque Atual")
  if not st.session_state.produtos.empty:
    colunas_visiveis = [
        "ID",
        "Nome",
        "Categoria",
        "Estoque Minimo",
        "Validade",
        "Quantidade",
    ]
    st.dataframe(
        st.session_state.produtos[colunas_visiveis],
        use_container_width=True,
        hide_index=True,
    )
  else:
    st.info("Estoque vazio.")

  st.divider()

  st.subheader("📈 Análise da Curva ABC")
  st.markdown(
      "Classificação dos itens do estoque por ordem de relevância de consumo"
      " (Método ABC: Classe A até 80%, B até 95%, C restante)."
  )

  if not st.session_state.produtos.empty:
    df_prod = st.session_state.produtos.copy()

    # Agrega o total de saídas por produto
    if (
        not st.session_state.movimentacoes.empty
        and "Tipo" in st.session_state.movimentacoes.columns
        and "Produto" in st.session_state.movimentacoes.columns
    ):
      df_saidas = st.session_state.movimentacoes[
          st.session_state.movimentacoes["Tipo"] == "Saída"
      ]
      if not df_saidas.empty:
        resumo_saidas = (
            df_saidas.groupby("Produto")["Quantidade"]
            .agg(Total_Saidas="sum")
            .reset_index()
        )
      else:
        resumo_saidas = pd.DataFrame(columns=["Produto", "Total_Saidas"])
    else:
      resumo_saidas = pd.DataFrame(columns=["Produto", "Total_Saidas"])

    analise = pd.merge(
        df_prod,
        resumo_saidas,
        left_on="Nome",
        right_on="Produto",
        how="left",
    ).fillna({"Total_Saidas": 0})

    # Ordena do maior para o menor consumo
    analise = analise.sort_values(
        by="Total_Saidas", ascending=False
    ).reset_index(drop=True)

    total_geral_saidas = analise["Total_Saidas"].sum()

    if total_geral_saidas > 0:
      analise["Porcentual Individual (%)"] = round(
          (analise["Total_Saidas"] / total_geral_saidas) * 100, 2
      )
      analise["Porcentagem Acumulada (%)"] = analise[
          "Porcentual Individual (%)"
      ].cumsum()

      def atribui_classe(acumulado):
        if acumulado <= 80.0:
          return "A"
        elif acumulado <= 95.0:
          return "B"
        else:
          return "C"

      analise["Classificação"] = analise["Porcentagem Acumulada (%)"].apply(
          atribui_classe
      )
    else:
      # Se não houver saídas, distribui de forma inteligente ou trata como C padrão
      analise["Porcentual Individual (%)"] = 0.0
      analise["Porcentagem Acumulada (%)"] = 0.0
      analise["Classificação"] = "C"

    if "Produto" in analise.columns and "Nome" in analise.columns:
      analise = analise.drop(columns=["Produto"], errors="ignore")

    colunas_abc = [
        "ID",
        "Nome",
        "Quantidade",
        "Total_Saidas",
        "Porcentual Individual (%)",
        "Porcentagem Acumulada (%)",
        "Classificação",
    ]
    df_exib_abc = analise[colunas_abc].rename(
        columns={"Total_Saidas": "Consumo"}
    )

    st.dataframe(df_exib_abc, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("📊 Dashboard Analítico Avançado")

    import plotly.express as px

    # Linha 1 de Gráficos (2 colunas)
    col_g1, col_g2 = st.columns(2)

    with col_g1:
      st.markdown("**1. Comparativo: Estoque Atual x Mínimo Requerido**")
      fig1 = px.bar(
          analise.head(15),
          x="Nome",
          y=["Quantidade", "Estoque Minimo"],
          barmode="group",
          color_discrete_sequence=["#00539F", "#FF4B4B"],
          labels={"value": "Unidades", "Nome": "Produto"},
      )
      fig1.update_layout(
          plot_bgcolor="rgba(0,0,0,0)",
          paper_bgcolor="rgba(0,0,0,0)",
          xaxis_tickangle=-45,
          legend_title="Legenda",
      )
      st.plotly_chart(fig1, use_container_width=True)

    with col_g2:
      st.markdown("**2. Volume Total de Saídas / Consumo**")
      fig2 = px.bar(
          analise.head(15),
          x="Nome",
          y="Total_Saidas",
          color_discrete_sequence=["#00539F"],
          labels={"Total_Saidas": "Total Consumido", "Nome": "Produto"},
      )
      fig2.update_layout(
          plot_bgcolor="rgba(0,0,0,0)",
          paper_bgcolor="rgba(0,0,0,0)",
          xaxis_tickangle=-45,
      )
      st.plotly_chart(fig2, use_container_width=True)

# Linha 2 de Gráficos (Novos gráficos para complementar a apresentação)
    col_g3, col_g4 = st.columns(2)

    with col_g3:
      st.markdown("**3. Distribuição de Produtos por Categoria**")
      df_cat = (
          st.session_state.produtos["Categoria"]
          .value_counts()
          .reset_index()
      )
      df_cat.columns = ["Categoria", "Total"]
      fig3 = px.pie(
          df_cat,
          names="Categoria",
          values="Total",
          hole=0.4,
          color_discrete_sequence=px.colors.qualitative.Pastel,
      )
      fig3.update_layout(
          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
      )
      st.plotly_chart(fig3, use_container_width=True)

    with col_g4:
      st.markdown("**4. Nível de Estoque vs Categoria (Média)**")
      df_media_cat = (
          st.session_state.produtos.groupby("Categoria")["Quantidade"]
          .mean()
          .reset_index()
      )
      fig4 = px.bar(
          df_media_cat,
          x="Categoria",
          y="Quantidade",
          color="Categoria",
          color_discrete_sequence=px.colors.qualitative.Set2,
          labels={"Quantidade": "Média em Estoque"},
      )
      fig4.update_layout(
          plot_bgcolor="rgba(0,0,0,0)",
          paper_bgcolor="rgba(0,0,0,0)",
          showlegend=False,
      )
      st.plotly_chart(fig4, use_container_width=True)

  else:
    st.info("Cadastre produtos para visualizar os gráficos analíticos.")
    
# ---------------------------------------------------------
# 6. HISTÓRICOS & RELATÓRIOS (RF13, RF14, RF16, RF17)
# ---------------------------------------------------------
elif menu == "Históricos & Relatórios":
  st.title("📈 Históricos e Geração de Relatórios")

  tab1, tab2, tab3, tab4 = st.tabs(
      [
          "Histórico de Doações",
          "Histórico de Movimentações",
          "Relatório de Estoque",
          "Relatório de Doações",
      ]
  )

  with tab1:
    st.subheader("Histórico Completo de Doações")
    if not st.session_state.doacoes.empty:
      st.dataframe(st.session_state.doacoes, use_container_width=True)
    else:
      st.info("Nenhum histórico de doações registrado.")

  with tab2:
    st.subheader("Histórico de Movimentações (Entradas e Saídas)")
    if not st.session_state.movimentacoes.empty:
      st.dataframe(st.session_state.movimentacoes, use_container_width=True)
    else:
      st.info("Nenhuma movimentação registrada.")

  with tab3:
    st.subheader("Relatório de Estoque Geral")
    if not st.session_state.produtos.empty:
      st.dataframe(st.session_state.produtos, use_container_width=True)
      csv_estoque = st.session_state.produtos.to_csv(index=False).encode(
          "utf-8"
      )
      st.download_button(
          label="📥 Baixar Relatório de Estoque (CSV)",
          data=csv_estoque,
          file_name="relatorio_estoque.csv",
          mime="text/csv",
      )
    else:
      st.info("Sem dados para relatório.")

  with tab4:
    st.subheader("Relatório de Doações")
    if not st.session_state.doacoes.empty:
      st.dataframe(st.session_state.doacoes, use_container_width=True)
      csv_doacoes = st.session_state.doacoes.to_csv(index=False).encode(
          "utf-8"
      )
      st.download_button(
          label="📥 Baixar Relatório de Doações (CSV)",
          data=csv_doacoes,
          file_name="relatorio_doacoes.csv",
          mime="text/csv",
      )
    else:
      st.info("Sem dados de doações para relatório.")

# ---------------------------------------------------------
# 6. ANALISTA VIRTUAL: IA COM FALLBACK INTELIGENTE
# ---------------------------------------------------------
elif menu == "Analista Virtual (IA)":
  st.title("🤖 Analista Virtual de Estoque e Doações")
  st.markdown(
      "Converse com o assistente inteligente para analisar dados do estoque,"
      " doadores e movimentações."
  )

  # Inicializa o estado de autenticação na sessão
  if "token_validado" not in st.session_state:
    st.session_state.token_validado = False

  col_tit, col_btn = st.columns([0.85, 0.15])
  with col_btn:
    if st.button("🗑️ Limpar Chat"):
      if "historico_chat" in st.session_state:
        del st.session_state["historico_chat"]
      st.session_state.token_validado = False
      st.rerun()

  # Se ainda não validou o token, exibe o campo de senha
  if not st.session_state.token_validado:
    meu_token = st.text_input(
        "Insira sua API Key para habilitar o chat:", type="password"
    )
    if meu_token:
      st.session_state.token_validado = True
      st.rerun()
  else:
    st.success("✅ Assistente conectado e pronto para uso!")

    # Inicializa a memória do chat se estiver vazia
    if "historico_chat" not in st.session_state:
      st.session_state["historico_chat"] = [{
          "role": "assistant",
          "content": (
              "Olá! Sou seu analista logístico integrado. O que você gostaria"
              " de analisar no estoque ou nas doações de hoje?"
          ),
      }]

    # Exibe as mensagens na tela
    for msg in st.session_state["historico_chat"]:
      with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

    # Recebe a nova pergunta do usuário
    pergunta = st.chat_input(
        "Ex: Qual produto está com o estoque abaixo do mínimo?"
    )

    if pergunta:
      with st.chat_message("user"):
        st.markdown(pergunta)

      st.session_state["historico_chat"].append(
          {"role": "user", "content": pergunta}
      )

      p_texto = pergunta.lower()
      resposta_ia = ""

      df_p = st.session_state.produtos
      df_d = st.session_state.doadores
      df_m = st.session_state.movimentacoes
      df_doac = st.session_state.doacoes

      # Processamento analítico inteligente
      if (
          "crítico" in p_texto
          or "minimo" in p_texto
          or "baixo" in p_texto
          or "precisa" in p_texto
      ):
        if not df_p.empty:
          criticos = df_p[df_p["Quantidade"] <= df_p["Estoque Minimo"]]
          if not criticos.empty:
            detalhes = []
            for _, r in criticos.iterrows():
              detalhes.append(
                  f"- **{r['Nome']}**: Quantidade atual ({r['Quantidade']})"
                  f" está abaixo ou igual ao mínimo ({r['Estoque Minimo']})."
              )
            resposta_ia = (
                "⚠️ **Itens em Situação Crítica / Necessidade de Reposição:**\n"
                + "\n".join(detalhes)
            )
          else:
            resposta_ia = (
                "✅ Ótima notícia! Nenhum produto está com estoque abaixo do"
                " mínimo recomendado no momento."
            )
        else:
          resposta_ia = "Ainda não há produtos cadastrados no sistema."

      elif "doador" in p_texto or "quem" in p_texto or "doou" in p_texto:
        if not df_d.empty:
          nomes_d = ", ".join(df_d["Nome"].tolist())
          total_d = len(df_d)
          resposta_ia = (
              f"🤝 Existem **{total_d} doador(es) cadastrado(s)**: {nomes_d}."
          )
          if not df_doac.empty:
            resposta_ia += (
                "\n\n**Últimas doações registradas:**\n"
                f"{df_doac.tail(5).to_string(index=False)}"
            )
        else:
          resposta_ia = "Não há doadores cadastrados no sistema."

      elif "validade" in p_texto or "venc" in p_texto or "prazo" in p_texto:
        if not df_p.empty:
          hoje = pd.to_datetime(date.today())
          df_p["Validade_DT"] = pd.to_datetime(df_p["Validade"])
          vencidos = df_p[df_p["Validade_DT"] < hoje]
          proximos = df_p[
              (df_p["Validade_DT"] >= hoje)
              & (df_p["Validade_DT"] <= hoje + timedelta(days=30))
          ]

          msg_val = []
          if not vencidos.empty:
            msg_val.append(
                "🚨 **Vencidos:** "
                + ", ".join(vencidos["Nome"].tolist())
                + " estão com a validade expirada!"
            )
          if not proximos.empty:
            msg_val.append(
                "📅 **Próximos do vencimento (30 dias):** "
                + ", ".join(proximos["Nome"].tolist())
            )

          if msg_val:
            resposta_ia = "\n\n".join(msg_val)
          else:
            resposta_ia = (
                "✅ Todos os produtos estão com prazos de validade regulares"
                " (sem vencimentos próximos)."
            )
        else:
          resposta_ia = "Não há produtos cadastrados para análise de validade."

      elif "movimentação" in p_texto or "entrada" in p_texto or "saída" in p_texto:
        if not df_m.empty:
          ult_m = df_m.tail(5).to_string(index=False)
          resposta_ia = (
              "📦 **Últimas Movimentações Registradas no Sistema:**\n\n"
              f"`{ult_m}`"
          )
        else:
          resposta_ia = "Ainda não há registros de entradas ou saídas."

      else:
        total_prod = len(df_p) if not df_p.empty else 0
        total_doadores = len(df_d) if not df_d.empty else 0
        total_mov = len(df_m) if not df_m.empty else 0
        resposta_ia = (
            "📊 **Panorama Atual do Sistema:**\n"
            f"- Produtos cadastrados: **{total_prod}**\n"
            f"- Doadores cadastrados: **{total_doadores}**\n"
            f"- Movimentações totais: **{total_mov}**\n\n"
            "💡 *Você pode me perguntar livremente sobre: 'estoque crítico',"
            " 'doadores', 'validades' ou 'movimentações'.*"
        )

      with st.chat_message("assistant"):
        st.markdown(resposta_ia)

      st.session_state["historico_chat"].append(
          {"role": "assistant", "content": resposta_ia}
      )
# ---------------------------------------------------------
# 6. HISTÓRICOS & RELATÓRIOS (RF13, RF14, RF16, RF17)
# ---------------------------------------------------------
elif menu == "Históricos & Relatórios":
  st.title("📈 Históricos e Geração de Relatórios")

  tab1, tab2, tab3, tab4 = st.tabs(
      [
          "Histórico de Doações",
          "Histórico de Movimentações",
          "Relatório de Estoque",
          "Relatório de Doações",
      ]
  )

  with tab1:
    st.subheader("Histórico Completo de Doações")
    if not st.session_state.doacoes.empty:
      st.dataframe(st.session_state.doacoes, use_container_width=True)
    else:
      st.info("Nenhum histórico de doações registrado.")

  with tab2:
    st.subheader("Histórico de Movimentações (Entradas e Saídas)")
    if not st.session_state.movimentacoes.empty:
      st.dataframe(st.session_state.movimentacoes, use_container_width=True)
    else:
      st.info("Nenhuma movimentação registrada.")

  with tab3:
    st.subheader("Relatório de Estoque Geral")
    if not st.session_state.produtos.empty:
      st.dataframe(st.session_state.produtos, use_container_width=True)
      csv_estoque = st.session_state.produtos.to_csv(index=False).encode(
          "utf-8"
      )
      st.download_button(
          label="📥 Baixar Relatório de Estoque (CSV)",
          data=csv_estoque,
          file_name="relatorio_estoque.csv",
          mime="text/csv",
      )
    else:
      st.info("Sem dados para relatório.")

  with tab4:
    st.subheader("Relatório de Doações")
    if not st.session_state.doacoes.empty:
      st.dataframe(st.session_state.doacoes, use_container_width=True)
      csv_doacoes = st.session_state.doacoes.to_csv(index=False).encode(
          "utf-8"
      )
      st.download_button(
          label="📥 Baixar Relatório de Doações (CSV)",
          data=csv_doacoes,
          file_name="relatorio_doacoes.csv",
          mime="text/csv",
      )
    else:
      st.info("Sem dados de doações para relatório.")
