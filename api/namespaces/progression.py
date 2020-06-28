from flask_restx import Namespace, Resource, abort
from flask import request
import pymongo
from utils.db import connect

CHAPTER_COLORS = {
	1: "#9670E0",
	2: "#FFE822",
	3: "#ED9AB5",
	4: "#A84349",
	5: "#3F32A5",
	6: "#9FF9AB",
	7: "#C3C2C4",
	8: "#FFAF57",
	9: "#50FEE4",
	10: "#7AD1FF",
	11: "#C3C2C4",
	12: "#FFE822",
	13: "#A84349",
	14: "#ED9AB5",
	15: "#9FF9AB",
	16: "#3F32A5",
	17: "#50FEE4",
	18: "#7AD1FF",
  	19: "#FFAF57",
	20: "#9670E0"
	}

ns_progression = Namespace('progression', description='Progression into chapters and lessons of the game')

@ns_progression.doc(params={
    'student': 'An integer between 111 and 60820',
    "subject": "A subject as included in the list [letters, numbers]"
})
@ns_progression.route("/chapters/students/<int:student>/subjects/<string:subject>")
class StudentChaptersSubject(Resource):
    @ns_progression.response(200, 'OK')
    @ns_progression.response(404, 'No data')
    @ns_progression.response(406, "Incorrect parameter")
    @ns_progression.response(500, "Database Error")
    def get(self, subject, student):
        """
        VIEW the progression by chapters of a student on a subject 
        
        ### Description
        
        Expose the table `student_chapter` given the student and the dataset that corresponds to the subject
        along with the table 'student_chapters' that gives the overview of chapters for this student

        Student_chapter is built upon student_lesson that are available only for datasets that have a lesson level
        
        ### Methods

        SELECT * FROM student_chapter
        WHERE student=_<student>_ AND subject=_<subject>_
       
        ### Documentation
  
		Consult [progression documentation](http://doc.ludoeducation.fr/researcher-guide/progression/)
        """
        db = connect()
        if int(student) not in range(111, 60821):
            raise abort(406, "L'identifiant de l'élève  `{}` est incorrect. Vérifiez son identifiant".format(student))
        if student not in db.students.distinct("student"):
            raise abort(404, "L'élève `{}` n'a pas été trouvé".format(student))
        if subject == "letters":
            subject_name = "Français"
            dataset = "gp"
        elif subject == "numbers":
            subject_name = "Maths"
            dataset = "numbers"
        else: 
            raise abort(406, "Le nom du sujet  `{}` est incorrect. Vérifiez son identifiant".format(subject))
        chapters = db.student_chapters.find_one({"student": student, "subject": subject}, {"_id":0, "records":0}) 
        
             
        if chapters is None:
            chapters_list = db.student_chapter.distinct("chapter", {"student": student, "subject": subject})
            if len(chapters_list) == 0:
                raise abort(
                                404, 
                                "Pas de données pour l'étudiant {} sur le sujet {}".format(student, subject)
                            )
            else:
                chapters = {"chapter_ids": sorted(chapters_list)} 
            
        else:
            progression = []
            for n in chapters["chapter_ids"]:
                progression.extend(list(db.student_chapter.find({"student": student, "chapter":n},{"records":0, "_id":0})))
        return {
                    "type":"progression", 
                    "progression": progression,
                    "data": chapters, 
                    "dataset": dataset, 
                    "subject": subject, 
                    "subject_name": subject_name, 
                    "student": student,
                    "csv": "{}/csv".format(request.base_url),
                }


