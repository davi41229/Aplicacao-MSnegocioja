from app import app,model
from app.models import models

from flask import render_template,request, redirect, url_for, jsonify, make_response

from flask import flash
from datetime import datetime, timedelta
from werkzeug.security import  check_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
import hashlib
import jwt

from app import db
from app.models.models import User


from sklearn.linear_model import LinearRegression
import numpy as np

import matplotlib.pyplot as plt
import io
import base64

import pickle

import re
import os

from functools import wraps
import requests



# Decorator para verificar autenticação do usuário
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('jwt')
        if not token:
            flash('Por favor, faça o login para acessar esta página', 'error')
            return redirect('/login')
        try:
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = data['user_id']
            user = User.query.get(user_id)
            if not user:
                flash('Usuário não encontrado', 'error')
                return redirect('/login')
            return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            flash('Sua sessão expirou. Por favor faça login novamente', 'error')
            return redirect('/logout')
    return decorated_function


#------------------------------------------



# rota inicial da aplicacao
@app.route('/')
def index():
    return render_template('index.html')


#------------------------------------------




# Rota de registro de usuario (configurada)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        pin = request.form['pin']
        photo = request.files['photo']

        # Salvar a foto em base64
        photo_data = base64.b64encode(photo.read()).decode('utf-8')

        # Validar telefone com regex
        phone_regex = r'^\d{2}(?:\d{8}|\d{9})$'
        if not re.match(phone_regex, phone):
            flash('Numero de telefone invalido', 'error')
            return render_template('register.html')

        # Validar email com regex
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            flash('Endereço de e-mail invalido', 'error')
            return render_template('register.html')

        try:
            user = User(name, email, phone, pin, photo_data)
            db.session.add(user)
            db.session.commit()
            flash('Cadastro realizado. Faça login.', 'success')
            return redirect('/login')
        except IntegrityError:
            db.session.rollback()
            flash('Email já existe', 'error')

    return render_template('register.html')


