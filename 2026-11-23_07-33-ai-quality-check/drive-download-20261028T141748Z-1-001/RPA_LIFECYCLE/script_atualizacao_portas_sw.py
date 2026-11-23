import pandas as pd
from netmiko import ConnectHandler
import re
import getpass

# 1. Credenciais de acesso solicitadas no terminal
USERNAME = input("Digite o seu utilizador: ")
PASSWORD = getpass.getpass("Digite a sua palavra-passe: ")

# 2. Lista de IPs dos switches
switches = [
    "10.140.55.151", "10.140.55.152", "10.140.55.153", "10.140.55.154",
    "10.140.55.155", "10.140.55.156", "10.140.55.157", "10.140.55.158",
    "10.140.55.159", "10.140.55.160", "10.140.55.161", "10.140.55.162",
    "10.140.55.163", "10.140.55.164", "10.140.55.165", "10.230.82.145",
    "10.140.0.18", "10.140.0.25", "10.140.0.26", "10.140.0.52",
    "10.140.0.53", "10.140.0.54", "10.140.0.56", "10.140.0.57",
    "10.140.0.58", "10.140.0.59", "10.140.0.60", "10.140.0.64",
    "10.140.0.120", "10.140.0.121", "10.140.0.122", "10.140.0.123",
    "10.140.0.124", "10.140.0.125", "10.140.0.126", "10.140.0.127",
    "10.140.0.128", "10.140.0.130", "10.140.0.247", "10.140.0.253"
]

mapeamento_status = {
    "connected": "Actived",
    "notconnect": "Available",
    "disabled": "Disabled",
    "err-disabled": "Error"
}

dados_switches = {}
dados_sumario = []  # Lista para armazenar as métricas de visão geral

for ip in switches:
    print(f"\n[-] A ligar ao switch {ip}...")
    
    device = {
        "device_type": "cisco_ios",
        "host": ip,
        "username": USERNAME,
        "password": PASSWORD,
        "timeout": 15,
    }

    try:
        net_connect = ConnectHandler(**device)
        
        prompt = net_connect.find_prompt()
        hostname = re.sub(r'[^a-zA-Z0-9_-]', '', prompt) 
        nome_separador = hostname[:31] if hostname else ip

        output = net_connect.send_command("show interface status", use_textfsm=True)
        
        linhas = []
        if isinstance(output, list):
            # Contadores gerais
            actived_count = 0
            available_count = 0
            
            # Contadores específicos para portas Gi (GigabitEthernet)
            gi_total_count = 0
            gi_available_count = 0
            
            for port in output:
                port_name = port.get("port", "")
                status_original = port.get("status", "").lower()
                status_convertido = mapeamento_status.get(status_original, status_original.capitalize())

                # Atualiza os contadores gerais (para visualização no sumário)
                if status_convertido == "Actived":
                    actived_count += 1
                elif status_convertido == "Available":
                    available_count += 1

                # Atualiza os contadores específicos para cálculo do rate APENAS das portas "Gi"
                if port_name.startswith("Gi") or port_name.startswith("gi"):
                    gi_total_count += 1
                    if status_convertido == "Available":
                        gi_available_count += 1

                linhas.append({
                    "Ports Number": port_name,
                    "Status": status_convertido,
                    "Line/Equipament": port.get("name", ""), 
                    "Device": "",  
                    "VLAN": port.get("vlan", ""),
                    "Duplex": port.get("duplex", ""),
                    "Speed": port.get("speed", "")
                })
            
            # Cálculo da taxa de portas disponíveis apenas para as portas "Gi" em formato float 0.x
            if gi_total_count > 0:
                available_rate = round(gi_available_count / gi_total_count, 4)
            else:
                available_rate = 0.0

            # Adiciona os dados ao sumário
            dados_sumario.append({
                "HostName": nome_separador,
                "Actived ports": actived_count,
                "Available ports": available_count,
                "Available ports rate": available_rate
            })

        else:
            print(f"[!] Não foi possível estruturar a saída do switch {ip}.")
            continue

        dados_switches[nome_separador] = pd.DataFrame(linhas)
        net_connect.disconnect()
        print(f"[✓] Dados recolhidos de {nome_separador} com sucesso.")

    except Exception as e:
        print(f"[X] Erro ao processar o switch {ip}: {e}")

# 3. Exportar para Excel com aba de sumário e abas individuais
ficheiro_saida = "Novo_Mapeamento_Fisico_Switches.xlsx"

if dados_switches:
    print("\n[+] A gerar o ficheiro Excel...")
    with pd.ExcelWriter(ficheiro_saida, engine='openpyxl') as writer:
        
        # 1. Cria a primeira aba de Sumário
        df_sumario = pd.DataFrame(dados_sumario)
        df_sumario.to_excel(writer, sheet_name="Sumario", index=False)
        
        # 2. Cria as abas individuais para cada switch
        for aba, df in dados_switches.items():
            df.to_excel(writer, sheet_name=aba, index=False)
            
    print(f"[✓] Ficheiro gerado com sucesso: {ficheiro_saida}")
else:
    print("\n[!] Nenhum dado foi recolhido. O ficheiro não foi criado.")