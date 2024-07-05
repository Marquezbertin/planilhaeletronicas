import unittest
from flask import Flask
from flask_testing import TestCase
from flask_mail import Mail, Message
import pandas as pd
from io import BytesIO
import os
from datetime import datetime
import tempfile

# Importando a aplicação Flask
from app import app, enviar_email

class TestApp(TestCase):

    def create_app(self):
        # Configuração da aplicação para testes
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['MAIL_SUPPRESS_SEND'] = True  # Suprimindo o envio real de e-mails durante os testes
        return app

    def setUp(self):
        # Configuração inicial antes de cada teste
        self.app = self.create_app().test_client()
        self.ctx = self.app.application.app_context()
        self.ctx.push()

    def tearDown(self):
        # Limpeza após cada teste
        self.ctx.pop()

    def test_registro_nova_venda(self):
        # Teste de registro de nova venda
        data = {
            'codigo_venda': '001',
            'data': '2024-07-05',
            'id_loja': 'A001',
            'produto': 'Produto Teste',
            'quantidade': '10',
            'valor_unitario': '50.0'
        }
        response = self.app.post('/upload', data=data)
        self.assert_redirects(response, '/')

    def test_edicao_venda_registrada(self):
        # Teste de edição de venda registrada
        data = {
            'codigo_venda': '002',
            'data': '2024-07-05',
            'id_loja': 'A002',
            'produto': 'Produto Teste 2',
            'quantidade': '5',
            'valor_unitario': '25.0'
        }
        # Primeiro, registra uma nova venda
        self.app.post('/upload', data=data)
        # Depois, edita a venda registrada
        data_editada = {
            'codigo_venda': '002',
            'data': '2024-07-05',
            'id_loja': 'A002',
            'produto': 'Produto Editado',
            'quantidade': '8',
            'valor_unitario': '30.0'
        }
        response = self.app.post('/upload', data=data_editada)
        self.assert_redirects(response, '/')

    def test_exclusao_venda_registrada(self):
        # Teste de exclusão de venda registrada
        data = {
            'codigo_venda': '003',
            'data': '2024-07-05',
            'id_loja': 'A003',
            'produto': 'Produto Teste 3',
            'quantidade': '3',
            'valor_unitario': '15.0'
        }
        # Primeiro, registra uma nova venda
        self.app.post('/upload', data=data)
        # Depois, exclui a venda registrada
        response = self.app.post('/delete/003')
        self.assert_redirects(response, '/')

    def test_validacao_quantidade_produtos(self):
        # Teste de validação de quantidade de produtos
        data_invalida = {
            'codigo_venda': '004',
            'data': '2024-07-05',
            'id_loja': 'A004',
            'produto': 'Produto Teste 4',
            'quantidade': 'texto_invalido',
            'valor_unitario': '20.0'
        }
        response = self.app.post('/upload', data=data_invalida)
        self.assertIn(b'Quantidade deve ser um número inteiro.', response.data)

    def test_validacao_valor_unitario_produtos(self):
        # Teste de validação de valor unitário dos produtos
        data_invalida = {
            'codigo_venda': '005',
            'data': '2024-07-05',
            'id_loja': 'A005',
            'produto': 'Produto Teste 5',
            'quantidade': '2',
            'valor_unitario': 'texto_invalido'
        }
        response = self.app.post('/upload', data=data_invalida)
        self.assertIn(b'Valor Unitário deve ser um número válido.', response.data)

    def test_geracao_envio_relatorio_email(self):
        # Teste de geração e envio de relatório por e-mail
        data = {
            'codigo_venda': '006',
            'data': '2024-07-05',
            'id_loja': 'A006',
            'produto': 'Produto Teste 6',
            'quantidade': '4',
            'valor_unitario': '30.0',
            'email': 'teste@example.com'
        }
        response = self.app.post('/upload', data=data)
        self.assertIn(b'Relatório gerado e enviado por email com sucesso!', response.data)

    def test_filtragem_vendas_por_data(self):
        # Teste de filtragem de vendas por data
        # Primeiro, registra algumas vendas
        data1 = {
            'codigo_venda': '007',
            'data': '2024-07-01',
            'id_loja': 'A007',
            'produto': 'Produto Teste 7',
            'quantidade': '2',
            'valor_unitario': '20.0'
        }
        self.app.post('/upload', data=data1)

        data2 = {
            'codigo_venda': '008',
            'data': '2024-07-05',
            'id_loja': 'A008',
            'produto': 'Produto Teste 8',
            'quantidade': '3',
            'valor_unitario': '25.0'
        }
        self.app.post('/upload', data=data2)

        data3 = {
            'codigo_venda': '009',
            'data': '2024-07-10',
            'id_loja': 'A009',
            'produto': 'Produto Teste 9',
            'quantidade': '1',
            'valor_unitario': '15.0'
        }
        self.app.post('/upload', data=data3)

        # Depois, aplica o filtro de data
        response = self.app.get('/filtrar_vendas?data_inicial=2024-07-01&data_final=2024-07-05')
        self.assertIn(b'Produto Teste 7', response.data)
        self.assertIn(b'Produto Teste 8', response.data)
        self.assertNotIn(b'Produto Teste 9', response.data)

    def test_exportacao_relatorio_pdf(self):
        # Teste de exportação de relatório para PDF
        data = {
            'codigo_venda': '010',
            'data': '2024-07-05',
            'id_loja': 'A010',
            'produto': 'Produto Teste 10',
            'quantidade': '2',
            'valor_unitario': '30.0'
        }
        self.app.post('/upload', data=data)

        response = self.app.get('/exportar_pdf')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Relatório de Vendas', response.data)
        self.assertIn(b'Produto Teste 10', response.data)

    def test_importacao_dados_vendas_arquivo_externo(self):
        # Teste de importação de dados de vendas de arquivo externo
        # Cria um arquivo CSV temporário com dados de vendas
        csv_data = 'codigo_venda,data,id_loja,produto,quantidade,valor_unitario\n' \
                   '011,2024-07-05,A011,Produto Teste 11,3,35.0\n' \
                   '012,2024-07-05,A012,Produto Teste 12,4,40.0\n'
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as csv_file:
            csv_file.write(csv_data.encode())

        # Realiza a importação dos dados do arquivo CSV
        with open(csv_file.name, 'rb') as f:
            response = self.app.post('/importar_dados', data=dict(file=(f, 'dados_vendas.csv')), content_type='multipart/form-data')

        os.remove(csv_file.name)  # Remove o arquivo CSV temporário após o teste

        self.assert_redirects(response, '/')

    def test_configuracao_email_envio_automatico(self):
        # Teste de configuração de e-mail para envio automático
        data = {
            'mail_server': 'smtp.gmail.com',
            'mail_port': '587',
            'mail_use_tls': 'True',
            'mail_use_ssl': 'False',
            'mail_username': 'seu_email@gmail.com',
            'mail_password': 'sua_senha',
            'mail_default_sender': 'seu_email@gmail.com'
        }
        response = self.app.post('/configurar_email', data=data)
        self.assert_redirects(response, '/')

if __name__ == '__main__':
    unittest.main()

