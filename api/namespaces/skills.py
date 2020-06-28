from flask_restx import Namespace, Resource, abort
from flask import request
import time
from utils.db import connect

ns_letters = Namespace('letters', description='Consult skills on letters')
ns_numbers = Namespace('numbers', description='Consult skills on numbers')

db = connect()

@ns_letters.route("/words")
class WordsList(Resource):
    @ns_letters.response(200, 'Success')
    @ns_letters.response(404, 'No data')
    @ns_letters.response(406, "Incorrect parameter")
    @ns_letters.response(500, "Database Error")
    def get(self):
        """
        Consult all the words effectively seen by students in the game

        ### Methods
        Table words is created with script db/stats/words.py
        
        ```sql
 	    FROM student_words
        group words, along with their nb_letters
        sum nb_records
        calculate AVG(median_time_reaction, %CA, nb_records
        insert unique [student, student, ...] 
        insert unique [classroom, classroom, ...]       
        OUT words
        ```
        ### Output example
        ```
        {
            "subject": "letters",
            "subject_name": "Fran\u00e7ais",
            "type": "words",
            "words": [
                {
                    "word": "demi",
                    "avg_%CA": 56.69098870056497,
                    "nb_students": 354,
                    "nb_records": 982,
                    "avg_time_reaction": 2.3198094717514124
                },
                {
                    "word": "lit",
                    "avg_%CA": 55.00021238938053,
                    "nb_students": 565,
                    "nb_records": 1753,
                    "avg_time_reaction": 2.3354187203539825
                },
                {
                    "word": "bazar",
                    "avg_%CA": 64.48783018867924,
                    "nb_students": 106,
                    "nb_records": 238,
                    "avg_time_reaction": 2.177630712264151
                },
                ...
                ],
            "data": [
                {
                    "word": "demi",
                    "nb_letters": 4,
                    "avg_%CA": 56.69098870056497,
                    "nb_records": 982,
                    "avg_nb_records": 2.774011299435028,
                    "avg_time_reaction": 2.3198094717514124,
                    "nb_students": 354,
                    "nb_classrooms": 38
                },
                ...
            ]
        }
        ```

  		## Documentation
  		
    	Consult [skills documentation](http://doc.ludoeducation.fr/researcher-guide/letters/)
        """
        if db.words.count() == 0:
            return abort(500, "La table words est vide")
        raw_words = list(db.words.find({}, {"_id":0}))      
        words = [{"word":n["word"], "avg_%CA":n["avg_%CA"], "nb_students": n["nb_students"], "nb_records":n["nb_records"], "avg_time_reaction": n["avg_time_reaction"]} for n in raw_words]
        return {
            "subject": "letters",
            "subject_name": "Français",
            "title": "Les mots présentés à la classe",
            "type": "words",
            "words": words,
            "data": raw_words,
            "csv": "{}/csv".format(request.base_url),
            "doc": "Liste des mots vus par la classe"
        }

@ns_letters.doc(params={
    'student': 'An integer between 111 and 60820'})
