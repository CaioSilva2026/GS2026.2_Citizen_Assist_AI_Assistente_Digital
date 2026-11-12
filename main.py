
import os

from base_conhecimento import BaseConhecimento
from assistente import Assistente

def mostrar_boas_vindas(assistente):
    print("\n" + "=" * 60)
    print(f"              {assistente.nome}")
    print("=" * 60)
    print("\nOlá! Seja bem-vindo ao Nexo.")
    print("Seu assistente digital de orientação para jovens no primeiro emprego.")
    print("\nComo usar:")
    print("  1. Digite o número da opção desejada.")
    print("  2. Faça perguntas sobre documentos, trabalho e direitos.")
    print("  3. Consulte os assuntos disponíveis pelo menu de categorias.")
    print("  4. Digite 0 para voltar ou sair de uma tela.")
    print("\nImportante:")
    print("  - O Nexo não é um canal oficial de atendimento.")
    print("  - As orientações são baseadas em fontes oficiais.")
    print("  - Nunca informe CPF, telefone, e-mail ou outros dados pessoais.")
    print("\n" + "=" * 60)

def mostrar_menu():
    print("\n=== MENU PRINCIPAL - NEXO ===")
    print("1. Fazer uma pergunta")
    print("2. Consultar assuntos por categoria")
    print("3. Ver indicadores de atendimento")
    print("4. Exportar atendimentos para CSV")
    print("0. Sair")

    print("\nAntes de sair, você poderá avaliar sua experiência.")

def main():
    # Garante que a pasta de dados exista.
    os.makedirs("data", exist_ok=True)

    # Inicializa a base de conhecimento.
    base = BaseConhecimento("data/base_conhecimento.json")
    if not base.carregar():
        print("\nNão foi possível carregar a base de conhecimento.")
        print("Verifique se o arquivo data/base_conhecimento.json existe")
        print("e se o conteúdo está no formato JSON correto.")
        return
    # Inicializa o assistente.
    assistente = Assistente("Nexo", base)
    mostrar_boas_vindas(assistente)
    # Menu principal.
    while True:
        mostrar_menu()

        opcao = assistente.ler_opcao(
            "Digite o número da opção desejada: ",
            4
        )
        if opcao == 1:
            assistente.perguntar()
        elif opcao == 2:
            assistente.navegar()
        elif opcao == 3:
            assistente.indicadores()
        elif opcao == 4:
            assistente.exportar_csv()
        elif opcao == 0:
            print("\n" + "=" * 60)
            print("Antes de sair, conte como foi sua experiência.")
            assistente.pedir_nota()
            # Exporta os atendimentos antes de encerrar.
            assistente.exportar_csv()
            print("\nObrigado por utilizar o Nexo!")
            print("Sua opinião ajuda a melhorar o assistente.")
            print("=" * 60)
            break
if __name__ == "__main__":
    main()
