import os
import discord
import asyncio
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from discord.ext import commands
from groq import APITimeoutError as timeoutgroq
from groq import Groq
from openai import  APITimeoutError as timeoutopenai
from openai import OpenAI
from memoriaAI import conectar, encerrar_conexao
from dotenv import load_dotenv
from aiohttp import web

load_dotenv()

# Configuração das chaves de acesso
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Carrega todas as chaves do arquivo .env
CHAVES_API = [
    os.getenv("API_PRINCIPAL"),
    os.getenv("API_RESERVA1"),
    os.getenv("API_RESERVA2"),
    os.getenv("API_RESERVA3"),
    os.getenv("API_RESERVA4"),
    os.getenv("API_RESERVA5"),
    os.getenv("API_RESERVA6"),
    os.getenv("API_RESERVA7"),
    os.getenv("API_RESERVA8"),
    os.getenv("API_RESERVA9"),
    os.getenv("API_RESERVA10"),
    os.getenv("API_RESERVA11"),
    os.getenv("API_RESERVA12"),
    os.getenv("API_RESERVA13")
    
]

# Filtra a lista para garantir que não vai usar chaves vazias ou nulas
CHAVES_ATIVAS = [chave for chave in CHAVES_API if chave]

# Define qual o modelo do seu bot
MODELO_GROQ = "openai/gpt-oss-20b"
MODELO_OPENROUTER = "openrouter/free"
MODELO_GEMINI = "gemini-3.1-flash-lite"
MODELO_Z_IA ="glm-4.7-flash"


# Variável que controla qual chave está ativa no momento (começa na primeira: índice 0)

indice_chave_atual = 0
primeira_chave = CHAVES_ATIVAS[indice_chave_atual]
if primeira_chave.startswith("sk-or-"):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=primeira_chave,
        default_headers={"HTTP-Referer": "https://github.com", "X-Title": "Discord Bot"},
        timeout= 60.0
    )
    modelo_atual=MODELO_OPENROUTER

elif primeira_chave.startswith("gsk_"):
    client = Groq(api_key=CHAVES_ATIVAS[indice_chave_atual] , timeout = 60.0)
    modelo_atual = MODELO_GROQ

elif primeira_chave.startswith("AQ."):
        client =OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=primeira_chave,
        timeout=60.0
    )
        modelo_atual = MODELO_GEMINI




def rotacionar_chave_api():
    global indice_chave_atual, client , modelo_atual
    
    # Avança para a próxima chave. Se chegar na ultima, volta para a 1ª (índice 0)
    indice_chave_atual = (indice_chave_atual + 1) % len(CHAVES_ATIVAS)
    chave_nova = CHAVES_ATIVAS[indice_chave_atual]
    
    # Verifica se a nova chave pertence ao OpenRouter
    if chave_nova.startswith("sk-or-"):
        # Se for a chave do OpenRouter, inicializa usando o cliente OpenAI apontado para eles
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=chave_nova,
            timeout= 60.0,
            default_headers={
                "HTTP-Referer": "https://github.com",
                "X-Title": "Discord Bot"
            }
        )
        modelo_atual = MODELO_OPENROUTER
        
    elif chave_nova.startswith("gsk_"):
        # Atualiza o cliente global com a nova chave automaticamente
        client = Groq(api_key=CHAVES_ATIVAS[indice_chave_atual], timeout= 60.0)
        modelo_atual = MODELO_GROQ

    elif chave_nova.startswith("AQ."):
        client =OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=chave_nova,
        timeout=60.0
    )
        modelo_atual = MODELO_GEMINI

    
    
    print(f"🔄 [SISTEMA] Chave limite atingido! Trocando para a API Key #{indice_chave_atual + 1}")


# --- FUNÇÕES AUXILIARES DO BANCO DE DADOS ---

def todos_os_lembretes_dos_usuarios():
    conexao = conectar()
    cursor = conexao.cursor()
    query = 'SELECT * FROM public.memoriaai'
    cursor.execute(query)
    bancodedados = cursor.fetchall()
    cursor.close()
    encerrar_conexao(conexao)
    return bancodedados


