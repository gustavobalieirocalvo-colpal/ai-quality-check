import requests

# Cole sua URL aqui (mantenha entre aspas)
URL_APPS_SCRIPT = "https://script.google.com/a/macros/colpal.com/s/AKfycbxRpC5ZZQcZ91mNAXAVTXC4hOMtfem2zPAsZQ3r9Cs3yzLlCJkCBgtYQjMzatTzvK21/exec"

def testar_conexao():
    print("⏳ Conectando com a planilha do Google Sheets...")
    
    try:
        # O Python "bate na porta" da planilha
        resposta = requests.get(URL_APPS_SCRIPT)
        
        # Lê a resposta
        dados = resposta.json()
        
        print("\n✅ Conexão estabelecida com sucesso!")
        print(f"📊 A planilha tem {len(dados)} linhas (incluindo o cabeçalho).")
        print("\nPrimeira linha lida (Cabeçalho):")
        print(dados[0])
        
    except Exception as e:
        print(f"\n❌ Erro ao conectar: {e}")

if __name__ == "__main__":
    testar_conexao()