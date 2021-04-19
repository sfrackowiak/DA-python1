import hashlib
from datetime import datetime, timedelta
from fastapi import FastAPI, Response, status
from pydantic import BaseModel

app = FastAPI()
app.id = 1
app.patients = {}


class UserIn(BaseModel):
    name: str
    surname: str


class UserOut(BaseModel):
    id: int
    name: str
    surname: str
    register_date: str
    vaccination_date: str


@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.get("/method")
def method():
    return {"method": "GET"}


@app.post("/method")
def method(response: Response):
    response.status_code = status.HTTP_201_CREATED
    return {"method": "POST"}


@app.delete("/method")
def method():
    return {"method": "DELETE"}


@app.put("/method")
def method():
    return {"method": "PUT"}


@app.options("/method")
def method():
    return {"method": "OPTIONS"}


@app.get("/auth")
def auth(response: Response, password: str = None, password_hash: str = None):
    if password is None or password_hash is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return
    hashed = hashlib.sha512(password.encode('utf-8'))
    if password_hash == hashed.hexdigest():
        response.status_code = status.HTTP_204_NO_CONTENT
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED


@app.post("/register", response_model=UserOut)
def register(info: UserIn, response: Response):
    to_add = len(info.name) + len(info.surname)
    reg_date = datetime.today().strftime('%Y-%m-%d')
    vac_date = (datetime.today() + timedelta(days=to_add)).strftime('%Y-%m-%d')
    user = {"id": app.id, "name": info.name, "surname": info.surname, "register_date": reg_date, "vaccination_date": vac_date}
    app.patients[app.id] = user
    app.id += 1
    response.status_code = status.HTTP_201_CREATED
    return user


@app.get("/patient/{patient_id}", response_model=UserOut)
def auth_patient(patient_id: int, response: Response):
    if patient_id < 1:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return
    if patient_id not in app.patients:
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    return app.patients[patient_id]