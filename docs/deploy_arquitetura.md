# Deploy: batch ou sob pedido?

O PDF do challenge pedia para escrever o desenho de deploy e justificar. Abaixo a opção defendida neste trabalho.

A peça que entrego é uma API **sob pedido**: um POST com um cliente em JSON e a resposta traz probabilidade e classe no limiar lido do `config`. É predição linha a linha por HTTP, não um batch de milhões de linhas por noite — embora o modelo fosse pequeno o suficiente para aguentar tráfego modesto sem drama.

Batch (job noturno, mandar arquivo de scores para o CRM) também seria caminho válido em produção. Optei pela API porque o enunciado obriga FastAPI e porque assim mostro contrato HTTP, `/health` e validação sem montar um segundo sistema só para o desenho em batch. No mundo real as duas coisas coexistem: lista grande sai do *warehouse*, dúvida no *front* bate na API.

Em produção a sério ainda entrariam coisas que aqui não montei: login, limite de taxa, *reverse proxy* dedicado. O que fiz para o bónus da FIAP foi **Docker** + **Google Cloud Run** na região `europe-west1`: a API pública fica em `https://churn-telco-api-169412920601.europe-west1.run.app` (Swagger em `/docs`, o mesmo contrato que em local). O HTTPS vem do próprio serviço; não tratei de autenticação de chamadas.
