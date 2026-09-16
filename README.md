# 🤖 AI_V4 — Assistente Virtual no Discord

> AI_V4 é a quarta versão do meu projeto de assistente virtual, agora integrado ao Discord, com sistema de memória, lembretes automáticos, banco de dados PostgreSQL, múltiplas APIs de inteligência artificial e rotação automática de chaves.

O projeto foi desenvolvido como parte da minha evolução no aprendizado de **Python**, aumentando gradualmente a complexidade da aplicação a cada versão.

---

## 📌 Sobre o projeto

A **AI_V4** funciona como um assistente virtual dentro do Discord.

### Ela é capaz de:

* 💬 Conversar com o usuário
* 🧠 Manter histórico recente das conversas
* 📝 Criar lembretes
* ✏️ Editar lembretes
* ❌ Excluir lembretes
* 🧹 Limpar todos os lembretes
* ⏰ Avisar automaticamente quando um lembrete estiver próximo
* 🔔 Enviar avisos até 30 minutos antes do lembrete
* 🔄 Reiniciar os status de aviso quando um lembrete é editado
* 🗄️ Armazenar os lembretes no PostgreSQL
* 🔄 Alternar automaticamente entre diferentes chaves de API
* 🤖 Utilizar diferentes provedores de modelos de IA
* 🧩 Interpretar comandos através de expressões regulares
* 📋 Processar múltiplos comandos em uma única resposta
* 🌎 Trabalhar com o horário de America/Sao_Paulo
* 📱 Funcionar diretamente através do Discord
* ☁️ Ser executada em ambiente de nuvem

---

## 🖼️ Prints do projeto

> Espaço reservado para adicionar prints da AI_V4 funcionando no Discord.

### 💬 Conversando com a AI

**<img width="847" height="776" alt="Captura de tela 2026-09-12 161258" src="https://github.com/user-attachments/assets/13866a6b-7c8e-4b26-a08c-12a54c89fb13" />
**

---

### ⏰ Sistema de lembretes

**<img width="870" height="410" alt="Captura de tela 2026-09-12 154825" src="https://github.com/user-attachments/assets/01981226-16bd-42ac-9248-3f491053182b" />
**

---

### 🔔 Aviso automático

O sistema verifica os lembretes automaticamente a cada **30 segundos**.

Quando um lembrete está dentro da janela de 30 minutos antes do horário programado, a AI pode enviar um aviso indicando quanto tempo falta.

Quando o horário do lembrete chega, o bot envia uma segunda mensagem informando que está na hora de realizar a tarefa.

O sistema utiliza dois status no banco de dados:

* `aviso_30min` → indica se o aviso antecipado já foi enviado
* `enviado` → indica se o lembrete principal já foi enviado

Quando um lembrete é editado, os dois status são redefinidos para `False`, fazendo com que o lembrete editado seja tratado como um novo agendamento.

Todos os horários são tratados utilizando o fuso:

`America/Sao_Paulo`

**<img width="857" height="366" alt="Captura de tela 2026-09-12 160720" src="https://github.com/user-attachments/assets/e3efaca3-277e-4582-8524-8f0f6efef80e" />
**

---

# COMO TESTAR O BOT
O bot foi instalado na Nuvem, quem quiser pode se sentir livre para testar o bot!
basta estar no servidor de **testes** entrar no **chat privado** da AI e testar os comandos a vontade!

**AVISO** é possível que demore cerca de 30 segundos a 1 minuto para responder a primeira mensagem por estar dormindo na hospedagem da nuvem, apartir disso, ela responde normalmente 

