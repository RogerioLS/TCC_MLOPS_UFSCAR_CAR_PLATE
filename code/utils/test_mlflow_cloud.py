import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pandas as pd
import numpy as np

from mlflow.tracking import MlflowClient
import mlflow

# URL do servidor MLflow
mlflow.set_tracking_uri("http://ec2-54-147-25-167.compute-1.amazonaws.com:5000/")

# Verificar se o experimento já existe ou está excluído
client = MlflowClient()
experiment_name = "Iris Classification Experiment"
experiment = client.get_experiment_by_name(experiment_name)

if experiment and experiment.lifecycle_stage == 'deleted':
    # Restaurar experimento excluído
    client.restore_experiment(experiment.experiment_id)
    print(f"Experimento '{experiment_name}' restaurado.")
elif not experiment:
    # Criar novo experimento se ele não existir
    mlflow.create_experiment(experiment_name)
    print(f"Novo experimento '{experiment_name}' criado.")

# Definir o experimento ativo no MLflow
mlflow.set_experiment(experiment_name)

# Carregar o dataset Iris
iris = load_iris()
X = iris.data
y = iris.target
feature_names = iris.feature_names
target_names = iris.target_names

# Dividir o dataset em treinamento e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Criar e treinar o modelo
model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)

# Fazer previsões
y_pred = model.predict(X_test)

# Avaliar o modelo
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred, target_names=target_names, output_dict=True)
conf_matrix = confusion_matrix(y_test, y_pred)
conf_matrix_df = pd.DataFrame(conf_matrix, index=target_names, columns=target_names)

# Iniciar um novo run
with mlflow.start_run():
    # Logar parâmetros do modelo
    mlflow.log_param("model", "Logistic Regression")
    mlflow.log_param("max_iter", 200)
    mlflow.log_param("solver", "lbfgs")
    mlflow.log_param("multi_class", "auto")
    mlflow.log_param("penalty", "l2")
    
    # Logar métricas
    mlflow.log_metric("accuracy", accuracy)
    for label, metrics in report.items():
        if label != 'accuracy':
            mlflow.log_metric(f"{label}_precision", metrics['precision'])
            mlflow.log_metric(f"{label}_recall", metrics['recall'])
            mlflow.log_metric(f"{label}_f1-score", metrics['f1-score'])
    
    # Logar matriz de confusão
    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_matrix_df, annot=True, cmap="Blues", fmt="g")
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted labels')
    plt.ylabel('True labels')
    plt.savefig("confusion_matrix.png")
    mlflow.log_artifact("confusion_matrix.png")

    # Logar o modelo
    mlflow.sklearn.log_model(model, "model")

    # Logar características e amostras de dados
    plt.figure(figsize=(10, 6))
    for i in range(X.shape[1]):
        plt.subplot(1, 4, i+1)
        plt.scatter(X[:, i], y, alpha=0.5)
        plt.title(f'Feature: {feature_names[i]}')
        plt.xlabel('Feature Value')
        plt.ylabel('Target Value')
    plt.tight_layout()
    plt.savefig("feature_scatter_plots.png")
    mlflow.log_artifact("feature_scatter_plots.png")

    # Logar gráficos de treinamento e validação (se disponível)
    # Exemplo fictício: Gráficos de treinamento e validação
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, 6), np.random.rand(5), label='Train Loss')
    plt.plot(range(1, 6), np.random.rand(5), label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss')
    plt.legend()
    plt.savefig("training_validation_loss.png")
    mlflow.log_artifact("training_validation_loss.png")

print("Run successfully logged with maximum parameters and images.")