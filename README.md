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


## Breadcrumbs
[PT-BR]


Os **breadcrumbs** reduzem o número de ações que um usuários precisa tomar para chegar a uma página de nível superior e melhorar o nível de encontrabilidade de seções e páginas.

No amadeus estamos utilizando a lib [django-bootstrap-breadcrumbs](http://django-bootstrap-breadcrumbs.readthedocs.io/en/latest/) para oferecer essa facilidade aos nosso usuários.

**Como usar:**


O pacote já se encontra instalado no projeto. Ele está na lista das dependências que se encontram no arquivo `requirements.txt`, que já foi instalado anteriormente. Então para usar a lib num template, você só precisa fazer o load da tag: ```{% load django_bootstrap_breadcrumbs %}```

O pacote assume que você tem uma boa organização de urls no seu projeto para que ele possa funcionar como esperado. Ele funciona a base herança de templates, como assim?

No arquivo ```core > templates > base.html``` existe um bloco denominado ***breadcrumbs***, que é o bloco que deve ser alterado pelos templates que herdam do ```base.html```. O outro bloco que vem logo a seguir ***render_breadcrumbs*** é o bloco responsável por renderizar todo o HTML que é gerado pelo bloco enterior, e ele só deve ser usado uma única vez.
TODOS os arquivos que herdam do template ```base.html``` ou de outro template que herdou dele, deve implementar o bloco ***breadcrumbs***.

***Exemplo***


Como a nossa dashboard começa na app ```app```, é nesse app que foi feito a primeira herança do bloco ***breadcrumbs*** e a partir dalí todos os apps estendem dos templates dessa app.
Vamos ilustrar um exemplo de breadcrumbs que vai até a página de criar uma discilina dentro de um curso:

```1 - home.html```


O arquivo ```1``` se encontra na app ```app``` e ele faz herança do template ```base.html```


```python
1  {% block breadcrumbs %}
2
3      {% clear_breadcrumbs %}
4      {% breadcrumb 'Home' 'app:index' %}
5  
6  {% endblock %}
7
8  {% block render_breadcrumbs %}
9      {% render_breadcrumbs %}
10 {% endblock %}
```

A linha 3 é responsável por 'limpar' todo o breadcrumbs feito anteriormente, ou seja, se existisse algum breadcrumbs no trmplate herdado por ```home.html```, ele não vai existir a partir desse template. Por isso é recomendado usar essa tag somente no template root do breadcrumbs, egg: na home.

A linha 4, é onde a mágica acontece. É o breadcrumb da página em si.
O primeiro parâmetro da template tag: o 'Home', é o texto que vai ficar linkado(quando você estiver em uma outra página). Ele pode ser um texto, que tem que vir entres aspas, por exemplo 'Home', ou pode ser uma variavel do template que nesse caso não precisa de aspas. O segundo parâmetro é a url da página em que o template em questão vai ser exibida, ou seja, ele chama a sua própria ulr, como era de se esperar.

***OBS:*** Se a url tivesse um parâmetro, ele devia ser passado como um terceiro argumento da template tag.

***OBS2:*** A linha 9 só precisa ser chamado uma única vez e deve ser na template home, egg: os templates que não são o root do breadcrumbs não precisam subsvrever o bloco 'render_breadcrumbs'

```2 - courses > templates > course > index.html```


O arquivo ```2``` é o index da app ```courses``` e ele herda o template ```1```.


```python
1 {% block breadcrumbs %}
2
3     {{ block.super }}
4     {% breadcrumb 'Courses' 'course:manage' %}
5
6 {% endblock %}
```

A linha 3 traz todo o breadcrumbs que já  foi feito anteriormente para a página corrente, e a linha 4 acrescenta um novo elemento na lista dos breadcrumbs. Observe que você não precisa se preocupar em dizer qual página está sendo exibida e nem costomizar nenhum HTML. A template tag já faz tudo isso por você. Você só precisa dar um nome para o link, chamar a ulr da página e passar algum parâmetro para a ulr(caso for preciso).

```3 - courses > templates > course > view.html```


O arquivo 3 é o template de um curso específico, e ele herda do template ```2```.


```python
1 {% block breadcrumbs %}
2
3     {{ block.super }}
4     {% breadcrumb course 'course:view' course.slug %}
5
6 {% endblock %}
```

Repare que o primeiro parâmetro agora é uma variavel do template que representa o nome do curso, e o terceiro parâmetro é um argumento para a url(eles não precisam de aspas).

```4 - courses > templates > subject > create.html```


O arquivo ```4``` é o template de criar uma disciplica e ele herda do template ```3```.



```python
1 {% block breadcrumbs %}
2     {{ block.super }}
3     {% breadcrumb 'Create subject' 'course:create_subject' course.slug %}
4 {% endblock breadcrumbs %}
```

Feito isso o breadcrumbs da página 'Criar disciplina' fica da seguinte forma:


 [Home]() / [Cursos]() / [Nome do Curso]() / Criar disciplina


[EN-SU]


**Breadcrumbs** reduce the number of actions a user needs to take to reach a top-level page and improve the level of reachability of sections and pages.

In amadeus we are using lib [django-bootstrap-breadcrumbs](http://django-bootstrap-breadcrumbs.readthedocs.io/en/latest/) to offer this facility to our users.


**How to use:**


The package is already installed in the project. It is in the list of dependencies that are in the `requirements.txt` file, which has already been installed previously. So to use lib in a template, you just need to load the tag: ```{% load django_bootstrap_breadcrumbs %}```

The package assumes that you have a good organization of urls in your project so that it can work as expected. It works the base inheritance of templates, how so?

In the file ```core > templates > base.html``` there is a block called ***breadcrumbs***, which is the block that should be changed by the templates that inherit from ``` base.html```. The other block coming soon ***render_breadcrumbs*** is the block responsible for rendering all the HTML that is generated by the enterior block, and it should only be used once.
ALL files that inherit from the template ```base.html``` or from another template that inherited from it, should implement the block ***breadcrumbs***.


***Example***


As our dashboard starts in the app ```app```, it is in this app that was made the first inheritance of the block ***breadcrumbs*** and from there all the apps extend from the templates of this app.
Let's illustrate an example of breadcrumbs that goes up the page to create a subject within a course:

```1 - home.html```


The ```1``` file is found in the ```app``` app and it inherits from the ``` base.html``` template


``` Python
1  {% block breadcrumbs %}
2
3       {% clear_breadcrumbs %}
4       {% breadcrumb 'Home' 'app: index' %}
5
6  {% endblock %}
7
8  {% block render_breadcrumbs %}
9      {% render_breadcrumbs %}
10 {% endblock %}
```

Line 3 is responsible for 'clearing' all previously made breadcrumbs, that is, if there were any breadcrumbs in the trmplate inherited by ``` home.html```, it will not exist from that template. So it is recommended to use this tag only in the breadcrumbs root template, egg: na home.

Line 4, is where magic happens. It is the breadcrumb of the page itself.
The first parameter of the template tag: 'Home' is the text that will be linked (when you are on another page). It can be a text, which has to be enclosed in quotation marks, for example 'Home', or it can be a template variable that in this case does not need quotation marks. The second parameter is the url of the page in which the template in question is going to be displayed, that is, it calls its own ulr, as expected.

***NOTE:*** If the url had a parameter, it should be passed as a third argument of the template tag.

***NOTE 2:*** Line 9 only needs to be called once and should be in the template home, egg: non-root templates of breadcrumbs do not need to subscribe to the 'render_breadcrumbs'

```2 - courses > templates > course > index.html```


The ```2``` file is the index of the ```courses``` app and it inherits the ```1``` template.


``` python
1 {% block breadcrumbs %}
2
3     {{ block.super }}
4     {% breadcrumb 'Courses' 'course: manage' %}
5
6 {% endblock %}
```

Line 3 brings all the breadcrumbs that were previously made to the current page, and line 4 adds a new element to the breadcrumbs list. Note that you do not have to worry about which page is being displayed or costomising any HTML. The template tag does all this for you. You just need to give the link a name, call the ulr of the page and pass some parameter to the ulr (if necessary).

```3 - courses > templates > course > view.html```


File 3 is the template for a specific course, and it inherits from the ```2``` template.


``` python
1 {% block breadcrumbs %}
2
3     {{ block.super }}
4     {% breadcrumb course 'course: view' course.slug %}
6 {% endblock %}
```

Notice that the first parameter is now a template variable that represents the course name, and the third parameter is an argument to the url (they do not need quotation marks).

```4 - courses > templates > subject > create.html```


The ```4``` file is the template for creating a discipline and it inherits from the ```3``` template.



``` python
1 {% block breadcrumbs%}
2     {{ block.super }}
3     {% breadcrumb 'Create subject' 'course: create_subject' course.slug %}
4 {% endblock breadcrumbs %}
```

Once this is done, the breadcrumbs of the 'Create discipline' page is as follows:


[Home]() / [Courses]() / [Course Name]() / Create Subject


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
