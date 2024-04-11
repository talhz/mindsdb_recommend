# Teradata Handler

This is the implementation of the Teradata handler for MindsDB.

## Teradata Database

Teradata Vantage Advanced SQL Engine (formerly known as Teradata Database) is a connected multi-cloud data platform offering for enterprise analytics, that enables users to solve complex data challenges from start to scale. It supports huge data warehouse applications and was designed with a patented massively parallel processing (MPP) architecture. [Read more](https://docs.teradata.com/r/Teradata-VantageTM-Advanced-SQL-Engine-Release-Summary/June-2022/Introduction/What-is-Teradata-Vantage).

## Implementation

This handler was implemented using `teradatasql` - the Python driver for Teradata.

The required arguments to establish a connection are,

* `host`: the host name or IP address of the Teradata Vantage instance
* `user`: specifies the user name
* `password`: specifies the password for the user
* `database`: sets the database for the connection

## Usage

Assuming you created a database in Teradata called `HR` and you have a table called `Employees` that was created using
the following SQL statements:

~~~~sql
CREATE
DATABASE HR
AS PERMANENT = 60e6, -- 60MB
   SPOOL = 120e6; -- 120MB

CREATE
SET TABLE HR.Employees (
   GlobalID INTEGER,
   FirstName VARCHAR(30),
   LastName VARCHAR(30),
   DateOfBirth DATE FORMAT 'YYYY-MM-DD',
   JoinedDate DATE FORMAT 'YYYY-MM-DD',
   DepartmentCode BYTEINT
)
UNIQUE PRIMARY INDEX ( GlobalID );

INSERT INTO HR.Employees (GlobalID,
                          FirstName,
                          LastName,
                          DateOfBirth,
                          JoinedDate,
                          DepartmentCode)
VALUES (101,
        'Adam',
        'Tworkowski',
        '1980-01-05',
        '2004-08-01',
        01);
~~~~

In order to make use of this handler and connect to the Teradata database in MindsDB, the following syntax can be used:

~~~~sql
CREATE DATABASE teradata_db
WITH ENGINE = 'teradata',
PARAMETERS = {
    "host": "192.168.0.41",
    "user": "dbc",
    "password": "dbc",
    "database": "HR"
};

~~~~

**Note**: The above example assumes usage of Teradata Vantage running on Oracle VirtualBox.

Now, you can use this established connection to query your database as follows:

~~~~sql
SELECT * FROM teradata_db.Employees;
~~~~

|GlobalID | FirstName | LastName   | DateOfBirth | JoinedDate | DepartmentCode |
|---------|-----------|------------|-------------|------------|----------------|
|101      | Adam      | Tworkowski | 1980-01-05  | 2004-08-01 | 1              |

![MindsDB using Teradata Integration](https://i.imgur.com/GfSd9yW.png)
