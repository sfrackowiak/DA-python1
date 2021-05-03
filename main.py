import hashlib
import secrets
from datetime import datetime, timedelta
from fastapi import FastAPI, Response, status, Request, Depends, Cookie, HTTPException
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
app.id = 1
app.patients = {}
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()
app.secret_key = "dosyc krotki sekretny kluczyk"
app.access_tokens = []


class UserIn(BaseModel):
    name: str
    surname: str


class UserOut(BaseModel):
    id: int
    name: str
    surname: str
    register_date: str
    vaccination_date: str


@app.get("/hello")
def hello(request: Request):
    return templates.TemplateResponse("hello.html", {"request": request, "today_date": datetime.today().strftime('%Y-%m-%d')})


def correct_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_login = secrets.compare_digest(credentials.username, "4dm1n")
    correct_password = secrets.compare_digest(credentials.password, "NotSoSecurePa$$")
    if not (correct_login and correct_password):
        return False
    return True


@app.post("/login_session")
def login_session(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    response.status_code = status.HTTP_201_CREATED
    if not (correct_credentials(credentials)):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return
    session_token = hashlib.sha256(f"{app.secret_key}".encode()).hexdigest()
    app.access_tokens.append(session_token)
    response.set_cookie(key="session_token", value=session_token)
    return


@app.post("/login_token")
def login_session(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    response.status_code = status.HTTP_201_CREATED
    if not (correct_credentials(credentials)):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return
    session_token = hashlib.sha256(f"{app.secret_key}".encode()).hexdigest()
    app.access_tokens.append(session_token)
    response.set_cookie(key="session_token", value=session_token)
    return {"token": session_token}


@app.get("/welcome_session")
def welcome_session(request: Request, response: Response, session_token: str = Cookie(None), format: str = None):
    if session_token not in app.access_tokens:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return
    if format is None:
        return "Welcome!"
    if format == "json":
        return {"message": "Welcome!"}
    return templates.TemplateResponse("welcome.html", {"request": request})


@app.get("/welcome_token")
def welcome_token(request: Request, response: Response, token: str = None, format: str = None):
    if token not in app.access_tokens:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return
    if format is None:
        return "Welcome!"
    if format == "json":
        return {"message": "Welcome!"}
    return templates.TemplateResponse("welcome.html", {"request": request})


@app.get("/")
def root():
    return {"message": "Hello world!"}


@app.api_route(
    path="/method", methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"], status_code=200
)
def read_request(request: Request, response: Response):
    request_method = request.method

    if request_method == "POST":
        response.status_code = status.HTTP_201_CREATED

    return {"method": request_method}


@app.get("/auth")
def auth(response: Response, password: str = None, password_hash: str = None):
    if password is None or password_hash is None or password == '' or password_hash == '':
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return
    hashed = hashlib.sha512(password.encode('utf-8'))
    if password_hash == hashed.hexdigest():
        response.status_code = status.HTTP_204_NO_CONTENT
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED


@app.post("/register", response_model=UserOut)
def register(info: UserIn, response: Response):
    to_add = sum(c.isalpha() for c in info.name) + sum(c.isalpha() for c in info.surname)
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
