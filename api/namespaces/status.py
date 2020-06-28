from flask_restx import Namespace, Resource, abort
from utils.db import connect


ns_status = Namespace('status', description='Status of the API')

@ns_status.route("/")
class Status(Resource):
    def get(self):
        try:
            return {"status": True, "message": "OK"}
        except Exception as e:
            return {"status": False, "message": "Exception: {}".format(e)}
            
@ns_status.route("/tables")
class Status(Resource):
    def get(self):
        db = connect()
        if len(list(db.collection_names())) == 35:
            return {"status": True, "tables": db.collection_names()}
        else:
            return {"status": False, "count": len(list(db.collection_names())), "tables": db.collection_names()}

@ns_status.route("/records")
class StudentDataset(Resource):
    def get(self):
        """
        Records

        ### Description
        
        Numbers of records in table records

        ### Methods
        
        Step: insert
        From files into datasets/clean/  inserted into  dataset
        See steps/insert
        ### Output example:
        ```json
        data = { 
            "total" : 112, 
            
        }
        ```
        """
        return {"total": db.records.count(), "status" : True}