@ns_progression.doc({"classroom": "An integer between 1 and 60", "subject": "A string in the included list ['numbers','letters' ]"})
@ns_progression.route("/chapters/classrooms/<int:classroom>/subjects/<string:subject>")
class ClassroomSubjectChapter(Resource):
    @ns_progression.response(200, 'Success')
    @ns_progression.response(404, 'No data')
    @ns_progression.response(406, "Incorrect parameter")
    @ns_progression.response(500, "Database Error")
    def get(self, classroom, subject):
        """ 
        View the classroom progression by student by chapter on a given subject 
        
        ### Description
        
        Expose the table `student_chapters` given the student and the dataset that corresponds to the subject        
        Student_chapter is built upon student_lesson that are available only for datasets that have a lesson level

        ### Methods

        See the complete documentation on method: htts://lab.driss.org/kalulu/docs/stats/progression.md
        
        ### Output example
        
        ```json
        {
            "title": "Progression des élèves de la classe 45 en Maths",
            "y_label": "Elèves",
            "chapter_label": "Jardins",
            "x_label": "Défis réalisés sur le chemin des nombres",
            "x_axis_labels": ["1","2","3","0",...],
            "x_axis_index": [1, 2, 3, 4, ...],
            "chapter_labels": [1, 1, 1, 2, ...],
            "chapter_colors": ["#9670E0","#9670E0","#9670E0","#FFE822",...],
            "y_axis_labels": [4511,4512,4521,4522,4531,4551,4562],
            "y_axis_index": [0,1,2,3,4,5,6],
            "legend": "Progression des élèves en Maths",
            "data": [
                {
                    "student": 4511,
                    "classroom": 45,
                    "group": "m/r",
                    "dataset": "numbers",
                    "subject": "numbers",
                    "lesson_ids": [],
                    "tags": [],
                    "timespents": [],
                    "%CA_colors": [],
                    "chapters": [],
                },
                ...
            ],
            "dataset": "numbers",
            "subject": "numbers",
            "subject_name": "Maths",
            "classroom": 45
        }
        ```
        """
        db = connect()
        if int(classroom) not in range(1, 60):
            raise abort(406, "L'identifiant de la classe `{}` est incorrect, vérifiez votre identifiant.".format(classroom))
        if int(classroom) not in db.students.distinct("classroom"):
            raise abort(404, "La classe `{}` n'a pas été trouvée".format(classroom))
        if subject not in ["letters", "numbers"]:
            raise abort(406, "Le sujet `{}` n'existe pas encore.".format(subject))
        if subject == "letters":
            sujet = "lettres"
            subject_name = "Français"
            dataset = "gp"
        else:
            sujet = "nombres"
            subject_name = "Maths"
            dataset = "numbers"
        # dataset_ref = db.datasets.find_one({"dataset": dataset})
        # if dataset_ref is None:
        #     raise abort(406, "Le nom du dataset `{}` est incorrect.".format(dataset))
        # else:
        #     if dataset_ref["subject"] == "letters":
        #         subject_name = "Français"
        #     else:
        #         subject_name = "Maths"
        lessons_refs = list(db.path.find({"subject": subject}, {"_id":0}))
        lessons = db.path.distinct("lesson",{"subject": subject})
        u_tags = sorted([(t,db.path.find_one({"tag":t}, {"lesson":1})["lesson"]) for t in db.path.distinct("tag", {"dataset": dataset})], key=lambda x: x[1])
        tags = [n[0] for n in u_tags]
        class_lessons = sorted(list(db.student_lessons.find({"classroom": classroom, "subject": subject}, {"_id":0, "start":0, "end":0, "records":0})), key = lambda x: x["student"], reverse=True)
        students = sorted([db.students.find_one({"student": n["student"]}) for n in class_lessons], key= lambda x: x["student"], reverse=True)
        if len(class_lessons) == 0:
            raise abort(    404, 
                            "Pas de données pour la classe {} sur le sujet {}.".format(classroom, subject),
                            title =  "Progression des élèves de la classe {} en {}".format(classroom, subject_name)
                        )
        return {
                    "title": "Progression des élèves de la classe {} en {}".format(classroom, subject_name),
                    "chapter_label": "Jardins",
                    "x_label": "Défis réalisés sur le chemin des {}".format(sujet),
                    "x_axis_labels": tags,
                    "x_axis_index": lessons,
                    "chapter_labels": [l["chapter"] for l in lessons_refs],
                    "chapter_colors": [CHAPTER_COLORS[int(l["chapter"])] for l in lessons_refs],
                    "y_label": "Elèves",
                    "y_axis_labels": [n["student"] for n in class_lessons],
                    "y_axis_index": [n[0] for n in enumerate(class_lessons)],
                    "students": students,
                    "data": class_lessons, 
                    "dataset": dataset, 
                    "subject":subject, 
                    "subject_name": subject_name, 
                    "classroom": classroom,
                    "csv": "{}/csv".format(request.base_url),
                    
                }
        

