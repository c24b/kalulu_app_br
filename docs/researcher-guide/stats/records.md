# Records


## Definition

### Records table
Table records is created at the [`insert` step](../../contribution-guide/steps.md) consists of all information found in each [document](./files.md) inside the directory datasets/clean/ mapped and inserted into the table `records` of the database.

### Record item
The main information unit is expressed as a `record`: it consists of all the information stored by the game for any interaction by any student on any dataset: one line for one interaction along with the contextual information provided in the document name such as student_id, classroom_id, dataset.

## Fields
### Record fields

|unixTime |score|isClicked | value| elapsedTime| assessmentEndTime| tag | chapter | classroom |student | group | dataset | subject | game | word | day | stimulus | target|
|----------|----|-----| -----| -----------| -----------------| --- | ------- | --------- |------- | ----- | ------- | ------- | ---- |----- |----|----- |----|


Fields of records vary depending on type of [dataset](./datasets.md) of the document provided
insertion script create correspondancies:
to have same key and value for each record that need to be process (e.g tag)
and compute some field to ease postprocessing (e.g. date)

- gp and numbers:

```json
{
    "unixTime" : ISODate("2019-02-08T11:05:31Z"),
    "isClicked" : 1,
    "score" : 1,
    "elapsedTime" : 1.241623,
    "stimulus" : "é-e",
    "target" : "é-e",
    "classroom" : 1,
    "student" : 111,
    "tag" : "é",
    "value" : "é-e",
    "dataset" : "gp",
    "date" : "2019-02-08",
    "game" : "25"
 }
```

- gapfill_lang

```json
{
    "_id" : ObjectId("5d1b11adbc61b6d221d97f88"),
    "unixTime" : ISODate("2019-01-15T09:30:23Z"),
    "isClicked" : 1,
    "score" : 1,
    "elapsedTime" : 3.762145,
    "stimulus" : "foudre",
    "target" : "foudre",
    "classroom" : 1,
    "student" : 111,
    "word_nb" : 89,
    "tag" : "foudre", // Computed but not in raw dataset (tag = value = target)
    "value" : "foudre",
    "dataset" : "gapfill_lang",
    "date" : "2019-01-15",
    "game" : "ants"
}
```

- assessments_maths and assessments_language
```json
{
    "_id" : ObjectId("5d1b1191bc61b6d221d371cb"),
    "unixTime" : ISODate("2019-05-21T09:00:44Z"),
    "score" : 1,
    "elapsedTime" : 0.184267,
    "value" : "7",
    "assessmentEndTime" : ISODate("2019-05-21T09:00:47Z"),
    "tag" : "7",
    "chapter" : 8,
    "lesson" : null,
    "max_chapter" : 20,
    "classroom" : 1,
    "student" : 111,
    "dataset" : "assessments_maths",
    "game" : "fish",
    "date" : "2019-05-21"
}
```

### Methods

Main method for defining and inserting a `record` is stored in `db/steps/insert.py`

1. Generate the references of a given document:
  extract from filename: ClassroomNb, TabletNb,StudentNb, dataset_name

2. Given the dataset name and its slug: launch the corresponding function
    insert_<dataset_slug>()

3. Update table games given the key game of each record
