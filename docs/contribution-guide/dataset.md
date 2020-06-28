## Dataset


Table `datasets` consists of the main file types stored in the server. 

It defines the type of game records, the structure of the file, the keys avaialable for a record and the progression level.

Each dataset belongs to a subject that can be `numbers` or `letters`.



|dataset        | slug                                      | type               |             subject        | files_nb |
|------------|-------------------------------------------|--------------------|----------------------------|
| name  of the dataset     | script shortcut name (internal use)       | (chapter OR lesson)| (letters OR numbers )      | number of files found|

- assessments_language
- assessments_maths
- gp
- numbers
- gapfill_lang

``` json
> db.datasets.findOne()
{
    "_id" : ObjectId("5d24d04c773b4c1a66a70899"),
    "dataset" : "assessments_language",
    "slug" : "assessments",
    "subject" : "lettres",
    "type" : "chapter",
    "files_nb": 743
}
```
