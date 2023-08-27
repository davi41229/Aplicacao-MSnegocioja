from app import app,db

from app.controllers import default
from app.models import models

import os



"""
para rodar em desenvolvimento de teste em maquina

if __name__ == '__main__':
    if not os.path.exists('storage.db'):
        db.create_all()
    app.run(debug=True,host="0.0.0.0", port=7540)

"""




# para fazer o deploy e iniciar no servidor do render

if __name__ == '__main__':
    if not os.path.exists('storage.db'):
        db.create_all()
    port = int(os.getenv("PORT"), "5000")
    app.run(host="0.0.0.0", port=port)


