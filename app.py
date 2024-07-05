from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import pandas as pd
from io import BytesIO
import os
from flask_mail import Mail, Message
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configurações do Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'bertinmarquez84@gmail.com'
app.config['MAIL_PASSWORD'] = 'odti nden wqjz uipd'
app.config['MAIL_DEFAULT_SENDER'] = 'bertinmarquez84@gmail.com'

mail = Mail(app)

def enviar_email(recipient, directory, file_content):
    try:
        msg = Message("Relatório de Vendas", recipients=[recipient], bcc=['bertinmarquez84@gmail.com'])
        msg.body = "Segue em anexo o relatório de vendas."
        msg.attach("Relatorio_Vendas.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", file_content)
        mail.send(msg)
        return True
    except Exception as e:
        print(f'Erro ao enviar o email: {str(e)}')
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        codigo_venda = request.form.getlist('codigo_venda')
        data = [request.form.get('data')] * len(codigo_venda)
        id_loja = request.form.getlist('id_loja')
        produto = request.form.getlist('produto')
        quantidade = request.form.getlist('quantidade')
        valor_unitario = request.form.getlist('valor_unitario')

        data_formatada = [datetime.strptime(d, '%Y-%m-%d').strftime('%d/%m/%Y') for d in data]

        data_dict = {
            'Código Venda': codigo_venda,
            'Data': data_formatada,
            'ID Loja': id_loja,
            'Produto': produto,
            'Quantidade': quantidade,
            'Valor Unitário': valor_unitario,
        }

        tabela_vendas = pd.DataFrame(data_dict)

        tabela_vendas['Quantidade'] = pd.to_numeric(tabela_vendas['Quantidade'], errors='coerce').fillna(0).astype(int)
        tabela_vendas['Valor Unitário'] = pd.to_numeric(tabela_vendas['Valor Unitário'], errors='coerce').fillna(0).astype(float)
        tabela_vendas['Valor Final'] = tabela_vendas['Quantidade'] * tabela_vendas['Valor Unitário']

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            tabela_vendas.to_excel(writer, sheet_name='Vendas', index=False)
        output.seek(0)

        directory = request.form.get('directory', './')
        file_path = os.path.join(directory, 'Relatorio_Vendas.xlsx')
        with open(file_path, 'wb') as f:
            f.write(output.getbuffer())

        recipient = request.form.get('email', 'bertinmarquez84@gmail.com')
        enviado = enviar_email(recipient, directory, output.getvalue())
        if enviado:
            flash('Relatório gerado e enviado por email com sucesso!')
        else:
            flash('Relatório gerado, mas ocorreu um erro ao enviar o email.')

    except Exception as e:
        flash(f'Erro ao processar o pedido: {str(e)}')

    return redirect(url_for('index'))

@app.route('/save', methods=['POST'])
def save_file():
    try:
        data = request.json['data']
        directory = request.json['directory']

        tabela_vendas = pd.DataFrame(data)

        tabela_vendas['Quantidade'] = pd.to_numeric(tabela_vendas['Quantidade'], errors='coerce').fillna(0).astype(int)
        tabela_vendas['Valor Unitário'] = pd.to_numeric(tabela_vendas['Valor Unitário'], errors='coerce').fillna(0).astype(float)
        tabela_vendas['Valor Final'] = tabela_vendas['Quantidade'] * tabela_vendas['Valor Unitário']

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            tabela_vendas.to_excel(writer, sheet_name='Vendas', index=False)
        output.seek(0)

        file_path = os.path.join(directory, 'Relatorio_Vendas.xlsx')
        with open(file_path, 'wb') as f:
            f.write(output.getbuffer())

        return jsonify({'message': 'Arquivo salvo com sucesso!'}), 200
    except Exception as e:
        print(f'Erro ao salvar o arquivo: {str(e)}')
        return jsonify({'message': f'Erro ao salvar o arquivo: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