@ns_progression.doc(params={
    'student': 'An integer between 111 and 60820',
    "subject": "A subject as included in the list [letters, numbers]"
})
@ns_progression.route("/lessons/students/<int:student>/subjects/<string:subject>")
class StudentLessonsSubject(Resource):
    @ns_progression.response(200, 'Success')
    @ns_progression.response(404, 'No data')
    @ns_progression.response(406, "Incorrect parameter")
    @ns_progression.response(500, "Database Error")
    def get(self, subject, student):
        """
        VIEW the progression by chapters of a student on a subject 
        
        ### Description
        
        Expose the table `student_chapter` given the student and the dataset that corresponds to the subject
        along with the table 'student_chapters' that gives the overview of chapters for this student

        Student_chapter is built upon student_lesson that are available only for datasets that have a lesson level
        
        
        ### Documentation
  
		Consult [progression documentation](http://doc.ludoeducation.fr/researcher-guide/progression/)
        """
        print("GET LESSON")
        db = connect()
        if int(student) not in range(111, 60821):
            raise abort(406, "L'identifiant de l'élève  `{}` est incorrect. Vérifiez son identifiant".format(student))
        if student not in db.students.distinct("student"):
            raise abort(404, "L'élève `{}` n'a pas été trouvé".format(student))
        if subject == "letters":
            subject_name = "Français"
            dataset = "gp"
        else:
            subject_name = "Maths"
            dataset = "numbers"
        lessons = db.student_lessons.find_one({"student": student, "dataset": dataset}, {"_id":0, "lessons":0}) 
        progression = []
        
        for n in lessons["lesson_ids"]:
            student_lesson = db.student_lesson.find({"lesson":n},{"records":0, "_id":0, "start":0, "end":0})
            progression.extend(list(student_lesson))
            
        if len(lessons) == 0:
            raise abort(404, "Pas de données pour l'étudiant {} sur le sujet {}".format(student, subject))
        return {
                    "type":"progression", 
                    "progression": progression,
                    "data": lessons, 
                    "dataset": dataset, 
                    "subject": subject, 
                    "subject_name": subject_name, 
                    "student": student,
                    "csv": "{}/csv".format(request.base_url),
                    "doc": '''
			Ce graphique représente la progression de chaque élève de la classe en {}:
			- les élèves sont ordonnés par numéro de tablette puis par identifiant (axe vertical)
			- chaque point correspond à une leçon complétée (axe horizontal)
			- chaque leçon est colorée en fonction du score de bonne réponse par comparaison avec l'ensemble des scores de bonne réponses pour cette leçon</li> 
				
			La couleur de la leçon correspond au score de bonne réponse de l'élève par rapport 
			à l'ensemble des élèves (toute classe confonfue) ayant complété cette même leçon.
			
			-	Un point vert: le score de bonne réponse pour cette leçon est supérieur ou égal au score moyen pour cette leçon
			-	Un point orange: le score de bonne réponse pour cette leçon est inférieur ou égal à 1 écart type de la moyenne pour cette leçon
			-	Un point rouge: le score de bonne réponse pour cette leçon est deux fois inférieur au score moyen pour cette leçon
			
			Accédez au détail de l'élève en cliquant sur l'un des points qui lui correspond.
			'''.format(subject_name)
                }

@ns_progression.doc(params={
    'student': 'An integer between 111 and 60820',
    "subject": "A subject as included in the list [letters, numbers]"
})
@ns_progression.route("/lessons/students/<int:student>/subjects/<string:subject>/last")
class StudentLastLesson(Resource):
    @ns_progression.response(200, 'Success')
    @ns_progression.response(404, 'No data')
    @ns_progression.response(406, "Incorrect parameter")
    @ns_progression.response(500, "Database Error")
    def get(self, subject, student):
        """
        Consult the last lesson  activity of the student on a specific subject 
        
        ### Description
        
        Expose the table `student_lessons` given the student and the dataset that corresponds to the subject
        
        Student_lesson is built upon datasets that have a lesson level
        
                
        ### Documentation
  
		Consult [progression documentation](http://doc.ludoeducation.fr/researcher-guide/progression/)
        
        ### Output example
        
        ```json
        
        ```
        """
        if int(student) not in range(111, 60821):
            raise abort(406, "L'identifiant de l'élève  `{}` est incorrect. Vérifiez son identifiant".format(student))
        if student not in db.students.distinct("student"):
            raise abort(404, "L'élève `{}` n'a pas été trouvé".format(student))
        if subject == "letters":
            subject_name = "Français"
            dataset = "gp"
        else:
            subject_name = "Maths"
            dataset = "numbers"
        lessons = db.student_lessons.find_one({"student": student, "dataset": dataset}, {"_id":0, "lessons":0}) 
        last_lesson_id = lessons["lesson_ids"][-1]
        if len(chapters) == 0:
            raise abort(404, "Pas de données pour l'étudiant {} sur le sujet {}".format(student, subject))
        last_lesson = db.student_lesson.find_one({"student": student, "dataset": dataset, "lesson":last_lesson_id}, {"_id":0, "records":0})
        last_lesson["start"] = convert_datetime_to_str(last_chapter["start"]) 
        last_lesson["end"] = convert_datetime_to_str(last_chapter["end"])
        return {
                    "type": "last_lesson",
                    "last_lesson": last_chapter,
                    "data": last_chapter, 
                    "dataset": dataset, 
                    "subject": subject, 
                    "subject_name": subject_name, 
                    "student": student,
                    "csv": "{}/csv".format(request.base_url),
                    "doc": "{}/docs/progression#last_lesson".format(request.url_root)
                }

