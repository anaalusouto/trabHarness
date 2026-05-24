import boto3
import requests
import time
import json

sqs = boto3.client('sqs', region_name='us-east-1')

fila_url = 'https://sqs.us-east-1.amazonaws.com/707402671151/FilaDocumentos'
url_ollama = "http://localhost:11434/api/generate"

with open("prompts/extrator.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

print("Worker iniciado. Vigiando a fila de documentos na AWS...")

arquivo_saida = "resultado_final.jsonl"

while True:
    resposta_sqs = sqs.receive_message(
        QueueUrl=fila_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=5
    )

    if 'Messages' in resposta_sqs:
        mensagem = resposta_sqs['Messages'][0]
        recibo = mensagem['ReceiptHandle']
        texto_documento = mensagem['Body']

        print(f"\n[!] Nova tarefa recebida! Tamanho: {len(texto_documento)} caracteres.")

        payload = {
            "model": "qwen2.5:1.5b",
            "system": system_prompt,
            "prompt": f"Leia APENAS o texto a seguir e extraia os dados.\n\nTEXTO:\n{texto_documento}",
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.0,
                "top_p": 0.1
            }
        }

        max_tentativas = 3
        sucesso = False

        for tentativa in range(1, max_tentativas + 1):
            try:
                inicio_tempo = time.time()
                resposta_ollama = requests.post(url_ollama, json=payload, timeout=120)
                fim_tempo = time.time()

                latencia = fim_tempo - inicio_tempo

                if resposta_ollama.status_code == 200:
                    dados_extraidos = resposta_ollama.json()["response"]

                    resultado_consolidado = {
                        "texto_original": texto_documento[:50] + "... (truncado)",
                        "dados_estruturados": json.loads(dados_extraidos),
                        "metricas": {
                            "latencia_segundos": round(latencia, 2)
                        }
                    }

                    with open(arquivo_saida, "a", encoding="utf-8") as f:
                        f.write(json.dumps(resultado_consolidado, ensure_ascii=False) + "\n")

                    sqs.delete_message(QueueUrl=fila_url, ReceiptHandle=recibo)
                    print(f"Tarefa concluída em {round(latencia, 2)}s e agregada no {arquivo_saida}.")
                    sucesso = True
                    break

                else:
                    print(f"Erro da IA na tentativa {tentativa}. Status: {resposta_ollama.status_code}")

            except Exception as e:
                print(f"Falha na inferência na tentativa {tentativa}: {e}")

            if not sucesso and tentativa < max_tentativas:
                tempo_espera = 2 ** tentativa
                print(f"Aguardando {tempo_espera}s antes de tentar novamente (Backoff)...")
                time.sleep(tempo_espera)

        if not sucesso:
            print(">> ATENÇÃO: Falha definitiva no processamento. A mensagem voltou para a fila SQS.")

    else:
        print(".", end="", flush=True)
        time.sleep(2)