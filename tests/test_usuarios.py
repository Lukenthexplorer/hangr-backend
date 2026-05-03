from bson import ObjectId
from werkzeug.security import generate_password_hash

USER_ID = str(ObjectId())


def make_user(email='joao@test.com', senha='senha123'):
    return {
        '_id': ObjectId(USER_ID),
        'nome': 'João Teste',
        'email': email,
        'cidade': 'São Paulo',
        'avatar_url': '',
        'senha_hash': generate_password_hash(senha),
        'ativo': True,
    }


class TestCriarUsuario:
    def test_sucesso(self, client):
        c, db = client
        db.usuarios.find_one.return_value = None
        db.usuarios.insert_one.return_value.inserted_id = ObjectId(USER_ID)

        resp = c.post('/usuarios', json={
            'nome': 'João Teste',
            'email': 'joao@test.com',
            'senha': 'senha123',
        })

        assert resp.status_code == 201
        data = resp.get_json()
        assert 'usuario' in data
        assert data['usuario']['email'] == 'joao@test.com'
        assert 'senha_hash' not in data['usuario']

    def test_campos_faltando(self, client):
        c, db = client
        resp = c.post('/usuarios', json={'nome': 'João'})
        assert resp.status_code == 400

    def test_senha_curta(self, client):
        c, db = client
        db.usuarios.find_one.return_value = None
        resp = c.post('/usuarios', json={
            'nome': 'João', 'email': 'j@test.com', 'senha': '123',
        })
        assert resp.status_code == 400

    def test_email_duplicado(self, client):
        c, db = client
        db.usuarios.find_one.return_value = make_user()
        resp = c.post('/usuarios', json={
            'nome': 'João', 'email': 'joao@test.com', 'senha': 'senha123',
        })
        assert resp.status_code == 409

    def test_json_invalido(self, client):
        c, db = client
        resp = c.post('/usuarios', data='não é json', content_type='text/plain')
        assert resp.status_code in (400, 415)


class TestLogin:
    def test_sucesso(self, client):
        c, db = client
        db.usuarios.find_one.return_value = make_user('joao@test.com', 'senha123')

        resp = c.post('/login', json={'email': 'joao@test.com', 'senha': 'senha123'})

        assert resp.status_code == 200
        assert 'usuario' in resp.get_json()

    def test_senha_errada(self, client):
        c, db = client
        db.usuarios.find_one.return_value = make_user('joao@test.com', 'correta')

        resp = c.post('/login', json={'email': 'joao@test.com', 'senha': 'errada'})
        assert resp.status_code == 401

    def test_usuario_nao_existe(self, client):
        c, db = client
        db.usuarios.find_one.return_value = None

        resp = c.post('/login', json={'email': 'naoexiste@test.com', 'senha': 'senha123'})
        assert resp.status_code == 401

    def test_campos_faltando(self, client):
        c, db = client
        resp = c.post('/login', json={'email': 'joao@test.com'})
        assert resp.status_code == 400


class TestListarUsuarios:
    def test_retorna_lista(self, client):
        c, db = client
        db.usuarios.find.return_value = [make_user()]

        resp = c.get('/usuarios')

        assert resp.status_code == 200
        data = resp.get_json()
        assert 'usuarios' in data
        assert data['total'] == 1


class TestAtualizarUsuario:
    def test_sucesso(self, client):
        c, db = client
        usuario_atualizado = make_user()
        usuario_atualizado['nome'] = 'Nome Novo'
        db.usuarios.find_one_and_update.return_value = usuario_atualizado

        resp = c.patch(f'/usuarios/{USER_ID}', json={'nome': 'Nome Novo'})

        assert resp.status_code == 200
        assert resp.get_json()['usuario']['nome'] == 'Nome Novo'

    def test_campo_invalido_ignorado(self, client):
        c, db = client
        resp = c.patch(f'/usuarios/{USER_ID}', json={'senha_hash': 'hack'})
        assert resp.status_code == 400
