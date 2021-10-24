from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from sqlalchemy import desc, asc
from ..modelos import db, Usuario, Tarea, TareaSchema
from flask import request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from datetime import datetime
import os
from flask import send_from_directory
import smtplib


class VistaRegistro(Resource):
    def post(self):
        contrasena1 = request.json["password1"]
        contrasena2 = request.json["password2"]
        if validar_clave(contrasena1) is False:
            return {
                "mensaje": "la contrasena no cumple con los parametros de seguridad [debe ser entre 8 y 20 caracteres, contener un caracter especial y una mayúscula]"}
        if contrasena1 == contrasena2:
            try:
                nuevo_usuario = Usuario(nombre=request.json["username"], contrasena=contrasena1,
                                        correo=request.json["email"])
                db.session.add(nuevo_usuario)
                db.session.commit()
                return {"mensaje": "usuario creado exitosamente"}
            except IntegrityError:
                db.session.rollback()
                return {"mensaje": "El email ya existe"}
        else:
            return {"mensaje": "el usuario no se creo, clave no coincide"}


class VistaAutenticador(Resource):
    def post(self):
        u_nombre = request.json["username"]
        u_contrasena = request.json["password"]
        usuario = Usuario.query.filter_by(nombre=u_nombre, contrasena=u_contrasena).first()
        if usuario:
            token_de_acceso = create_access_token(identity=usuario.id)
            data = {'estado': 'ok', 'token': token_de_acceso}
            return data, 200
        else:
            data = {'estado': 'Nok'}
            return data, 404


class VistaTareas(Resource):
    def __init__(self):
        self.tarea_schema = TareaSchema()

    @jwt_required
    def post(self):
        resultado = subir_archivo()
        filename = resultado[0]
        newformat = resultado[1]
        if filename != "404":
            current_user_id = get_jwt_identity()
            nueva_tarea = Tarea(filename=filename,
                                newformat=newformat,
                                usuario_id=current_user_id,
                                timestamp=datetime.now(),
                                status="UPLOADED")
            db.session.add(nueva_tarea)
            db.session.commit()
            data = {'estado': 'La tarea se creo'}
            return data, 200
        else:
            data = {'estado': 'Archivo no subido, tarea no se creo'}
            return data, 404

    @jwt_required
    def get(self):
        current_user_id = get_jwt_identity()
        print(current_user_id)
        if request.args.get('max', None):
            return [self.tarea_schema.dump(ca) for ca in
                    Tarea.query.filter_by(usuario_id=current_user_id).limit(int(request.args.get('max', None))).all()]
        if request.args.get('order', None):
            if request.args.get('order', None) == '0':
                return [self.tarea_schema.dump(ca) for ca in
                        Tarea.query.filter_by(usuario_id=current_user_id).order_by(asc(Tarea.id)).all()]
            else:
                return [self.tarea_schema.dump(ca) for ca in
                        Tarea.query.filter_by(usuario_id=current_user_id).order_by(desc(Tarea.id)).all()]
        return [self.tarea_schema.dump(ca) for ca in Tarea.query.filter_by(usuario_id=current_user_id).all()]


class VistaTarea(Resource):
    def __init__(self):
        self.tarea_schema = TareaSchema()

    @jwt_required
    def put(self, id_task):
        tarea = Tarea.query.get_or_404(id_task)
        if tarea.status == "PROCESSED":
            filename = tarea.filename[:-3] + tarea.newformat
            borrar_archivo(filename)
        tarea.newformat = request.json.get("newformat", tarea.newformat)
        tarea.status = "UPLOADED"
        db.session.commit()
        return self.tarea_schema.dump(tarea)

    @jwt_required
    def get(self, id_task):
        return TareaSchema().dump(Tarea.query.get_or_404(id_task))

    @jwt_required
    def delete(self, id_task):
        tarea = Tarea.query.get_or_404(id_task)
        filename = tarea.filename[:-3] + tarea.newformat
        print("Un textico antes ", filename)
        if tarea.status == 'PROCESSED':
            borrar_archivo(tarea.filename)
            borrar_archivo(filename)
            db.session.delete(tarea)
            db.session.commit()
        return 200


class VistaConversor(Resource):
    ##descargar el archivo
    def get(self, filename):
        working_directory = os.getcwd()
        return send_from_directory(working_directory + "/archivos/", filename)


def subir_archivo():
    files = request.files.getlist("archivoup")
    newformat = request.form.get("newformat")
    for file in files:
        filename = secure_filename(file.filename)
        try:
            working_directory = os.getcwd()
            file.save(working_directory + "/archivos/" + filename)
        except FileNotFoundError:
            return "404"
    return filename, newformat


def borrar_archivo(filename):
    try:
        working_directory = os.getcwd()
        if os.path.exists(working_directory + "/archivos/" + filename):
            os.remove(working_directory + "/archivos/" + filename)
    except FileNotFoundError:
        return None
    return True


def validar_clave(clave):
    specialChar = ['$', '@', '#', '%']
    val = True

    if len(clave) < 8:
        val = False

    if len(clave) > 20:
        val = False

    if not any(char.isdigit() for char in clave):
        val = False
    if not any(char.isupper() for char in clave):
        val = False

    if not any(char.islower() for char in clave):
        val = False

    if not any(char in specialChar for char in clave):
        val = False
    return val
