import unittest
from unittest.mock import patch, MagicMock, call
from main import App  # Remplacez 'your_module' par le nom de votre module

class TestApp(unittest.TestCase):
    @patch('main.os.getenv')
    def setUp(self, mock_getenv):
        # Configuration des variables d'environnement mockées
        mock_getenv.side_effect = lambda x: {'HOST': 'http://localhost', 'TOKEN': 'dummy_token', 'T_MAX': '25', 'T_MIN': '15', 'DATABASE_URL': 'dummy_url'}.get(x)
        self.app = App()

    @patch('main.psycopg2.connect')
    def test_init_db_connection_success(self, mock_connect):
        # Test réussi de la connexion à la base de données
        self.assertIsNotNone(self.app.db_connection)
        mock_connect.assert_called_once()

    @patch('main.psycopg2.connect')
    def test_init_db_connection_failure(self, mock_connect):
        # Simulation d'une erreur lors de la connexion à la base de données
        mock_connect.side_effect = Exception("Connection failed")
        with self.assertRaises(Exception):
            self.app.init_db_connection()

    @patch('main.requests.get')
    @patch('main.json.loads')
    @patch('main.psycopg2.connect')
    def test_send_action_to_hvac_and_save(self, mock_connect, mock_loads, mock_get):
        # Test de l'envoi d'une action au HVAC et de l'enregistrement dans la base de données
        mock_response = MagicMock()
        mock_response.text = '{"timestamp": "2023-04-01T12:00:00", "action": "TurnOnAc"}'
        mock_get.return_value = mock_response
        mock_loads.return_value = {"timestamp": "2023-04-01T12:00:00", "action": "TurnOnAc"}

        self.app.send_action_to_hvac("TurnOnAc")
        mock_get.assert_called_once()
        # Ici, vous pouvez ajouter des assertions supplémentaires pour vérifier l'interaction avec la base de données

    @patch('main.psycopg2.connect')
    def test_save_temperature_to_database(self, mock_connect):
        # Test de l'enregistrement des données de température dans la base de données
        mock_cursor = mock_connect.return_value.cursor.return_value
        self.app.save_temperature_to_database("2023-04-01T12:00:00", 22.5)
        mock_cursor.execute.assert_called_once_with("INSERT INTO sensor_data (timestamp, temperature) VALUES (%s, %s)", ("2023-04-01T12:00:00", 22.5))  