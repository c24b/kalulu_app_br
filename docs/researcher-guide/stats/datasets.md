## Datasets

Dataset consists of the main raw files types stored in the server needed for the analysis, the api and the graph


|name        | slug                       | type               |             subject        |
|------------|----------------------------|--------------------|----------------------------|
| name       | script shortcut name       | (chapter OR lesson)| (letters OR numbers )      |

- assessments_language
- assessments_maths
- gp
- numbers
- gapfill_lang

``` json
> db.datasets.findOne()
{
    "_id" : ObjectId("5d24d04c773b4c1a66a70899"),
    "name" : "assessments_language",
    "slug" : "assessments",
    "subject" : "lettres",
    "type" : "chapter"
}
```
