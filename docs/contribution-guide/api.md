# API

API is exposed at port 5000 and is a facility to consult, export database tables
and feed the graphs of the dashboard.

6 main endpoints are available:

* activity
* progression
* tasks
* numbers
* letters
* admin

Every endpoint exposes inline its own documentation: description method and output. 

Example:
!()[screenshots/api_doc_inline.png]

## Activity

Display activity metrics such as nb_records, nb_days, nb_sequences(nb_tries), timespent, CA, CA_rate on a specific subject and a specific dataset for a given student.

Classroom activity display the activity metrics more the comparison of performances with all the students



## Progression

Main goal is to display information on a kid progression
Progression in the database is expressed in terms of lesson and chapter which numbers are defined in the table `path` which is built upon referential files

In the game, when a new lesson has been started we consider that the last lesson as been validated (same for chapters). In the data, records are ordered by notions no matter the lesson or the chapter, scripts re-ordered the notions (such a grapheme-phoneme, words or numbers) to preserve the chapters and lessons linear progression of the pedagogical path pre-defined.

## Tasks

Display information on 2 specific tasks: 
- decision: 
- confusion

at student level and global level

## Numbers

Display information metrics on skills acquired in numbers games depending on the game:
- identification
- counting
- association

at student level

## Letters

Display information metrics on skills acquired in letters games:
- words
- syllabs

## Admin

Display, edit, delete the information conerning the process and the datasets at different level:

- student
- classroom
- files

##### How to use the API in a script

``` python
def load_json_data_fromAPI(param):
	API_URL = "http://x.x.x.x:5000"
	endpoint_path = "/student/{}/activity".format(params)
	r_url = os.path.join(API_URL, classroom_dataset_lesson_path)
	resp = requests.get(r_url)
	print(r_url, resp.status_code)
	if resp.status_code < 300:
		data = json.loads(resp.text)
		return data
```

