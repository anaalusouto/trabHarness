import boto3
import PyPDF2

sqs = boto3.client('sqs', region_name='us-east-1')
fila_url = 'https://sqs.us-east-1.amazonaws.com/707402671151/FilaDocumentos'  # Não esqueça de colocar sua URL!

caminho_pdf = 'documento.pdf'

print(f"Lendo o documento: {caminho_pdf}")

with open(caminho_pdf, 'rb') as arquivo:
    leitor_pdf = PyPDF2.PdfReader(arquivo)
    total_paginas = len(leitor_pdf.pages)

    print(f"Total de páginas encontradas: {total_paginas}. Enviando para a fila...")

    for numero_pagina in range(total_paginas):
        pagina = leitor_pdf.pages[numero_pagina]
        texto_pagina = pagina.extract_text()

        if texto_pagina.strip():
            pacote = f"--- PÁGINA {numero_pagina + 1} ---\n{texto_pagina}"

            sqs.send_message(
                QueueUrl=fila_url,
                MessageBody=pacote
            )
            print(f"Página {numero_pagina + 1} enviada com sucesso!")

print("Fase 'Map' concluída! Todos os chunks estão na fila aguardando processamento.")