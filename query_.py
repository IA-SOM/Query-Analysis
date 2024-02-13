import sqlparse
import re


class SQLParser:

    def __init__(self,query:str) -> None:
        self.__query:str=query
    def is_valid(self):
        try:
            sqlparse.parse(self.__query)
            return True, "Valid SQL query"
        except Exception as e:
            return False, str(e)


class Query:
    def __init__(self,query:str) -> None:
        self.__query=query
        self.__tables:list=[]
        self.__success:bool=True
        self.__message:str=''
        self.__attribute_problem:str=''
        self.__table_now:str=''


    @property
    def table_now(self):
        return self.__table_now
    @table_now.setter
    def table_now(self, new___table_now):
        self.__table_now = new___table_now


    @property
    def attribute_problem(self):
        return self.__attribute_problem
    @attribute_problem.setter
    def attribute_problem(self, new_attribute_problem):
        self.__attribute_problem = new_attribute_problem

    @property
    def message(self):
        return self.__message
    @message.setter
    def message(self, new_message):
        self.__message = new_message

    @property
    def success(self):
        return self.__success

    @success.setter
    def success(self, new_success):
        self.__success = new_success

    @property
    def tables(self):
        return self.__tables

    @tables.setter
    def tables(self, new_tables):
        self.__tables = new_tables

    @property
    def query(self):
        return self.__query

    @query.setter
    def query(self, new_query):
        self.__query = new_query
    
    def type(self)->str:
        # Regular expressions to match different SQL statement types
        select_pattern = re.compile(r'\bSELECT\b', re.IGNORECASE)
        update_pattern = re.compile(r'\bUPDATE\b', re.IGNORECASE)
        delete_pattern = re.compile(r'\bDELETE\b', re.IGNORECASE)
        insert_pattern = re.compile(r'\bINSERT\b', re.IGNORECASE)
        create_table_pattern = re.compile(r'\bCREATE\s+TABLE\b', re.IGNORECASE)
        create_database_pattern = re.compile(r'\bCREATE\s+DATABASE\b', re.IGNORECASE)
        drop_table_pattern = re.compile(r'\bDROP\s+TABLE\b', re.IGNORECASE)

        # Match patterns to determine statement type
        if re.search(select_pattern, self.query):
            return "SELECT"
        elif re.search(update_pattern, self.query):
            return "UPDATE"
        elif re.search(delete_pattern, self.query):
            return "DELETE"
        elif re.search(insert_pattern, self.query):
            return "INSERT"
        elif re.search(create_table_pattern, self.query):
            return "CREATE TABLE"
        elif re.search(create_database_pattern, self.query):
            return "CREATE DATABASE"
        elif re.search(drop_table_pattern, self.query):
            return "DROP TABLE"
        else:
            return "UNKNOWN"
    
    def transform(self, sql_statement:str) -> None:
        # Extract table name
        table_name = re.search(r'CREATE TABLE (\w+)', sql_statement).group(1)
        self.table_now=table_name.capitalize()+'('
        # Check if the table already exists
        if table_name in self.get_table_names():
            # Table exists, delete it
            self.tables = [table for table in self.tables if table.__name__ != table_name]

        # Extract column definitions
        columns = re.findall(r'(\w+) (\w+(?:\(\d+(?:,\d+)?\))?)', sql_statement)

        # Generate class definition
        class_definition = f"class {table_name.capitalize()}:\n"

        # Generate __init__ method
        init_method = "    def __init__(self"
        columns=columns[1:]
        for column_name, data_type in columns:
                class_definition += f"    {column_name} = None\n"
                init_method += f", {column_name}=None"
        init_method += "):\n"
        class_definition += init_method
        for column_name, _ in columns:
            self.table_now+=column_name+','
            class_definition += f"        self.{column_name} = {column_name}\n"

        # Append the new class definition
        self.tables.append(class_definition)
        self.table_now=self.table_now[:-1]+')'
    
    def table_exists(self)->bool:
        # Extract the table name from the query
        match = re.search(r'\bFROM\s+(\w+)\b', self.query, re.IGNORECASE)
        if match:
            table_name = match.group(1).lower()
            self.table_now=table_name.capitalize()
            # Check if the table name exists in the list of table names
            return table_name in self.get_table_names()
        else:
            return False
    
    def get_table_names(self)->list:
        # Extract table names from the strings representing class definitions
        table_names = []
        for table_definition in self.tables:
            # Find the class name within the string
            match = re.search(r'class\s+(\w+):', table_definition)
            if match:
                table_names.append(match.group(1).lower())  # Append the lowercase table name

        return table_names


    def attributes_exist_in_table(self, selected_attributes)->bool:
        table_name = self.get_table_name_from_query()
        if table_name:
            table_attributes = [attr.lower() for attr in self.get_table_attributes(table_name)]
            for attr in selected_attributes:
                if attr not in table_attributes:
                    self.attribute_problem=attr
                    return False
            return True
        else:
            return False

    def get_table_name_from_query(self)->str|None:
        pattern = ''
        # Regular expressions to match table names in different SQL statements
        if self.type()== "SELECT":
            pattern = re.compile(r'\bFROM\s+(\w+)\b', re.IGNORECASE)
        elif self.type()== "UPDATE":
            pattern = re.compile(r'\bUPDATE\s+(\w+)\b', re.IGNORECASE)
        elif self.type()== "DELETE":
            pattern = re.compile(r'\bDELETE\s+FROM\s+(\w+)\b', re.IGNORECASE)
        elif self.type()== "INSERT":
            pattern = re.compile(r'\bINTO\s+(\w+)\b', re.IGNORECASE)
        elif self.type()== "DROP TABLE":
            pattern = re.compile(r'\bDROP\s+TABLE\s+(\w+)\b', re.IGNORECASE)
        match=pattern.search(self.query) if pattern else None
        if match:
            return match.group(1).lower()
        else:
            return None

    def get_table_attributes(self, table_name:str)->list:
        i:int=-1
        for table in self.get_table_names():
            i+=1
            if table == table_name:
                # Extract attributes from class definition
                attributes = re.findall(r'\b(\w+)\b', str(self.tables[i]))
                return [attribute.lower() for attribute in attributes]
        return []
    def extract_selected_attributes(self)->list:
        # Extract selected attributes from the query
        match = re.search(r'\bSELECT\s+(.+?)\bFROM\b', self.query, re.IGNORECASE)
        if match:
            selected_attributes_str = match.group(1)
            selected_attributes = [attr.strip().lower() for attr in selected_attributes_str.split(',')]
            return selected_attributes
        else:
            return []

    def extract_updated_attributes(self)->dict:
        # Assuming self.query contains the UPDATE query
        # Parse the query to extract updated attributes and their new values
        updated_attributes = {}
        set_clause_match = re.search(r'SET\s+(.+?)\s+WHERE', self.query, re.IGNORECASE)
        if set_clause_match:
            set_clause = set_clause_match.group(1)
            set_pairs = set_clause.split(',')
            for pair in set_pairs:
                attribute, value = pair.strip().split('=')
                updated_attributes[attribute.strip().lower()] = value.strip()
        return updated_attributes

    def response(self,valid:bool,message:str)->None:
        self.success = valid
        self.message = message
    def send(self)->tuple:
        return self.success,self.message
    def event(self) -> tuple:
        sql_parser = SQLParser(self.query)
        is_valid, validation_message = sql_parser.is_valid()

        if not is_valid:
            return self.response(False,validation_message)

        query_type = self.type()

        if query_type == "CREATE TABLE":
            self.transform(self.query)
            self.response(True,f"Table {self.table_now} created successfully.")
        elif query_type == "DROP TABLE":
            pass
        elif query_type == "SELECT":
            if self.table_exists():
                selected_attributes = self.extract_selected_attributes()
                if self.attributes_exist_in_table(selected_attributes):
                    self.response(True,f"Selected attributes exist in the table {self.table_now}.")
                else:
                    self.response(False,f"Selected attribute {self.attribute_problem} do not exist in the table {self.table_now}.")
            else:
                self.response(False,f"Table {self.table_now} does not exist.")

        elif query_type == "UPDATE":
            updated_attributes = self.extract_updated_attributes()
            if self.attributes_exist_in_table(list(updated_attributes.keys())):
                # Process the updated attributes as needed
                self.success = True
                self.message = "UPDATE query processed successfully."
            else:
                self.response(False,f"UPDATE attribute {self.attribute_problem} do not exist in the table {self.table_now}.")
        else:
            self.response(False,"Query type recognized.")

        return self.send()


