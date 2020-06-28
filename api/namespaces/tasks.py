from flask_restx import Namespace, Resource, abort
from flask import request
from utils.db import connect

ns_tasks = Namespace('tasks', description='Consult specific tasks on the game: confusion, decision')
db = connect()

@ns_tasks.doc({
    "student": "An integer between 111 and 60820",
    "subject": "A string included in ['letters', 'numbers']",
    })
@ns_tasks.route("/confusion/students/<student>/subjects/<string:subject>")
class StudentConfusionMatrix(Resource):
    @ns_tasks.response(200, 'Success')
    @ns_tasks.response(404, 'No data')
    @ns_tasks.response(406, "Incorrect parameter")
    @ns_tasks.response(500, "Database Error")
    def get(self, student, subject):
        """
        Confusion matrix by student by subject
        
        ### Description
        
        Display confusion matrix on given subject by chapter
        each target and stimulus with CA_rate (confusion rate between 0 to 1)
        confusion_rate = 1 always confuse
        confusion_rate = 0 identifies correctly

        ### Methods
        
        From student_confusion_matrix TABLE
        SELECT student and SUBJECT
        For extensive documentation see in docs /stats/confusion

  		## Documentation
  		
    	Consult [tasks documentation](http://doc.ludoeducation.fr/researcher-guide/tasks/)
        """
        try:
            student = int(student)
        except ValueError:
            # print(student)
            return abort(406, "L'identifiant de l'élève {} est incorrect.".format(student))
        # student = int(student)
        if db.student_confusion_matrix.count() == 0:
            return abort(500, "Table student_confusion_matrix is empty.")
        if student not in range(111, 60821):
            return abort(406, "L'identifiant de l'élève {} est incorrect.".format(student))
        if student not in db.student_confusion.distinct("student"):
            return abort(406, "L'identifiant de l'élève {} est incorrect.".format(student))
        if subject not in ["letters", "numbers"]:
            return abort(406, "Le sujet {} est incorrect.".format(subject))
        documents = db.student_confusion_matrix.count({"student":student, "subject": subject})
        if documents == 0:
            return abort(
                404, 
                "Pas de données disponibles pour l'élève {} et le sujet {}.".format(student, subject))
        if subject == "letters":
            subject_name = "Français"
            title = "Lettres"
            CV = ["V", "C"]
            titles = ["Voyelles", "Consonnes"]
            raw_confusion = [
                sorted(list(db.student_confusion_matrix.find({"student": student, "subject": "letters", "CV": "V"},{"_id": 0})), key=lambda x: x["chapter"]),
                sorted(list(db.student_confusion_matrix.find({"student": student, "subject": "letters", "CV":"C"},{"_id": 0})), key=lambda x: x["chapter"])
            ]
            doc = """

Les deux matrices ci-dessous représentent la maîtrise et les confusions entre les correspondances graphème-phonème « cibles » et leurs « distracteurs ». Par exemple, dans le jeux « la grenouille », si l’enfant doit écrire le mot “chat”, il commence par chercher le graphème “ch”. Sur l’écran il voit défiler le “ch” mais aussi les distracteurs ‘f’ et ‘v’. Pour toutes les possibilités entre le choix cible et le choix distracteur, nous mesurons la réponse de l’enfant.


Les matrices sont séparées en voyelles et consonnes car, dans Kalulu, les consonnes sont uniquement distracteurs pour les consonnes et les voyelles sont uniquement distracteur pour les voyelles. Dans l’exemple du ‘ch’ dans le mot ‘chat’, les distracteurs proposés seront toujours des consonnes.


Sur l’axe X (horizontal) sont représentés les correspondances graphème-phonème « cible »

Sur l’axe Y (vertical) sont représentés les correspondances graphème-phonème « distracteur »


Dans le graphique :

Sur la diagonale est représenté le taux de réponse pour une cible. Ce taux de réponse représente la réussite de l’enfant à toucher la cible chaque fois qu’elle est présentée.  Si par exemple, on présente à l’enfant deux fois la cible (par exemple, le ‘ch’ dans le mot “chat”) mais qu’il ne la touche que la troisième fois, son taux de réponse sera de 33%, et la case sera de plus en plus rouge. Cela signifie que l’enfant est encore hésitant dans sa réponse. Dans le jeu, l’enfant n’est pas pénalisé mais ces informations peuvent vous être pertinentes. Si l’enfant touche rapidement la bonne réponse, la case est blanche. L’enfant maîtrise donc la correspondance.


En dehors de la diagonale, sont représentés les taux de réponses entre la cible et les distracteurs. Si l’enfant touche un distracteur, la case représentant cette correspondance cible-distracteur est de plus en plus rouge. Si l’enfant évite le distracteur, la case reste blanche.

Les cases grises représentent des combinaisons que l’enfant n’a jamais vu.
			"""
            try:
                chapters = sorted(set([n["chapter"] for n in raw_confusion[0]] + [n["chapter"] for n in raw_confusion[1]]))
                confusion = [
                    {
                        "chapters":sorted([n["chapter"] for n in raw_confusion[0]]), 
                        "title":"Voyelles",
                        "CV":"V", 
                        "xaxis": raw_confusion[0][0]["xaxis"],
                        "yaxis": raw_confusion[0][0]["yaxis"],
                        "xaxis_label": raw_confusion[0][0]["xaxis_label"],
                        "yaxis_label": raw_confusion[0][0]["yaxis_label"],
                        "data": raw_confusion[0],
                        "doc": doc
                    },
                    {
                        "chapters":sorted([n["chapter"] for n in raw_confusion[1]]), 
                        "title":"Consonnes",
                        "CV":"C", 
                        "xaxis": raw_confusion[1][0]["xaxis"],
                        "yaxis": raw_confusion[1][0]["yaxis"],
                        "xaxis_label": raw_confusion[1][0]["xaxis_label"],
                        "yaxis_label": raw_confusion[1][0]["yaxis_label"],
                        "data": raw_confusion[1],
                        "doc": doc
                    }
                ]

                
            except IndexError:
                chapters = sorted(set([n["chapter"] for n in raw_confusion[0]]))
                confusion = [
                    {
                        
                        "chapters":[n["chapter"] for n in raw_confusion[0]], 
                        "title":"Voyelles",
                        "CV":"V", 
                        "xaxis": raw_confusion[0][0]["xaxis"],
                        "yaxis": raw_confusion[0][0]["yaxis"],
                        "xaxis_label": raw_confusion[0][0]["xaxis_label"],
                        "yaxis_label": raw_confusion[0][0]["yaxis_label"],
                        "data": raw_confusion[0],
                        "doc": doc
                    },
                    {
                        "chapters":[n["chapter"] for n in raw_confusion[0]], 
                        "title":"Consonnes",
                        "CV":"C", 
                        "xaxis": [],
                        "yaxis": [],
                        "xaxis_label": raw_confusion[0][0]["xaxis_label"],
                        "yaxis_label": raw_confusion[0][0]["yaxis_label"],
                        "data": [],
                        "doc": doc
                    }
                ]
        else:
            subject_name = "Maths"
            title = "Nombres"
            CV = ["N"]
            titles = ["Nombres"]
            raw_confusion = [
                sorted(list(db.student_confusion_matrix.find({"student": student, "subject": "numbers", "CV": "N"},{"_id": 0})), key=lambda x: x["chapter"]),
            ]
            chapters = sorted(set([n["chapter"] for n in raw_confusion[0]]))
            doc = '''
			La matrice ci-dessous représente la maîtrise et les confusions entre les nombres « cibles » et leurs « distracteurs ». Par exemple, dans le jeux « la chenille », si l’enfant doit trouver la suite numérique “4,5,6,7”, il commence par chercher le chiffre “4”. Sur l’écran il voit défiler le ‘4’ mais aussi les distracteurs ‘3’ et ‘5’. Pour toutes les possibilités entre le choix cible et le choix distracteur, nous mesurons la réponse de l’enfant.
Sur l’axe X (horizontal) sont représentés les nombres « cibles »
Sur l’axe Y (vertical) sont représentés les nombres « distracteurs »

Dans le graphique :
Sur la diagonale est représenté le taux de réponse pour une cible. Ce taux de réponse représente la réussite de l’enfant à toucher la cible chaque fois qu’elle est présentée.  Par exemple, si on présente à l’enfant deux fois la cible ‘4’ dans la suite numérique “4,5,6,7” mais qu’il ne la touche que la troisième fois, son taux de réponse sera de 33%, et la case sera de plus en plus rouge. Cela signifie que l’enfant est encore hésitant dans sa réponse. Dans le jeu, l’enfant n’est pas pénalisé mais ces informations peuvent vous être pertinentes. Si l’enfant touche rapidement la bonne réponse, la case est blanche. L’enfant maîtrise donc le nombre.

En dehors de la diagonale, sont représentés les taux de réponses entre la cible et les distracteurs. Si l’enfant touche un distracteur, la case représentant cette correspondance cible-distracteur est de plus en plus rouge. Si l’enfant évite le distracteur, la case reste blanche.

Les cases grises représentent des combinaisons que l’enfant n’a jamais vu.

			'''
            confusion = [
                    {
                        "chapters":sorted([n["chapter"] for n in raw_confusion[0]]), 
                        "title":"Nombres",
                        "CV":"N", 
                        "xaxis": raw_confusion[0][0]["xaxis"],
                        "yaxis": raw_confusion[0][0]["yaxis"],
                        "xaxis_label": raw_confusion[0][0]["xaxis_label"],
                        "yaxis_label": raw_confusion[0][0]["yaxis_label"],
                        "data": raw_confusion[0],
                        "doc": doc
                    },
                    
            ]
        # print(raw_confusion[0])
        return {
            "type":"confusion",
            "student": student,
            "subject": subject,
            "title": title,
            "CV": CV,
            "titles": titles,
            "subject_name": subject_name,
            "chapters": chapters,
            "confusion": confusion,
            "csv": "{}/csv".format(request.base_url),
            "doc": doc
        }


