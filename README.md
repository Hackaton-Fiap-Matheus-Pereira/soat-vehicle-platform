# SOAT Vehicle Platform - Fase 3

API de revenda de veiculos criada para o trabalho substitutivo do Tech Challenge SOAT. A solucao usa dois servicos independentes para manter dados pessoais separados dos dados transacionais.

## Arquitetura

```text
Cliente -> Identity API (8001) -> MySQL auth_db
       \-> Vehicle API  (8002) -> MySQL vehicle_db
                 ^ valida JWT emitido pelo Identity API
```

- **Identity API:** cadastro, login, hash Argon2 e emissao de JWT. E o unico servico que conhece nome, e-mail e senha.
- **Vehicle API:** cadastro e edicao por administrador, catalogo publico, compra autenticada e historico de vendidos. Guarda somente `buyer_id`.
- **Consistencia:** a compra bloqueia a linha do veiculo (`SELECT FOR UPDATE`) e ha uma restricao unica por veiculo.
- **Infraestrutura:** Docker Compose local; manifests Kubernetes; Terraform para namespace, configuracoes e segredos.
- **Documentacao:** Swagger em `/docs` e OpenAPI em `/openapi.json` em cada API.

## Requisitos atendidos

| Requisito | Implementacao |
|---|---|
| Cadastrar veiculo | `POST /vehicles` (admin) |
| Editar veiculo | `PATCH /vehicles/{id}` (admin; vendido e imutavel) |
| Cadastro previo do comprador | `POST /auth/register` |
| Compra pela internet | `POST /vehicles/{id}/purchase` (JWT obrigatorio) |
| Disponiveis por menor preco | `GET /vehicles/available` |
| Vendidos por menor preco | `GET /vehicles/sold` (admin) |
| Dados pessoais separados | Servico e banco exclusivos de identidade |
| CI/CD e Pull Requests | GitHub Actions testa todo PR e publica imagens na `main` |
| Deploy automatizado | Docker, Kubernetes e Terraform |

## Executar localmente

Pre-requisitos: Docker Desktop e Docker Compose.

```bash
git clone URL_DO_SEU_REPOSITORIO
cd NOME_DO_REPOSITORIO
cp .env.example .env
docker compose up --build
```

Espere os bancos ficarem saudaveis. Acesse:

- Identity Swagger: http://localhost:8001/docs
- Vehicle Swagger: http://localhost:8002/docs
- Health checks: http://localhost:8001/health e http://localhost:8002/health

O ambiente local cria o administrador `admin@example.com` / `Admin123!`. Troque essas credenciais e `JWT_SECRET` fora do ambiente de demonstracao.

### Demonstracao ponta a ponta

Com os containers em execucao, rode no PowerShell:

```powershell
./scripts/demo.ps1
```

O script cadastra um comprador, autentica comprador e administrador, cadastra e edita um veiculo, lista o estoque, realiza a compra e lista os vendidos.

## Testes

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install ".[dev]"
ruff check .
pytest -q
```

## Kubernetes e Terraform

1. Substitua `OWNER/REPOSITORY` em `k8s/apps.yaml` pelas imagens do seu GitHub Container Registry.
2. Crie `terraform/terraform.tfvars` a partir do exemplo e use senhas consistentes entre as URLs e os bancos.
3. Aplique infraestrutura e workloads:

```bash
cd terraform
terraform init
terraform plan
terraform apply
cd ..
kubectl apply -f k8s/databases.yaml
kubectl apply -f k8s/apps.yaml
kubectl get all -n soat
```

O Terraform cria namespace, Secret e ConfigMap. Os manifests criam os dois bancos persistentes e as APIs com duas replicas, probes e limites de recursos. Para uma apresentacao local, use Minikube ou Kind; em nuvem, configure o contexto do cluster gerenciado.

> Nunca versione `terraform.tfvars`, `.env` ou senhas reais. Em producao, prefira um gerenciador de segredos e JWT assimetrico (RS256/JWKS).

## CI/CD e fluxo de Pull Request

- Abra uma branch e um Pull Request; os jobs `test` e `e2e` executam lint, testes e o fluxo completo em containers.
- Proteja a branch `main` no GitHub exigindo aprovacao e os checks `test` e `deploy-kind`.
- O job `deploy-kind` cria um cluster Kubernetes temporario, implanta bancos e APIs e executa o fluxo completo.
- Ao fazer merge, o job `publish` tambem publica as duas imagens no GHCR, com tags `latest` e SHA do commit.

### Deploy automatico sem conta de nuvem

O GitHub Actions cria um cluster Kind isolado dentro do runner. Nenhum kubeconfig ou secret precisa ser cadastrado. A pipeline constroi as imagens localmente, carrega-as no cluster, cria credenciais exclusivas de teste, aplica os manifests, aguarda os pods e executa `scripts/demo.ps1` contra as APIs implantadas.

Em Pull Requests, o fluxo automatico e:

```text
lint e testes -> cluster Kind -> build -> deploy Kubernetes -> teste ponta a ponta
```

Depois do merge em `main`, o job `publish` publica as imagens no GitHub Container Registry. O cluster Kind e temporario e descartado ao final, o que e apropriado para validar e comprovar a automacao sem custos de nuvem.

## Modelo de dados

`auth_db.users`: identidade, credenciais com hash e papel (`buyer` ou `admin`).

`vehicle_db.vehicles`: marca, modelo, ano, cor, preco e estado (`available` ou `sold`).

`vehicle_db.sales`: veiculo unico, `buyer_id` opaco, preco congelado no momento da venda e data. Nao ha dados pessoais no banco transacional.

## Decisoes e regras de negocio

- Somente administradores cadastram e editam veiculos ou consultam vendas.
- O catalogo disponivel e publico; a compra exige cadastro e login anteriores.
- Veiculos vendidos nao podem ser editados nem comprados novamente.
- O preco da venda e copiado para preservar o historico.
- Listagens sao paginadas (`limit` e `offset`) e ordenadas por preco crescente.
- E-mail e unico e normalizado para minusculas.

## Estrutura

```text
auth_service/       API independente de identidade
vehicle_service/    API independente de estoque e vendas
migrations/         migrations Alembic selecionadas por servico
tests/              testes automatizados
k8s/                manifests Kubernetes
terraform/          infraestrutura como codigo
scripts/demo.ps1    roteiro executavel ponta a ponta
.github/workflows/  pipeline de CI/CD
```

## Roteiro sugerido para o video

1. Mostre a arquitetura e a separacao dos bancos no README.
2. Mostre o PR com o check de CI aprovado.
3. Execute `docker compose up --build` e mostre os quatro containers saudaveis.
4. Abra os dois Swagger e destaque que autenticacao e vendas sao APIs separadas.
5. Rode `scripts/demo.ps1` e mostre o fluxo completo.
6. Tente comprar o mesmo veiculo novamente e mostre o erro HTTP 409.
7. Mostre `kubectl get all -n soat`, os StatefulSets, Deployments e health probes.
8. Encerre mostrando `terraform plan` e as migrations Alembic.

## Entrega

O enunciado solicita um PDF final com dois links: o repositorio GitHub e o video publicado. Use o modelo em `docs/ENTREGA.md` depois que as URLs existirem.
