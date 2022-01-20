from lib2to3.pgen2 import token
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import mysql.connector
import uvicorn
import json
from datetime import datetime
import time

app = FastAPI(title="Token Management")


def db_init():
    mydb = mysql.connector.connect(
    host="mysqldb",
    user="root",
    password="p@ssw0rd1"
  )
    cursor = mydb.cursor()

    cursor.execute("DROP DATABASE IF EXISTS token")
    cursor.execute("CREATE DATABASE token")
    cursor.close()

    mydb = mysql.connector.connect(
        host="mysqldb",
        user="root",
        password="p@ssw0rd1",
        database="token"
    )
    cursor = mydb.cursor()

    cursor.execute("DROP TABLE IF EXISTS token")
    cursor.execute("CREATE TABLE token (tokenid INTEGER, count INTEGER, status BOOLEAN, time FLOAT)")
    cursor.close()

    return 'init database'



def timestamp(dt):
    return time.mktime(dt.timetuple()) + dt.microsecond / 1e6




class UserIN(BaseModel):
    tokenid: int = Field(...)
    count: int = Field(...)


class BaggageCount(BaseModel):
    count: int = Field(...)


class UserOUtToken(BaseModel):
    tokenid: int


class UserOUT(BaseModel):
    tokenid: int
    count: int
    status: bool
    time:float


@app.get('/')
async def index():
    temp = db_init()
    return {"Hello": temp}

#, response_model=List[UserOUT]
@app.get('/getUser', response_model=List[UserOUT])
async def get_all_user():
    mydb = mysql.connector.connect(
        host="mysqldb",
        user="root",
        password="p@ssw0rd1",
        database="token"
    )
    cursor = mydb.cursor()
    query = "select * from token"
    cursor.execute(query)
    results = cursor.fetchall()
    row_headers=[x[0] for x in cursor.description] 
    json_data=[]
    for result in results:
        json_data.append(dict(zip(row_headers,result)))

    
    cursor.close()
    return json_data

    
    
    
@app.get("/getActiveToken", response_model=List[UserOUtToken])
async def get_active_token():
    mydb = mysql.connector.connect(
        host="mysqldb",
        user="root",
        password="p@ssw0rd1",
        database="token"
    )
    cursor = mydb.cursor()

    query = "SELECT tokenid FROM token WHERE STATUS =TRUE"
    cursor.execute(query)
    results = cursor.fetchall()
    row_headers=[x[0] for x in cursor.description[0]] 
    json_data=[]
    for result in results:
        json_data.append(dict(zip(row_headers,result)))
    cursor.close()
    return results
    


@app.get('/getAvailableToken')
async def get_available_token():
    mydb = mysql.connector.connect(
        host="mysqldb",
        user="root",
        password="p@ssw0rd1",
        database="token"
    )
    cursor = mydb.cursor()
    query = "SELECT COUNT(tokenid) as count FROM token WHERE STATUS =FALSE"
    cursor.execute(query)
    results = cursor.fetchone()
    print("************")
    print(results)
    print("************")
    cursor.close()
    return results[0]


@app.get("/getUser/{id}", response_model=UserOUT)
async def get_by_id(id: int):
    
    mydb = mysql.connector.connect(
        host="mysqldb",
        user="root",
        password="p@ssw0rd1",
        database="token"
    )
    cursor = mydb.cursor()
    query = "SELECT * FROM token WHERE tokenid=" + str(id)
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()

    if result is None:
        raise HTTPException(status_code=404, detail="Data not found")
    return result


@app.post('/createUser', response_model=UserOUT)
async def create_user(r: UserIN):
    mydb = mysql.connector.connect(
        host="mysqldb",
        user="root",
        password="p@ssw0rd1",
        database="token"
    )
    print("*********************")
    print("DOne")
    print("*********************")

    cursor = mydb.cursor()
    query = "INSERT INTO token (tokenid, count,status, time) VALUES (1,100,1,5.05)" 
    print("****************")
    print(query)
    print("****************")
    cursor.execute(query)
    # cursor.commit()
    cursor.close()
    return await get_by_id(id)


@app.delete('/delete/{id}')
async def delete_by_id(id: int):
    mydb = mysql.connector.connect(
        host="mysqldb",
        user="root",
        password="p@ssw0rd1",
        database="token"
    )
    cursor = mydb.cursor()
    query = "DELETE FROM token where tokenid=" + str(id)

    temp = cursor.execute(query)
    cursor.commit()
    cursor.close()
    if temp > 0:
        return {"Message": "Successfully deleted"}
    else:
        raise HTTPException(status_code=404, detail="Data Not found")


@app.put('/updateBaggageCount/{id}', response_model=UserOUT)
async def update_baggage_count(id: int, r: BaggageCount = Depends()):
    mydb = mysql.connector.connect(
        host="mysqldb",
        user="root",
        password="p@ssw0rd1",
        database="token"
    )
    cursor = mydb.cursor()
    query = "UPDATE token set count="+str(r.count) + ", time="+ str(timestamp(datetime.now()))+" WHERE tokenid="+str(id)
    cursor.execute(query)
    cursor.commit()
    cursor.close()

    return await get_by_id(id)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0",port=5000)






