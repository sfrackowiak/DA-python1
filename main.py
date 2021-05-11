import sqlite3
from fastapi import FastAPI, HTTPException, status

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
        "SELECT CustomerID, CompanyName, Address, PostalCode, City, Country FROM Customers ORDER BY UPPER(CustomerID)").fetchall()
    customers_list = []
    for x in customers:
        customer_addr = ""
        if x['Address'] is not None:
            customer_addr += x['Address']
        customer_addr += " "
        if x['PostalCode'] is not None:
            customer_addr += x['PostalCode']
        customer_addr += " "
        if x['City'] is not None:
            customer_addr += x['City']
        customer_addr += " "
        if x['Country'] is not None:
            customer_addr += x['Country']
        customer = {"id": x['CustomerID'], "name": x['CompanyName'], "full_address": customer_addr}
        customers_list.append(customer)

    return {"customers": customers_list}


@app.get("/products/{product_id}")
async def products(product_id: int):
    product = app.db_connection.execute(
        "SELECT ProductID, ProductName FROM Products WHERE ProductID = :product_id",
        {'product_id': product_id}).fetchone()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return {"id": product['ProductID'], "name": product['ProductName']}


@app.get("/employees")
async def employees(limit: int, offset: int, order: str):
    if order not in ["first_name", "last_name", "city"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if order == "first_name":
        order = "FirstName"
    elif order == "last_name":
        order = "LastName"
    else:
        order = "City"

    query = f"SELECT EmployeeID, LastName, FirstName, City FROM Employees ORDER BY UPPER({order})"
    if limit is not None:
        query += f" LIMIT {limit}"
    if offset is not None:
        query += f" OFFSET {offset}"

    employees = app.db_connection.execute(query).fetchall()

    return \
        {
            "products_extended":
                [
                    {
                        "id": x['EmployeeID'],
                        "last_name": x['LastName'],
                        "first_name": x['FirstName'],
                        "city": x['City']
                    }
                    for x in employees
                ]
        }
