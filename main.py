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


@app.get("/customers")
async def customers():
    customers = app.db_connection.execute(
        "SELECT CustomerID, CompanyName, Address, PostalCode, City, Country FROM Customers ORDER BY CustomerID").fetchall()
    customers_list = []
    for x in customers:
        customer_addr = ""
        if x['Address'] is not None:
            customer_addr += x['Address'] + " "
        if x['PostalCode'] is not None:
            customer_addr += x['PostalCode'] + " "
        if x['City'] is not None:
            customer_addr += x['City'] + " "
        if x['Country'] is not None:
            customer_addr += x['Country']
        customer = {"id": x['CustomerID'], "name": x['CompanyName'], "full_address": customer_addr}
        customers_list.append(customer)

    return {"customers": customers_list}