def buscar_lembretes_do_banco(usuario_id, canal_id):
    """Busca os lembretes específicos salvos para este canal/usuário."""
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        
        # Busca as duas colunas necessárias
        query = "SELECT horario, lembrete FROM public.memoriaAI WHERE usuario_id=%s AND canal_id=%s"
        cursor.execute(query, (str(usuario_id), str(canal_id)))
        resultados = cursor.fetchall()
        
        cursor.close()
        encerrar_conexao(conexao)
        
        # Se não houver resultados, retorna logo o aviso
        if not resultados:
            return "Nenhum lembrete anotado ainda."
            
        lembretes_limpos = []
        for horario, lembrete in resultados:
            # Se o horário for um objeto de tempo do banco, formata para string HH:MM
            if horario is not None:
                # Caso o banco retorne como string ou objeto datetime.time, extraímos os minutos e horas
                # Garantindo o formato amigável 'HH:MM'
                hora_formatada = horario.strftime('%H:%M') if hasattr(horario, 'strftime') else str(horario)[:5]
                texto_completo = f"[{hora_formatada}] {lembrete}"
            else:
                texto_completo = f"{lembrete}"
                
            lembretes_limpos.append(texto_completo)
        
        # Junta todos os lembretes quebrando linha (\n) para ficar legível no Discord
        return "\n".join(lembretes_limpos)

    except Exception as e:
        print(f"Erro ao ler banco de dados: {e}")
        return "Nenhum lembrete anotado ainda."


def editar_lembrete_do_banco(novo_texto, texto_antigo , usuario_id , canal_id,horario_novo=None):
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        if horario_novo is not None:

            query = """
                UPDATE public.memoriaai 
                SET lembrete = %s, horario = %s, aviso_30min=%s , enviado=%s 
                WHERE lembrete = %s AND usuario_id = %s AND canal_id = %s
            """
            cursor.execute(query, (novo_texto ,horario_novo,False , False,  texto_antigo, usuario_id, canal_id ))
        else:
            query = """
                UPDATE public.memoriaai 
                SET lembrete = %s, aviso_30min=%s , enviado=%s 
                WHERE lembrete = %s AND usuario_id = %s AND canal_id = %s
            """
            cursor.execute(query, (novo_texto ,False , False,  texto_antigo, usuario_id, canal_id ))
        
        if cursor.rowcount > 0:
            print(f"Sucesso! {cursor.rowcount} ao editar.")
            conexao.commit() 
            sucesso = True
        else:
            print("\nA query rodou, mas nenhum lembrete correspondente foi editado.\n\n")
            # Nenhuma linha alterada, então não precisa commitar nada
            sucesso = False
        
        cursor.close()
        encerrar_conexao(conexao)
        return sucesso
    except Exception as e:
        print(f"Erro ao editar do banco de dados: {e}")
        return False

    
def excluir_lembrete_do_banco(texto_lembrete, usuario_id, canal_id , horario = None):
    tem_horario = False
    if horario is not None:
        tem_horario = True

    try:
        conexao = conectar()
        cursor = conexao.cursor()
        
        if tem_horario:
            query = """
                DELETE FROM public.memoriaai
                WHERE lembrete = %s
                AND usuario_id = %s
                AND canal_id = %s
                AND horario = %s
            """
            cursor.execute(query,(texto_lembrete, usuario_id, canal_id,horario))
        else:
            query = """
                DELETE FROM public.memoriaai
                WHERE lembrete = %s
                AND usuario_id = %s
                AND canal_id = %s
            """

            cursor.execute(query,(texto_lembrete, usuario_id, canal_id))
        if cursor.rowcount > 0:
            print(f"Sucesso! {cursor.rowcount} ao excluir.")
            conexao.commit() 
            sucesso = True
        else:
            print("\nA query rodou, mas nenhum lembrete correspondente foi excluido.\n\n")
            # Nenhuma linha alterada, então não precisa commitar nada
            sucesso = False
            
        cursor.close()
        
        encerrar_conexao(conexao)
        return sucesso
    except Exception as e:
        print(f"Erro ao excluir do banco de dados: {e}")
        return False

def limpar_lembretes_do_banco(usuario_id , canal_id):
    """Apaga todos os registros da tabela memoriaAI."""
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        
        
        query = "DELETE FROM public.memoriaai WHERE usuario_id=%s AND canal_id=%s;"
        cursor.execute(query,(usuario_id,canal_id))
        if cursor.rowcount > 0:
            conexao.commit() 
            print("-> Todos os lembretes do usuario selecionado foram excluídos do banco com sucesso!")
            sucesso = True
        else:
            print("\nA query rodou, não foi possivel limpar o banco de dados.\n\n")
            # Nenhuma linha alterada, então não precisa commitar nada
            sucesso = False
        

        cursor.close()
        encerrar_conexao(conexao)
        return sucesso
    except Exception as e:
        print(f"Erro ao limpar o banco de dados: {e}")
        return False