@ns_letters.route("/words/students/<int:student>")
class StudentWordsList(Resource):
    @ns_letters.response(200, 'Success')
    @ns_letters.response(404, 'No data')
    @ns_letters.response(406, "Incorrect parameter")
    @ns_letters.response(500, "Database Error")
    def get(self, student):
        """
        Consult the words seen by a student
        
        ### Methods

        Table student_words is created with script db/stats/words.py
        
        ```sql
        FROM student_tag 
	    filter out dataset (gapfill_lang and assessments_language)
	    filter out tag that has type="word" in db.path table
	    filter out only words that have been clicked and have then an elapsedTime set (not -1)
	    insert the scores into student_words table
	    add color for each word (0.25 red, 0.50 orange, 0.75 green) 
        OUT student_words
        ```
        
        ### Output example
        ```json
        {
            "student": 112,
            "type": words,
            "subject": "letters",
            "subject_name: "Français", 
            "words": [
                    {
                    "word": "allé",
                    "%CA": 62.5,
                    "color": "orange"
                    },
                    {
                    "word": "ami",
                    "%CA": 33.33,
                    "color": "red"
                    },
                    ...
            ],
            "data": [
                {
                    "%CA": 83.33,
                    "nb_letters": 4,
                    "type": "word",
                    "median_time_reaction": 1.0619675000000002,
                    "classroom": 1,
                    "word": "all\u00e9",
                    "CA": 5,
                    "nb_records": 6,
                    "student": 112,
                    "color": "green"
                },
                {
                    "%CA": 0.0,
                    "nb_letters": 3,
                    "type": "word",
                    "median_time_reaction": 1.6829735000000001,
                    "classroom": 1,
                    "word": "ami",
                    "CA": 0,
                    "nb_records": 6,
                    "student": 112,
                    "color": "red"
                },
                ...
            ]
        }
        ```
        
  		## Documentation
  		
    	Consult skills documentation http://doc.ludoeducation.fr/researcher-guide/letters/
        """
        try:
            student = int(student)
        except ValueError:
            return abort(406, "L'identifiant de l'élève {} est incorrect".format(student)) 
        if student not in range(111, 60820):
            return abort(406, "L'identifiant de l'élève {} est incorrect".format(student))
        if int(student) not in db.students.distinct("student"):
            return abort(404, "L'élève {} n'existe pas".format(student))
        if db.student_words.count() == 0:
            return abort(500, "La table student_words est vide")
        raw_student_words = list(db.student_words.find({"student": student, "type": "word"}, {"_id":0, "records":0}))
        student_words = [{"word":n["word"], "%CA":n["%CA"], "color": n["color"], "nb_records":n["nb_records"]} for n in raw_student_words]
        if len(student_words) == 0:
            return abort(404, "L'élève {} n'a pas encore vu de mots".format(student), title="Mots")
        return {
            "title": "mots",
            "nb_records": len(student_words),
            "type": "words", 
            "student": student,
            "subject": "letters",
            "subject_name": "Français",
            "words": student_words,
            "data": raw_student_words,
            "csv": "{}/csv".format(request.base_url),
            "doc": '''
            Tous les mots vus par l'élève : Voici une liste de mots que nous avons proposé de lire à l’élève au cours des jeux « les fourmis » et « le poisson ». La liste de mots est composée de deux couleurs. En vert, l’enfant a lu correctement le dernier mot vu. En orange, l’enfant ne maîtrise pas encore le mot.
            '''
        }

@ns_letters.doc(params={
    'student': 'An integer between 111 and 60820'})
