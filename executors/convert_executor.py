import os
from flaskr.modelos import Tarea, db


class Convert:
    @staticmethod
    def pending_tasks() -> [Tarea]:
        return db.session.query(Tarea).filter(Tarea.status == 'UPLOADED').all()

    def run(self):
        tasks = self.pending_tasks()
        if tasks:
            for t in tasks:
                command = 'ffmpeg -i ' + str(t.file) + ' ' + str(t.newformat)
                try:
                    os.system(command)
                    print("Conversión realizada con exito")
                except Exception as e:
                    print(e)
            print(f'{len(tasks)} Tareas ejecutadas')
        else:
            print(f'No hay tareas por hacer')

