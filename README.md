# Classificador de E-mails – Produtivo x Improdutivo

Aplicação web simples em **Flask + Transformers** que:
- Classifica e-mails em **Produtivo** ou **Improdutivo** via **Zero-Shot Classification** (modelo multilíngue).
- Sugere uma **resposta automática** adequada.

---

## 🚀 Como rodar localmente (passo a passo em 1 bloco)

```bash
# 1. Clone o repositório
git clone <URL_DO_SEU_REPOSITORIO>
cd email_classifier_app-main

# 2. Crie e ative um ambiente virtual
python -m venv .venv
# Ativar no Windows:
.venv\Scripts\activate
# Ativar no Linux/Mac:
# source .venv/bin/activate

# 3. Instale as dependências
pip install --upgrade pip
pip install -r requirements.txt

# (Opcional) Caso tenha problemas com Torch no Windows:
# pip install torch --index-url https://download.pytorch.org/whl/cpu

# 4. Execute a aplicação
python run_local.py

# Acesse no navegador:
# http://localhost:5000


> Na primeira execução o modelo será baixado automaticamente (pode levar alguns minutos).

## Deploy no Render (gratuito)

1. Faça **fork** ou envie este repositório ao GitHub.
2. Em **render.com**, crie um **Web Service** conectando ao seu repositório.
3. Configure:
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `gunicorn app:app`
4. Deploy. A primeira execução será mais lenta para baixar o modelo.

**Dicas de Deploy**
- Prefira regiões próximas ao Brasil para menor latência.
- Se faltar memória, troque o modelo em `utils/nlp.py` por um mais leve:
  - `"typeform/distilbert-base-uncased-mnli"` (inglês – leve)
  - `"MoritzLaurer/deberta-v3-base-mnli-fever-anli"` (médio)
- Como *fallback*, implemente regras simples se o modelo não carregar (exemplo no código).

## Estrutura
```
email_classifier_app-main/
├─ api/
│  └─ app.py
├─ templates/
│  └─ index.html
├─ utils/
│  ├─ nlp.py
│  └─ pdf.py
├─ examples/
│  ├─ exemplo_produtivo.txt
│  └─ exemplo_improdutivo.txt
├─ requirements.txt
├─ run_local.py
└─ render.yaml

```
