from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)

app.secret_key= 'chave_super_secreta'

# Configurando o banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meubanco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Criando o banco de dados
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(100), nullable=False)
    tipo_usuario = db.Column(db.String(50), nullable= False)

    def __repr__(self):
        return f'<Usuario {self.nome}>'


class Beneficiario(db.Model):
    id= db.Column(db.Integer, primary_key= True)
    nome= db.Column(db.String(100), nullable= False)
    matricula= db.Column(db.String(100), nullable= False, unique= True)
    data_entrada= db.Column(db.DateTime, nullable= False)
    status= db.Column(db.String(30), nullable= False)

    def __repr__(self):
        return f'<Beneficiario{self.nome}>'


class Autorizacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Um número que identifica cada autorização
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # Qual usuário fez a autorização (chave estrangeira)
    matricula = db.Column(db.String(100), db.ForeignKey('beneficiario.matricula'), nullable=False)  # Qual beneficiário recebeu a autorização (chave estrangeira)
    data_autorizacao = db.Column(db.DateTime, nullable=False)  # Data da autorização
    status = db.Column(db.String(50), nullable=False)  # Status da autorização (por exemplo, aprovada ou negada)
    senha= db.Column(db.String(20), nullable=True)
    cod_procedimento= db.Column(db.String(20), nullable=False)
    nome_procedimento= db.Column(db.String(50), nullable=False)
    nome_local= db.Column(db.String(50), nullable= False)
    nome_atendente= db.Column(db.String(50), nullable= False)
    
    beneficiario = db.relationship('Beneficiario', backref='autorizacoes')  # Relacionamento com o beneficiário

    def __repr__(self):
        return f'<Autorizacao {self.id}, Beneficiario {self.matricula_beneficiario}>'


# Criando o banco de dados e as tabelas
with app.app_context():
    db.create_all()


    ###rotas
@app.route('/')
def index():
    return redirect(url_for('login'))

#rotas de exibição    
@app.route('/exibe')
def exibir():
    usuarios = Usuario.query.all()
    return str([f'nome: {user.nome}, email: {user.email}, tipo_usuario{user.tipo_usuario}' for user in usuarios])

@app.route('/exibir_benef')
def exibe():
    beneficiarios= Beneficiario.query.all()
    return str([f'nome: {user.nome}, matricula{user.matricula}, data_entrada:{user.data_entrada}, status:{user.status}'for user in beneficiarios])

@app.route('/aut_show')
def show():
    autorizacoes= Autorizacao.query.all()
    return str([
        f'Matrícula: {autorizacao.matricula}, Data da Autorização: {autorizacao.data_autorizacao}, '
        f'Status: {autorizacao.status}, Senha: {autorizacao.senha}, Código do Procedimento: {autorizacao.cod_procedimento}, '
        f'Nome do Procedimento: {autorizacao.nome_procedimento}, Local: {autorizacao.nome_local}, '
        f'Atendente: {autorizacao.nome_atendente}' 
        for autorizacao in autorizacoes
    ])

#rotas de cadastro
@app.route('/cadastra', methods= ['GET', 'POST'])
def cadastrar():
    if request.method == "POST":
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo_usuario= request.form['tipo_usuario']

        novo_usr = Usuario(nome=nome, email=email, senha=senha, tipo_usuario= tipo_usuario)
        db.session.add(novo_usr)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/cadastro_beneficiario', methods= ['GET','POST'])
def cadastrar_benef():
    if request.method == 'POST':
        nome= request.form['nome']
        matricula= request.form['matricula']
        data_entrada_str= request.form['data_entrada']
        status= request.form['status']

        #converter a dara para string
        data_entrada= datetime.strptime(data_entrada_str,'%Y-%m-%d').date()

        novo_beneficiario= Beneficiario(nome= nome, matricula= matricula, data_entrada=data_entrada, status= status)

        db.session.add(novo_beneficiario)
        db.session.commit()

        return redirect(url_for('autoriza_loc'))

    return render_template('cadastro_beneficiarios.html')


# login.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email= request.form.get('email')
        senha= request.form.get('senha')

        
        if not email or not senha:
            return 'campos não preenchidos'
        usuario= Usuario.query.filter_by(email=email).first()

        if usuario:
            if usuario.senha == senha:
                session['usuario_id'] = usuario.id
                session['nome_usuario']= usuario.nome
                session['tipo_usuario']= usuario.tipo_usuario
                
                if usuario.tipo_usuario == 'Credenciado':
                    return redirect(url_for('autoriza'))
                
                elif usuario.tipo_usuario == 'Autorizador':
                    return redirect(url_for('autoriza_loc'))
                
                elif usuario.tipo_usuario == 'Amacor':
                    return redirect(url_for('autoriza'))
                else:
                    return 'Tipo de Usuario não reconhecido'
                
            else:
                return 'senha inválida'
            
        else:
            return 'usuario não encontrado'
    
    return render_template('login.html')


#paginas de inicio
@app.route('/autoriza')
def autoriza(): 
    nome_usuario= session.get('nome_usuario')
    tipo_usuario= session.get('tipo_usuario')

    if nome_usuario:
        return render_template('autoriza.html', nome= nome_usuario, tipo= tipo_usuario)
    
    else:
        return redirect(url_for('login'))

@app.route('/autoriza_loc', methods= ['GET','POST'])
def autoriza_loc():
    nome_usuario= session.get('nome_usuario')
    tipo_usuario= session.get('tipo_usuario')

    if nome_usuario:
        return render_template('autoriza_loc.html', nome= nome_usuario, tipo= tipo_usuario)
    else:
        return redirect(url_for('login'))


#criando autorização.
@app.route('/cria_aut', methods= ['POST', 'GET'])
def cria_aut():

    usuario_id= session.get('usuario_id')
    nome_usuario= session.get('nome_usuario')
    
    if usuario_id == None:
        return redirect(url_for('login'))

    if request.method == 'POST':
        senha = request.form.get('senha')
        matricula = request.form.get('matricula')
        data_autorizacao_str = request.form.get('data_autorizacao')
        status = request.form.get('status')
        cod_procedimento = request.form.get('cod_procedimento')
        nome_procedimento = request.form.get('nome_procedimento')
        nome_local = request.form.get('nome_local')
        nome_atendente = request.form.get('nome_atendente')


        #converter a data para str
        data_autorizacao= None

        if data_autorizacao_str:
            try:
                data_autorizacao = datetime.strptime(data_autorizacao_str, '%Y-%m-%d').date()
            except ValueError:
                return "Erro: Formato de data invalido."        


        nova_autorizacao = Autorizacao(
            usuario_id=usuario_id,
            matricula=matricula,
            senha=senha,
            data_autorizacao=data_autorizacao,
            status=status,
            cod_procedimento=cod_procedimento,
            nome_procedimento=nome_procedimento,
            nome_local=nome_local,
            nome_atendente=nome_atendente
        )
        db.session.add(nova_autorizacao)
        db.session.commit()
        


    return render_template('cria_aut.html', nome= nome_usuario)

@app.route('/valida_aut')
def valida_aut():
    autorizacoes= Autorizacao.query.all()

    return render_template('valida_aut.html', autorizacoes=autorizacoes)

if __name__ == '__main__':
    app.run(debug=True)
    