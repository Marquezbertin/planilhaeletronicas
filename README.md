# Sistema de Registro de Vendas
Este sistema foi desenvolvido para permitir o registro de vendas e a geração de relatórios em formato Excel. Ele é implementado como uma aplicação web usando Flask e Pandas para manipulação de dados, e Flask-Mail para envio opcional de relatórios por e-mail.

## Funcionalidades
* Registro de Vendas: O sistema permite que o usuário insira detalhes de vendas, incluindo código de venda, data, ID da loja, produto, quantidade e valor unitário.
* Cálculo Automático: Ao inserir a quantidade e o valor unitário, o sistema calcula automaticamente o valor total da venda.
* Adição Dinâmica de Linhas: É possível adicionar novas linhas dinamicamente para registrar múltiplas vendas em uma única sessão.
* Opções Opcionais: O usuário pode especificar um diretório para salvar o relatório gerado em formato Excel e um endereço de e-mail para enviar o relatório.
* Validação de Entrada: Validações são implementadas para garantir que os campos obrigatórios sejam preenchidos corretamente. Por exemplo, a quantidade deve ser um número inteiro e o valor unitário deve ser um número válido.
* Responsividade: O sistema é responsivo, adaptando-se a diferentes tamanhos de tela para uma melhor experiência do usuário em dispositivos móveis e desktops.

## Uso
Acesso ao Sistema:

Clone o repositório e execute a aplicação Flask.
Acesse o sistema através do navegador.

## Preenchimento do Formulário:

Preencha os detalhes da venda nos campos correspondentes.
Para adicionar mais vendas, clique no botão "Adicionar Linha".
Opções Opcionais:

Opcionalmente, informe um diretório para salvar o relatório e/ou um endereço de e-mail para enviar o relatório por e-mail.
Envio e Salvamento:

Ao clicar em "Enviar", o sistema gera um relatório em formato Excel com base nos dados inseridos.
Se especificado, o relatório também é salvo no diretório informado e enviado por e-mail.

## Requisitos
Python 3.x
Flask
Pandas
Flask-Mail
Configuração do Ambiente

Instale as dependências Python necessárias:
bash
Copiar código
pip install flask pandas Flask-Mail

Configure as variáveis de ambiente necessárias para o envio de e-mails (SMTP).

Execute a aplicação:

bash
Copiar código
python app.py

## Autor
Desenvolvido por Bruno Bertin Marquez (@Bruno Bertin Marquez) - 2024
