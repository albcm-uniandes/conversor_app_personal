from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from ..modelos import db, Usuario, Tarea, TareaSchema
from flask import request
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from datetime import datetime
import os
from flask import send_from_directory


class VistaRegistro(Resource):
    def post(self):
        contrasena1 = request.json["password1"]
        # Todo: seguridaf
        contrasena2 = request.json["password2"]
        if contrasena1 == contrasena2:
            try:
                nuevo_usuario = Usuario(nombre=request.json["username"], contrasena=contrasena1,
                                        correo=request.json["email"])
                db.session.add(nuevo_usuario)
                db.session.commit()
                return {"mensaje": "usuario creado exitosamente"}
            except IntegrityError:
                db.session.rollback()
                return {"El email ya existe"}
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
        filename = subir_archivo()
        if filename != "404":
            current_user_id = get_jwt_identity()
            newformat = "wma"  ## TODO request.args.get('newformat')
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
        # Todo: Filtros
        return [self.tarea_schema.dump(ca) for ca in Tarea.query.filter_by(usuario_id=current_user_id).all()]


class VistaTarea(Resource):
    def __init__(self):
        self.tarea_schema = TareaSchema()

    @jwt_required
    def put(self, id_task):
        tarea = Tarea.query.get_or_404(id_task)
        tarea.newformat = request.json.get("newformat", tarea.newformat)
        tarea.status = "UPLOADED"
        # Todo: Eliminar el archivo
        db.session.commit()
        return self.tarea_schema.dump(tarea)

    @jwt_required
    def get(self, id_task):
        return TareaSchema().dump(Tarea.query.get_or_404(id_task))

    @jwt_required
    def delete(self, id_task):
        tarea = Tarea.query.get_or_404(id_task)
        db.session.delete(tarea)
        # Todo: Validar estado
        # Todo: Eliminar archivos
        db.session.commit()
        return 200


class VistaConversor(Resource):
    ##descargar el archivo
    def get(self, filename):
        working_directory = os.getcwd()
        return send_from_directory(working_directory + "/archivos/", filename)


def subir_archivo():
    print("Funciona")
    files = request.files.getlist("archivoup")
    for file in files:
        filename = secure_filename(file.filename)
        try:
            working_directory = os.getcwd()
            file.save(working_directory + "/archivos/" + filename)
        except FileNotFoundError:
            return "404"
    return filename