@ns_letters.route("/syllabs/students/<int:student>")
class StudentSyllabsList(Resource):
    @ns_letters.response(200, 'Success')
    @ns_letters.response(404, 'No data')
    @ns_letters.response(406, "Incorrect parameter")
    @ns_letters.response(500, "Database Error")
    def get(self, student):
        """
        Consult the syllabs seen by a student

        ### Methods
 
        Table student_words is created with script db/stats/words.py
        
        ```sql
        FROM records
        SELECT records WHERE dataset='gp' AND WHERE '.' in record[target] or '.' in record[stimulus] AND WHERE group != "guest" 
        GROUP BY classroom, student, target
        SUM nb_records, CA
        ADD [stimulus, stimulus,...]
        CALCULATE %CA, color(%CA), word
        OUT student_syllabs
        ```

        ### Output example
        ```json
        {
            "student": 112,
            "type": "syllabs",
            "subject": "letters",
            "subject_name": "Fran\u00e7ais",
            "syllabs": [
                {
                    "word": "une",
                    "syllab": "u-y.n-n.e-#",
                    "%CA": 100.0,
                    "nb_records": 3,
                    "color": "green"
                },
                {
                    "word": "qua",
                    "syllab": "qu-k.a-a",
                    "%CA": 85.71,
                    "nb_records": 42,
                    "color": "green"
                },
                {
                    "word": "ve",
                    "syllab": "v-v.e-%",
                    "%CA": 100.0,
                    "nb_records": 4,
                    "color": "green"
                }, 
                ...
            ],
            "data":[
                {
                    "classroom": 1,
                    "student": 112,
                    "group": "r/m",
                    "dataset": "gp",
                    "syllab": "u-y.n-n.e-#",
                    "stimuli": [
                        "u-y.n-n.e-#"
                    ],
                    "CA": 3,
                    "nb_records": 3,
                    "%CA": 100.0,
                    "color": "green",
                    "word": "une"
                },
                {
                    "classroom": 1,
                    "student": 112,
                    "group": "r/m",
                    "dataset": "gp",
                    "syllab": "qu-k.a-a",
                    "stimuli": [
                        "",
                        "qu-k.a-a",
                        "o-O.r-R",
                        "gu-g.\u00e9-e"
                    ],
                    "CA": 36,
                    "nb_records": 42,
                    "%CA": 85.71,
                    "color": "green",
                    "word": "qua"
                },
                {
                    "classroom": 1,
                    "student": 112,
                    "group": "r/m",
                    "dataset": "gp",
                    "syllab": "v-v.e-%",
                    "stimuli": [
                        "v-v.e-%"
                    ],
                    "CA": 4,
                    "nb_records": 4,
                    "%CA": 100.0,
                    "color": "green",
                    "word": "ve"
                },
                ...
            ]
        }
        ```
        
  		## Documentation
  		
    	Consult skills documentation http://doc.ludoeducation.fr/researcher-guide/letters/
        """
        try:
            student = int(student)
        except ValueError:
            return abort(406, "L'identifiant de l'élève {} est incorrect".format(student))

        if db.student_syllabs.count() == 0:
            return abort(500, "La table student_syllabs est vide")        
        if student not in range(111, 60820):
            return abort(406, "L'identifiant de l'élève {} est incorrect".format(student))
        if int(student) not in db.students.distinct("student"):
            return abort(404, "L'élève {} n'existe pas".format(student))
        raw_syllabs = list(db.student_syllabs.find({"student": student}, {"_id":0, "records":0}))
        syllabs = [
            {"word":n["word"], "syllab": n["syllab"],  "%CA": n["%CA"], "nb_records":n["nb_records"], "color":n["color"]} 
            for n in raw_syllabs
        ]

        if len(raw_syllabs) == 0:
            return abort(404, "L'élève {} n'a pas encore vu de syllabes".format(student), title="Syllabes")
        return {
            "title": "syllabes",
            "nb_records": len(syllabs),
            "student": student,
            "type": "syllabs", 
            "subject": "letters",
            "subject_name": "Français",
            "syllabs": syllabs,
            "data": raw_syllabs,
            "csv": "{}/csv".format(request.base_url),
            "doc": '''
            Toutes les syllabes vues par l'élève : Voici une liste de mots que nous avons proposé de lire à l’élève au cours des jeux « les fourmis » et « le poisson ». La liste de mots est composée de deux couleurs. En vert, l’enfant a lu correctement le dernier mot vu. En orange, l’enfant ne maîtrise pas encore le mot.'''

        }
@ns_numbers.doc(params={
    'student': 'An integer between 111 and 60820'})
