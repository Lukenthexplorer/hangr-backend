from bson import ObjectId

PARTY_ID = str(ObjectId())
USER_ID = str(ObjectId())


def make_party(codigo='ABC123'):
    return {
        '_id': ObjectId(PARTY_ID),
        'titulo': 'Party Teste',
        'criada_por': USER_ID,
        'cidade': 'São Paulo',
        'status': 'aberta',
        'codigo_convite': codigo,
        'criada_em': None,
        'ativa': True,
        'membros': [],
        'votes': [],
    }


class TestCriarParty:
    def test_sucesso(self, client):
        c, db = client
        db.parties.insert_one.return_value.inserted_id = ObjectId(PARTY_ID)

        resp = c.post('/parties', json={
            'titulo': 'Rolê de sexta',
            'criada_por': USER_ID,
            'cidade': 'São Paulo',
            'codigo_convite': 'ABC123',
        })

        assert resp.status_code == 201
        data = resp.get_json()
        assert data['party']['titulo'] == 'Rolê de sexta'
        assert data['party']['cidade'] == 'São Paulo'

    def test_campos_faltando(self, client):
        c, db = client
        resp = c.post('/parties', json={'titulo': 'Só o título'})
        assert resp.status_code == 400

    def test_json_invalido(self, client):
        c, db = client
        resp = c.post('/parties', data='nao eh json', content_type='text/plain')
        assert resp.status_code in (400, 415)


class TestGetParty:
    def test_encontrada(self, client):
        c, db = client
        db.parties.find_one.return_value = make_party('XYZ999')

        resp = c.get('/parties/XYZ999')

        assert resp.status_code == 200
        assert resp.get_json()['party']['codigo_convite'] == 'XYZ999'

    def test_nao_encontrada(self, client):
        c, db = client
        db.parties.find_one.return_value = None

        resp = c.get('/parties/NOTEXIST')
        assert resp.status_code == 404

    def test_codigo_convertido_para_maiusculo(self, client):
        c, db = client
        db.parties.find_one.return_value = make_party('ABC123')

        resp = c.get('/parties/abc123')
        assert resp.status_code == 200


class TestListarParties:
    def test_retorna_lista_com_usuario_id(self, client):
        c, db = client
        db.parties.find.return_value.sort.return_value.limit.return_value = [make_party()]

        resp = c.get(f'/parties?usuario_id={USER_ID}')

        assert resp.status_code == 200
        data = resp.get_json()
        assert 'parties' in data
        assert len(data['parties']) == 1

    def test_retorna_lista_vazia(self, client):
        c, db = client
        db.parties.find.return_value.sort.return_value.limit.return_value = []

        resp = c.get('/parties')
        assert resp.status_code == 200
        assert resp.get_json()['parties'] == []


class TestAdicionarMembro:
    def test_sucesso(self, client):
        c, db = client
        db.parties.find_one.return_value = make_party('ABC123')
        db.usuarios.find_one.return_value = {'_id': ObjectId(USER_ID), 'nome': 'João'}
        db.parties.update_one.return_value.modified_count = 1

        resp = c.post('/parties/ABC123/membros', json={'usuario_id': USER_ID})
        assert resp.status_code == 201

    def test_party_nao_encontrada(self, client):
        c, db = client
        db.parties.find_one.return_value = None

        resp = c.post('/parties/NAOEXISTE/membros', json={'usuario_id': USER_ID})
        assert resp.status_code == 404

    def test_sem_usuario_id(self, client):
        c, db = client
        resp = c.post('/parties/ABC123/membros', json={})
        assert resp.status_code == 400
