import csv
import json
import os

# Força o Python a usar a pasta exata onde este script está salvo
pasta_atual = os.path.dirname(os.path.abspath(__file__))
caminho_csv = os.path.join(pasta_atual, 'todas_as_solucoes.csv')
caminho_js = os.path.join(pasta_atual, 'banco_solucoes.js')

jogos_com_solucoes = {}
linhas_lidas = 0

try:
    with open(caminho_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader) # Pula o cabeçalho
        
        for row in reader:
            if len(row) >= 2:
                mao = row[0].strip()
                solucao = row[1].strip()
                
                if mao not in jogos_com_solucoes:
                    jogos_com_solucoes[mao] = []
                jogos_com_solucoes[mao].append(solucao)
                linhas_lidas += 1

    with open(caminho_js, 'w', encoding='utf-8') as f:
        f.write("// Arquivo gerado automaticamente\n")
        f.write("const bancoSolucoes = " + json.dumps(jogos_com_solucoes, indent=4) + ";\n")
        f.write("const maosValidas = Object.keys(bancoSolucoes).map(x => JSON.parse(x));\n")

    print("✅ SUCESSO! O arquivo 'banco_solucoes.js' foi gerado na mesma pasta.")
    print(f"-> Mãos únicas: {len(jogos_com_solucoes)}")
    print(f"-> Soluções totais: {linhas_lidas}")

except Exception as e:
    print(f"❌ Erro: {e}")