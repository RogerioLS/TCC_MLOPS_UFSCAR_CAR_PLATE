"""Módulo para interação com o DynamoDB."""

from src import Any, Dict, Optional, boto3, st, time


class DynamoDBInteraction:
    """Classe para interação com o DynamoDB."""

    def __init__(self):
        """Inicializa a instância do DynamoDBInteraction."""
        self.dynamodb = boto3.resource("dynamodb")

    def fetch_plate_data(
        self, table_name: str, object_name: str, max_retries: int = 9, delay: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Busca informações da placa no DynamoDB com base no nome do objeto.

        Args:
            table_name (str): Nome da tabela no DynamoDB.
            object_name (str): Nome do objeto correspondente no S3.
            max_retries (int): Número máximo de tentativas de busca.
            delay (int): Tempo de espera entre as tentativas (em segundos).

        Returns:
            Optional[Dict[str, Any]]: Dados da placa ou None, se não encontrado.
        """
        table = self.dynamodb.Table(table_name)

        for attempt in range(max_retries):
            try:
                response = table.scan()
                items = response.get("Items", [])

                # Busca o registro mais recente com o nome do objeto
                matching_items = [
                    item for item in items if item.get("PK") == object_name
                ]
                if matching_items:
                    plate_data = max(
                        matching_items, key=lambda x: x.get("timestamp", 0)
                    )
                    if plate_data.get("detected") == 0:
                        return plate_data
                    if (
                        plate_data.get("detected") == 1
                        and plate_data.get("detected_text") is not None
                    ):
                        return plate_data
                time.sleep(delay)  # Aguarda antes de tentar novamente
            except Exception as e:
                st.error(f"Erro ao buscar dados no DynamoDB: {str(e)}")
                return None

        st.error(
            "Tempo de espera esgotado. Não foi possível encontrar informações relacionadas à placa."
        )
        return None
