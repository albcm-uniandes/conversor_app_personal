from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    contrasena = db.Column(db.String(128))
    correo = db.Column(db.String(128), unique=True)


class Tarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))
    filename = db.Column(db.String(128))
    new_format = db.Column(db.String(128))
    status = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime)


class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True


class TareaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Tarea
        include_relationships = True
        load_instance = True