@ns_tasks.doc({
    "subject": "A string included in ['letters', 'numbers']",
    })
@ns_tasks.route("/confusion/subjects/<string:subject>")
class ConfusionMatrix(Resource):
    @ns_tasks.response(200, 'Success')
    @ns_tasks.response(404, 'No data')
    @ns_tasks.response(406, "Incorrect parameter")
    @ns_tasks.response(500, "Database Error")
    def get(self, subject):
        """
        Confusion matrix by subject
        
        ### Description
        
        Display confusion matrix on given subject by chapter
        each target and stimulus with CA_rate (confusion rate between 0 to 1)
        Confusion_rate :1 always confuse
        Confusion_rate :0 identifies correctly
        
        ### Methods
        
        From confusion_matrix table
        SELECT SUBJECT

        
  		## Documentation
  		
    	Consult [tasks documentation](http://doc.ludoeducation.fr/researcher-guide/tasks/)
        
        """
        if db.confusion_matrix.count() == 0:
            return abort(500, "Table confusion_matrix is empty.")
        if subject not in ["letters", "numbers"]:
            return abort(406, "Le sujet {} est incorrect.".format(subject))
        if subject == "letters":
            subject_name = "Français"
            title = "Lettres"
            CV = ["V", "C"]
            doc = '''
			Ce graphique représente les notions (graphème/phonème) les plus sujettes à confusion
             
            sous la forme de deux matrices: Les Voyelles et les Consonnes. 
            
            Chaque notion abordée apparait selon l'ordre des leçons définie par la progression pédagogique.  
            
            Le jeu consiste à sélectionner le bon graphème/phonème parmi 3 valeurs proposées.
            
            Sur l'axe horizontal, les notions qui s'affichent à l'écran et on été proposées à l'élève. (Stimulus)
            
            Sur l'axe vertical, les notions ciblées qui sont abordées et soumises au test. (Cible) 
            
            Pour définir s'il y a confusion, on calcule le nombre de mauvaises réponses par rapport au total de réponses 
            pour la combinaison entre la valeur testée et la valeur proposée qui donne un taux de confusion.
            
            - S'il y a confusion complète le taux de confusion est de 1, la case est alors rouge.
            
            - S'il n'y a aucune confusion, le taux de confusion est de 0, la case est alors blanche.
            
            Une gradation de couleur du blanc et au rouge permet de visualiser le degré de confusion.
            
            La case est grise quand cette combinaison de graphème/phonème n'a pas été proposée.
			'''
            titles = ["Voyelles", "Consonnes"]
            raw_confusion = [
                list(db.confusion_matrix.find({"subject": "letters", "CV": "V"},{"_id": 0})),
                list(db.confusion_matrix.find({"subject": "letters", "CV":"C"},{"_id": 0}))
            ]
            confusion = [
                {
                    # "chapters":list(set([n["chapter"] for n in raw_confusion[0]])), 
                    "title":"Voyelles",
                    "CV":"V", 
                    "xaxis": raw_confusion[0][0]["xaxis"],
                    "yaxis": raw_confusion[0][0]["yaxis"],
                    "xaxis_label": raw_confusion[0][0]["xaxis_label"],
                    "yaxis_label": raw_confusion[0][0]["yaxis_label"],
                    "data": raw_confusion[0],
                    
                },
                {
                    # "chapters":list(set([n["chapter"] for n in raw_confusion[0]])), 
                    "title":"Consonnes","CV":"C", 
                    "xaxis": raw_confusion[1][0]["xaxis"],
                    "yaxis": raw_confusion[1][0]["yaxis"],
                    "xaxis_label": raw_confusion[1][0]["xaxis_label"],
                    "yaxis_label": raw_confusion[1][0]["yaxis_label"],
                    "data": raw_confusion[1],
                    
                }
            ]
            if len(raw_confusion) == 0:
                return abort(404, "Pas de données disponibles pourle sujet {}.".format(subject), title ="Lettres")
            
        else:
            subject_name = "Maths"
            title = "Nombres"
            CV = [None]
            doc =  '''
			Ce graphique représente les notions (nombres) les plus sujettes à confusion
             
            sous la forme d'une matrice Nombres. 
            
            Chaque notion abordée apparait selon l'ordre des leçons définie par la progression pédagogique.  
            
            Le jeu consiste à sélectionner le bon nombre parmi 3 valeurs proposées.
            
            Sur l'axe horizontal, les notions qui s'affichent à l'écran et on été proposées à l'élève. (Stimulus)
            
            Sur l'axe vertical, les notions ciblées qui sont abordées et soumises au test. (Cible) 
            
            Pour définir s'il y a confusion, on calcule le nombre de mauvaises réponses par rapport au total de réponses 
            pour la combinaison entre la valeur testée et la valeur proposée qui donne un taux de confusion.
            
            - S'il y a confusion complète le taux de confusion est de 1, la case est alors rouge.
            
            - S'il n'y a aucune confusion, le taux de confusion est de 0, la case est alors blanche.
            
            Une gradation de couleur du blanc et au rouge permet de visualiser le degré de confusion.
            
            La case est grise quand cette combinaison de graphème/phonème n'a pas été proposée.
			'''
            titles = ["Nombres"]
            raw_confusion = [
                sorted(list(db.confusion_matrix.find({"subject": "numbers"},{"_id": 0}))),
            ]
            
            confusion = [
                {
                    # "chapters":list(set([n["chapter"] for n in raw_confusion[0]])), 
                    "title":"Nombres",
                    "CV":"N", 
                    "xaxis": raw_confusion[0][0]["xaxis"],
                    "yaxis": raw_confusion[0][0]["yaxis"],
                    "xaxis_label": raw_confusion[0][0]["xaxis_label"],
                    "yaxis_label": raw_confusion[0][0]["yaxis_label"],
                    "data": raw_confusion[0],
                    
                }
            ]
        if len(raw_confusion) == 0:
            return abort(404, "Pas de données disponibles pour le sujet {}.".format(subject), title ="Nombres")
        else:
            # chapters = [n["chapter"] for n in raw_confusion[0]]
            # print(raw_confusion[0])
            return {
                "type":"confusion",
                "subject": subject,
                "title": title,
                "CV": CV,
                "titles": titles,
                "subject_name": subject_name,
                # "chapters": chapters,
                "confusion": confusion,
                # "data": raw_confusion,
                "csv": "{}/csv".format(request.base_url),
                "doc": doc
                }



