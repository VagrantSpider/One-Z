
import sqlite3
from random import randint


# sqlite3 doesnt return error or status codes so may need to find a workaround

class Query:
    KeyNum = None
    Name =None
    Description= None
    TargetOS = None
    Format = None
    Function = None
    Liner = None
    Vars = None

class Result:
    KeyNum = None
    Name =None
    Description= None
    TargetOS = None
    Format = None
    Function = None
    Liner = None
    Vars = None


class LinerDB():
    def __init__(self,db_path):
        self.db_path = db_path
        pass

    # no args, returns list
    def GetAllOSTypes(self):
        OS_TYPES = []
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()

        SQL_Statement = "SELECT DISTINCT target FROM linerlist;"
        cur.execute(SQL_Statement)
        result = cur.fetchall()
        con.close()

        # OS_TYPES.insert(0, "all")

        for i in result:
        	OS_TYPES.append(i[0])

        return OS_TYPES

    def GetOSTypesFiltered(self,format,function):
        qArgs = []
        hasWhere = False
        WhereLst = []
        OS_TYPES = []

        SQL_Statement = "SELECT DISTINCT target FROM linerlist"

        con = sqlite3.connect(self.db_path)
        cur = con.cursor()

        if format:
            hasWhere = True
            WhereLst.append(" format = ?")
            qArgs.append(format)

        if function:
            hasWhere = True
            WhereLst.append(" function = ?")
            qArgs.append(function)

        if hasWhere:
            SQL_Statement += " WHERE"
            Andflag = False
            for statement in WhereLst:
                if Andflag:
                    SQL_Statement += " AND"
                SQL_Statement += statement
                Andflag = True

        SQL_Statement += ";"

        cur.execute(SQL_Statement,qArgs)
        result = cur.fetchall()
        con.close()

        # OS_TYPES.insert(0, "all")

        for i in result:
        	OS_TYPES.append(i[0])

        return OS_TYPES

    # no args, returns list
    def GetAllFunctionTypes(self):
        FUNCTION_TYPES = []
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()

        SQL_Statement = "SELECT DISTINCT function FROM linerlist;"
        cur.execute(SQL_Statement)
        result = cur.fetchall()
        con.close()

        # FUNCTION_TYPES.insert(0, "all")

        for i in result:
        	FUNCTION_TYPES.append(i[0])

        return FUNCTION_TYPES

    def GetFunctionTypesFiltered(self,targetos,format):
        qArgs = []
        hasWhere = False
        WhereLst = []
        FUNCTION_TYPES = []

        SQL_Statement = "SELECT DISTINCT function FROM linerlist"

        con = sqlite3.connect(self.db_path)
        cur = con.cursor()

        if targetos:
            hasWhere = True
            WhereLst.append(" target = ?")
            qArgs.append(targetos)

        if format:
            hasWhere = True
            WhereLst.append(" format = ?")
            qArgs.append(format)

        if hasWhere:
            SQL_Statement += " WHERE"
            Andflag = False
            for statement in WhereLst:
                if Andflag:
                    SQL_Statement += " AND"
                SQL_Statement += statement
                Andflag = True

        SQL_Statement += ";"

        cur.execute(SQL_Statement,qArgs)
        result = cur.fetchall()
        con.close()

        # OS_TYPES.insert(0, "all")

        for i in result:
        	FUNCTION_TYPES.append(i[0])

        return FUNCTION_TYPES

    # no args, returns list
    def GetAllFormatTypes(self):
        FORMAT_TYPES = []
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()

        SQL_Statement = "SELECT DISTINCT format FROM linerlist;"
        cur.execute(SQL_Statement)
        result = cur.fetchall()
        con.close()

        # FORMAT_TYPES.insert(0, "all")

        for i in result:
        	FORMAT_TYPES.append(i[0])

        return FORMAT_TYPES

    def GetFormatTypesFiltered(self,targetos,function):
        qArgs = []
        hasWhere = False
        WhereLst = []
        FORMAT_TYPES = []

        SQL_Statement = "SELECT DISTINCT format FROM linerlist"

        con = sqlite3.connect(self.db_path)
        cur = con.cursor()

        if targetos:
            hasWhere = True
            WhereLst.append(" target = ?")
            qArgs.append(targetos)

        if function:
            hasWhere = True
            WhereLst.append(" function = ?")
            qArgs.append(function)

        if hasWhere:
            SQL_Statement += " WHERE"
            Andflag = False
            for statement in WhereLst:
                if Andflag:
                    SQL_Statement += " AND"
                SQL_Statement += statement
                Andflag = True

        SQL_Statement += ";"

        cur.execute(SQL_Statement,qArgs)
        result = cur.fetchall()
        con.close()

        # OS_TYPES.insert(0, "all")

        for i in result:
        	FORMAT_TYPES.append(i[0])

        return FORMAT_TYPES


    # args Query(), returns list of Result() objects
    def QueryDB(self,queryClass):
        qArgs = []
        hasWhere = False
        WhereLst = []
        SQL_Statement = "SELECT * FROM linerlist"

        con = sqlite3.connect(self.db_path)
        cur = con.cursor()

        if queryClass.Name:
            hasWhere = True
            WhereLst.append(" name = ?")
            qArgs.append(queryClass.Name)

        if queryClass.Description:
            hasWhere = True
            WhereLst.append(" description = ?")
            qArgs.append(queryClass.Description)

        if queryClass.TargetOS:
            hasWhere = True
            WhereLst.append(" target = ?")
            qArgs.append(queryClass.TargetOS)

        if queryClass.Format:
            hasWhere = True
            WhereLst.append(" format = ?")
            qArgs.append(queryClass.Format)

        if queryClass.Function:
            hasWhere = True
            WhereLst.append(" function = ?")
            qArgs.append(queryClass.Function)

        if queryClass.Liner:
            hasWhere = True
            WhereLst.append(" liner = ?")
            qArgs.append(queryClass.Liner)

        if queryClass.Vars:
            hasWhere = True
            WhereLst.append(" vars = ?")
            qArgs.append(queryClass.Vars)

        if hasWhere:
            SQL_Statement += " WHERE"
            Andflag = False
            for statement in WhereLst:
                if Andflag:
                    SQL_Statement += " AND"
                SQL_Statement += statement
                Andflag = True

        SQL_Statement += ";"
        cur.execute(SQL_Statement,qArgs)
        tmpresult = cur.fetchall()
        con.close()

        returnlist = []
        for i in tmpresult:
            tmpclass = Result()
            tmpclass.KeyNum = i[0]
            tmpclass.Name = i[1]
            tmpclass.Description = i[2]
            tmpclass.TargetOS = i[3]
            tmpclass.Format = i[4]
            tmpclass.Function = i[5]
            tmpclass.Liner = i[6]
            tmpclass.Vars = i[7]

            returnlist.append(tmpclass)
        return returnlist

    def AddLiner(self,queryclass):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()

        SQL_Statement = "INSERT INTO linerlist (id , name, description, target,format, function, liner, vars) VALUES(?,?,?,?,?,?,?,?)"
        queryclass.KeyNum = randint(10000000, 99999999)


        cur.execute(SQL_Statement, (queryclass.KeyNum, queryclass.Name, queryclass.Description, queryclass.TargetOS, queryclass.Format, queryclass.Function, queryclass.Liner, queryclass.Vars))
        con.commit()
        con.close()

    def RemoveLiner(self,targetos,format,function,name):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()

        SQL_Statement = "DELETE FROM linerlist WHERE target = ? AND format = ? AND function = ? AND name = ?;"
        cur.execute(SQL_Statement,(targetos,format,function,name))
        con.commit()
        con.close()

    def UpdateLiner(self,targetos,format,function,name,queryclass):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()

        SQL_Statement = "DELETE FROM linerlist WHERE target = ? AND format = ? AND function = ? AND name = ?;"
        cur.execute(SQL_Statement,(targetos,format,function,name))
        con.commit()

        queryclass.KeyNum = randint(10000000, 99999999)
        SQL_Statement = "INSERT INTO linerlist (id ,name,description, target,format, function, liner, vars) VALUES(?,?,?,?,?,?,?,?)"
        cur.execute(SQL_Statement, (queryclass.KeyNum, queryclass.Name, queryclass.Description, queryclass.TargetOS, queryclass.Format, queryclass.Function, queryclass.Liner, queryclass.Vars))
        con.commit()
        con.close()

    def GetLiner(self,targetos,format,function,name):
        result = Result()

        con = sqlite3.connect(self.db_path)
        cur = con.cursor()

        SQL_Statement = "SELECT * FROM linerlist WHERE target = ? AND format = ? AND function = ? AND name = ?;"
        cur.execute(SQL_Statement,(targetos,format,function,name))
        tmpresult = cur.fetchone()

        result.KeyNum = tmpresult[0]
        result.Name = tmpresult[1]
        result.Description = tmpresult[2]
        result.TargetOS = tmpresult[3]
        result.Format = tmpresult[4]
        result.Function = tmpresult[5]
        result.Liner = tmpresult[6]
        result.Vars = tmpresult[7]

        con.close()
        return result



#import DB
# a = DB.LinerDB(DB_PATH)
#
# b = DB.Query()
# b.TargetOS = 'windows'
# b.Format = 'cmd'
# b.Function = 'Dropper'
# # b.name = 'test'
#
# list = a.QueryDB(b)
# for i in list:
#     print(i.TargetOS +"/"+ i.Format +"/"+ i.Name)

# print("\n")
# c = DB.Query()
# c.Description = 'just a test'
# c.Format = 'cmd'
# c.Function = 'Dropper'
# c.Liner = 'echo "test" > test.txt;'
# c.TargetOS = 'windows'
# c.Name = 'testliner'
# c.Vars = 'URL,PASSWORD'

# print(a.QueryDB(c)[0].Liner)

# a.AddLiner(c)
# a.RemoveLiner('windows', 'cmd', 'Dropper', 'testliner')
# print(a.GetLiner('windows','cmd','Dropper','bat_dropper').Liner)
