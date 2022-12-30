from unittest import TestCase
from unittest.mock import patch
from db import models
from api import get_current_user, authenticate_user
from fastapi import HTTPException
from jose import JWTError


class TestInit(TestCase):

    @patch("api.Database")
    def setUp(self, mock_db):
        self.mock_db = mock_db

    @patch("api.get_username_from_token")
    def test_get_current_user(self, mock_get_username_from_token):
        token = "token"
        username = "rado21"
        user = models.User(id=2, username=username, hashed_password="1234")
        mock_get_username_from_token.return_value = username
        self.mock_db.get_user_by_username.return_value = user

        actual = get_current_user(self.mock_db, token)

        self.assertEqual(actual, user)
        mock_get_username_from_token.assert_called_once_with(token)
        self.mock_db.get_user_by_username.assert_called_once_with(username=username)

    @patch("api.get_username_from_token")
    def test_get_current_user_with_no_username_from_token(self, mock_get_username_from_token):
        token = "token"
        mock_get_username_from_token.return_value = None

        self.assertRaises(HTTPException, get_current_user, self.mock_db, token)
        mock_get_username_from_token.assert_called_once_with(token)

    @patch("api.get_username_from_token")
    def test_get_current_user_with_JWTError(self, mock_get_username_from_token):
        token = "token"
        mock_get_username_from_token.side_effect = JWTError()

        self.assertRaises(HTTPException, get_current_user, self.mock_db, token)
        mock_get_username_from_token.assert_called_once_with(token)

    @patch("api.get_username_from_token")
    def test_get_current_user_with_no_matching_user(self, mock_get_username_from_token):
        token = "token"
        username = "rado21"
        mock_get_username_from_token.return_value = username
        self.mock_db.get_user_by_username.return_value = None

        self.assertRaises(HTTPException, get_current_user, self.mock_db, token)
        mock_get_username_from_token.assert_called_once_with(token)
        self.mock_db.get_user_by_username.assert_called_once_with(username=username)

    @patch("api.verify_password")
    def test_authenticate_user(self, mock_verify_password):
        username = "rado21"
        password = "1234"
        user = models.User(id=2, username=username, hashed_password="abcd")
        self.mock_db.get_user_by_username.return_value = user
        mock_verify_password.return_value = True

        self.assertEqual(user, authenticate_user(self.mock_db, username, password))
        self.mock_db.get_user_by_username.assert_called_once_with(username=username)
        mock_verify_password.assert_called_once_with(password, user.hashed_password)

    @patch("api.verify_password")
    def test_authenticate_user_with_not_existing_user(self, mock_verify_password):
        username = "rado21"
        password = "1234"
        self.mock_db.get_user_by_username.return_value = None
        mock_verify_password.return_value = True

        self.assertEqual(None, authenticate_user(self.mock_db, username, password))
        self.mock_db.get_user_by_username.assert_called_once_with(username=username)

    @patch("api.verify_password")
    def test_authenticate_user_with_wrong_password(self, mock_verify_password):
        username = "rado21"
        password = "1234"
        user = models.User(id=2, username=username, hashed_password="abcd")
        self.mock_db.get_user_by_username.return_value = user
        mock_verify_password.return_value = False

        self.assertEqual(None, authenticate_user(self.mock_db, username, password))
        self.mock_db.get_user_by_username.assert_called_once_with(username=username)
        mock_verify_password.assert_called_once_with(password, user.hashed_password)
