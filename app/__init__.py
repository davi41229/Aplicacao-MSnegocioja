from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from sklearn.linear_model import LinearRegression


from datetime import timedelta



app = Flask(__name__)
model = LinearRegression()


 # configuraçoes da aplicacao
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///storage.db'
app.config['SECRET_KEY'] = 'a-paciencia-e-uma-virtude'
app.config['JWT_SECRET_KEY'] = 'paciencia-e-experiencia'
app.config['JWT_EXPIRATION_DELTA'] = timedelta(hours=1)

db = SQLAlchemy(app)