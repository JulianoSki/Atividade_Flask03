
from flask import Flask, make_response
from markupsafe import escape
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask import url_for
from flask import redirect
from flask_login import (current_user,  LoginManager,
                         login_user, logout_user, login_required)
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost:3306/meubanco'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.secret_key = 'shiva00'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class Usuario(db.Model):
    __tablename__ = "usuario"
    id = db.Column('usu_id', db.Integer, primary_key=True)
    nome = db.Column('usu_nome', db.String(256))
    sobrenome = db.Column('usu_sobrenome', db.String(256))
    CPF = db.Column('usu_cpf', db.String(256))
    email = db.Column('usu_email', db.String(256))
    telefone = db.Column('usu_telefone', db.Integer)
    senha = db.Column('usu_senha', db.String(256))

    def __init__(self, nome, sobrenome, cpf, email, telefone, senha):
        self.nome = nome
        self.sobrenome = sobrenome
        self.CPF = cpf
        self.email = email
        self.telefone = telefone
        self.senha = senha

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Cliente(db.Model):
    __tablename__ = "cliente"
    id = db.Column('clie_id', db.Integer, primary_key=True)
    nome = db.Column('clie_nome', db.String(256))
    email = db.Column('clie_email', db.String(256))
    senha = db.Column('clie_senha', db.String(256))
    dp_id = db.Column('dp_id', db.Integer,
                      db.ForeignKey("dados_pessoais.dp_id"))
    end_id = db.Column('end_id', db.Integer,
                       db.ForeignKey("endereco.end_id"))
    ped_id = db.Column('ped_id', db.Integer,
                       db.ForeignKey("pedido.ped_id"))

    def __init__(self, nome, email, senha, dp_id, end_id, ped_id):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.dp_id = dp_id
        self.end_id = end_id
        self.ped_id = ped_id


class Dados_Pessoais(db.Model):
    __tablename__ = "dados_pessoais"
    id = db.Column('dp_id', db.Integer, primary_key=True)
    nome = db.Column('dp_nome', db.String(256))
    sobrenome = db.Column('dp_sobrenome', db.String(256))
    email = db.Column('dp_email', db.String(256))
    cpf = db.Column('dp_cpf', db.String(256))
    telefone = db.Column('dp_telefone', db.Integer)

    def __init__(self, nome, sobrenome, email, cpf, telefone):
        self.nome = nome
        self.sobrenome = sobrenome
        self.email = email
        self.CPF = cpf
        self.telefone = telefone


class Pedido(db.Model):
    __tablename__ = "pedido"
    id = db.Column('ped_id', db.Integer, primary_key=True)
    preco_total = db.Column('ped_preco_total', db.Float)
    frete = db.Column('ped_frete', db.Float)
    numero_pedido = db.Column('ped_numero_pedido', db.Integer)
    anu_id = db.Column('anu_id', db.Integer,
                       db.ForeignKey("anuncio.anu_id"))

    def __init__(self, preco_total, frete, numero_pedido, anu_id):
        self.preco_total = preco_total
        self.frete = frete
        self.numero_pedido = numero_pedido
        self.anu_id = anu_id


class Endereco(db.Model):
    __tablename__ = "endereco"
    id = db.Column('end_id', db.Integer, primary_key=True)
    logradouro = db.Column('end_logradouro', db.String(256))
    numero = db.Column('end_numero', db.Integer)
    cep = db.Column('end_cep', db.Integer)
    bairro = db.Column('end_bairro', db.String(256))
    cidade = db.Column('end_cidade', db.String(256))
    estado = db.Column('end_estado', db.String(256))
    complemento = db.Column('end_complemento', db.String(256))

    def __init__(self, logradouro, numero, cep, bairro, cidade, estado, complemento):
        self.logradouro = logradouro
        self.numero = numero
        self.cep = cep
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado
        self.complemento = complemento


class Anuncio(db.Model):
    __tablename__ = "anuncio"
    id = db.Column('anu_id', db.Integer, primary_key=True)
    nome = db.Column('anu_nome', db.String(256))
    desc = db.Column('anu_desc', db.String(256))
    qtd = db.Column('anu_qtd', db.Integer)
    preco = db.Column('anu_preco', db.Float)
    categoria = db.Column('anu_categoria', db.String(256))

    def __init__(self, nome, desc, qtd, preco, categoria):
        self.nome = nome
        self.desc = desc
        self.qtd = qtd
        self.preco = preco
        self.categoria = categoria


