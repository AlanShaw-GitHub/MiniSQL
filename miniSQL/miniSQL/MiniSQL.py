import cmd
import APIManager.api
import CatalogManager.catalog
import IndexManager.index
import sys
import time
import os

class miniSQL(cmd.Cmd):
    intro = 'Welcome to the MiniSQL database server.\nType help or ? to list commands.\n'
    def do_select(self,args):
        # APIManager.api.select(args.replace(';', ''))
        try:
            APIManager.api.select(args.replace(';',''))
        except Exception as e:
            print(str(e))

    def do_create(self,args):
        try:
            APIManager.api.create(args.replace(';',''))
        except Exception as e:
            print(str(e))

    def do_drop(self,args):
        try:
            APIManager.api.drop(args.replace(';',''))
        except Exception as e:
            print(str(e))

    def do_insert(self,args):
        try:
            APIManager.api.insert(args.replace(';',''))
        except Exception as e:
            print(str(e))

    def do_delete(self,args):
        try:
            APIManager.api.delete(args.replace(';',''))
        except Exception as e:
            print(str(e))

    def do_commit(self,args):
        time_start = time.time()
        __finalize__()
        time_end = time.time()
        print('Modifications has been commited to local files,',end='')
        print(" time elapsed : %fs." % (time_end - time_start))

    def do_quit(self,args):
        __finalize__()
        print('Goodbye.')
        sys.exit()

    def emptyline(self):
        pass

    def default(self, line):
        print('Unrecognized command.\nNo such symbol : %s' % line)

    def help_commit(self):
        print()
        text = "To reduce file transfer's time, this SQL server is designed to "+\
        "'lasy' write changes to local files, which means it will not store changes "+\
        "until you type 'quit' to normally exit the server. if this server exit "+\
        "unnormally, all changes will be lost. If you want to write changes to "+\
        "local files immediately, please use 'commit' command.\n"
        print(text)

    def help_quit(self):
        print()
        print('Quit the program and write changes to local file.')

    def help_select(self):
        print()
        print("select * from student;")
        print("select num from student where num >= 2 and num < 10 and gender = 'male';")

    def help_create(self):
        print()
        print("create table student (ID int, name char(10),gender char(10)"
              ",enroll_date char(10),primary key(ID));")

    def help_drop(self):
        print()
        print("drop table student;")

    def help_insert(self):
        print('''
insert into student values ( 1,'Alan','male','2017.9.1');
insert into student values ( 2,'rose','female','2016.9.1');
insert into student values ( 3,'Robert','male','2016.9.1');
insert into student values ( 4,'jack','male','2015.9.1');
insert into student values ( 5,'jason','male','2015.9.1');
insert into student values ( 6,'Hans','female','2015.9.1');
insert into student values ( 7,'rosa','male','2014.9.1');
insert into student values ( 8,'messi','female','2013.9.1');
insert into student values ( 9,'Neymar','male','2013.9.1');
insert into student values ( 10,'Christ','male','2011.9.1');
insert into student values ( 11,'shaw','female','2010.9.1');
''')

    def help_delete(self):
        print()
        print("delete from students")
        print("delete from student where sno = '88888888';")

def exec_from_file(filename):
    f = open(filename)
    text = f.read()
    f.close()
    comands = text.split(';')
    comands = [i.strip().replace('\n','') for i in comands]
    __initialize__()
    for comand in comands:
        if comand == '':
            continue
        if comand[0] == '#':
            continue
        if comand.split(' ')[0] == 'insert':
            try:
                APIManager.api.insert(comand[6:])
            except Exception as e:
                print(str(e))
        elif comand.split(' ')[0] == 'select':
            try:
                APIManager.api.select(comand[6:])
            except Exception as e:
                print(str(e))
        elif comand.split(' ')[0] == 'delete':
            try:
                APIManager.api.delete(comand[6:])
            except Exception as e:
                print(str(e))
        elif comand.split(' ')[0] == 'drop':
            try:
                APIManager.api.drop(comand[4:])
            except Exception as e:
                print(str(e))
        elif comand.split(' ')[0] == 'create':
            try:
                APIManager.api.create(comand[6:])
            except Exception as e:
                print(str(e))
    __finalize__()


def __initialize__():
    CatalogManager.catalog.__initialize__(os.getcwd())
    IndexManager.index.__initialize__(os.getcwd())

def __finalize__():
    CatalogManager.catalog.__finalize__()
    IndexManager.index.__finalize__()

if __name__ == '__main__':
    errortext = '''
MiniSQL -u [username] -p [password] (optional)-execfile [filename]
\tLogin operators : 
\t\t-u username\tusername for MiniSQL.
\t\t-p password\tpassword for MiniSQL.\n
\tExecute SQL file operators : 
\t\t-execfile filename\tSQL filename to be executed for MiniSQL.
'''
    if len(sys.argv) < 5:
        print('ERROR : Unsupported syntax, please login.\n',errortext)
        sys.exit()
    if sys.argv[1] != '-u' or sys.argv[3] != '-p':
        print('ERROR : Unsupported syntax, please login.\n',errortext)
        sys.exit()
    __initialize__()
    if sys.argv[2] == 'root' and sys.argv[4] == '123456':
        APIManager.api.__root = True
    elif IndexManager.index.exist_user(username=sys.argv[2],password=sys.argv[4]):
        APIManager.api.__root = False
    else:
        print('Error : username or password is not correct,please '
              'check and login again.\n',errortext)
        sys.exit()
    if len(sys.argv) > 5:
        if sys.argv[5] != '-execfile':
            print('ERROR : Unsupported syntax.\n',errortext)
        exec_from_file(sys.argv[6])
        sys.exit()
    print("MiniSQL database server, version 1.0.0-release, (x86_64-apple-darwin)\n"
          "Copyright 2018 @ Alan Shaw from ZJU. Course final project for DBS.\n"
          "These shell commands are defined internally.  Type `help' to see this list.\n"
          "Type `help name' to find out more about the function `name'.\n")

    miniSQL.prompt = '(%s)' % sys.argv[2] + 'MiniSQL > '
    miniSQL().cmdloop()