#------------------------------------------

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        pin = request.form['pin']

        # Validar email com regex
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            flash('Endereço de e-mail invalido', 'error')
            return render_template('login_page.html')

        try:
            user = User.query.filter_by(email=email).one()
            if check_password_hash(user.pin, pin):
                # Gerar JWT
                token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA']}, app.config['JWT_SECRET_KEY'], algorithm='HS256')

                # Salvar o JWT no banco
                user.token = token
                db.session.commit()

                # Configurar cookie
                flash('Usuario logado', 'success!')
                response = make_response(redirect('/profile'))
                response.set_cookie('jwt', token, expires=datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA'])
                return response
            else:
                flash('Credenciais inválidas', 'error')
        except NoResultFound:
            flash('Usuário não encontrado', 'error')

    return render_template('login_page.html')

#------------------------------------------

    

# Rota de perfil
@app.route('/profile')
@login_required
def profile(user):
    # Verificar o JWT no cookie
    token = request.cookies.get('jwt')
    if not token:
        flash('PFaça o login para acessar seu perfil', 'error')
        return redirect('/login')

    try:
        data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']
        user = User.query.get(user_id)
        if not user:
            flash('Usuário não encontrado', 'error')
            return redirect('/login')

        return render_template('profile.html', user=user)
    except jwt.ExpiredSignatureError:
        flash('Sua sessão expirou. Por favor faça login novamente', 'error')
        return redirect('/logout')

#------------------------------------------


# Rota de edição de perfil
@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(user):
    # Verificar o JWT no cookie
    token = request.cookies.get('jwt')
    if not token:
        flash('Faça login para editar seu perfil', 'error')
        return redirect('/login')

    try:
        data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']
        user = User.query.get(user_id)
        if not user:
            flash('Usuário não encontrado', 'error')
            return redirect('/login')

        if request.method == 'POST':
            user.name = request.form['name']
            user.email = request.form['email']
            user.phone = request.form['phone']
            photo = request.files['photo']

            if photo:
                # Salvar a foto em base64
                user.photo = base64.b64encode(photo.read()).decode('utf-8')

            db.session.commit()
            flash('Perfil atualizado com sucesso', 'success')
            return redirect('/profile')

        return render_template('edit_profile.html', user=user)
    except jwt.ExpiredSignatureError:
        flash('Sua sessão expirou. Por favor faça login novamente', 'error')
        return redirect('/logout')
    
#------------------------------------------


# Rota de exclusão de perfil
@app.route('/profile/delete', methods=['GET', 'POST'])
@login_required
def delete_profile(user):
    # Verificar o JWT no cookie
    token = request.cookies.get('jwt')
    if not token:
        flash('Por favor, faça o login para excluir seu perfil', 'error')
        return redirect('/login')

    try:
        data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']
        user = User.query.get(user_id)
        if not user:
            flash('Usuário não encontrado', 'error')
            return redirect('/login')

        if request.method == 'POST':
            db.session.delete(user)
            db.session.commit()

            # Remover o JWT do banco
            user.token = None
            db.session.commit()

            # Remover o cookie
            response = make_response(redirect('/login'))
            response.set_cookie('jwt', '', expires=0)
            flash('Perfil excluído com sucesso', 'success')
            return response

        return render_template('delete_profile.html', user=user)
    except jwt.ExpiredSignatureError:
        flash('Sua sessão expirou. Por favor faça login novamente', 'error')
        return redirect('/logout')
    

#------------------------------------------

# Rota de logout
@app.route('/logout')
@login_required
def logout(user):
    # Excluir o JWT do cookie
    token = request.cookies.get('jwt')
    if not token:
        return redirect('/login')

    try:
        data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']
        user = User.query.get(user_id)
        if not user:
            return redirect('/login')

        # Remover o JWT do banco
        user.token = None
        db.session.commit()

        # Remover o cookie
        flash('Logout feito com sucesso', 'success')
        response = make_response(redirect('/login'))
        response.set_cookie('jwt', '', expires=0)
        return response
    except jwt.ExpiredSignatureError:
        return redirect('/login')
    

#------------------------------------------



# rota para previsao de valor (rota configurada)
@app.route('/pagina_predict_valor')
def pagina_predict_valor():
    return render_template('predict_valor.html')


#------------------------------------------


# previsao_valor
@app.route('/predict_valor', methods=['POST'])
def predict_valor():
    val1 = float(request.form['val1'])
    val2 = float(request.form['val2'])
    val3 = float(request.form['val3'])
    val4 = float(request.form['val4'])
    X_train = np.array([[1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6], [4, 5, 6, 7], [5, 6, 7, 8]])
    y_train = np.array([5, 6, 7, 8, 9])
    X_test = np.array([[val1, val2, val3, val4]])
    model.fit(X_train, y_train)
    prediction = model.predict(X_test)[0]
    return render_template('result_valor.html', prediction=prediction)


#------------------------------------------





"""
#### ERRO para rodar no servidor render ==>
# File "/opt/render/project/src/app/controllers/default.py", line 320, in <module>
# modelo = pickle.load(open('modelo.pkl', 'rb'))
#  TypeError: __randomstate_ctor() takes from 0 to 1 positional arguments but 2 were given


# INICIO DO CODIGO 

# Carregar o modelo treinado
modelo = pickle.load(open('modelo.pkl', 'rb'))

# rota inicial classificacao_RNA
@app.route('/classificacao_RNA')
def classificacao_RNA():
    return render_template('classificacao_RNA.html')


#------------------------------------------


# classificacao_RNA  (rota configurada)
@app.route('/result_RNA', methods=['POST'])
def result_RNA():
    # Obter os valores das variáveis do formulário
    dinheiro = float(request.form['dinheiro'])
    tempo = request.form['tempo']
    convidado = request.form['convidado']
    gasolina = float(request.form['gasolina'])
    
    # Converter as variáveis categóricas para numéricas
    tempo = 1 if tempo == 'aberto' else 0
    convidado = 1 if convidado == 'sim' else 0
    
    # Preparar os dados de entrada para classificação
    dados = [[dinheiro, tempo, convidado, gasolina]]
    
    # Classificar os dados de entrada com o modelo treinado
    resultado = modelo.predict(dados)[0]
    
    # Definir o resultado como 'Ir à festa' ou 'Não ir à festa'
    resultado = 'Ir à festa' if resultado == 1 else 'Não ir à festa'
    
    return render_template('result_RNA.html', resultado=resultado)

    
# FIM DO CODIGO 


"""
#### ERRO para rodar no servidor render ==>
# File "/opt/render/project/src/app/controllers/default.py", line 320, in <module>
# modelo = pickle.load(open('modelo.pkl', 'rb'))
#  TypeError: __randomstate_ctor() takes from 0 to 1 positional arguments but 2 were given


#------------------------------------------



# pagina para pequisar cnpj (rota configurada)
@app.route('/pesquisa_cnpj')
def pesquisa_cnpj():
    return render_template('pesquisa_cnpj.html')


#------------------------------------------
   

# rota de  pequisa cnpj
@app.route('/cnpj', methods=['GET'])
def cnpj():
    cnpj = request.args.get('cnpj')

      # Verifica se o CNPJ informado é válido usando regex
    if not re.match(r'^\d{14}$', cnpj):
        return jsonify({'error': 'CNPJ inválido'})


    if cnpj:
        data = consultar_receita_federal(cnpj)
        if data:
            return render_template('pesquisa_cnpj.html', data=data)
        else:
            return render_template('pesquisa_cnpj.html', error='Erro ao consultar CNPJ')
    else:
        return render_template('pesquisa_cnpj.html')

def consultar_receita_federal(cnpj):
    url = f'https://www.receitaws.com.br/v1/cnpj/{cnpj}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None
    except requests.exceptions.RequestException:
        return None



#------------------------------------------



# dashboard financeiro
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        try:
            receitas = [float(request.form['receita1']), float(request.form['receita2']), float(request.form['receita3'])]
            despesas = [float(request.form['despesa1']), float(request.form['despesa2']), float(request.form['despesa3'])]
            lucros = [float(request.form['lucro1']), float(request.form['lucro2']), float(request.form['lucro3'])]

            if len(receitas) != 3 or len(despesas) != 3 or len(lucros) != 3:
                raise ValueError("Insira exatamente 3 valores para cada campo")

            mostrar_grafico_pizza(receitas, "Receitas", 'receitas_pizza.png')
            mostrar_grafico_pizza(despesas, "Despesas", 'despesas_pizza.png')
            mostrar_grafico_pizza(lucros, "Lucros", 'lucros_pizza.png')
            comparar_receitas_despesas_lucros(receitas, despesas, lucros, 'comparacao_pizza.png')
            prever_valores(receitas, despesas, lucros, 'previsao_receitas.png', 'previsao_despesas.png', 'previsao_lucros.png')
            prever_lucro_previsto(receitas, despesas, 'lucro_previsto.png')

            return redirect('/result_dashboard')

        except Exception as e:
            return f"Erro: {str(e)}"

    return render_template('dashboard.html')

def mostrar_grafico_pizza(valores, titulo, filename):
    fig, ax = plt.subplots()
    cores = ['#ff6666', '#66b3ff', '#99ff99']
    labels = ['Valor 1', 'Valor 2', 'Valor 3']
    ax.pie(valores, labels=labels, autopct='%1.1f%%', colors=cores, startangle=90)
    ax.set_title(titulo)
    plt.savefig(f'app/static/img/{filename}')
    plt.close()

def comparar_receitas_despesas_lucros(receitas, despesas, lucros, filename):
    fig, ax = plt.subplots()
    cores = ['#ff6666', '#66b3ff', '#99ff99']
    labels = ['Receitas', 'Despesas', 'Lucros']
    valores = [receitas[-1], despesas[-1], lucros[-1]]
    ax.pie(valores, labels=labels, autopct='%1.1f%%', colors=cores, startangle=90)
    ax.set_title('Comparação entre Receitas, Despesas e Lucros')
    plt.savefig(f'app/static/img/{filename}')
    plt.close()

def prever_valores(receitas, despesas, lucros, filename_receitas, filename_despesas, filename_lucros):
    x = np.arange(1, 4)
    y_receitas = np.array(receitas)
    y_despesas = np.array(despesas)
    y_lucros = np.array(lucros)

    model_receitas = LinearRegression()
    model_despesas = LinearRegression()
    model_lucros = LinearRegression()

    model_receitas.fit(x.reshape(-1, 1), y_receitas.reshape(-1, 1))
    model_despesas.fit(x.reshape(-1, 1), y_despesas.reshape(-1, 1))
    model_lucros.fit(x.reshape(-1, 1), y_lucros.reshape(-1, 1))

    x_pred = np.arange(1, 6)
    y_receitas_pred = model_receitas.predict(x_pred.reshape(-1, 1))
    y_despesas_pred = model_despesas.predict(x_pred.reshape(-1, 1))
    y_lucros_pred = model_lucros.predict(x_pred.reshape(-1, 1))

    fig, ax = plt.subplots()
    ax.plot(x, y_receitas, marker='o', label='Receitas')
    ax.plot(x_pred, y_receitas_pred, marker='o', label='Receitas (Previstas)')
    ax.set_title('Previsão de Receitas')
    ax.set_xlabel('Mês')
    ax.set_ylabel('Valor ($)')
    ax.legend()
    plt.savefig(f'app/static/img/{filename_receitas}')
    plt.close()

    fig, ax = plt.subplots()
    ax.plot(x, y_despesas, marker='o', label='Despesas')
    ax.plot(x_pred, y_despesas_pred, marker='o', label='Despesas (Previstas)')
    ax.set_title('Previsão de Despesas')
    ax.set_xlabel('Mês')
    ax.set_ylabel('Valor ($)')
    ax.legend()
    plt.savefig(f'app/static/img/{filename_despesas}')
    plt.close()

    fig, ax = plt.subplots()
    ax.plot(x, y_lucros, marker='o', label='Lucros')
    ax.plot(x_pred, y_lucros_pred, marker='o', label='Lucros (Previstos)')
    ax.set_title('Previsão de Lucros')
    ax.set_xlabel('Mês')
    ax.set_ylabel('Valor ($)')
    ax.legend()
    plt.savefig(f'app/static/img/{filename_lucros}')
    plt.close()

def prever_lucro_previsto(receitas, despesas, filename):
    x = np.arange(1, 4)
    y_receitas = np.array(receitas)
    y_despesas = np.array(despesas)

    y_lucros_pred = y_receitas - y_despesas

    fig, ax = plt.subplots()
    cores = ['#66b3ff', '#99ff99', '#ff6666']
    ax.bar(x, y_lucros_pred, color=cores)
    ax.set_title('Lucro Previsto')
    ax.set_xlabel('Mês')
    ax.set_ylabel('Valor ($)')
    plt.savefig(f'app/static/img/{filename}')
    plt.close()


#------------------------------------------



@app.route('/result_dashboard')
def result_dashboard():
    return render_template('result_dashboard.html')
