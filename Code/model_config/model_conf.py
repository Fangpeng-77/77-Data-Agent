import pymysql

conn = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    password="123456",
    database="77db",
    charset="utf8mb4"
)

zhipu_ak = ""
model_name = "glm-4"
model_name_web_search = "glm-4-air"