@ns_numbers.route("/identification/students/<int:student>")
class StudentDigitsIdItem(Resource):
    @ns_numbers.response(200, 'Success')
    @ns_numbers.response(404, 'No data')
    @ns_numbers.response(406, "Incorrect parameter")
    @ns_numbers.response(500, "Database Error")
    def get(self, student):
        """
        Consult the result on identification numbers games
        
        ### Methods
        
        Table student_identification is created with script db/stats/digits.py
        
        ```sql
        FROM records 
        WHERE dataset='numbers' and game matchs [crabs, jellyfish]
        GROUP BY student, subject, subject
        FILTER timespent != -1
        CREATE timespents [timespent, timespent, ...]
        
        CREATE games unique[game, game, ...] 
        CREATE tags unique [tag, tag, ...]
        SUM score, nb_records
        CALCULATE %CA, color(%CA)
        OUT student_identification
        ```
        ### Output
        ```json
            {
                "type": identification,
                "subject": "numbers",
                "subject_name": "Maths",
                "student": 3284,
                "classroom": 32,
                "data": [{
                    "games" : [
                        "crabs"
                    ],
                    "score" : 2308,
                    "nb_records" : 2695,
                    "student" : 3284,
                    "subject" : "numbers",
                    "dataset" : "numbers",
                    "timespent" : 2489.583685,
                    "%CA" : 85.64,
                    "color" : "green"
                    }],
                "identification": [
                    {
                        "games" : ["crabs"],
                        "%CA" : 85.64,
                        "color" : "green",
                        "timespent": "00:02:56",       
                    }
                ]
            }
        ```
        
  		## Documentation
  		
    	Consult [skills documentation](http://doc.ludoeducation.fr/researcher-guide/numbers/)
        """
        try:
            student = int(student)
        except ValueError:
            return abort(406, "L'identifiant de l'élève {} est incorrect".format(student))
        if student not in range(111, 60821):
            abort(406, "L'identifiant de l'élève {} est incorrect".format(student))
        if int(student) not in db.students.distinct("student"):
            return abort(404, "L'élève {} n'existe pas".format(student))
        if db.student_identification.count() == 0:
            return abort(500, "La table student_identification est vide")
        student_digits = db.student_identification.find_one({"student": student}, {"_id": 0})
        if student_digits is None:
            return abort(404, "L'élève n'a pas encore identifié de nombres", title= "J'entends et je trouve")
        return {
            "type": "identification", 
            "title": "J'entends et je trouve",
            "student": student,
            "subject": "numbers",
            "img": ["jellyfish", "crab"],
            "imgs": [("/src/assets/img/gauge_icon_jellyfish_full.png", 150),("/src/assets/img/gauge_icon_crab_full.png", 150)],
            "subject_name": "Maths",
            "classroom": student_digits["classroom"],
            "data": [student_digits],
            "identification": [{"games":student_digits["games"],"%CA":student_digits["%CA"], "timespent":time.strftime('%H:%M:%S', time.gmtime(student_digits["timespent"])), "color": student_digits["color"]}],  
            "csv": "{}/csv".format(request.base_url),
            "doc": '''Dans les jeux des crabes et des pieuvres, l’enfant doit associer la dénomination d’un nombre avec le nombre écrit ou la quantité dans sa forme symbolique (un dé). Voici le taux de réussite de l’enfant pour cette compétence.'''
        }
@ns_numbers.route("/association/students/<int:student>")
class StudentAssociationIdItem(Resource):
    @ns_numbers.response(200, 'Success')
    @ns_numbers.response(404, 'No data')
    @ns_numbers.response(406, "Incorrect parameter")
    @ns_numbers.response(500, "Database Error")
    def get(self, student):
        """
        Consult the result on association numbers games
        
        ### Methods
        
        Table student_association is created with script db/stats/digits.py
        
        ```sql
        FROM records 
        WHERE dataset='numbers' and game matchs [turle, ants]
        GROUP BY student, subject, subject
        FILTER timespent != -1
        CREATE timespents [timespent, timespent, ...]
        
        CREATE games unique[game, game, ...] 
        CREATE tags unique [tag, tag, ...]
        SUM score, nb_records
        CALCULATE %CA, color(%CA)
        OUT student_identification
        ```
        ### Output
        ```json
            {
                "type": identification,
                "subject": "numbers",
                "subject_name": "Maths",
                "student": 3284,
                "classroom": 32,
                imgs: []
                "data": [{
                    "games" : [
                        "crabs"
                    ],
                    "score" : 2308,
                    "nb_records" : 2695,
                    "student" : 3284,
                    "subject" : "numbers",
                    "dataset" : "numbers",
                    "timespent" : 2489.583685,
                    "%CA" : 85.64,
                    "color" : "green"
                    }],
                "identification": [
                    {
                        "games" : ["crabs"],
                        "%CA" : 85.64,
                        "color" : "green",
                        "timespent": "00:02:56",       
                    }
                ]
            }
        ```
        
  		## Documentation
  		
    	Consult skills documentation : http://doc.ludoeducation.fr/researcher-guide/numbers/
        """
        try:
            student = int(student)
        except ValueError:
            return abort(406, "L'identifiant de l'élève {} est incorrect".format(student))
        if student not in range(111, 60821):
            abort(406, "L'identifiant de l'élève {} est incorrect".format(student))
        if int(student) not in db.students.distinct("student"):
            return abort(404, "L'élève {} n'existe pas".format(student))
        if db.student_association.count() == 0:
            return abort(500, "La table student_identification est vide")
        student_digits = db.student_association.find_one({"student": student}, {"_id": 0})
        if student_digits is None:
            return abort(404, "L'élève n'a pas encore identifié de nombres", title="J'associe un nombre avec une quantité")
        return {
            "type": "association", 
            "student": student,
            "subject": "numbers",
            "title": "J'associe un nombre avec une quantité",
            "img": ["ant","turle"],
            "imgs": [("/src/assets/img/gauge_icon_ant_full.png", 150),("/src/assets/img/gauge_icon_turtle_full.png", 150)],
            "subject_name": "Maths",
            "classroom": student_digits["classroom"],
            "data": [student_digits],
            "association": [{"games":student_digits["games"],"%CA":student_digits["%CA"], "timespent":time.strftime('%H:%M:%S', time.gmtime(student_digits["timespent"])), "color": student_digits["color"]}],  
            "csv": "{}/csv".format(request.base_url),
            "doc": '''Dans les jeux des crabes et des pieuvres, l’enfant doit associer la dénomination d’un nombre avec le nombre écrit ou la quantité dans sa forme symbolique (un dé). Voici le taux de réussite de l’enfant pour cette compétence.'''
        }
