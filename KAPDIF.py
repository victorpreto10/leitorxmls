import streamlit as st
import re


# Função para processar os dados de operações inseridos pelo usuário
def processar_dados(dados):
    operacoes = {}
    regex = re.compile(r'([CV])\s(\S+)\s.*?(\d+)(k|K)\s.*?@\s*(\+?-?\d+)')
    for linha in dados:
        match = regex.search(linha)
        if match:
            operacao, ticker, quantidade_str, milhar, valor = match.groups()
            quantidade = int(quantidade_str) * 1000
            valor = int(valor)
            linha_id = f"{ticker}-{quantidade}-{valor}-{operacao}"
            if ticker not in operacoes:
                operacoes[ticker] = {"C": [], "V": []}
            operacoes[ticker][operacao].append((linha, quantidade, valor, linha_id))
    return operacoes


# Atualize esta função conforme necessário para o seu uso
def mostrar_operacoes(operacoes, ticker_escolhido, px_ref):
    if ticker_escolhido in operacoes:
        if 'selecionados' not in st.session_state:
            st.session_state['selecionados'] = set()
        compras = sorted(operacoes[ticker_escolhido]["C"], key=lambda x: x[2], reverse=True)
        vendas = sorted(operacoes[ticker_escolhido]["V"], key=lambda x: x[2])
        for lista_operacoes, tipo in [(compras, "Compras"), (vendas, "Vendas")]:
            st.subheader(f"{tipo} para {ticker_escolhido}:")
            for operacao in lista_operacoes:
                # Correção na fórmula de diferencial para compras e vendas
                diferencial = ((-operacao[2] / 10000) * px_ref) if tipo == "Compras" else (
                            (operacao[2] / 10000) * px_ref)
                checkbox_id = operacao[3]
                check = st.checkbox(f"{operacao[0]} | Diferencial: {diferencial:.6f} R$", key=checkbox_id,
                                    value=checkbox_id in st.session_state['selecionados'])
                if check:
                    st.session_state['selecionados'].add(checkbox_id)
                else:
                    st.session_state['selecionados'].discard(checkbox_id)
    pass


if 'dados_operacoes' not in st.session_state:
    st.session_state['dados_operacoes'] = []

if 'px_ref_por_ativo' not in st.session_state:
    st.session_state['px_ref_por_ativo'] = {}

if 'limpar_adicionais' not in st.session_state:
    st.session_state['limpar_adicionais'] = False

st.title("NIVÉIS ARBITRAGEM KAPITALO ")

with st.sidebar:
    st.header("Inserir e Gerenciar Dados")
    if not st.session_state['dados_operacoes']:
        dados_raw = st.text_area("Cole os dados das operações aqui:", height=150, key="dados_iniciais", value="")
        if st.button("Salvar Dados Iniciais"):
            if dados_raw:
                linhas = dados_raw.strip().split("\n")
                st.session_state['dados_operacoes'].extend(linhas)
                st.success("Dados adicionados com sucesso!")

        # Botão para adicionar operações adicionais
    dados_adicionais = st.text_area("Cole operações adicionais aqui:", height=150, key="dados_adicionais",
                                    value=st.session_state.get('dados_adicionais', ''))
    if st.button("Adicionar Operações"):
        if dados_adicionais:
            linhas_adicionais = dados_adicionais.strip().split("\n")
            st.session_state['dados_operacoes'].extend(linhas_adicionais)
            st.success("Operações adicionais adicionadas com sucesso!")
            st.session_state['limpar_adicionais'] = True

    # Botão para apagar todos os dados
    if st.button("Apagar Todos os Dados"):
        st.session_state['dados_operacoes'] = []
        st.session_state['px_ref_por_ativo'] = {}
        st.session_state['limpar_adicionais'] = False
        st.experimental_rerun()

# Exibição das operações e interação com o usuário para seleção de ticker e Px Ref.
if st.session_state['dados_operacoes']:
    operacoes_processadas = processar_dados(st.session_state['dados_operacoes'])
    tickers = list(operacoes_processadas.keys())
    ticker_escolhido = st.selectbox("Escolha um ticker:", [""] + tickers)
    if ticker_escolhido:
        px_ref_key = f"px_ref_{ticker_escolhido}"
        px_ref = st.number_input("Px Ref.:", min_value=0.01, step=0.01, format="%.2f", key=px_ref_key,
                                 value=st.session_state['px_ref_por_ativo'].get(ticker_escolhido, 0.01))
        st.session_state['px_ref_por_ativo'][ticker_escolhido] = px_ref
        mostrar_operacoes(operacoes_processadas, ticker_escolhido, px_ref)