def salvar_lembrete_no_banco(texto_lembrete, usuario_id, canal_id, horario=None):
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        query = """INSERT INTO public.memoriaai (usuario_id, canal_id, lembrete, horario) VALUES (%s, %s, %s,%s)"""
        cursor.execute(query, (usuario_id, canal_id, texto_lembrete,horario))
        if cursor.rowcount > 0:
            print(f"Sucesso! {cursor.rowcount} Lembrete salvo.")
            conexao.commit() 
            sucesso = True
        else:
            print("\n\nA query rodou, mas nenhum lembrete correspondente foi achado.\n")
            sucesso = False
        cursor.close()
        encerrar_conexao(conexao)
        return sucesso
    except Exception as e:
        print(f"Erro ao salvar no banco de dados: {e}")
        return False


#======================AVISOS DE LEMBRETES AUTOMATICOS===================
async def lembrete_30min_avisado(usuario_id , canal_id ,lembrete , horario=None):
    conexao = conectar()
    cursor = conexao.cursor()
    if horario is not None:
        query = "UPDATE public.memoriaai SET aviso_30min = %s WHERE lembrete = %s AND usuario_id= %s AND canal_id=%s AND horario=%s"
        cursor.execute(query, (True , lembrete , usuario_id, canal_id, horario))
    else:
        query = "UPDATE public.memoriaai SET aviso_30min = %s WHERE lembrete = %s AND usuario_id= %s AND canal_id=%s"
        cursor.execute(query, (True , lembrete , usuario_id, canal_id))
    if cursor.rowcount > 0:
        print(f"\nSucesso! {cursor.rowcount} lembrete de 30 min avisado.\n")
        conexao.commit()
        sucesso = True
        
    else:
        print("\nA query rodou, mas nenhum lembrete correspondente foi editado.\n\n")
        # Nenhuma linha alterada, então não precisa commitar nada
        sucesso = False
        
    
    cursor.close()
    encerrar_conexao(conexao)
    return sucesso


async def enviar_lembrete_30min(usuario_id ,canal_id ,lembrete,  minutos , horario= None):
    canal = bot.get_channel(int(canal_id))
    if canal is None:
        canal = await bot.fetch_channel(int(canal_id))
    await canal.send(f"⏰ Daqui a {minutos} minutos: {lembrete}")
    await lembrete_30min_avisado(usuario_id ,canal_id , lembrete , horario)

async def lembretes_avisados(usuario_id , canal_id ,lembrete , horario=None):
    conexao = conectar()
    cursor = conexao.cursor()
    if horario is not None:
        query = "UPDATE public.memoriaai SET enviado = %s WHERE lembrete = %s AND usuario_id= %s AND canal_id=%s AND horario=%s"
        cursor.execute(query, (True , lembrete , usuario_id, canal_id, horario))
    else:
        query = "UPDATE public.memoriaai SET enviado = %s WHERE lembrete = %s AND usuario_id= %s AND canal_id=%s"
        cursor.execute(query, (True , lembrete , usuario_id, canal_id))
    if cursor.rowcount > 0:
        print(f"\nSucesso! {cursor.rowcount} , editando lembrete que foi marcado como avisado.\n")
        conexao.commit() 
        
    else:
        print("\nA query rodou, mas nenhum lembrete correspondente foi editado.\n\n")
        # Nenhuma linha alterada, então não precisa commitar nada
        
    
    cursor.close()
    encerrar_conexao(conexao)

async def avisar_lembrete_AGORA(usuario_id , canal_id ,lembrete , horario=None):
    canal = bot.get_channel(int(canal_id))
    if canal is None:
        canal = await bot.fetch_channel(int(canal_id))
    await canal.send(f"⏰ ESTÁ NA HORA DE : {lembrete}")
    if horario is not None:
        await lembretes_avisados(usuario_id ,canal_id , lembrete,horario)
    else:
        await lembretes_avisados(usuario_id ,canal_id , lembrete)
    


