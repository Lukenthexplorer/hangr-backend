class TestCategorias:
    def test_retorna_lista(self, client):
        c, db = client
        db.categorias.find.return_value.sort.return_value = [
            {'slug': 'restaurantes', 'nome': 'Restaurantes', 'emoji': '🍽️', 'ordem': 1},
            {'slug': 'bares', 'nome': 'Bares', 'emoji': '🍺', 'ordem': 2},
        ]

        resp = c.get('/categorias')

        assert resp.status_code == 200
        data = resp.get_json()
        assert 'categorias' in data
        assert len(data['categorias']) == 2
        assert data['categorias'][0]['slug'] == 'restaurantes'

    def test_lista_vazia(self, client):
        c, db = client
        db.categorias.find.return_value.sort.return_value = []

        resp = c.get('/categorias')

        assert resp.status_code == 200
        assert resp.get_json()['categorias'] == []


class TestConfiguracoes:
    def test_retorna_configuracoes(self, client):
        c, db = client
        db.configuracoes.find.return_value = [
            {'chave': 'gps_threshold', 'valor': 500},
            {'chave': 'timer_default', 'valor': 60},
        ]

        resp = c.get('/configuracoes')

        assert resp.status_code == 200
        data = resp.get_json()
        assert 'configuracoes' in data
        assert data['configuracoes']['gps_threshold'] == 500
        assert data['configuracoes']['timer_default'] == 60

    def test_sem_configuracoes(self, client):
        c, db = client
        db.configuracoes.find.return_value = []

        resp = c.get('/configuracoes')

        assert resp.status_code == 200
        assert resp.get_json()['configuracoes'] == {}
