# utils/nlp.py
import re
import unicodedata
from typing import Dict, Any
from transformers import pipeline

# Modelo multilíngue NLI
_MODEL_ID = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"

_classifier = None

# Rótulos finais
FINAL_LABELS = ["Produtivo", "Improdutivo"]

# Candidate labels descritivos (o que o modelo enxerga)
# Dica: descreva o domínio, não um adjetivo abstrato.
CANDIDATE_MAP = {
    "Produtivo": (
        "relacionado a trabalho: tarefas, prazos, reuniões, suporte, chamados, "
        "projetos, entregas ou alinhamentos profissionais"
    ),
    "Improdutivo": (
        "conteúdo pessoal ou social, felicitações, correntes, marketing, newsletter, "
        "promoções, spam, memes, convites informais"
    ),
}
CANDIDATES = [CANDIDATE_MAP["Produtivo"], CANDIDATE_MAP["Improdutivo"]]
REVERSE = {v: k for k, v in CANDIDATE_MAP.items()}

# Template em PT-BR ajuda a ancorar o NLI
HYPOTHESIS = "Este e-mail é {}."

# Threshold de confiança mínimo para confiar no modelo puro
MIN_CONF = 0.60  # Retornamos ao limite original

# Padrões fortes para improdutivo (atalhos de alto sinal)
STRONG_IMPRODUTIVO = [
    r"\bparab[eé]ns\b", r"\bfeliz\s+anivers[aá]rio\b", r"\bboas\s+festas\b",
    r"\bnewsletter\b", r"\bunsubscribe\b", r"\boferta(s)?\b", r"\bpromo(ção|coes?)\b",
    r"\bdesconto(s)?\b", r"\bsorteio(s)?\b", r"\bmarketing\b", r"\bdivulga(ção|coes?)\b",
    r"\bconvite\b.*\bhappy\s*hour\b", r"\bmeme(s)?\b", r"\bconvite\b", r"\binscrição\b",
    r"\bwebinar\b"
]

def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    return re.sub(r"\s+", " ", text).strip()

def clean_text(text: str) -> str:
    """Limpeza leve: normaliza, baixa caixa e remove disclaimers óbvios."""
    if not text:
        return ""
    text = _normalize(text)
    # remove disclaimers comuns
    text = re.sub(r"(?is)this message.*confidential.*do not share.*", " ", text)
    return text

def get_classifier():
    global _classifier
    if _classifier is None:
        _classifier = pipeline(
            task="zero-shot-classification",
            model=_MODEL_ID
        )
    return _classifier

def _strong_improdutivo_hit(text_low: str) -> bool:
    return any(re.search(p, text_low) for p in STRONG_IMPRODUTIVO)

def classify_email(text: str) -> Dict[str, Any]:
    """
    Retorna:
      {
        'label': 'Produtivo'|'Improdutivo',
        'score': float,
        'raw': {...}  # saída completa do HF para auditoria
      }
    """
    txt = clean_text(text)
    txt_low = txt.lower()

    # Heurística forte antes do modelo
    if _strong_improdutivo_hit(txt_low):
        return {"label": "Improdutivo", "score": 0.99, "raw": {"reason": "rule_improdutivo"}}

    clf = get_classifier()
    out = clf(
        txt,
        candidate_labels=CANDIDATES,
        hypothesis_template=HYPOTHESIS,
        multi_label=False  # classificação exclusiva
    )

    # `out['labels']` já vem ordenado por score desc
    top_label_text = out["labels"][0]
    top_score = float(out["scores"][0])

    mapped_label = REVERSE.get(top_label_text, "Produtivo")  # fallback seguro
    # Se confiança baixa, use heurística leve adicional
    if top_score < MIN_CONF:
        # alguns sinais levemente produtivos
        prod_signals = [r"\bchamado\b", r"\bprojeto\b", r"\breuni[aã]o\b", r"\bdeadline\b",
                         r"\bstatus\b", r"\bentrega(s)?\b", r"\bticket\b", r"\bsuporte\b"]
        if any(re.search(p, txt_low) for p in prod_signals):
            mapped_label = "Produtivo"
        else:
            mapped_label = "Improdutivo"
        # reduza o score para refletir incerteza
        top_score = min(top_score, 0.59)  

    return {"label": mapped_label, "score": top_score, "raw": out}

def suggest_reply(text: str, label: str) -> str:
    text_low = (text or "").lower()
    if label == "Produtivo":
        if any(k in text_low for k in ["chamado", "ticket", "status", "andamento"]):
            return ("Olá! Obrigado pela atualização. Vamos verificar o status e retornamos até {DATA/PRAZO} "
                    "com os próximos passos.")
        if any(k in text_low for k in ["erro", "bug", "não consigo", "nao consigo", "problema", "falha"]):
            return ("Olá! Obrigado pelo relato. Para agilizar, poderia informar prints, horário aproximado "
                    "do erro e o número do chamado (se houver)? Abriremos/atualizaremos o ticket e "
                    "retornaremos até {DATA/PRAZO}.")
        if any(k in text_low for k in ["anexo", "arquivo", "documento"]):
            return ("Olá! Recebemos o arquivo. Vamos validar o conteúdo e retornamos com a confirmação "
                    "ou próximos passos até {DATA/PRAZO}.")
        return ("Olá! Obrigado pela mensagem. Registramos sua solicitação e retornaremos com os próximos "
                "passos até {DATA/PRAZO}. Caso tenha informações adicionais, responda a este e-mail.")
    else:
        if any(k in text_low for k in ["parabéns", "felicitações", "obrigado", "agradeço"]):
            return ("Muito obrigado pela mensagem! Ficamos à disposição quando precisar.")
        return ("Obrigado pelo contato! Caso precise de ajuda ou tenha alguma solicitação específica, "
                "é só responder este e-mail.")