from flaskr.modelos.modelos import db, Tarea

import os


class Conversor:

    def pending_tasks(self) -> [Tarea]:
        return db.session.query(Tarea).filter(Tarea.status == 'UPLOADED').all()

    def convert(self):
        tasks = self.pending_tasks()
        for task in tasks:
            command = 'ffmpeg -i ' + str(task.file) + ' ' + str(task.new_format)
            try:
                os.system(command)
                print("Conversión realizada con exito")
            except Exception as e:
                print(e)
        print(f'{len(tasks)} Tareas ejecutadas')
