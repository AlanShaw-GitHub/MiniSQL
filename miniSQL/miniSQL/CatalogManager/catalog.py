import json
import os
import re
import IndexManager.index

tables = {}
path = ''
indexs = {}

class table_instance():
    def __init__(self,table_name,primary_key = 0):
        self.table_name = table_name
        self.primary_key = primary_key

    columns =[]

class column():
    def __init__(self,column_name,is_unique,type = 'char',length = 16):
        self.column_name = column_name
        self.is_unique = is_unique
        self.type = type
        self.length = length

def __initialize__(__path):
    global path
    path = __path
    if not os.path.exists(os.path.join(path,'dbfiles/catalog_files')):
        os.makedirs(os.path.join(path,'dbfiles/catalog_files'))
        f = open(os.path.join(path,'dbfiles/catalog_files/tables_catalog.msql'),'w')
        f.close()
        f = open(os.path.join(path,'dbfiles/catalog_files/indexs_catalog.msql'),'w')
        f.close()
        tables['sys'] = table_instance('sys',0)
        indexs['sys_default_index'] = {'table':'sys','column':'username'}
        columns = []
        columns.append(column('username',True))
        columns.append(column('password', False))
        tables['sys'].columns = columns
        __store__()
    __load__()

def __finalize__():
    __store__()

def __load__():
    f = open(os.path.join(path,'dbfiles/catalog_files/tables_catalog.msql'))
    json_tables = json.loads(f.read())
    for table in json_tables.items():
        __table = table_instance(table[0],table[1]['primary_key'])
        columns = []
        for __column in table[1]['columns'].items():
            columns.append(column(__column[0],
                                  __column[1][0],__column[1][1],__column[1][2]))
        __table.columns = columns
        tables[table[0]] = __table
    f.close()
    f = open(os.path.join(path, 'dbfiles/catalog_files/indexs_catalog.msql'))
    json_indexs = f.read()
    json_indexs = json.loads(json_indexs)
    for index in json_indexs.items():
        indexs[index[0]] = index[1]
    f.close()

def __store__():
    __tables = {}
    for items in tables.items():
        definition = {}
        definition['primary_key'] = items[1].primary_key
        __columns = {}
        for i in items[1].columns:
            __columns[i.column_name] = [i.is_unique,i.type,i.length]
        definition['columns'] = __columns
        __tables[items[0]] = definition
    json_tables = json.dumps(__tables)
    f = open(os.path.join(path,'dbfiles/catalog_files/tables_catalog.msql'),'w')
    f.write(json_tables)
    f.close()
    f = open(os.path.join(path, 'dbfiles/catalog_files/indexs_catalog.msql'), 'w')
    f.write(json.dumps(indexs))
    f.close()

def check_types_of_table(table,values):
    cur_table = tables[table]
    if len(cur_table.columns) != len(values):
        raise Exception("Catalog Module : table '%s' "
                        "has %d columns." % (table,len(cur_table.columns)))
    for index,i in enumerate(cur_table.columns):
        if i.type == 'int':
            value = int(values[index])
        elif i.type == 'float':
            value = float(values[index])
        else:
            value = values[index]
            if len(value) > i.length:
                raise Exception("Catalog Module : table '%s' : column '%s' 's length"
                         " can't be longer than %d." % (table, i.column_name,i.length))

        if i.is_unique:
            IndexManager.index.check_unique(table,index,value)

def exists_table(table):
    for key in tables.keys():
        if key == table:
            raise Exception("Catalog Module : table already exists.")

def not_exists_table(table):
    for key in tables.keys():
        if key == table:
            return
    raise Exception("Catalog Module : table not exists.")

def not_exists_index(index):
    for key in indexs.keys():
        if key == index:
            return
    raise Exception("Catalog Module : index not exists.")

def exists_index(index):
    for key in indexs.keys():
        if key == index:
            raise Exception("Catalog Module : index already exists.")

def create_table(table,statement):
    global tables
    primary_place = re.search('primary key *\(',statement).end()
    primary_place_end = re.search('\)',statement[primary_place:]).start()
    primary_key = statement[primary_place:][:primary_place_end].strip()
    cur_table = table_instance(table,primary_key)
    lists = statement.split(',')
    columns = []
    for cur_column_statement in lists[0:len(lists)-1]:
        cur_column_statement = cur_column_statement.strip()
        cur_lists = cur_column_statement.split(' ')
        is_unique = False
        type = 'char'
        column_name = cur_lists[0]
        if re.search('unique',concat_list(cur_lists[1:])) or column_name == primary_key:
            is_unique = True
        if re.search('char',concat_list(cur_lists[1:])):
            length_start = re.search('\(',concat_list(cur_lists[1:])).start()+1
            length_end = re.search('\)', concat_list(cur_lists[1:])).start()
            length = int(concat_list(cur_lists[1:])[length_start:length_end])

        elif re.search('int', concat_list(cur_lists[1:])):
            length = 0
            type = 'int'
        elif re.search('float', concat_list(cur_lists[1:])):
            length = 0
            type = 'float'
        else:
            raise Exception("Catalog Module : Unsupported type for %d." % column_name)
        columns.append(column(column_name,is_unique,type,length))
    cur_table.columns = columns
    seed = False
    for index,__column in enumerate(cur_table.columns):
        if __column.column_name == cur_table.primary_key:
            cur_table.primary_key = index
            seed = True
            break
    if seed == False:
        raise Exception("Catalog Module : primary_key '%s' not exists."
                        % cur_table.primary_key)

    tables[table] = cur_table


def drop_table(table):
    tables.pop(table)

def drop_index(index):
    indexs.pop(index)
    print("Successfully delete index '%s'." % index)

def create_index(index_name,table,column):
    indexs[index_name] = {'table':table,'column':column}

def check_select_statement(table,conditions,__columns):
    # raise an exception if something is wrong
    columns = []
    for i in tables[table].columns:
        columns.append(i.column_name)
    if conditions != '':
        conditions = re.sub('and|or',',',conditions)
        conditions_lists = conditions.split(',')
        for i in conditions_lists:
            if i.strip().split(' ')[0] not in columns:
                raise Exception("Catalog Module : no such column"
                                " name '%s'." % i.strip().split(' ')[0])
    if __columns == '*':
        return

    __columns_list = __columns.split(',')
    for i in __columns_list:
        if i.strip() not in columns:
            raise Exception("Catalog Module : no such column name '%s'." % i.strip())


def concat_list(lists):
    statement = ''
    for i in lists:
        statement = statement + i
    return statement

if __name__ == '__main__':
    # new_table = table_instance('my_table','yes')
    # new_table.columns.append(column('yes',True))
    # new_table.columns.append(column('no',False))
    # tables['my_table'] = new_table
    __initialize__('/Users/alan/Desktop/CodingLife/Python/miniSQL')
    ##__store__()