@ns_progression.doc({"classroom": "An integer between 1 and 60", "subject": "A string in the included list ['numbers','letters' ]"})
@ns_progression.route("/lessons/classrooms/<int:classroom>/subjects/<string:subject>")
class ClassroomSubjectChapter(Resource):
    @ns_progression.response(200, 'Success')
    @ns_progression.response(404, 'No data')
    @ns_progression.response(406, "Incorrect parameter")
    @ns_progression.response(500, "Database Error")
    def get(self, classroom, subject):
        """ 
        View the classroom progression by student by lesson on a given subject 
        
        ### Description
        
        Expose the table `student_lessons` given the student and the dataset that corresponds to the subject        
        
        ### Methods

        See the complete documentation on method: htts://lab.driss.org/kalulu/docs/stats/progression.md
        
        ### Output example
        
        ```json
        
        ```
                
        ### Documentation
  
		Consult [progression documentation](http://doc.ludoeducation.fr/researcher-guide/progression/)
        """
        db = connect()
        if int(classroom) not in range(1, 60):
            raise abort(406, "L'identifiant de la classe `{}` est incorrect, vérifiez votre identifiant.".format(classroom))
        if int(classroom) not in db.students.distinct("classroom"):
            raise abort(404, "La classe `{}` n'a pas été trouvée".format(classroom))
        if subject not in ["letters", "numbers"]:
            raise abort(406, "Le sujet `{}` n'existe pas encore.".format(subject))
        if subject == "letters":
            subject_name = "Français"
            dataset = "gp"
        else:
            subject_name = "Maths"
            dataset = "numbers"
        dataset_ref = db.datasets.find_one({"dataset": dataset})
        if dataset_ref is None:
            raise abort(406, "Le nom du dataset `{}` est incorrect.".format(dataset))
        else:
            if dataset_ref["subject"] == "letters":
                subject_name = "lettres"
            else:
                subject_name = "nombres"
        lessons_refs = list(db.path.find({"dataset": dataset}, {"_id":0}))
        class_lessons = list(db.student_lessons.find({"classroom": classroom, "dataset": dataset}, {"_id":0, "lessons":0}))
        if len(class_lessons) == 0:
            raise abort(404, "Pas de données pour la classe {} sur le sujet {}.".format(classroom, subject))
        return {
                    "title": "Progression des élèves de la classe {} en {}.".format(classroom, subject_name),
                    "y_label": "Elèves",
                    "chapter_label": "Jardins",
                    "x_label": "Défis réalisés sur le chemin des {}".format(subject_name),
                    "x_axis_labels": [l["tag"] for l in lessons_refs],
                    "x_axis_index": [l["lesson"] for l in lessons_refs],
                    "chapter_labels": [l["chapter"] for l in lessons_refs],
                    "chapter_colors": [CHAPTER_COLORS[int(l["chapter"])] for l in lessons_refs],
                    "y_axis_labels": [n["student"] for n in class_lessons],
                    "y_axis_index": [n[0] for n in enumerate(class_lessons)],
                    "legend": '''Progression des élèves en {}.Chaque point représente une lesson validée. La couleur du point correspond à son score comparé à l'ensemble des élèves: - rouge: pourcentage de bonnes réponses < 2 écarts-types de la médiane. - orange : < 1 écart-type - vert: >= 1 écart-type'''.format(subject_name),
                    "data": class_lessons, 
                    "dataset": dataset, 
                    "subject":dataset_ref["subject"], 
                    "subject_name": subject_name, 
                    "classroom": classroom,
                    "csv": "{}/csv".format(request.base_url),
                    "doc": '''
                        Ce graphique représente la progression de chaque élève de la classe en {}:
                        - les élèves sont ordonnés par numéro de tablette puis par numéro
                        - chaque point correspond à une leçon completée
                        - chaque leçon est coloré en fonction du score de bonne réponse par comparaison avec l'ensemble des scores de bonne réponses pour cette leçon</li> 
                        
                        La couleur de la leçon correspond au score de bonne réponse de l'élève par rapport 
                        à l'ensemble des élèves (toute classe confondue) ayant complété cette même leçon.
                        
                        - Un point vert: le score de bonne réponse pour cette leçon est supérieur ou égal au score moyen pour cette leçon
                        - Un point orange: le score de bonne réponse pour cette leçon est inférieur au score moyen pour cette leçon
                        - Un point rouge: le score de bonne réponse pour cette leçon est deux fois inférieur au score moyen pour cette leçon
                        '''.format(subject_name)
            }
        