@app.route("/usuario/editar/<int:id>", methods=['GET', 'POST'])
def editarusuario(id):
    usuario = Usuario.query.get(id)
    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        usuario.sobrenome = request.form.get('sobrenome')
        usuario.cpf = request.form.get('cpf')
        usuario.telefone = request.form.get('telefone')
        usuario.email = request.form.get('email')
        usuario.senha = request.form.get('passwd')
        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for('usuario'))

    return render_template('editar_usuario.html', usuario=usuario, titulo="Usuario")


@app.route("/usuario/deletar/<int:id>")
def deletarusuario(id):
    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))


@ app.route("/")
@login_required
def home():
    return render_template("index.html")


@app.route("/cadastro/usuario")
def usuario():
    return render_template('usuario.html', usuarios=Usuario.query.all(), titulo="Usuario")


@app.route("/usuario/criar_conta", methods=['POST'])
def criar_conta():
    usuario = Usuario(request.form.get('nome'), request.form.get(
        'sobrenome'), request.form.get('cpf'), request.form.get('email'), request.form.get('telefone'), request.form.get('passwd'))
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))


@app.route("/cadastro/endereco")
@login_required
def endereco():
    return render_template('endereco.html', enderecos=Endereco.query.all(), titulo="Endereco")


@app.route("/endereco/criar_endereco", methods=['POST'])
def criar_endereco():
    endereco = Endereco(request.form.get('logradouro'), request.form.get(
        'numero'), request.form.get('cep'), request.form.get('bairro'), request.form.get('cidade'), request.form.get('estado'), request.form.get('complemento'))
    db.session.add(endereco)
    db.session.commit()
    return redirect(url_for('endereco'))


@app.route("/endereco/editar/<int:id>", methods=['GET', 'POST'])
def editarendereco(id):
    endereco = Endereco.query.get(id)
    if request.method == 'POST':
        endereco.logradouro = request.form.get('logradouro')
        endereco.numero = request.form.get('numero')
        endereco.cep = request.form.get('cep')
        endereco.bairro = request.form.get('bairro')
        endereco.cidade = request.form.get('cidade')
        endereco.estado = request.form.get('estado')
        endereco.complemento = request.form.get('complemento')
        db.session.add(endereco)
        db.session.commit()
        return redirect(url_for('endereco'))

    return render_template('editar_endereco.html', endereco=endereco, titulo="Endereco")


@app.route("/endereco/deletar/<int:id>")
def deletarendereco(id):
    endereco = Endereco.query.get(id)
    db.session.delete(endereco)
    db.session.commit()
    return redirect(url_for('endereco'))


@app.route("/cadastro/anuncio")
@login_required
def anuncio():
    return render_template('anuncio.html', anuncios=Anuncio.query.all(), titulo="Anuncio")


@app.route("/anuncio/anunciar", methods=['POST'])
def anunciar():
    anuncio = Anuncio(request.form.get('nome'), request.form.get('desc'), request.form.get(
        'qtd'), request.form.get('preco'), request.form.get('categoria'))
    db.session.add(anuncio)
    db.session.commit()
    return redirect(url_for('anuncio'))


@ app.route("/cadastro/cadastro_user", methods=["POST"])
def cadastro_user():
    return request.form


@ app.route("/perguntar/perguntas")
@login_required
def perguntas():
    return render_template("perguntas.html")


@ app.route("/perguntar/fazer_perguntas", methods=["POST"])
def fazer_perguntas():
    return request.form


@ app.route("/anuncio/comprar")
@login_required
def comprar():
    return render_template("comprar.html")


@ app.route("/anuncio/realizar_compra", methods=["POST, GET"])
def realizar_compra():
    return request.form


@ app.route("/relatorios")
def relatorios():
    return render_template("relatorios.html")


@ app.route("/relatorios/emitir_vendas", methods=["POST, GET"])
def emitir_vendas():
    return request.form


# @app.errorhandler(404)
# def pagina_erro(error):
    # return render_template('pagina_erro.html')


@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(id)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        passwd = hashlib.sha512(
            str(request.form.get('passwd')).encode("utf-8")).hexdigest()

        user = Usuario.query.filter_by(email=email, senha=passwd).first()

        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()
    db.create_all()

# py -3 -m venv .venv
# .venv\scripts\activate
# pip install mysqlclient
# pip install mysql-connector-python
# pip install pymysql
