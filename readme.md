## Aplicacao Melhore seu Negocio já

- funcionalidades
* login
* calculadora
* previsão de probabilidade
* previsao de valor
* classificação RNA
* Pesquisar CNPJ
* Dashboard Financeiro

# login
- cadastrar usuarios, logar, logout, pagina de perfil com edição e deleção, com login_required
- autenticacao via token jwt com token de expiração de 1hora
- salva o token em banco apos login e deleta apos logout
- cadastra: name,email com regex,phone com regex,pin de 5 digitos,upload de foto

# calculadora
- calculadora algaritmica
- html, css, js (projeto do online tutoriais)

# Previsao de probabilidade
- formulário HTML que recebe quatro valores e envia esses dados para um aplicativo Flask  
- usa Scikit-Learn para treinar um modelo de regressão logística
- calcular a probabilidade do valor ser menor que 50.



# precisao de valores
- Formulário HTML que recebe quatro valores e envia esses dados para um aplicativo Flask
- usa Scikit-Learn para treinar um modelo de regressão linear e 
- fazer uma previsão do próximo valor com base nos dados inseridos.




# classificacao RNA
- implementação utiliza o algoritmo KNN para classificar os dados de entradacom base nos exemplos fornecidos. 
- O modelo KNN é treinado com um conjunto de dados de treinamento fornecido no código de exemplo. 
- Após o treinamento, o modelo é salvo no arquivo modelo.pkl utilizando a biblioteca pickle.
- Ao acessar a aplicação no navegador, você pode preencher os valores das quatro variáveis e obter o resultado da classificação para a festa.


# pesquisa CNPJ
- verifica se o cnpj é valido usando regex 
- faz a pesquisa ,consultando a api www.receitaws.com.br/v1/cnpj/ da receita federal
- mostra os resultados em uma tabela ordenada com bootstrap-v5


# dashboard financeiro
- pega tres rceitas , tres despesas, e tres lucros em reais digitados pelos inputs
- Gera um dashboard com graficos pizza, grafico de linhas e graficos de colunas com as comparaçoes em percentual e cores com titulos utilizando as tecnologias==> python,flask,matplotlib,numpy.
- e faz as previsoes do lucro,receita e despeza com a sklearn e regressão logistica de  quanto os valores tendem a aumentar e ou diminuir. 
gerando um dashbord completo na tela . também usa-se try exception para tratar os erros.
- todas as figuras dos graficos, ficam salvas em formato .png e no path==> static/img




#### tecnologias
* phython
* flask
* scikit-learn
* matplotlib
* bootstrap
* html,css,js
* sqlite3
* sqlalchemy


- versoes que não dá erro no sqlalchemy
* Flask-SQLAlchemy==2.5.1
* SQLAlchemy==1.4.35

- erro > AttributeError: 'str' object has no attribute 'decode'
* usar a versao abaixo solucao
PyJWT==1.7.1


- pip install -r requirements.txt
- source venv/bin/activate
- 
