# Deploy: batch ou sob pedido?

O PDF do challenge pedia para escrever o desenho de deploy e justificar. Abaixo a opção defendida neste trabalho.

A peça que entrego é uma API **sob pedido**: um POST com um cliente em JSON e a resposta traz probabilidade e classe no limiar lido do `config`. É predição linha a linha por HTTP, não um batch de milhões de linhas por noite — embora o modelo fosse pequeno o suficiente para aguentar tráfego modesto sem drama.

Batch (job noturno, mandar arquivo de scores para o CRM) também seria caminho válido em produção. Optei pela API porque o enunciado obriga FastAPI e porque assim mostro contrato HTTP, `/health` e validação sem montar um segundo sistema só para o desenho em batch. No mundo real as duas coisas coexistem: lista grande sai do *warehouse*, dúvida no *front* bate na API.

O que não fizemos (e não era obrigatório): empacotar em Docker, TLS, login, limite de taxa, *reverse proxy*. O bónus de nuvem seria expor o mesmo `uvicorn` atrás de um URL gerido (Cloud Run, ECS, o que a FIAP aceitar) quando sobrar tempo.
