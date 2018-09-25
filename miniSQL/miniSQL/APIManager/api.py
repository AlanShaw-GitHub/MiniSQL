import re
import CatalogManager.catalog
import IndexManager.index
import time

__root = True
def select(args):
    time_start = time.time()
    args = re.sub(r' +', ' ', args).strip().replace('\u200b','')
    lists = args.split(' ')
    start_from = re.search('from', args).start()
    end_from = re.search('from', args).end()
    columns = args[0:start_from].strip()
    if re.search('where', args):
        start_where = re.search('where', args).start()
        end_where = re.search('where', args).end()
        table = args[end_from+1:start_where].strip()
        conditions = args[end_where+1:].strip()
    else:
        table = args[end_from+1:].strip()
        conditions = ''
    CatalogManager.catalog.not_exists_table(table)
    CatalogManager.catalog.check_select_statement(table,conditions,columns)
    IndexManager.index.select_from_table(table,conditions,columns)
    time_end = time.time()
    print(" time elapsed : %fs." % (time_end-time_start))


def create(args):
    time_start = time.time()
    args = re.sub(r' +', ' ', args).strip().replace('\u200b','')
    lists = args.split(' ')
    if lists[0] == 'table':
        start_on = re.search('table', args).end()
        start = re.search('\(', args).start()
        end = find_last(args,')')
        table = args[start_on:start].strip()
        statement = args[start + 1:end].strip()
        CatalogManager.catalog.exists_table(table)
        IndexManager.index.create_table(table,statement)
        CatalogManager.catalog.create_table(table,statement)

    elif lists[0] == 'index':
        index_name = lists[1]
        if lists[2] != 'on':
            raise Exception("API Module : Unrecoginze symbol for command 'create index',it should be 'on'.")
        start_on = re.search('on',args).start()
        start = re.search('\(',args).start()
        end = find_last(args, ')')
        table = args[start_on:start].strip()
        column = args[start+1:end].strip()
        CatalogManager.catalog.exists_index(index_name)
        CatalogManager.catalog.create_index(index_name,table,column)
        IndexManager.index.create_index(index_name,table,column)

    else:
        raise Exception("API Module : Unrecoginze symbol for command 'create',it should be 'table' or 'index'.")
    time_end = time.time()
    print("Successfully create table '%s', time elapsed : %fs."
          % (table,time_end - time_start))

def drop(args):
    time_start = time.time()
    args = re.sub(r' +', ' ', args).strip().replace('\u200b','')
    if args[0:5] == 'table':
        table = args[6:].strip()
        if table == 'sys':
            raise Exception("ERROR : Can't delete 'sys' table, it is necessary for MiniSQL server to run.")
        CatalogManager.catalog.not_exists_table(table)
        CatalogManager.catalog.drop_table(table)
        IndexManager.index.delete_table(table)
        time_end = time.time()
        print("Successfully delete table '%s', time elapsed : %fs." % (table,time_end - time_start))

    elif args[0:5] == 'index':
        index = args[6:].strip()
        CatalogManager.catalog.not_exists_index(index)
        CatalogManager.catalog.drop_index(index)

    else:
        raise Exception("API Module : Unrecoginze symbol for command 'drop',it should be 'table' or 'index'.")


def insert(args):
    time_start = time.time()
    args = re.sub(r' +', ' ', args).strip().replace('\u200b','')
    lists = args.split(' ')
    if lists[0] != 'into':
        raise Exception("API Module : Unrecoginze symbol for command 'insert',it should be 'into'.")
    table = lists[1]
    if table == 'sys' and __root  == False:
        raise Exception("ERROR : Can't modify 'sys' table, you are not root.")
    if lists[2] != 'values':
        raise Exception("API Module : Unrecoginze symbol for command 'insert',it should be 'values'.")
    value = args[re.search('\(',args).start()+1:find_last(args,')')]
    values = value.split(',')
    CatalogManager.catalog.not_exists_table(table)
    CatalogManager.catalog.check_types_of_table(table,values)
    IndexManager.index.insert_into_table(table,values)
    time_end = time.time()
    print(" time elapsed : %fs." % (time_end-time_start))

def delete(args):
    time_start = time.time()
    args = re.sub(r' +', ' ', args).strip().replace('\u200b','')
    lists = args.split(' ')
    if lists[0] != 'from':
        raise Exception("API Module : Unrecoginze symbol for command 'delete',it should be 'from'.")
    table = lists[1]
    if table == 'sys' and __root  == False:
        raise Exception("ERROR : Can't modify 'sys' table, you are not root.")
    CatalogManager.catalog.not_exists_table(table)
    if len(lists) == 2:
        IndexManager.index.delete_from_table(table,[])
    else:
        IndexManager.index.delete_from_table(table,lists[3:])
    time_end = time.time()
    print(" time elapsed : %fs." % (time_end-time_start))

def find_last(string,str):
    last_position=-1
    while True:
        position=string.find(str,last_position+1)
        if position==-1:
            return last_position
        last_position=position