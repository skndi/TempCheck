import datetime
from unittest import TestCase
from unittest.mock import patch
import db
import util
from db import schemas, models
from db import exceptions


class TestDatabase(TestCase):

    @patch("sqlalchemy.orm.Session")
    @patch("sqlalchemy.orm.Query")
    def setUp(self, mock_session, mock_query):
        self.db = db.Database(mock_session)
        self.mock_session = mock_session
        self.db._session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        self.mock_query = mock_query

    def test_get_user_by_username(self):
        username = "rado21"
        user = models.User(id=2, username=username, hashed_password="1234")
        self.mock_query.first.return_value = user

        self.assertEqual(user, self.db.get_user_by_username(username))
        self.mock_query.filter.assert_called_once()
        self.mock_query.first.assert_called_once()
        self.mock_session.query.assert_called_once_with(models.User)

    @patch("db.get_password_hash")
    def test_create_user(self, mock_get_password_hash):
        mock_get_password_hash.side_effect = lambda password: password + "5"
        user = schemas.UserCreate(username="rado21", password="1234")
        db_user = self.db.create_user(user)

        self.assertEqual(user.username, db_user.username)
        self.assertEqual("12345", db_user.hashed_password)
        self.mock_session.add.assert_called_once_with(db_user)
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once_with(db_user)

    def test_create_alert_for_user(self):
        alert = schemas.AlertCreate(target=22.3, direction=schemas.Direction.OVER)
        user_id = 123
        db_alert = self.db.create_alert_for_user(alert, user_id)

        self.assertEqual(db_alert.target, alert.target)
        self.assertEqual(db_alert.direction, alert.direction)
        self.assertEqual(db_alert.owner_id, user_id)
        self.mock_session.add.assert_called_once_with(db_alert)
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once_with(db_alert)

    def test_change_alert_state_with_existing_owned_alert(self):
        user = models.User(id=2, username="rado21", hashed_password="1234")
        alert = models.Alert(id=1, target=22.3, direction=schemas.Direction.OVER, active=False, owner_id=2, owner=user)
        self.mock_query.first.return_value = alert

        actual = self.db.change_alert_state(alert.id, True, user.username)

        self.assertEqual(alert, actual)
        self.assertEqual(actual.active, True)
        self.mock_query.filter.assert_called_once()
        self.mock_query.first.assert_called_once()
        self.mock_session.query.assert_called_once_with(models.Alert)
        self.mock_session.commit.assert_called_once()

    def test_change_alert_state_with_existing_not_owned_alert(self):
        user = models.User(id=2, username="rado21", hashed_password="1234")
        alert = models.Alert(id=1, target=22.3, direction=schemas.Direction.OVER, active=False, owner_id=2,
                             owner=user)
        self.mock_query.first.return_value = alert

        self.assertRaises(exceptions.AlertNotOwnedError, self.db.change_alert_state, alert.id, True, "not_rado21")
        self.mock_query.filter.assert_called_once()
        self.mock_query.first.assert_called_once()
        self.mock_session.query.assert_called_once_with(models.Alert)
        self.mock_session.commit.assert_not_called()

    def test_change_alert_state_with_not_existing_alert(self):
        self.mock_query.first.return_value = None

        self.assertRaises(exceptions.AlertNotFoundError, self.db.change_alert_state, 123, True, "rado21")
        self.mock_query.filter.assert_called_once()
        self.mock_query.first.assert_called_once()
        self.mock_session.query.assert_called_once_with(models.Alert)
        self.mock_session.commit.assert_not_called()

    def test_delete_alert_with_existing_owned_alert(self):
        user = models.User(id=2, username="rado21", hashed_password="1234")
        alert = models.Alert(id=1, target=22.3, direction=schemas.Direction.OVER, active=False, owner_id=2, owner=user)
        self.mock_query.first.return_value = alert

        self.db.delete_alert(alert.id, user.username)
        self.mock_query.filter.assert_called_once()
        self.mock_query.first.assert_called_once()
        self.mock_session.query.assert_called_once_with(models.Alert)
        self.mock_session.delete.assert_called_once_with(alert)
        self.mock_session.commit.assert_called_once()

    def test_delete_alert_with_existing_not_owned_alert(self):
        user = models.User(id=2, username="rado21", hashed_password="1234")
        alert = models.Alert(id=1, target=22.3, direction=schemas.Direction.OVER, active=False, owner_id=2, owner=user)
        self.mock_query.first.return_value = alert

        self.assertRaises(exceptions.AlertNotOwnedError, self.db.delete_alert, alert.id, "not_rado21")
        self.mock_query.filter.assert_called_once()
        self.mock_query.first.assert_called_once()
        self.mock_session.query.assert_called_once_with(models.Alert)
        self.mock_session.commit.assert_not_called()
        self.mock_session.delete.assert_not_called()

    def test_delete_alert_with_not_existing_alert(self):
        self.mock_query.first.return_value = None

        self.assertRaises(exceptions.AlertNotFoundError, self.db.delete_alert, 123, "rado21")
        self.mock_query.filter.assert_called_once()
        self.mock_query.first.assert_called_once()
        self.mock_session.query.assert_called_once_with(models.Alert)
        self.mock_session.commit.assert_not_called()
        self.mock_session.delete.assert_not_called()

    def test_add_sensor_data(self):
        sensor_data = schemas.SensorDataCreate(temperature=22.1, humidity=88.5)
        db_sensor_data = self.db.add_sensor_data(sensor_data)

        self.assertEqual(sensor_data.humidity, db_sensor_data.humidity)
        self.assertEqual(sensor_data.temperature, db_sensor_data.temperature)
        self.mock_session.add.assert_called_once_with(db_sensor_data)
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once_with(db_sensor_data)

    def test_get_sensor_data(self):
        sensor_data = [
            models.SensorData(id=1, timestamp=datetime.datetime.utcnow(), temperature=24.5, humidity=99.5)
        ]
        self.mock_query.all.return_value = sensor_data

        self.assertEqual(sensor_data, self.db.get_sensor_data(util.Period.DAY))
        self.mock_query.filter.assert_called_once()
        self.mock_query.all.assert_called_once()
        self.mock_session.query.assert_called_once_with(models.SensorData)

    def test_del(self):
        self.db.__del__()
        self.mock_session.close.assert_called_once()