@ns_numbers.doc(params={
    'student': 'An integer between 111 and 60820'})
@ns_numbers.route("/counting/students/<int:student>")
class StudentDigitsCountingItem(Resource):
    @ns_numbers.response(200, 'Success')
    @ns_numbers.response(404, 'No data')
    @ns_numbers.response(406, "Incorrect parameter")
    @ns_numbers.response(500, "Database Error")
    def get(self, student):
        """
        Consult the result on counting digits game specifying student id
        
        
        ### Methods

        Table student_counting is created with script db/stats/digits.py
        
        ```
        FROM records 
        WHERE dataset='numbers' and game matchs [caterpillar]
        GROUP BY student, subject, subject
        FILTER timespent != -1
        CREATE timespents [timespent, timespent, ...]
        CREATE games unique[game, game, ...] 
        CREATE tags unique [tag, tag, ...]
        SUM score, nb_records
        CALCULATE %CA, color(%CA)
        OUT student_counting
        ```
        ### OUTPUT
        ```json
            {
                "type": identification,
                "subject": "numbers",
                "subject_name": "Maths",
                "student": 3284,
                "classroom": 32,
                "data": [{
                    "games" : [
                        "crabs"
                    ],
                    "score" : 2308,
                    "nb_records" : 2695,
                    "student" : 3284,
                    "subject" : "numbers",
                    "dataset" : "numbers",
                    "timespent" : 2489.583685,
                    "%CA" : 85.64,
                    "color" : "green"
                    }],
                "identification": [
                    {
                        "games" : ["crabs"],
                        "%CA" : 85.64,
                        "color" : "green",
                        "timespent": "00:02:56",
                    }
                ]
            }
        
  		## Documentation
  		
    	Consult [skills documentation](http://doc.ludoeducation.fr/researcher-guide/numbers/)
        """
        try:
            student = int(student)
        except ValueError:
            return abort(406, "L'identifiant de l'élève {} est incorrect".format(student))
        if student not in range(111, 60820):
            return abort(406, "L'identifiant de l'élève {} est incorrect".format(student))
        if student not in db.students.distinct("student"):
            return abort(404, "L'élève {} n'existe pas".format(student))
        if db.student_counting.count() == 0:
            return abort(500, "La table student_counting est vide")
        student_digits = db.student_counting.find_one({"student": student}, {"_id": 0})
        if student_digits is None:
            return abort(404, "L'élève n'a pas encore compté de nombres", title="Je compte")
        return {
            "type": "counting",
            "title": "Je compte",
            "student": student,
            "classroom": student_digits["classroom"],
            "img": ["caterpillar"],
            "imgs": [("/src/assets/img/gauge_icon_caterpillar_full.png", 300)],
            "subject": "numbers",
            "subject_name": "Maths",
            "data": [student_digits],
            "counting": [
                {
                    "games":student_digits["games"],
                    "%CA":student_digits["%CA"], 
                    "timespent": time.strftime('%H:%M:%S', time.gmtime(student_digits["timespent"])), 
                    "color": student_digits["color"]    
                }
            ],  
            "csv": "{}/csv".format(request.base_url),
            "doc": '''Dans le jeu de la chenille, l’enfant doit compter et trouver la suite numérique. Par exemple, l’enfant peut commencer avec le nombre 30 et il lui est demandé de compter et trouver la suite numérique jusqu’à 35. Voici le taux de réussite de l’enfant pour cette compétence.''',
        }
        