@ns_tasks.doc({
    "student": "An integer between 111 and 60820",
    "subject": "A string caracter included in ['letters', 'numbers']",
    })
@ns_tasks.route("/decision/students/<int:student>/subjects/<subject>")
class StudentSubjectDecision(Resource):
    @ns_tasks.response(200, 'Success')
    @ns_tasks.response(400, 'Not found')
    @ns_tasks.response(406, "Not acceptable")
    @ns_tasks.response(500, "Database Error")
    def get(self, student, subject):
        '''
        Decision matrix by subject
        
        ### Description
        
        Display decision matrix on given subject
        
        ### Methods
        See docs.db.stats.decision.md
        
        ### Output
        ```json
            {
                "type": "decision",
                "student": 112,
                "subject": "letters",
                "subject_name": "Français",
                "title": "Reconnaissance des mots",
                "xaxis_label": "Temps médian de réaction(en sec.)",
                "yaxis_label": "Nombre de lettres",
                "data": [], //raw_matrix unorderd
                "decision": { 
                    1: {
                        "series":[
                            {   type:"word",
                                color:"green",
                                "label": Mot",
                                x:[], 
                                y:[], 
                                z[[x,y]...]
                        ], 
                        "xaxis": []
                        },
                    ...
                    average: {
                        ...
                    }
                }
            }
        ```
        
  		## Documentation
  		
    	Consult tasks documentation http://doc.ludoeducation.fr/researcher-guide/tasks/
        '''
        try:
            student = int(student)
        except ValueError:
            return abort(406, "L'identifiant de l'élève {} est incorrect.".format(student))
        if db.student_decision_matrix.count() == 0:
            return abort(500, "Table student_decision_matrix is empty.")
        if student not in list(db.students.distinct("student")):
            return abort(406, "L'élève n'existe pas.")
        elif subject not in ["letters", "numbers"]:
            return abort(406, "Le sujet n'existe pas encore.")
        if subject == "letters":
            subject_name = "Français"
            title = "Lecture des mots et des pseudomots"
            doc = '''Ce graphique est issu du jeu ‘le poisson’. Des mots ou des pseudo-mots sont présentés à l’enfant qui doit les trier. Sur l’axe-X (horizontal) est représenté le nombre de lettres. Sur l’axe-Y (vertical) est représenté son temps de lecture en secondes. Quand l’enfant est en phase de décodage, la vitesse de lecture est modifié par le nombre de lettres à lire. Une fois que l’enfant automatise la lecture, toutes les lettres sont traités simultanément dans un mot. Le nombre de lettres n’a donc plus d’influence sur la vitesse (cette règle est limitée à des mots inférieurs à 8 lettres). Par contre, l’enfant doit continuer à décoder les pseudo-mots. On doit donc continuer à observer que sa vitesse est modifiée par le nombre de lettres.
            '''
            decision = db.student_decision_matrix.find_one({"student": student, "subject": subject},{"_id": 0})
            if decision is None:
                return abort(404, "L'élève n'a pas encore complété ce jeu.", title=title )
        else:
            subject_name = "Maths"
            title = "Comparer et trouver le nombre le plus grand"
            doc = '''Le jeu consiste à comparer deux nombres et à choisir le plus grand. Le graphique représente le temps de réaction (axe Y) en fonction de la distance entre les deux nombres à comparer (axe X). La recherche démontre que la distance en grandeur entre deux nombres module la vitesse de réponse. Plus il y de la distance entre deux nombres, plus la réponse est rapide. La vitesse pour comparer deux nombres est un fort prédicteur de la facilité pour l’arithmétique à l’école. Il est possible de visualiser la progression par jardin en le sélectionnant à l'aide du bouton glissière en bas et de consulter la moyenne.'''
            decision = db.student_decision_matrix.find_one({"student": student, "subject": subject},{"_id": 0})
            if decision is None:
                return abort(404, "L'élève n'a pas encore complété ce jeu.", title=title )
        return {
                "type":"decision",
                "student": student,
                "subject": subject,
                "subject_name": subject_name,
                "title": decision["graph"]["title"],
                "yaxis_label": decision["graph"]["yaxis_label"],
                "xaxis_label": decision["graph"]["xaxis_label"],
                "data": decision["matrix"],
                "decision": decision["graph"]["data"],
                "csv": "{}/csv".format(request.base_url),
                "doc": doc
            }
        
