import sqlite3
import smtplib
import string
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

#Configuração do banco de dados
connection = sqlite3.connect("users.db")

cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL)''')


#Código para recuperar senha(gerar codigo temporário)

def generate_reset_code():
	characters = string.ascii_letters + string.digits
	return ''.join(random.choice(characters) for i in range(8))


#Código para recuperar senha(enviar email)

def send_reset_email(email, name, reset_code):
	sender_email = "" #Inserir aqui email
	sender_password = "" #Inserir aqui senha

	subject = "Recuperação de senha"
	body = (f"Olá {name}!\n"
	        f"Você solicitou a recuperação da sua senha.\n"
	        f"Use o seguinte código para redifinir sua senha: \n"
	        f"{reset_code}\n"
	        f"Caso você não tenha solicitado a recuperação de sua senha, "
	        f"peço que desconsidere esse email. 😉\n"
	        f"Um abraço!\n"
	        f"- Equipe, Heljarmyrkr. 🧙🏻‍♂️ ")

	msg = MIMEMultipart('related')
	msg['From'] = sender_email
	msg['To'] = email
	msg['Subject'] = subject
	msg.attach(MIMEText(body, 'html'))

	try:
		# Para conectar ao servidor SMTP do Gmail
		with smtplib.SMTP('smtp.gmail.com', 587) as server:
			server.starttls()
			server.login(sender_email, sender_password)
			server.send_message(msg)
			print("Email de recuperação de senha enviado! ✉️")
	except Exception as e:
		print(f"Erro ao enviar email: {e}")


def forgot_password_and_reset():
	email = input("Digite o seu email cadastrado: ")
	cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
	user = cursor.fetchone()

	if user:
		reset_code = generate_reset_code()
		cursor.execute("UPDATE users SET password = ? WHERE email = ?", (reset_code, email))
		connection.commit()
		send_reset_email(email, user[1], reset_code)
		print("Um código de redefinição de senha foi enviado para o seu email. ✅")

		entered_code = input("Digite aqui o código que recebeu no seu email: ")
		if entered_code == reset_code:
			new_password = input("Digite sua nova senha: ")
			cursor.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
			connection.commit()
			print("Sua senha foi alterada com sucesso! ✅")
		else:
			print("Código de alteração de senha inválido! ❌")

	else:
		print("Email não encontrado ❌")


#Configuração do email de boas-vindas
def send_welcome_email(email, name):
	sender_email = "" #Inserir aqui email
	sender_password = "" #Inserir aqui senha

	subject = "🌦️ Sobre seu cadastro na minha plataforma!"
	body = (f"Olá {name}!\n"
	        f"Gostaria de agradecer por realizar o cadastro "
	        f"em minha plataforma! 😊️\n"
	        f"No momento está em desenvolvimento, 💻 "
	        f"mas assim que estiver liberado, um email será "
	        f"automaticamente enviado a você! ✉️\n"
	        f"Um abraço!\n"
	        f"- Equipe, Heljarmyrkr. 🧙🏻‍♂️\n<br>"

	        '<div style="text-align: center;">'
	        '<img src="cid:image" alt="Imagem de Boas-Vindas" style="width:900px;"/>'
	        '</div>')

	msg = MIMEMultipart('related')
	msg['From'] = sender_email
	msg['To'] = email
	msg['Subject'] = subject
	msg.attach(MIMEText(body, 'html'))

	#Código para anexar a imagem

	with open('')  as img_file: #Inserir aqui caminho para a imagem
		img = MIMEImage(img_file.read())
		img.add_header('Content-ID', '<image>')
		msg.attach(img)

	try:
		#Para conectar ao servidor SMTP do Gmail
		with smtplib.SMTP('smtp.gmail.com', 587) as server:
			server.starttls()
			server.login(sender_email, sender_password)
			server.send_message(msg)

			print("Email de boas-vindas enviado! ✉️")

	except Exception as e:
		print(f"Erro ao enviar email: {e}")


#Código para registro do usuário
def register_user():
	name = input("Digite o nome de usuário: ")
	email = input("Digite o email do usuário: ")
	password = input("Digite a senha do usuário: ")

	try:
		cursor.execute("INSERT INTO users (name, email, password) "
		               "VALUES (?, ?, ?)",
		               (name, email, password))

		connection.commit()

		print("Usuário cadastrado com sucesso! ✅")

		#Para ser enviando o email de boas-vindas
		send_welcome_email(email, name)

	except sqlite3.IntegrityError:
		print("Erro: Email já foi cadastrado. ⚠️")
	except sqlite3.Error as e:
		print(f"Erro no banco de dados: {e}")


#Código para login do usuário
def login():
	email = input("Digite seu email: ")
	password = input("Digite sua senha: ")

	cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
	user = cursor.fetchone()

	if user:
		print(f"Login bem-sucedido! ✅  Bem-vindo de volta, {user[1]}!")
		return True  #Para indicar que o login foi bem-sucedido
	else:
		print("Email ou senha incorretos. ❌ Tente novamente.")
		return False  #Para indicar que o login falhou


def app():
	print("Por enquanto não há nada! 😊")


is_logged_in = False


#Enviar email de teste
def send_test_email():
	name = "" #Inserir aqui nome
	email = "" #Inserir aqui email

	send_welcome_email(email, name)


#Menu principal
while True:
	if not is_logged_in:
		print("Olá bem-vindo!")
		print("O que gostaria?")
		option = input("1. Login 🔑\n"
		               "2. Cadastrar 🆕\n"
		               "3. Esqueci minha senha 🔒\n"
		               "4. Sair 🚪\n"
		               "5. Opção de DEV(enviar email teste) ✉️\n"
		               "Digite sua resposta: ")

		if option == '1':
			is_logged_in = login()
		elif option == '2':
			register_user()
		elif option == '3':
			forgot_password_and_reset()
		elif option == '5':
			send_test_email()
		elif option == '4':
			print("Até a proxima... 👋")
			break
		else:
			print("Opção inválida!")
	else:
		app()
		break

connection.close()