async def verificar_lembretes():
    while True:
        try:
            agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
            lembretes = todos_os_lembretes_dos_usuarios()
            
            # Se a conexão falhar e retornar None ou lista vazia, pula para o próximo ciclo
            if not lembretes:
                await asyncio.sleep(30)
                continue

            for lembrete in lembretes:
                usuario_id = lembrete[1]
                canal_id = lembrete[2]
                lembrete_escolhido = lembrete[3]
                horario = lembrete[4]  # Este é o objeto 'time' que vem do banco
                aviso_30minutos = lembrete[5]
                todos_avisos_enviados = lembrete[6]
                
                if horario is None:
                    continue
                
                # CORREÇÃO CRUCIAL AQUI: Junta a data de hoje + hora do banco + fuso de SP
                horario_lembrete = datetime.combine(
                    agora.date(),
                    horario,
                    tzinfo=ZoneInfo("America/Sao_Paulo")
                )
            
                diferenca = horario_lembrete - agora
                segundos = diferenca.total_seconds()

                if -300 < segundos < 300:
                    if todos_avisos_enviados == False:
                        await avisar_lembrete_AGORA(usuario_id, canal_id, lembrete_escolhido , horario)

                elif segundos < 0 and todos_avisos_enviados == False:
                    await lembretes_avisados(usuario_id, canal_id, lembrete_escolhido , horario)


                elif segundos <= 1800:
                    if aviso_30minutos == False:
                        minutos = int(segundos // 60)
                        await enviar_lembrete_30min(usuario_id, canal_id, lembrete_escolhido, minutos , horario)

        except Exception as e:
            # Proteção para o while True nunca morrer se o Supabase cair por 1 segundo
            print(f"❌ Erro no loop de verificação de lembretes: {e}")

        # Espera 30 segundos antes de verificar novamente
        await asyncio.sleep(30)

#============================================================================================ 


# Dicionário na memória para isolar a história curta de cada canal/usuário
historico_conversas = {}

async def obter_resposta_groq(id_contexto, mensagem_usuario, usuario_id, canal_id):
    """Executa a chamada da API atualizando os lembretes do banco em tempo real."""
    
    # CORREÇÃO: O prompt busca a memória atualizada do banco toda vez que uma mensagem chega
    lembretes_atuais = buscar_lembretes_do_banco(usuario_id , canal_id)

    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    
    PROMPT_SISTEMA = (
        "Seu nome é AI, uma assistente virtual pessoal focada em lembretes, organização e suporte diário NO DISCORD. "
        "Sua personalidade é extremamente simpática e acolhedora, agindo sempre como uma assistente muito dedicada.\n\n"
        "SEJA SEMPRE BREVE COM NO MAXÍMO 1800 CARACTERES"
        f"LEMBRE-SE, É MUITO IMPORTANTE QUE VOCÊ CALCULE OS LEMBRETES NO HORARIO DE AMERICA/SÃO PAULO/BRASIL, HORA ATUAL:{agora}"
        f"Estes são os lembretes do usuário recuperados do banco de dados agora: [{lembretes_atuais}]. "
        "Você deve SEMPRE lembrar o usuário de todos os LEMBRETES QUE ELE PEDIR. Se o usuário pedir, mostre essa lista com carinho.\n\n"
        "Quando for MOSTRAR os lembretes para o usuario, mostre os lembretes escrito corrigidamente"
        "Siga estritamente estas diretrizes:\n"
        ". Caso o usuario queira limpar todos os lembretes , Retorne no começo do texto o comando 'comandolimpar', excrevendo desta forma o Python executará , separando sua fala por | . Exemplo:'comandolimpar | Todos os seus lembretes foram limpos com sucesso!'\n"
        'REGRAS PARA EXCLUIR LEMBRETES:'
        """
        1. Se o usuário NÃO informar um horário, NÃO coloque horário no comando.

        Formato:
        excluirlembrete texto_do_lembrete | resposta

        Exemplo:
        Usuário: "exclua o lembrete ir comer"
        Comando:
        excluirlembrete ir comer | Pronto! Removi o lembrete.

        2. Se o usuário INFORMAR explicitamente um horário, coloque o horário.

        Exemplo:
        Usuário: "exclua o lembrete de ir comer das 15:00"
        Comando:
        excluirlembrete 15:00 ir comer | Pronto! Removi o lembrete.

        SE O USUARIO INFORMAR DIVERSOS COMANDOS DE UMA UNICA VEZ , SEPARE OS COMANDOS POR /

        EXEMPLO:

        Seu comando: comandoadicionar 19:00 ir comer/ comandoadicionar 22:00 ir jantar | pronto, seus lembretes foram agendados!

        3. NUNCA invente um horário.
        4. NUNCA copie um horário de outro lembrete apenas porque ele existe na memória.
        5. Se o usuário não informar horário, o horário deve ser NULL/None.
        """
        "A regra numero 2 é muito importante que seja escrito o comando da forma correta para que o Python possa fazer a exclusão do lembrete escolhido pelo usuario"
        "6. Caso o usuario queira adicionar um lembrete, Retorne no começo do texto o comando 'comandoadicionar' e o texto a ser adicionado ao banco de dados, excrevendo desta forma o Python executará.,Você deve corrigir a ortografia e salvar da forma que você preferir escrever des de que esteja de acordo com o que o usuario quer adicionar, Dando sempre preferencia para horario primeiro e depois o texto. Exemplo: 'comandoadicionar 07:00 ir a academia | Lembrete agendado com sucesso!'"
        "7. Caso o usuário queira editar um lembrete, você deve retornar uma linha de comando estrita para o sistema antes da sua resposta textual.Siga exatamente a estrutura abaixo, separando os argumentos por vírgula e a sua fala por uma barra vertical (|). As horas devem estar obrigatoriamente no formato HH:MM.Estrutura do comando:comandoeditar [HORA_ANTIGA], [HORA_NOVA], [TEXTO_ANTIGO], [TEXTO_NOVO] | [Sua mensagem de confirmação para o usuário] . Regras estritas:Primeiro argumento: A hora original (antiga) do lembrete no formato HH:MM.Segundo argumento: A nova hora desejada no formato HH:MM (se o usuário não mudar a hora, repita a hora antiga).Terceiro argumento: O texto/descrição antigo do lembrete que estava salvo.Quarto argumento: O novo texto/descrição do lembrete (se o usuário não mudar o texto, repita o texto antigo).Separação: Use uma vírgula para separar cada um dos 4 argumentos. Use o caractere | apenas para separar o comando da sua fala final .Exemplo de aplicação:Pedido do usuário: 'Troque o lembrete das 8 horas de ir correr para ir fazer compras às 14:00' Sua resposta exata: comandoeditar 08:00, 14:00, ir correr, ir fazer compras | Lembrete atualizado com sucesso! '"
        "8. Foco em Organização: Ajude ativamente com os compromissos.\n"
        "9. Tom de Voz: Use palavras gentis, mantenha o profissionalismo como uma assistente gentil \n"
        "10. Na organização, sempre de preferência a mostrar a hora primeiro(se tiver) e depois o lembrete, A hora deve ser formatada em hh:mm, se não tiver minuto somente o hh. Exemplo: '19:00 - Ir Jantar com meus parentes'"
        '''11. REGRAS DE FORMATAÇÃO:
        - NUNCA USE CRASES (`) OU BLOCOS DE CÓDIGO (```) NA PARTE DOS COMANDOS DO SISTEMA.
        - OS COMANDOS DEVEM SER SEMPRE TEXTO PURO, SEM FORMATAÇÃO.
        - O CARACTERE | DEVE SER USADO SOMENTE PARA SEPARAR O COMANDO DA FALA FINAL.
        - O CARACTERE / DEVE SER USADO SOMENTE PARA SEPARAR MÚLTIPLOS COMANDOS.
        - QUANDO ESTIVER MOSTRANDO CÓDIGO PARA O USUÁRIO, COMO CÓDIGO PYTHON OU OUTRA LINGUAGEM, VOCÊ PODE E DEVE USAR BLOCOS DE CÓDIGO , POREM, COM 6 CRASES(`) DESSA FORMA: ``````.EXEMPLO : 'Aqui está uma lista de codigo python ``````Python....`````` ...fico feliz em ajudar com seu projeto python'
        - FORA DE EXEMPLOS OU LISTAS DE CÓDIGO, NÃO USE BLOCOS ```.'''
        "Seja breve, organizada e responda sempre em português com muita doçura."
        "VOCÊ DEVE OBRIGATORIAMENTE MANDAR UMA FALA DEPOIS DA BARRA DE COMANDO PARA MELHOR EXPERIENCIA DO USUARIO!"
        f"Atenção: A lista {lembretes_atuais} mostra o historico de conversa com os lembretes que existem de verdade AGORA. Se um lembrete apareceu no histórico de conversas anterior, mas NÃO está nessa lista atualizada, significa que ele já foi excluído e não existe mais. Nunca mencione lembretes que não estão na lista atualizada."
        "Sempre leia atentamente enviando somente os lembretes ao inves de enviar as mensagens do usuario junto"
        "Lembre-se de caso o usuario diga que o lembrete não foi removido certifiquese de que está digitando o comando da maneira correta"
        f"Sempre diga quanto tempo falta para o lembrete mais proximo se ele estiver adicionando, editando, visualizando ou excluindo um lembrete, para que você use como referencia , esta é a hora atual {agora}"
        "Caso o usuario esteja apenas interagindo,com curiosidades ou coisas relacionadas , não mostre quanto tempo falta para os lembretes"
        
    )

    # Inicializa ou atualiza a instrução de sistema no histórico da sessão
    if id_contexto not in historico_conversas:
        historico_conversas[id_contexto] = [{"role": "system", "content": PROMPT_SISTEMA}]
    else:
        # Atualiza a primeira posição para garantir que a IA veja novos lembretes adicionados
        historico_conversas[id_contexto][0] = {"role": "system", "content": PROMPT_SISTEMA}
    
    # Adiciona a mensagem atual do usuário
    historico_conversas[id_contexto].append({"role": "user", "content": mensagem_usuario})


    # Limita o histórico na memória ram (mantém o sistema + últimas 12 mensagens)
    if len(historico_conversas[id_contexto]) > 13:
        instrucao_sistema = historico_conversas[id_contexto][0]
        ultimas_mensagens = historico_conversas[id_contexto][-12:]
        historico_conversas[id_contexto] = [instrucao_sistema] + ultimas_mensagens

    

#=================MUDAR CHAVES DE API CASO DE RUIM KSKSK=========
    global client
    tentativas = 0
    max_tentativas = len(CHAVES_ATIVAS)
    resposta_ia = ""

    while tentativas < max_tentativas:
        try:
            # Sua chamada síncrona rodando no executor (Mantida exatamente igual)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: client.chat.completions.create(
                    model=modelo_atual,
                    messages=historico_conversas[id_contexto],
                    temperature=0.7,
                )
            )
            
            # Se chegou aqui, a API respondeu! Salvamos a resposta e saímos do while
            resposta_ia = response.choices[0].message.content
            break
        except timeoutopenai:
            print("⏱️ Timeout! Rotacionando API...")
            rotacionar_chave_api()

        except timeoutgroq:
            print("⏱️ Timeout no Groq! Rotacionando API...")
            rotacionar_chave_api()
            
        except Exception as e:
            erro_texto = str(e).lower()
            erro_original_str = str(e)  # Mantém as maiúsculas/minúsculas para o JSON
            
            # 1. TRATAMENTO DO ERRO 400 (Modelo tentou usar ferramenta/Tool invisível)
            if "tool choice is none" in erro_texto or "failed_generation" in erro_texto:
                print("⚠️ [SISTEMA] Erro 400 detectado (Tool simulada). Extraindo comando escondido...")
                try:
                    import json
                    # Localiza onde começa o JSON de geração que falhou
                    inicio_json = erro_original_str.find('{"failed_generation"')
                    if inicio_json != -1:
                        fim_json = erro_original_str.rfind('}')
                        json_puro = erro_original_str[inicio_json:fim_json+1]
                        
                        dados_erro = json.loads(json_puro)
                        # Salva o texto gerado na variável resposta_ia
                        resposta_ia = dados_erro.get("failed_generation", {}).get("arguments", "")
                        
                        # Como conseguimos recuperar o texto com sucesso, quebramos o loop 'while' 
                        # para o código seguir adiante para o processamento de Regex
                        break 
                    else:
                        raise e
                except Exception as erro_extracao:
                    print(f"Não foi possível decodificar o argumento do erro: {erro_extracao}")
                    raise e

            # 2. SEU CÓDIGO ATUAL: Captura o erro 429 de limite diário do Groq
            elif "429" in erro_texto or "rate_limit" in erro_texto or "rate limit" in erro_texto:
                tentativas += 1
                if tentativas < max_tentativas:
                    rotacionar_chave_api()  # Muda o 'client' global para a próxima chave
                    continue  # Faz o 'while' voltar para o topo e tentar a MESMA mensagem com a chave nova
                else:
                    # Se estourar todas as chaves, para o loop e joga o erro para o on_message tratar
                    raise e
                    
            else:
                # Se for qualquer outro erro crítico, repassa o erro imediatamente
                raise e

