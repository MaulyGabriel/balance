import controller
from database import DataBase

db = DataBase(data_base='/home/madruga/developer/projects/config/config.db')

camera = controller.consult_camera(db)

communication = controller.consult_communication(db)

print(camera)

print(communication)
