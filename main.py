from query_ import SQLParser,Query



import re

def generate_class_from_sql(sql_statement):
    # Extract table name
    table_name = re.search(r'CREATE TABLE (\w+)', sql_statement).group(1)

    # Extract column definitions
    columns = re.findall(r'(\w+) (\w+(?:\(\d+(?:,\d+)?\))?)', sql_statement)

    # Generate class definition
    class_definition = f"class {table_name.capitalize()}:\n"

    # Generate __init__ method
    init_method = "    def __init__(self"
    for column_name, data_type in columns:
        class_definition += f"    {column_name} = None\n"
        init_method += f", {column_name}=None"
    init_method += "):\n"
    class_definition += init_method
    for column_name, _ in columns:
        class_definition += f"        self.{column_name} = {column_name}\n"

    # Return the generated class definition
    return class_definition

# Example SQL statement
sql_statement = """
CREATE TABLE Employees (
    EmployeeID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(100) UNIQUE,
    HireDate DATE,
    Salary DECIMAL(10, 2)
);
"""

query=Query(sql_statement)
print(query.event())

query.query = """
UPDATE Employees
SET FirstName = 'John', LastName = 'Doe'
WHERE EmployeeID = 123;
"""

print(query.event())






