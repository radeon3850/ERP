import sqlite3
import openpyxl
from sqlalchemy import create_engine
import pandas as pd

# create df from xlsx-file
def create_df():
    df=pd.read_excel("C:\\Users\\Roman\\Desktop\\Проэкт для Санька\\Виды работ.xlsx")
    df1=df[['Вид операции', 'Тип операции']][1:48]
    return df1


#create copy for engine SqlAlchemy and connection to DB
def write_to_db():
    engine = create_engine('sqlite:///test.db', echo=True)
    sqlite_connection = engine.connect()
    # write data from df1
    create_df().to_sql('works', sqlite_connection, if_exists='append')
    # close connect
    sqlite_connection.close()

if __name__=="__main__":
    write_to_db()