#============================================================

            
    fala_ia = resposta_ia
    partes = fala_ia.split("|" , 1)
    comandos_texto = partes[0]
    #segurança nunca é demais 
    comandos_texto = comandos_texto.replace("```", "").strip()
    comandos_texto = comandos_texto.replace("``````", "")
    comandos = comandos_texto.split("/")
    if len(partes) > 1:
        fala_ia = partes[1]
    else:
        fala_ia = partes[0]
        comandos_texto = ""
        comandos = []
    
    fala_ia = str(f"```{fala_ia}```")


    

    for comando in comandos:
        comando = comando.strip()

        

        if comando.lower().startswith('comandoadicionar'):
            padrao_adicionar = r"^\s*(comandoadicionar)\s+(?:(\d{1,2}:\d{2}),?\s+)?([^|]+?)\s*$"
            resultado_add = re.match(padrao_adicionar, comando, flags=(re.IGNORECASE | re.DOTALL))
            
           
            if resultado_add:
                comando_executado = resultado_add.group(1).strip()
                horario = resultado_add.group(2)  # Ficará None se não houver hora
                texto_lembrete = resultado_add.group(3).strip()
                


                match_hora_perdida = re.match(r"^(\d{1,2}:\d{2})\s+(.+)$", texto_lembrete)
                if match_hora_perdida:
                    horario = match_hora_perdida.group(1)
                    texto_lembrete = match_hora_perdida.group(2).strip()
                    texto_lembrete = texto_lembrete.replace("NULL", "")

                
                adicionar = salvar_lembrete_no_banco(texto_lembrete, usuario_id, canal_id, horario)
                if adicionar == True:
                    print("🎉 Match Adicionar Sucesso!")
                    print(f"1. Comando: {comando_executado}")
                    print(f"2. Horário: {horario}")
                    print(f"3. Texto do Lembrete: '{texto_lembrete}'")
                    print(f"4. Fala da IA: {fala_ia}\n\n")

                    historico_conversas[id_contexto].append({"role": "assistant", "content": fala_ia})
                    
                    
            else:
                print("Falha no match do comando adicionar.")
                    

        if comando.lower().startswith('comandolimpar'):
            padrao_limpar = r"^\s*(comandolimpar)(?:\s+([^|]+?))?\s*(?:\s*[|/]\s*(.+))?$"
            resultado_limpar = re.match(padrao_limpar, comando, flags=(re.IGNORECASE | re.DOTALL))
            if resultado_limpar:
                fala_ia = resultado_limpar.group(3).strip() if resultado_limpar.group(3) else "Todos os seus lembretes foram limpos!"

                limpar = limpar_lembretes_do_banco(usuario_id , canal_id)
                if limpar == True:
                    print("\nO banco de dados foi limpo!")
                    historico_conversas[id_contexto].append({"role": "assistant", "content": fala_ia})
                    

        if comando.lower().startswith('excluirlembrete'):
        # Novo padrão: Captura 'excluirlembrete', aceita aspas opcionais, pega o lembrete até a quebra de linha
            # Adicionada uma vírgula opcional \s*,?\s+ após a captura do horário
            padrao_excluir = r"^\s*(excluirlembrete)\s+(?:(\d{1,2}:\d{2})\s*,?\s+)?(.+?)\s*$"

            
            # Usamos re.DOTALL para que o ponto (.) capture também as quebras de linha da mensagem fofa
            match = re.search(padrao_excluir, comando, flags=re.IGNORECASE | re.DOTALL)
            if match:
                comando_executado = match.group(1).strip() 
                horario = match.group(2) # Pode ser None se não houver horário
                texto_do_lembrete = match.group(3).strip()

                #segurança no horario
                match_hora_perdida = re.match(r"^(\d{1,2}:\d{2})\s+(.+)$", texto_do_lembrete)
                if match_hora_perdida:
                    horario = match_hora_perdida.group(1)
                    texto_do_lembrete = match_hora_perdida.group(2).strip()

                print(f"texto do comando:{comando_executado}")
                print(f"texto lembrete: {texto_do_lembrete}")
                print(f"horario excluido:{horario}")
                print(f"Fala da AI: {fala_ia}")
                print(f"\nResultado do re match: {match}\n\n")

                

            
                excluir = excluir_lembrete_do_banco(texto_do_lembrete , usuario_id , canal_id , horario)
                if excluir == True:
                    print("\n[comando] Lembrete excluído do banco de dados com sucesso!")
                    if fala_ia == '':
                        fala_ia = "Lembrete Excluido"
                        historico_conversas[id_contexto].append({"role": "assistant", "content": fala_ia})
                        
                    else:
                        historico_conversas[id_contexto].append({"role": "assistant", "content": fala_ia})
                        
                else:
                    fala_ia = 'erro ao mecher no banco de dados'
                    historico_conversas[id_contexto].append({"role": "assistant", "content": fala_ia})
                    
            elif match is None:
                print('Match vazio')
                
        if comando.lower().startswith('comandoeditar'):
            padrao_editar = r"^\s*(comandoeditar)\s+(\d{1,2}:\d{2}),\s*(\d{1,2}:\d{2}),\s*([^|,]+),\s*([^|]+?)\s*$"
            resultado_editar = re.match(padrao_editar, comando, re.IGNORECASE | re.DOTALL)
            print(f' do match editar{resultado_editar}')

            if resultado_editar:
                comando_executado = resultado_editar.group(1)
                horario_antigo = resultado_editar.group(2)
                horario_novo = resultado_editar.group(3)
                texto_antigo = resultado_editar.group(4)
                texto_novo = resultado_editar.group(5)
                texto_novo = texto_lembrete.replace("NULL", "")
                
                print(f"Comando: {comando_executado}")
                print(f"Texto Novo: {texto_novo}")
                print(f"Texto Antigo (Banco): {texto_antigo}")
                print(f"fala da AI : {fala_ia}\n\n")
                editar = editar_lembrete_do_banco(texto_novo, texto_antigo , usuario_id , canal_id,horario_novo)
                if editar == True:
                    print("Lembrete editado com sucesso!\n")
                    historico_conversas[id_contexto].append({"role": "assistant", "content": fala_ia})
                    
                else:
                    print("\nErro ao editar o lembrete")
            else:
                print("Formato inválido.")







    if fala_ia == '':
        fala_ia = 'acho que consegui consegui limpar o banco de dados^^'
    # Guarda a resposta da IA na memória ram
    historico_conversas[id_contexto].append({"role": "assistant", "content": fala_ia})
    return fala_ia

    

