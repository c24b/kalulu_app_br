
## Front Web Application

    -[ ] Classroom Progression by Subject (Page 3) : X

    - [ ] Student Page by Subject (Page 4) Letters:
        - [ ] Widget Words X
        - [ ] Widget Syllabs X
        - [ ] Widget Info X
        - [ ] Graph Last Activity X
        - [ ] Confusion Matrix on last Chapter X
        - [ ] Graph Lexical Decision X

    - [ ] Student Page by Subject (Page 5) Numbers
        Widget Counting X
        Widget Identification X
        Widget Info X
        Graph Last Activity X
        Confusion Matrix on last Chapter *
        Graph Digital Decision X

    - [ ] Student Confusion Matrix by Chapters (Page 6) Numbers and Letters *

    - [ ] Global Confusion Matrix *

## CSV Facilities

Here it consists of the raw data exported form database set into a 2D matrix for you to be able to process and control the data inside R or Excel. I list here only what you specifically asked me as needed. In general everything that is inside a table and exposed to API to feed the graph are available.

    Still missing tests on this part.

    Classroom activity:
        start, end, timespent by subject X
        start, end, ttimespent by datasetX

    Student confusion matrix:
        letters : by Consonnants by Vowels with signal (HIT MISS, etc...) X
        numbers with signal (HIT MISS, etc...) X

    Confusion matrix:
        letters : by Consonnants by Vowels with signal (HIT MISS, etc...) *
        numbers with signal (HIT MISS, etc...) *

    Student Decision matrix:
        letters X
        numbers X

    Student Last chapter activity X

    Student Last lesson activity X

## API Access

Here it consists of the api access that feed the graph and give access to JSON format of the database

    doc is ok
    tests in local and in my server are ok (means it is stable)

It allows you also to update the database to perform some administrative tasks as specifically asked

    GRAPH ACCESS X
    RAW DATA TABLE ACCESS X
    ADMINISTRATIVE TASK
        Classroom and student: Edit classroom or student with password. X Regenerating the stats *
        Pedagogical path for letters (Internationalisation) ?
        Status/error report *