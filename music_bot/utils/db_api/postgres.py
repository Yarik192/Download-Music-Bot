import psycopg2

conn = psycopg2.connect(dbname="telegrambot", user="postgres",
                        password="1234", host="localhost")
cur = conn.cursor()
