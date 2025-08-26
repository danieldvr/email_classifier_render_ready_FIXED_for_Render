# Deploy no Render

## Passos rápidos
1. Faça login no Render em https://render.com
2. Clique em **New +** → **Web Service**.
3. Conecte seu repositório (GitHub/GitLab) com este projeto.
4. Render deve detectar **Python** automaticamente. Se não detectar, selecione **Python**.
5. Confirme o **Build Command**: `pip install -r requirements.txt`
6. Confirme o **Start Command**: `gunicorn -w 2 -k gthread -b 0.0.0.0:$PORT api.app:app`
7. Opcional: importe o arquivo `render.yaml` como **Blueprint** para provisionar o serviço já configurado.

> Obs.: Como o projeto usa `transformers` + `torch`, o build pode demorar e o container precisa baixar os modelos na primeira execução. Em planos free, isso pode levar mais tempo. Considere usar um plano com mais CPU/memória se necessário.
