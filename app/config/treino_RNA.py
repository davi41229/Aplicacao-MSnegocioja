import numpy as np
from sklearn.neural_network import MLPClassifier
import pickle


# Dados de treino (exemplos de João ir ou não à festa)
# Cada linha representa uma instância: [dinheiro, tempo, convidado, gasolina, ir_para_festa]
dados_treino = np.array([
    [150, 1, 1, 8, 1],   # Ir à festa
    [80, 0, 0, 12, 0],   # Não ir à festa
    [120, 1, 1, 5, 1],   # Ir à festa
    [50, 0, 1, 15, 0],   # Não ir à festa
    [200, 1, 0, 7, 1],   # Ir à festa
    [90, 0, 1, 9, 0]     # Não ir à festa
])

# Separar os dados de entrada (X) e os rótulos (y)
X_treino = dados_treino[:, :-1]
y_treino = dados_treino[:, -1]

# Criar e treinar o modelo de rede neural artificial
modelo = MLPClassifier(hidden_layer_sizes=(10,), activation='relu', max_iter=1000)
modelo.fit(X_treino, y_treino)

# Salvar o modelo treinado em um arquivo
with open('modelo.pkl', 'wb') as arquivo:
    pickle.dump(modelo, arquivo)