[Testar a AI](https://discord.gg/mDAr5VGxx)

## 🔗 Versões anteriores

A AI_V4 faz parte da evolução de um projeto que foi sendo desenvolvido em diferentes versões.

### 🤖 AIV1

**[AI V1](https://github.com/juandeoliveira147-sys/Projeto_AI/blob/main/ProjetoAI/Projeto_AI_1.0/Projeto_AI_1.0.py)**

Primeira versão do assistente virtual.

---

### 🤖 AIV2

**[AI V2](https://github.com/juandeoliveira147-sys/Projeto_AI/blob/main/ProjetoAI/Projeto_AI_2.0/Projeto_AI_2.0.py)**

Segunda versão, com novas funcionalidades e melhorias na estrutura do projeto.

---

### 🤖 AIV3

**[AI V3](https://github.com/juandeoliveira147-sys/Projeto_AI/blob/main/ProjetoAI/Projeto_AI_3.0/AI_V3.py)**

Terceira versão, responsável por introduzir novas funcionalidades, banco de dados e uma estrutura mais avançada.

---

## 🚀 AI_V4

Nesta versão, o projeto evoluiu para um **bot integrado ao Discord**, permitindo que o usuário interaja com a inteligência artificial diretamente através de mensagens.

A aplicação também possui um sistema de lembretes persistentes utilizando **PostgreSQL**.

---

## 🛠️ Tecnologias utilizadas

### Backend

* 🐍 Python
* 🐘 PostgreSQL
* 🤖 Discord.py

### Inteligência Artificial

* Groq
* OpenRouter
* Gemini
* Z.AI
* Modelos compatíveis com a API da OpenAI

### Bibliotecas

* `discord.py`
* `groq`
* `openai`
* `python-dotenv`
* `psycopg2`
* `asyncio`
* `re`

---

## 🧠 Arquitetura do projeto

O funcionamento principal da AI_V4 pode ser representado da seguinte maneira:

```text
                         ┌──────────────────┐
                         │      USUÁRIO     │
                         │     Discord      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     AI_V4.py     │
                         │    Discord Bot   │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
           ┌──────────────────┐       ┌──────────────────┐
           │    PostgreSQL    │       │ Histórico recente│
           │     Memória      │       │   da conversa    │
           └────────┬─────────┘       └──────────────────┘
                    │
                    ▼
           ┌──────────────────┐
           │   Prompt atual   │
           │ + lembretes      │
           │ + contexto       │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │    APIs de IA    │
           │                  │
           │ Groq             │
           │ OpenRouter       │
           │ Gemini           │
           └────────┬─────────┘
                    │
                    │ limite/erro
                    ▼
           ┌──────────────────┐
           │ Rotação de chaves│
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ Resposta da IA   │
           └────────┬─────────┘
                    │
             ┌──────┴──────┐
             │             │
             ▼             ▼
      ┌──────────────┐ ┌────────────────┐
      │ Fala normal  │ │ Comandos       │
      │              │ │ de lembretes   │
      └──────────────┘ └───────┬────────┘
                                │
                                ▼
                         ┌──────────────┐
                         │ Regex /      │
                         │ Processamento│
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │  PostgreSQL  │
                         │              │
                         │ Adicionar    │
                         │ Editar       │
                         │ Excluir      │
                         │ Limpar       │
                         └──────────────┘
```

---

## ⏰ Sistema automático de lembretes

O sistema de lembretes funciona paralelamente ao bot:

```text
PostgreSQL
    │
    ▼
Verificação a cada 30 segundos
    │
    ├──► Lembrete próximo?
    │         │
    │         └──► Aviso de 30 minutos
    │
    └──► Horário chegou?
              │
              └──► Envia mensagem no Discord
```

---

## 🔄 Sistema de rotação de APIs

A AI_V4 possui várias chaves de API configuradas através do arquivo `.env`.

Quando uma API atinge seu limite de utilização, o sistema pode trocar automaticamente para outra chave disponível.

```text
API 1
 │
 ├── Limite atingido
 │
 ▼
API 2
 ├── Nova tentativa com a mesma mensagem
 ├── Limite atingido
 │
 ▼
API 3
 ├── Nova tentativa com a mesma mensagem
 ├── Limite atingido
 │
 ▼
API 4
 │
 └── ...
```

Isso aumenta a disponibilidade do bot e permite distribuir as requisições entre diferentes chaves.

---

## 📝 Sistema de comandos

A inteligência artificial recebe instruções para utilizar comandos específicos quando precisa alterar os lembretes.

### ➕ Adicionar lembrete

```text
comandoadicionar [horário] [lembrete]
```

### ✏️ Editar lembrete

```text
comandoeditar horário_antigo, horário_novo, lembrete_antigo, lembrete_novo
```

### ❌ Excluir lembrete

```text
excluirlembrete [horário] [lembrete]
```

### 🧹 Limpar lembretes

```text
comandolimpar
```

A AI gera o comando em um formato específico e o Python identifica esse comando utilizando **expressões regulares (`re`)** antes de realizar a alteração no banco de dados.

---

## 📋 Múltiplos comandos

A AI_V4 também consegue processar vários comandos de lembretes em uma única interação.

Os comandos são separados pelo caractere `/`.

### Exemplo

```text
comandoadicionar 10:30 ir comer/comandoadicionar 14:00 estudar Python | Prontinho! Os dois lembretes foram agendados.

```
## 🗄️ Banco de dados

A AI_V4 utiliza **PostgreSQL** para armazenar os lembretes.

### Estrutura principal utilizada

```sql
CREATE TABLE memoriaAI (
    id SERIAL PRIMARY KEY,
    usuario_id VARCHAR(30) NOT NULL,
    canal_id VARCHAR(30) NOT NULL,
    lembrete TEXT NOT NULL,
    horario TIME,
    aviso_30min BOOLEAN DEFAULT FALSE,
    enviado BOOLEAN DEFAULT FALSE
);
```

O banco permite que cada lembrete seja associado ao:

* 👤 Usuário
* 💬 Canal
* 📝 Texto do lembrete
* ⏰ Horário
* 🔔 Status do aviso de 30 minutos
* ✅ Status de envio

---

## 📁 Estrutura do projeto

```text
AI_V4/
│
├── AI_V4.py
├── memoriaAI.py
├── .env
├── .gitignore
└── README.md
```

### `AI_V4.py`

Arquivo principal da aplicação.

Responsável por:

* Inicializar o bot do Discord
* Receber mensagens
* Conversar com os modelos de IA
* Gerenciar as APIs
* Processar comandos
* Controlar os lembretes
* Enviar notificações automáticas

### `memoriaAI.py`

Responsável pela conexão e encerramento da conexão com o PostgreSQL.

### `.env`

Armazena informações sensíveis, como:

```env
DISCORD_TOKEN=
API_PRINCIPAL=
API_RESERVA1=
API_RESERVA2=
...
API_RESERVA12=
```

> ⚠️ **O arquivo `.env` não deve ser publicado no GitHub.**

---

# ⚙️ Configuração

## 1. Clone o projeto

```bash
git clone https://github.com/juandeoliveira147-sys/discord-IA-chatbot-python-postgreSQL
```

## 2. Entre na pasta

```bash
cd AI_V4
```

## 3. Instale as dependências

```bash
pip install discord.py groq openai python-dotenv psycopg2
```

## 4. Configure o PostgreSQL

Crie o banco de dados:

```text
memoriaAI
```

Depois, crie a tabela `memoriaAI` utilizando a estrutura apresentada anteriormente.

No arquivo de conexão, configure:

```text
Usuário
Senha
Host
Porta
Banco de dados
```

> ⚠️ Substitua a senha de exemplo pela senha do seu PostgreSQL.

## 5. Configure o `.env`

Adicione o token do Discord e as chaves de API:

```env
DISCORD_TOKEN=seu_token

API_PRINCIPAL=sua_chave
API_RESERVA1=sua_chave
API_RESERVA2=sua_chave
...
API_RESERVA13=sua_chave
```

> 🔐 Nunca publique tokens, senhas ou chaves de API no GitHub.

## 6. Execute o projeto

```bash
python AI_V4.py
```

---

## 🎯 Objetivos de aprendizado

O desenvolvimento da AI_V4 permitiu praticar conceitos mais avançados de Python, incluindo:

* 🐍 Organização de um projeto maior
* 🔄 `async` / `await`
* 🤖 Integração com APIs
* 💬 Desenvolvimento de bot para Discord
* 🗄️ PostgreSQL
* 🔐 Variáveis de ambiente
* 🔑 Rotação de chaves de API
* 🧩 Expressões regulares
* 🧠 Histórico de conversação
* ⏰ Sistemas automáticos em segundo plano
* ⚠️ Tratamento de erros
* 📡 Requisições assíncronas
* 📝 Manipulação de dados
* 🏗️ Organização e separação de responsabilidades
* 🔁 Sistemas de fallback e rotação de APIs
* 🧪 Testes e debugging de sistemas assíncronos
* 🔍 Processamento de comandos com expressões regulares
* 🔀 Processamento de múltiplos comandos em uma única resposta
* 🕐 Manipulação de fusos horários
* 🔄 Controle de estado de lembretes
* 🌐 Execução de aplicações em nuvem

---

## 📈 Evolução do projeto

```text
AIV1
 │
 ▼
AIV2
 │
 ▼
AIV3
 │
 ▼
AI_V4
 │
 ├── Discord
 ├── PostgreSQL
 ├── Lembretes automáticos
 ├── Histórico
 ├── Múltiplas APIs
 └── Rotação de chaves
```

Cada versão representa uma etapa da evolução do projeto e do meu aprendizado em programação.

---

## 🔮 Possíveis melhorias futuras

Algumas funcionalidades que podem ser adicionadas futuramente:

* [ ] Melhorar o sistema de memória
* [ ] Criar uma interface própria para gerenciamento
* [ ] Adicionar mais ferramentas ao assistente
* [ ] Melhorar o sistema de contexto
* [ ] Criar sistema de usuários
* [ ] Adicionar mais integrações
* [ ] Melhorar o gerenciamento das APIs
* [ ] Criar uma arquitetura ainda mais modular

---

## 👨‍💻 Autor

**Juan De Oliveira**

Projeto desenvolvido durante meus estudos de programação e evolução com Python.

---

## 📄 Licença

Este projeto foi desenvolvido para fins de aprendizado e portfólio.
