# Amadeus 0.9
------

  Repositório para o back-end do projetos Amadeus, na versão 0.9

**Linguagem Utilizada no Projeto:**
* Python 3.5 
* Django 1.9

**Antes de começar o projeto instale:**
* Python 3.5
* Pip
* Virtualenv

***

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

## Link's úteis
[Git - Introdução e comandos básicos(PT-BR)](https://github.com/fernandomayer/git-rautu/blob/master/0_configuracao-inicial.md)