# 3. Configuração do Bot do Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def handle_ping(request):
    return web.Response(text="Bot está vivo!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/ping', handle_ping)
    port = int(os.environ.get("PORT", 8080)) 
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Servidor HTTP rodando na porta {port}")

@bot.event
async def setup_hook():
    bot.loop.create_task(start_web_server())

@bot.event
async def on_ready():
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    print(f"==================================================")
    print(f"  AI está ativada! ")
    print(f"  Conectado como: {bot.user}")
    print(f"Horario{agora}")
    print(f"==================================================")
    bot.loop.create_task(
        
        verificar_lembretes()
    )

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        texto_usuario = message.content.replace(f"<@{bot.user.id}>", "").strip()
        
        if not texto_usuario:
            await message.channel.send("Estou aqui! Precisa que eu anote algum lembrete? ")
            return

        id_contexto = str(message.channel.id)

        usuario_id = str(message.author.id)
        canal_id = str(message.channel.id)

    while True:
        async with message.channel.typing():
            try:
                resposta_rpg = await obter_resposta_groq(
                        id_contexto,
                        texto_usuario,
                        usuario_id,
                        canal_id
                )
                                    
                limite = 1900
                if len(resposta_rpg) > limite:
                    pedacos = [resposta_rpg[i:i+limite] for i in range(0, len(resposta_rpg), limite)]
                    for pedaco in pedacos:
                        await message.reply(pedaco)
                else:
                    await message.reply(resposta_rpg)

                break
                
            except Exception as e:
                # Transforma o erro em texto para analisar o que aconteceu
                erro_texto = str(e).lower()
                
                # (EXCEPT DE LIMITE DA API): Se o erro contiver códigos de limite do Groq
                if "429" in erro_texto or "rate_limit" in erro_texto or "rate limit" in erro_texto:
                    rotacionar_chave_api()
                    continue
                if "503" in str(e):
                    rotacionar_chave_api()
                    continue
                # (EXCEPT GERAL): Qualquer outro erro de banco de dados ou do bot
                else:
                    print(f"Erro detectado no processamento: {e}")
                    await message.reply("Desculpa... Tive um probleminha para acessar minhas anotações agora. (｡•́︿•̀｡)")
                    await message.reply("cai num erro desconhecido...estarei em manutenção por um tempo")
                    break

    await bot.process_commands(message)



# Executa o bot oficial
bot.run(DISCORD_TOKEN)
