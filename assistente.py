import csv
import json
import time
from datetime import datetime

# Limites da confiança (explicados no README).
PONTOS_MINIMOS = 3   # abaixo disso: "não encontrei"
PONTOS_ALTA = 6      # a partir daqui: confiança ALTA

CAMPOS_HISTORICO = ["data", "origem", "pergunta", "id_orientacao",
                    "encontrou", "ajudou", "tentativas", "tempo_segundos"]


class Assistente:

    def __init__(self, nome, base, caminho_historico="data/historico.json",
                 caminho_notas="data/notas.json"):
        self.nome = nome
        self.base = base
        self.caminho_historico = caminho_historico
        self.caminho_notas = caminho_notas
        self.historico = []
        self.notas = []
        self.carregar_historico()
        self.carregar_notas()

    # ---------- histórico ----------
    def carregar_historico(self):
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as f:
                dados = json.load(f)
            if not isinstance(dados, list):
                dados = []
            # descarta registros incompletos, para os indicadores não quebrarem
            self.historico = [
                a for a in dados
                if isinstance(a, dict)
                and all(campo in a for campo in CAMPOS_HISTORICO)
            ]
        except (FileNotFoundError, json.JSONDecodeError, OSError,
                UnicodeDecodeError):
            self.historico = []

    def salvar_historico(self):
        try:
            with open(self.caminho_historico, "w", encoding="utf-8") as f:
                json.dump(self.historico, f, ensure_ascii=False, indent=2)
        except OSError:
            print("Erro ao salvar o histórico.")

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou,
                  tentativas, tempo):
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo,
        }
        self.historico.append(atendimento)
        self.salvar_historico()

    # ---------- notas de facilidade ----------
    def carregar_notas(self):
        try:
            with open(self.caminho_notas, "r", encoding="utf-8") as f:
                dados = json.load(f)
            if not isinstance(dados, list):
                dados = []
            self.notas = [
                n for n in dados
                if isinstance(n, int) and 1 <= n <= 5
            ]
        except (FileNotFoundError, json.JSONDecodeError, OSError,
                UnicodeDecodeError):
            self.notas = []

    def salvar_notas(self):
        try:
            with open(self.caminho_notas, "w", encoding="utf-8") as f:
                json.dump(self.notas, f)
        except OSError:
            print("Erro ao salvar a nota.")

    def pedir_nota(self):
        nota = self.ler_opcao(
            "Dê uma nota de facilidade de 1 a 5 (0 para pular): ", 5)
        if nota == 0:
            return
        self.notas.append(nota)
        self.salvar_notas()

    # ---------- validações ----------
    def tem_dado_pessoal(self, texto):
        digitos = sum(1 for c in texto if c.isdecimal())
        return digitos >= 8 or "@" in texto

    def ler_sim_nao(self, mensagem):
        while True:
            resp = input(mensagem).strip().lower()
            if resp in ("s", "n"):
                return resp == "s"
            print("Digite apenas s ou n.")

    def ler_opcao(self, mensagem, maximo):
        while True:
            texto = input(mensagem).strip()
            if texto.isdecimal() and 0 <= int(texto) <= maximo:
                return int(texto)
            print(f"Opção inválida. Digite um número de 0 a {maximo}.")

    # ---------- atendimento por pergunta ----------
    def perguntar(self):
        print("\n=== Escrever uma dúvida ===")
        print("Para voltar ao menu, digite 0.")
        # Cada volta do while é UM atendimento (pode ter várias tentativas).
        while True:
            if not self.atender_pergunta():
                return
            print("\nVocê pode fazer outra pergunta.")

    def ler_pergunta(self):
        """Lê o texto da dúvida. Repete até vir algo válido (ou 0 para voltar)."""
        while True:
            texto = input(
                "\nQual sua dúvida sobre o primeiro emprego? (0 para voltar): "
            ).strip()
            if texto == "0":
                return texto
            if texto == "":
                print("Digite alguma coisa.")
            elif self.tem_dado_pessoal(texto):
                print("Não digite CPF, telefone ou e-mail.")
            else:
                return texto

    def atender_pergunta(self):
        """Faz um atendimento. Devolve False se a pessoa digitou 0 para voltar."""
        inicio = time.time()
        tentativas = 0
        ultima_pergunta = ""
        while True:
            texto = self.ler_pergunta()
            if texto == "0":
                if tentativas > 0:  # buscou, não achou e desistiu
                    self.registrar("pergunta", ultima_pergunta, None, False,
                                   False, tentativas,
                                   round(time.time() - inicio, 1))
                return False
            tentativas += 1
            ultima_pergunta = texto
            resultados = self.base.buscar(texto)
            if not resultados or resultados[0][0] < PONTOS_MINIMOS:
                self.mostrar_nao_encontrei()
                continue
            melhor = self.mostrar_resposta(resultados)
            ajudou = self.ler_sim_nao(
                "\nEssa orientação respondeu sua dúvida? (s/n): "
            )
            self.registrar("pergunta", ultima_pergunta, melhor.id, True,
                           ajudou, tentativas, round(time.time() - inicio, 1))
            print("\nAtendimento registrado.")
            return True

    def mostrar_nao_encontrei(self):
        print("\nNão encontrei uma orientação para essa dúvida.")
        print("Eu só respondo o que está na minha base, "
              "e não invento respostas.")
        print("Assuntos que eu conheço: "
              + ", ".join(self.base.categorias()) + ".")
        print("Tente usar outras palavras (ex.: 'FGTS', "
              "'carteira de trabalho', 'vaga falsa')")
        print("ou use a opção 2 do menu para ver tudo por assunto.")
        print("Você também pode digitar 0 para voltar.")

    def mostrar_resposta(self, resultados):
        """Mostra a melhor orientação e até 2 alternativas. Devolve a melhor."""
        pontos, melhor = resultados[0]
        nivel = "ALTA" if pontos >= PONTOS_ALTA else "MÉDIA"
        print(f"\nConfiança da resposta: {nivel} ({pontos} pontos)")
        melhor.exibir()

        alternativas = [r for r in resultados[1:3] if r[0] >= PONTOS_MINIMOS]
        if alternativas:
            print("\nOutras orientações que podem ajudar:")
            for p, o in alternativas:
                print(f" - {o.titulo} ({p} pontos)")
        return melhor

    # ---------- navegação por categorias ----------
    def navegar(self):
        while True:
            categorias = self.base.categorias()
            print("\n=== Assuntos ===")
            print("Escolha o assunto que você quer consultar:")
            for i, cat in enumerate(categorias, start=1):
                print(f"{i}. {cat}")
            print("0. Voltar")
            escolha = self.ler_opcao("Número do assunto (0 para voltar): ", len(categorias))
            if escolha == 0:
                return
            categoria = categorias[escolha - 1]

            while True:
                inicio = time.time()
                lista = self.base.por_categoria(categoria)
                print(f"\n=== {categoria} ===")
                print("Escolha a orientação que você quer ler:")
                for i, o in enumerate(lista, start=1):
                    print(f"{i}. {o.titulo}")
                print("0. Voltar")
                op = self.ler_opcao("Número da orientação (0 para voltar): ", len(lista))
                if op == 0:
                    break
                orientacao = lista[op - 1]
                orientacao.exibir()
                ajudou = self.ler_sim_nao(
                    "\nEssa orientação respondeu sua dúvida? (s/n): ")
                self.registrar("categoria", categoria, orientacao.id, True,
                               ajudou, 1, round(time.time() - inicio, 1))

    # ---------- indicadores ----------
    def indicadores(self):
        total = len(self.historico)
        if total == 0:
            print("\nAinda não há atendimentos registrados.")
            return

        encontrados = [a for a in self.historico if a["encontrou"]]
        ajudaram = [a for a in self.historico if a["ajudou"]]
        perguntas = [a for a in self.historico if a["origem"] == "pergunta"]

        pct_ajudou = len(ajudaram) / total * 100
        tentativas = sum(a["tentativas"] for a in self.historico) / total

        # "Resposta encontrada" só faz sentido para perguntas em texto livre:
        # a navegação por categorias sempre "encontra".
        if perguntas:
            achadas = [a for a in perguntas if a["encontrou"]]
            pct_encontrada = f"{len(achadas) / len(perguntas) * 100:.1f}%"
        else:
            pct_encontrada = "sem perguntas em texto livre"

        if encontrados:
            tempo = sum(a["tempo_segundos"] for a in encontrados) / len(encontrados)
        else:
            tempo = 0

        sem_solucao = []
        for a in self.historico:
            if not a["ajudou"] and a["origem"] == "pergunta":
                if a["pergunta"] not in sem_solucao:
                    sem_solucao.append(a["pergunta"])

        print("\n=== Indicadores ===")
        print(f"Atendimentos: {total}")
        print(f"Resposta encontrada (perguntas): {pct_encontrada}")
        print(f"Taxa de acerto (ajudou): {pct_ajudou:.1f}%")
        print(f"Tempo médio para encontrar: {tempo:.1f} s")
        print(f"Tentativas por atendimento: {tentativas:.1f}")
        if self.notas:
            media = sum(self.notas) / len(self.notas)
            print(f"Facilidade de uso: {media:.1f} (1 a 5, {len(self.notas)} notas)")
        else:
            print("Facilidade de uso: sem nota ainda")
        print("Dúvidas sem solução:")
        if sem_solucao:
            for d in sem_solucao:
                print(f"  - {d}")
        else:
            print("  (nenhuma)")

    # ---------- exportar CSV ----------
    def exportar_csv(self, caminho="data/atendimentos.csv"):
        if not self.historico:
            print("\nNada para exportar ainda.")
            return
        try:
            with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
                escritor = csv.DictWriter(f, fieldnames=CAMPOS_HISTORICO,
                                      extrasaction="ignore")
                escritor.writeheader()
                for a in self.historico:
                    escritor.writerow(a)
            print(f"\nArquivo exportado: {caminho}")
        except OSError:
            print("Erro ao gravar o CSV. Feche o arquivo se estiver aberto.")