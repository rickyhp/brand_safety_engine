from pymongo import MongoClient
import settings



class Mongodb_helper(object):
    def __init__(self):
        self.client = MongoClient("localhost",27017)
        self.db = self.client[settings.MONGODB_NAME]
        self.collection = self.db[settings.MONGODB_TABLE]
    
    def Insert_Record(self, record):
        try:
            existing = self.collection.find({settings.Image_Name_Column:record[settings.Image_Name_Column]})
            if existing.count() <=0:
                self.collection.insert(record)
                print('inserted record: ' + str(record))
        except Exception as e:
            print('Can not insert the record: {0}. Due to {1}'.format(str(record), e.__str__()))
    
    
    
    def Query(self, query_string, sort_string=None, top=10):
        try:
            if sort_string is None:
                return self.collection.find(query_string).limit(top)
            return self.collection.find(query_string).sort(sort_string, -1).limit(top)
        except Exception as e:
            print("Can not query the string. Due to {0}".format(e.__str__())) 
    
    def Query_Aggregate(self, pipe_line):
        try:
            if pipe_line is not None:
                return self.collection.aggregate(pipe_line)
            else:
                return None
        except Exception as e:
            print("Can not query the string. Due to {0}".format(e.__str__()))
    
    def Drop_DataBase(self, databaseName):
        self.client.drop_database(databaseName)

def Clear_AllRecords_In_Table(databaseName, tableName, client):
    db = client[databaseName]
    collection = db[tableName]
    collection.remove()

def Insert_Data_IntoMongoDB(databBaseName, tableName, client, valueDic, updateColumn = '', updateKey = ''):
    db = client[databBaseName]
    collection = db[tableName]
    if updateColumn == '':
        collection.insert_one(valueDic)
    else:
        queryFilter = {updateColumn : updateKey}
        record = collection.find_one(queryFilter)
        if record is not None:
            collection.update_one(queryFilter, {'$set': valueDic})
        else:
            collection.insert_one(valueDic)

# helper = Mongodb_helper()
# pipe_line = [{"$match": {"website_folder" : "www.businessinsider.sg/831e6e7f-fa4e-42fd-beb5-d5a7a49d356e"}}, {"$group": { "_id": "$website_folder", "maxAlcohol" : {"$max": "$result.alcohol"}, "maxGambling" : {"$max" : "$result.gambling"}}}]
# j = helper.Query_Aggregate(pipe_line)
# import pprint
# pprint.pprint(list(j))
