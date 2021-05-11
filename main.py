import sqlite3
from fastapi import FastAPI

app = FastAPI()


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")  # northwind specific
    app.db_connection.row_factory = sqlite3.Row


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/categories")
async def categories():
    categories = app.db_connection.execute(
        "SELECT CategoryID, CategoryName FROM Categories ORDER BY CategoryID").fetchall()
    return {"categories": [{"id": x['CategoryID'], "name": x['CategoryName']} for x in categories]}

    [{"employee": f"{x['FirstName']} {x['LastName']}", "region": x["TerritoryDescription"]} for x in data]

@app.get("/customers")
async def customers():
    customers = app.db_connection.execute(
        "SELECT CustomerID, CompanyName, Address, PostalCode, City, Country "
        "FROM Customers ORDER BY CustomerID").fetchall()
    return \
        {
            "customers": [
                {
                    "id": x['CustomerID'],
                    "name": x['CompanyName'],
                    "full_address": f"{x['Address']} {x['PostalCode']} {x['City']} {x['Country']}",
                }
                for x in customers]
        }
