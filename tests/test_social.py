from bson import ObjectId

USER_A = str(ObjectId())
USER_B = str(ObjectId())


class TestSeguir:
    def test_sucesso(self, client):
        c, db = client
        db.usuarios.find_one.return_value = {'_id': ObjectId(USER_B), 'nome': 'Maria'}
        db.follows.find_one.return_value = None

        resp = c.post('/seguir', json={'seguidor_id': USER_A, 'seguido_id': USER_B})

        assert resp.status_code == 201
        assert resp.get_json()['mensagem'] == 'Seguindo'

    def test_seguir_a_si_mesmo(self, client):
        c, db = client
        resp = c.post('/seguir', json={'seguidor_id': USER_A, 'seguido_id': USER_A})
        assert resp.status_code == 400

    def test_ja_segue(self, client):
        c, db = client
        db.usuarios.find_one.return_value = {'_id': ObjectId(USER_B)}
        db.follows.find_one.return_value = {'seguidor_id': USER_A, 'seguido_id': USER_B}

        resp = c.post('/seguir', json={'seguidor_id': USER_A, 'seguido_id': USER_B})
        assert resp.status_code == 200

    def test_campos_faltando(self, client):
        c, db = client
        resp = c.post('/seguir', json={'seguidor_id': USER_A})
        assert resp.status_code == 400

    def test_usuario_nao_existe(self, client):
        c, db = client
        db.usuarios.find_one.return_value = None

        resp = c.post('/seguir', json={'seguidor_id': USER_A, 'seguido_id': USER_B})
        assert resp.status_code == 404


class TestDeixarDeSeguir:
    def test_sucesso(self, client):
        c, db = client
        resp = c.delete(f'/seguir?seguidor_id={USER_A}&seguido_id={USER_B}')
        assert resp.status_code == 200

    def test_campos_faltando(self, client):
        c, db = client
        resp = c.delete(f'/seguir?seguidor_id={USER_A}')
        assert resp.status_code == 400


class TestBuscarUsuarios:
    def test_query_curta_retorna_vazio(self, client):
        c, db = client
        resp = c.get('/usuarios/buscar?q=a')
        assert resp.status_code == 200
        assert resp.get_json()['usuarios'] == []

    def test_encontra_usuarios(self, client):
        c, db = client
        db.usuarios.find.return_value.limit.return_value = [
            {'_id': ObjectId(USER_B), 'nome': 'João', 'cidade': 'SP'},
        ]
        db.follows.find.return_value = []

        resp = c.get(f'/usuarios/buscar?q=Jo&usuario_id={USER_A}')

        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['usuarios']) == 1
        assert data['usuarios'][0]['nome'] == 'João'
        assert data['usuarios'][0]['seguindo'] is False

    def test_marca_seguindo(self, client):
        c, db = client
        db.usuarios.find.return_value.limit.return_value = [
            {'_id': ObjectId(USER_B), 'nome': 'Maria', 'cidade': 'RJ'},
        ]
        db.follows.find.return_value = [{'seguido_id': USER_B}]

        resp = c.get(f'/usuarios/buscar?q=Ma&usuario_id={USER_A}')

        assert resp.status_code == 200
        assert resp.get_json()['usuarios'][0]['seguindo'] is True


class TestFeed:
    def test_retorna_feed_vazio(self, client):
        c, db = client
        db.follows.find.return_value = []
        db.parties.find.return_value.sort.return_value.limit.return_value = []

        resp = c.get(f'/feed?usuario_id={USER_A}')

        assert resp.status_code == 200
        assert resp.get_json()['feed'] == []

    def test_sem_usuario_id(self, client):
        c, db = client
        resp = c.get('/feed')
        assert resp.status_code == 400
