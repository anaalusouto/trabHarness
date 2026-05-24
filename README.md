# Pipeline Distribuído de Análise e Extração de Documentos (MapReduce Híbrido)

Este projeto implementa um ecossistema distribuído e tolerante a falhas para o processamento, padronização e extração de metadados estruturados a partir de documentos extensos (como relatórios científicos e botânicos). 

A arquitetura adota uma abordagem híbrida de alta performance, utilizando serviços de mensageria na nuvem para a orquestração e nós locais independentes (Small Language Models auto-hospedados) para a execução da inferência computacional.

## 🚀 Arquitetura do Sistema

O sistema foi desenhado seguindo o modelo conceitual **MapReduce**:

1. **Fase Map (Produtor):** Um script lê o arquivo PDF original, realiza o particionamento do texto em blocos discretos (*chunks* por página) e envia cada segmento como uma tarefa isolada para uma fila de mensageria no **Amazon SQS**.
2. **Fila de Mensagens (Orquestração):** O **Amazon SQS** atua como o cérebro centralizador, garantindo o desacoplamento total do sistema, persistência das tarefas e distribuição dinâmica da carga.
3. **Fase Reduce (Workers Distribuídos):** Múltiplos nós de processamento locais (executados nos laptops da equipe) consomem a fila de forma assíncrona. Cada nó interage com o motor de inferência local **Ollama** para processar o texto através de IA e consolidar os dados extraídos em um arquivo unificado de saída estruturada (`.jsonl`).

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.13+
- **Orquestração e Nuvem:** AWS SQS & Boto3 (SDK oficial da AWS)
- **Motor de Inferência Local:** Ollama (Modelo `qwen2.5:1.5b` quantizado para CPU)
- **Engenharia de Contexto:** Camada explícita de prompts isolados e parametrizados (Temperatura 0.0)
- **Processamento de Arquivos:** PyPDF2

## 📋 Funcionalidades Avançadas Implementadas

- **Camada Explícita de Engenharia de Contexto:** Os *system prompts* são mantidos e versionados estritamente fora do código-fonte da aplicação (diretório `/prompts`), garantindo isolamento e facilidade de ajuste fino.
- **Saída Estruturada Rígida:** O modelo é matematicamente forçado através de parâmetros da API a retornar um esquema JSON estrito (`format: json`), mitigando alucinações conversacionais.
- **Tolerância a Falhas (Retry com Exponential Backoff):** Caso o nó local sofra um engasgo de hardware ou perda temporária de conexão, o Worker captura a exceção, retém a mensagem e aplica reatentativas automáticas com espaçamento de tempo exponencial (2s, 4s, 8s). A tarefa só é deletada da fila SQS após o sucesso absoluto da consolidação.
- **Coleta de Métricas:** Monitoramento em tempo real da latência de inferência por página para posterior análise de performance de infraestrutura.

## 🔧 Como Configurar e Executar

### Pre-requisitos

1. **Instalar o Ollama e o Modelo:**
   Baixe o Ollama e, no terminal, execute o comando para baixar o SLM leve otimizado para CPU:
   ```bash
   ollama run qwen2.5:1.5b
2. Configurar as Credenciais da AWS:
  Garanta que o arquivo de credenciais da AWS está configurado corretamente no caminho padrão do seu sistema operacional (~/.aws/credentials ou C:\Users\USUARIO\.aws\credentials):

  ```
  [default]
  aws_access_key_id=SUA_ACCESS_KEY
  aws_secret_access_key=SUA_SECRET_KEY
  aws_session_token=SEU_SESSION_TOKEN
  Instalar as Dependências do Python:
```

   ```
  pip install boto3 requests PyPDF2
   ```
3. Execução
  Inicie o nó de processamento (Worker):
  No arquivo worker.py, insira a URL da sua fila SQS e execute:

```
  python worker.py
   ```
(O nó ficará em modo de escuta ativa, aguardando tarefas da nuvem).

4. Dispare a carga de trabalho (Produtor):
  Adicione o arquivo documento.pdf na raiz do projeto, insira a URL da fila SQS no arquivo produtor.py e execute:

```
python produtor.py
   ```
(O documento será fatiado e enviado para a fila. O Worker começará o processamento imediatamente).

##  📊 Formato de Saída (Dados Consolidados)
Os resultados são agregados linha por linha no formato JSON Lines (resultado_final.jsonl), estruturados da seguinte forma:

   ```
JSON
{
  "texto_original": "--- PÁGINA 1 --- O levantamento botânico realizado...",
  "dados_estruturados": {
    "resumo": "Síntese rigorosa dos dados ambientais contidos na página.",
    "entidades": ["Hevea brasiliensis", "Mapeamento Ecológico", "Sustentabilidade"]
  },
  "metricas": {
    "latencia_segundos": 24.11
  }
}
   ```
## 👥 Equipe de Desenvolvimento
Projeto desenvolvido para a disciplina de Programação Distribuída e Paralela por:

Ana Beatriz Nunes
Ana Luiza Souto
Carolline Mello
