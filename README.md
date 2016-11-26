# Amadeus 1.0

  Repositório para o back-end do projetos Amadeus, na versão 0.9

**Linguagem Utilizada no Projeto:**
* Python 3.5 
* Django 1.9
* Material Design Bootstrap [2]

**Antes de começar o projeto instale:**
* Python 3.5
* Pip
* Virtualenv
* Postgres

## 1 - COMEÇANDO O PROJETO

### 1.1 - Clonando o projeto

* Vá para a pasta onde queres guardar o projeto
* Escolha a opção de clonagem do projeto

#### HTTPS:

```bash
$ git clone https://github.com/amadeusproject/amadeuslms.git
```

#### SSH

```bash
$ git clone git@github.com:amadeusproject/amadeuslms.git
```


### 1.2 Preparando o ambiente

Agora que você já tem o projeto na sua máquina, precisamos preparar um ambiente próprio para as dependências do projeto. Crie um virtualenv com o seguinte comando abaixo:

**OBS:**  amadeus_env pode ser qualquer outro nome que você desejar(desde que não contenha caracteres especiais)

```bash
virtualenv amadeus_env -p python3.5
```
ative a virtualenv criada no passo anterior

```bash
source amadeus_env/bin/activate
```

Agora vá para a pasta root do projeto clonado e instale as dependências do projeto contidos no arquivo `requirements.txt`

```bash
pip install -r requirements.txt
```
Pronto. Você está apto a contribuir com o projeto.

### 1.3 Padrões de nome para `templates`, `views.py`, `models.py` e `forms.py`
---

Visando uma melhor organização do código e a total compreensão doque está sendo feito por cada integrante do projeto, é recomendado usar os seguintes nomes de arquivos/classes/funções

1. Templates

* `list_course.html`
* `create_course.html`
* `update_course.html`

2. Views . py

* `CourseView()`
* `CourseListView()`

Para Classes que envolvem formulários:
* `CourseFormView()`

3. Forms . py

* `ListCourseForm()`
* `CreateCourseForm`
* `UpdateCourseForm()`

[PT-BR]
##API Descrição
Estamos usando em sua maioria viewsets ( http://www.django-rest-framework.org/api-guide/viewsets/) para construir os endpoints da nossa API. Ela tem como função compartilhar os dados da instância do Amadeus com aplicações credenciadas.

##API Setup
**Criar aplicação**
* Vá para "/o/applications/" e clique "new application". Um formulário irá aparecer para preencher.
* No formulário, preencha somente o "Name" com o nome da aplicação, os campos "client id" e "client secret" são gerados automaticamente e não devem ser modificados. 
"Client type" deve ser confidential, e "Authorization Grant Type" como " Resource owner password-based".

**Obtendo um access Token**

* Crie um request, usando um usuário valido, usando o seguinte abaixo (lembre-se que isso é  um POST, estou usando um comando curl para fins de teste): 
curl -X POST -d "grant_type=password&username=<user_name>&password=<password>" -u"<client_id>:<client_secret>" http://amadeus/o/token/

* finalmente, com o seu access token, você pode testar um dos endpoints usando o template abaixo: 
curl -H "Authorization: Bearer <your_access_token>" -X POST -d"username=foo&password=bar" http://localhost:8000/users/ (inserting a new user)
 

* model list(GET) = list all objects from that mode in pagination mode, each page has 10
* model detail(GET) = give the details of the objects and most important fields of the ones objects its has relationships.
* model create

**API Endpoints **

**Courses (URL: coursesapi)**
* course list ("/coursesapi/")
* course detail ("/coursesapi/id") (id is a parameter)

**Subject (URL: subjectapi)**
* subject list ("/subjectapi/")
* subject detail ("/subjectapi/id") (id is a parameter)

**Topic (URL: topicsapi)**
* topics list ("/topicsapi/")
* topic detail ("/topicsapi/id") (id is a parameter)

**logs (URL: logs)**
* logs list ("/logs/")
* log detail ("/logs/id") (id is a parameter)




## Link's úteis
[Git - Introdução e comandos básicos(PT-BR)](https://github.com/fernandomayer/git-rautu/blob/master/0_configuracao-inicial.md)

[2] https://github.com/FezVrasta/bootstrap-material-design

[Django Breadcrumbs](http://django-bootstrap-breadcrumbs.readthedocs.io/en/latest/)


## Sprint WorkFlow
[PT-BR]
**Dia : Atividade**
* 01 Segunda: Retrospective/Planning
* 05 Sexta: Review
* 08 Segunda: Weekly Meeting
* 11 Quinta: Sprint Deadline
* 12 Sexta: Review/Deploy

[EN-US]

**Day  : Activity**
* 01 Monday: Retrospective/Planning
* 05 Friday: Review
* 08 Monday: Weekly Meeting
* 11 Thursday: Sprint Deadline
* 12 Friday: Review/Deploy
