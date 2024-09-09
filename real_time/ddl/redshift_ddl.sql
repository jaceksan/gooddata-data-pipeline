CREATE TABLE IF NOT EXISTS dim_customer (
    CustomerID BIGINT PRIMARY KEY,
    FirstName VARCHAR(255),
    LastName VARCHAR(255),
    Email VARCHAR(255) UNIQUE NOT NULL,
    Phone VARCHAR(50),
    Address VARCHAR(255),
    City VARCHAR(100),
    State VARCHAR(50),
    ZipCode VARCHAR(20),
    Country VARCHAR(100),
    Age BIGINT,
    Gender VARCHAR(10),
    MembershipStatus VARCHAR(50)
)
;
CREATE TABLE IF NOT EXISTS dim_product (
    ProductID BIGINT PRIMARY KEY,
    ProductName VARCHAR(255),
    ProductCategory VARCHAR(100),
    ProductSubcategory VARCHAR(100),
    Manufacturer VARCHAR(255),
    SupplierID BIGINT NOT NULL,
    UnitPrice DOUBLE PRECISION,
    Cost DOUBLE PRECISION,
    ProductDescription VARCHAR(1024),
    Size VARCHAR(50),
    Weight DOUBLE PRECISION,
    Color VARCHAR(50)
)
;
CREATE TABLE IF NOT EXISTS fact_sales (
    SalesID BIGINT PRIMARY KEY,
    CustomerID BIGINT REFERENCES dim_customer(CustomerID),
    ProductID BIGINT REFERENCES dim_product(ProductID),
    TransactionDate TIMESTAMP,
    Quantity BIGINT,
    SalesAmount DOUBLE PRECISION,
    Discount DOUBLE PRECISION,
    SalesChannel VARCHAR(128)
)
;
CREATE TABLE IF NOT EXISTS fact_inventory (
    InventoryID BIGINT PRIMARY KEY,
    ProductID BIGINT REFERENCES dim_product(ProductID),
    TransactionDate TIMESTAMP,
    MovementType VARCHAR(128),
    Quantity BIGINT,
    Location VARCHAR(512)
)
;




