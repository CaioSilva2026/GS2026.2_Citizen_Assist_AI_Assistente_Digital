import json
import re
import unicodedata

from orientacao import Orientacao

# Palavras comuns que não devem contar ponto no título (regra do +1).
PALAVRAS_IGNORADAS = {
    "como", "para", "com", "uma", "qual",
    "quais", "onde", "quando", "meu", "minha",
    "seu", "sua", "que", "dos", "das",
    "por", "tem", "ser", "fazer"
}


def normalizar(texto):
    """Minúsculas, sem acentos e sem pontuação, com espaço nas pontas."""
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caractere for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    return " " + " ".join(texto.split()) + " "


def radical(palavra):
    """Tira o plural simples, para 'golpes' casar com 'golpe'."""
    if palavra.endswith("es") and len(palavra) >= 8:
        return palavra[:-2]
    if palavra.endswith("s") and len(palavra) >= 5:
        return palavra[:-1]
    return palavra


def preparar(texto):
    """normalizar() + plural simples em cada palavra."""
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
            orientacoes = []
            for item in dados:
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
        except (json.JSONDecodeError, KeyError, TypeError,
                UnicodeDecodeError):
            print("Erro: arquivo da base está corrompido ou com campos faltando.")
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

        # Regra 1: palavra-chave que aparece na pergunta (+3)
        for palavra in orientacao.palavras_chave:
            if preparar(palavra) in pergunta_p:
                pontos += 3

        # Regra 2: palavra importante da pergunta (4+ letras) no título (+1)
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