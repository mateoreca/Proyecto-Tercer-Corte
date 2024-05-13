from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

app = Flask(__name__)

# Datos de ejemplo para simular una base de datos
empleados = [
    {"id": 1, "nombre": "Juan", "apellido": "Pérez", "cargo": "Analista", "salario": 5000, "telefono": "+1234567890", "contraseña": "123456", "email": "juan.perez@example.com"},
    {"id": 2, "nombre": "María", "apellido": "Gómez", "cargo": "Gerente", "salario": 8000, "telefono": "+0987654321", "contraseña": "password", "email": "maria.gomez@example.com"}
]

#Credencial de cuenta de Twilio
account_sid = 'TU_ACCOUNT_SID'
auth_token = 'TU_AUTH_TOKEN'
client = Client(account_sid, auth_token)

# Ruta para obtener todos los empleados
@app.route('/empleados', methods=['GET'])
def get_empleados():
    return jsonify(empleados)

# Ruta para obtener un empleado por su ID
@app.route('/empleados/<int:id>', methods=['GET'])
def get_empleado(id):
    empleado = next((empleado for empleado in empleados if empleado['id'] == id), None)
    if empleado:
        return jsonify(empleado)
    else:
        return jsonify({"mensaje": "Empleado no encontrado"}), 404

# Ruta para crear un nuevo empleado
@app.route('/empleados', methods=['POST'])
def crear_empleado():
    nuevo_empleado = request.json
    empleados.append(nuevo_empleado)
    return jsonify({"mensaje": "Empleado creado correctamente"}), 201

# Ruta para actualizar los datos de un empleado
@app.route('/empleados/<int:id>', methods=['PUT'])
def actualizar_empleado(id):
    empleado_actualizado = request.json
    empleado_existente = next((empleado for empleado in empleados if empleado['id'] == id), None)
    if empleado_existente:
        empleado_existente.update(empleado_actualizado)
        return jsonify({"mensaje": "Empleado actualizado correctamente"})
    else:
        return jsonify({"mensaje": "Empleado no encontrado"}), 404

# Ruta para eliminar un empleado por su ID
@app.route('/empleados/<int:id>', methods=['DELETE'])
def eliminar_empleado(id):
    global empleados
    empleados = [empleado for empleado in empleados if empleado['id'] != id]
    return jsonify({"mensaje": "Empleado eliminado correctamente"})

# Pago de nóminas diario
@app.route('/pago-nomina', methods=['POST'])
def pagar_nomina():
    # Implementación de la lógica para pagar la nómina
    # Esta función se ejecutará todos los días a las 6 pm hora colombiana
    now = datetime.now()
    if now.hour == 18:  # Verifica si es la hora de pagar la nómina
        # Lógica de pago de nómina
        enviar_notificaciones()
        return jsonify({"mensaje": "Nómina pagada correctamente"}), 200
    else:
        return jsonify({"mensaje": "Aún no es hora de pagar la nómina"}), 400

# Función para enviar notificaciones por mensaje de texto (Twilio)
def enviar_notificaciones():
    for empleado in empleados:
        mensaje = f"Estimado {empleado['nombre']}, su nómina ha sido pagada. Puede consultar su desprendible de pago en la plataforma."
        client.messages.create(body=mensaje, from_='+1TWILIO_NUMBER', to=empleado['telefono'])
        enviar_correo(empleado)

# Generación de desprendible de pago (simulación)
def generar_desprendible_pago(empleado):
    return f"Desprendible de pago para {empleado['nombre']} {empleado['apellido']}\n\nCargo: {empleado['cargo']}\nSalario: ${empleado['salario']}"

# Función para enviar correo electrónico con el desprendible de pago
def enviar_correo(empleado):
    desprendible = generar_desprendible_pago(empleado)
    # Guardar el desprendible en un archivo
    with open(f"{empleado['nombre']}_{empleado['apellido']}_desprendible.txt", "w") as file:
        file.write(desprendible)
    # Configuración del correo
    msg = MIMEMultipart()
    msg['From'] = 'tu_correo@example.com'
    msg['To'] = empleado['email']
    msg['Subject'] = 'Desprendible de pago'
    # Adjuntar el archivo
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(f"{empleado['nombre']}_{empleado['apellido']}_desprendible.txt", 'rb').read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f"{empleado['nombre']}_{empleado['apellido']}_desprendible.txt"))
    msg.attach(part)
    # Enviar el correo
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('tu_correo@example.com', 'tu_contraseña')
    text = msg.as_string()
    server.sendmail('tu_correo@example.com', empleado['email'], text)
    server.quit()

if __name__ == '__main__':
    app.run(debug=True)
