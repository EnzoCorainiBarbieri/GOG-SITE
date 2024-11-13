# Loja de Jogos com Flask

Este projeto é uma aplicação web desenvolvida em Flask que simula uma loja de jogos. Ele permite listar jogos da Steam, adicionar jogos ao carrinho, finalizar compras, além de oferecer funcionalidades de login, cadastro e perfil de usuário.

> **Atenção**: Este site utiliza a API da Steam para obter informações sobre os jogos. **Se você estiver acessando na rede da Unimax, o site pode não funcionar devido ao bloqueio de acesso à API da Steam.**

Para acessar o link da pagina no render: https://go-site-3j5p.onrender.com

# funcionalidades

### -PAGINA SEM LOGIN / INDEX

Quando o usuario entrar no link do site , e não tiver feito o login, ainda poderá vizualizar os jogos disponiveis, bem como valores e descrição, caso o usuario tente clicar em adicionar ao carrinho ele vai ser encaminhado para tela de login/cadastro.

Nesta tela possuimos tambem o botao no canto direito superior para efetuar login ou se cadastrar.

#### Vídeo de Demonstração

Assista ao vídeo no YouTube: [Clique aqui](https://www.youtube.com/watch?v=vk0w5Lr_gq4)

### -CADASTRO 

O usuario insere os dados de email, usuario e senha para se cadastrar no banco de dados. ( a senha é criptografada ) .

#### Vídeo de Demonstração

Assista ao vídeo no YouTube: [Clique aqui](https://www.youtube.com/watch?v=AiGVzFU72MU)

### -LOGIN 

Apos realizar o cadastro ou ja possuindo o cadastro realizado anteriormente, o usuario insere o email e a senha para logar na sua area de compras.

#### Vídeo de Demonstração

Assista ao vídeo no YouTube: [Clique aqui](https://www.youtube.com/watch?v=7KbS8-nTI6I)

### -Detalhes 

Ao clicar em cima de uma opção de jogo, voce vai ser levado para uma nova guia que tem as informacoes do jogo que foi selecionado e tambem é possivel adicionar ao carrinho estando nesta guia

#### Vídeo de Demonstração

Assista ao vídeo no YouTube: [Clique aqui](https://www.youtube.com/watch?v=FI2tRCNGREI)

### -Adicionar no carrinho 

O usuario pode selecionar quantos jogos quiser ao carrinho que ficara visivel a quantidade no icone de carrinho no canto superior direito, o icone tambem é um botão que leva a aba de carrinho de compras onde é possivel finalizar a venda.

#### Vídeo de Demonstração

Assista ao vídeo no YouTube: [Clique aqui](https://www.youtube.com/watch?v=B6j67yAOxTs)

### -Finalizar compra 

Na guia do carrinho é possivel ver o botao de finalizar compra, que é acompanhado pelo valor total da compra e descrição dos itens. é possivel remover os itens do carrinho antes de finalizar a compra.

#### Vídeo de Demonstração

Assista ao vídeo no YouTube: [Clique aqui](https://www.youtube.com/watch?v=CyAEAvGaF7k)

### -Perfil

Nesta guia é possivel visualizar o nome e email do usuario seguido das ultimas compras com o nome dos jogos e a sua descrição / valores. A mesma é acessivel pelo icone de perfil localizado na barra de navegação.

#### Vídeo de Demonstração

Assista ao vídeo no YouTube: [Clique aqui](https://www.youtube.com/watch?v=zHvQGo_26DE)

### -Cancelar pedido 

Continuando na guia perfil, podemos ver um botao de cancelar pedido , que ao clicar ele exclui a compra do perfil do usuario.

#### Vídeo de Demonstração

Assista ao vídeo no YouTube: [Clique aqui](https://www.youtube.com/watch?v=QyEtrh10qbY)


### -Aba de suporte 
Ao efetuar o login é possivel ver um link para a aba de suporte na barra de navegação , onde leva o usuario para um FAQ de perguntas frequentes e um formulario para entrar em contato com a GOG.

# contribuição
### Participantes 
[Gabriel Sanches Dolenc| RA: 52319298]

[Vitor Hideki Sugawara | RA: 52318621]

[Guilherme Nicchio | RA: 52318847]

[Pedro Fernandes | RA: 52318964]

[Guilherme Henrique | RA: 52318495]

[Enzo C. Barbieri  | RA: 52318316]

# Estrutura do codigo
app.py              # Arquivo principal da aplicação Flask

templates/          # Diretório contendo os templates HTML

static/             # Diretório para arquivos estáticos (CSS, JS, imagens)

requirements.txt    # Lista de dependências para instalação

README.md           # Documentação do projeto

## Tecnologias Utilizadas

- **Flask**: Framework web para o backend.
- **SQLAlchemy**: ORM para interagir com o banco de dados SQLite.
- **Bootstrap**: Framework CSS para design responsivo.
- **API da Steam**: Para obter informações sobre os jogos.
- **Flask-Caching**: Para cache das páginas e melhorar o desempenho.
- **Werkzeug**: Para hash de senhas, garantindo a segurança dos dados dos usuários.


# Principais Rotas e Funcionalidades

@app.route('/')
Exibe a lista de jogos obtida da API da Steam.
Permite pesquisa de jogos pelo título.

@app.route('/jogo/<int:jogo_id>')
Mostra detalhes de um jogo específico (descrição, imagem, desenvolvedor, publicador, etc.).

@app.route('/login', methods=['GET', 'POST'])
Permite que usuários façam login com e-mail e senha.

@app.route('/cadastro', methods=['GET', 'POST'])
Permite o cadastro de novos usuários com nome, e-mail e senha.

@app.route('/perfil')
Mostra o perfil do usuário logado e histórico de compras.

@app.route('/carrinho')
Exibe os jogos adicionados ao carrinho e o valor total.

@app.route('/finalizar_compra', methods=['POST'])
Finaliza a compra dos jogos no carrinho, registrando no banco de dados.

@app.route('/adicionar_ao_carrinho/<int:jogo_id>', methods=['POST'])
Adiciona um jogo ao carrinho do usuário logado.

@app.route('/remover_do_carrinho/<int:jogo_id>', methods=['POST'])
Remove um jogo do carrinho.
