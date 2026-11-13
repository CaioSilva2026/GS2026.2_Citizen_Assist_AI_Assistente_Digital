import json
import re
import unicodedata

from orientacao import Orientacao

PALAVRAS_IGNORADAS = {
    "como", "para", "com", "uma", "qual",
    "quais", "onde", "quando", "meu", "minha",
    "seu", "sua", "que", "dos", "das",
    "por", "tem", "ser", "fazer"
}

CAMPOS_TEXTO = ["categoria", "titulo", "resposta", "onde", "fonte",
                "verificado_em"]


def item_valido(item):

    if not isinstance(item, dict):
        return False
    if not isinstance(item.get("id"), int):
        return False
    for campo in CAMPOS_TEXTO:
        valor = item.get(campo)
        if not isinstance(valor, str) or valor.strip() == "":
            return False

    chaves = item.get("palavras_chave")
    if not isinstance(chaves, list) or len(chaves) == 0:
        return False
    if not all(isinstance(p, str) and p.strip() for p in chaves):
        return False
    documentos = item.get("documentos")
    if not isinstance(documentos, list):
        return False
    if not all(isinstance(d, str) for d in documentos):
        return False
    return True


def normalizar(texto):

    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caractere for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    return " " + " ".join(texto.split()) + " "


def radical(palavra):

    if palavra.endswith("es") and len(palavra) >= 8:
        return palavra[:-2]
    if palavra.endswith("s") and len(palavra) >= 5:
        return palavra[:-1]
    return palavra


def preparar(texto):
    palavras = normalizar(texto).split()
    return " " + " ".join(radical(p) for p in palavras) + " "


class BaseConhecimento:

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []

    def carregar(self):
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if not isinstance(dados, list) or len(dados) == 0:
                print("Erro: a base precisa ser uma lista com pelo menos 1 orientação.")
                return False
            orientacoes = []
            for posicao, item in enumerate(dados, start=1):
                if not item_valido(item):
                    print(f"Erro: o registro número {posicao} da base está "
                          "com campos faltando ou com o tipo errado.")
                    return False
                orientacoes.append(Orientacao(
                    item["id"], item["categoria"], item["titulo"],
                    item["palavras_chave"], item["resposta"],
                    item["documentos"], item["onde"],
                    item["fonte"], item["verificado_em"]
                ))
            self.orientacoes = orientacoes
            return True
        except FileNotFoundError:
            print("Erro: arquivo da base de conhecimento não encontrado.")
        except (json.JSONDecodeError, UnicodeDecodeError):
            print("Erro: arquivo da base está corrompido (JSON inválido).")
        except OSError:
            print("Erro: não foi possível abrir o arquivo da base.")
        return False

    def categorias(self):
        lista = []
        for o in self.orientacoes:
            if o.categoria not in lista:
                lista.append(o.categoria)
        return lista

    def por_categoria(self, categoria):
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        pergunta_p = preparar(pergunta)
        titulo_p = preparar(orientacao.titulo)
        pontos = 0

        for palavra in orientacao.palavras_chave:
            if preparar(palavra) in pergunta_p:
                pontos += 3

        palavras_titulo = set(titulo_p.split())
        for palavra in set(normalizar(pergunta).split()):
            if (
                len(palavra) >= 4
                and palavra not in PALAVRAS_IGNORADAS
                and radical(palavra) in palavras_titulo
            ):
                pontos += 1
        return pontos

    def buscar(self, pergunta):
        resultados = []
        for o in self.orientacoes:
            pontos = self.pontuar(pergunta, o)
            if pontos > 0:
                resultados.append((pontos, o))
        resultados.sort(key=lambda t: t[0], reverse=True)
        return resultados