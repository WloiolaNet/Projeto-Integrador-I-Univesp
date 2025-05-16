from django.test import TestCase
from django.contrib.auth.models import User, Group

class GrupoTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.grupo = Group.objects.create(name="Test Group")

    def test_grupo_criado(self):
        self.assertEqual(self.grupo.name, "Test Group")
