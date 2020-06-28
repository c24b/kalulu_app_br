from os.path import dirname, abspath, join

from .project import ROOT_DIR

FILES_DIR = join(ROOT_DIR, "files")
RAW_DIR = join(FILES_DIR, "raw")
CLEAN_DIR = join(FILES_DIR,"clean")
REFERENCES_DIR = join(FILES_DIR,"references")
ARCHIVED_DIR = join(FILES_DIR,"archived")

REFERENCES_FILES = {
    "gapfill_lang":[join(REFERENCES_DIR, "stimuli_wordsorting.csv")],
    "gp": [join(REFERENCES_DIR,"gp_progression_tag.csv"), join(REFERENCES_DIR,"letters_games_lesson.csv"), join(REFERENCES_DIR,"Letters_3game_perLesson.csv")],
    "numbers": [join(REFERENCES_DIR,"nb_progression_tag.csv"), join(REFERENCES_DIR,"numbers_games_lesson.csv"),join(REFERENCES_DIR,"Numbers_3game_perLesson.csv")],
    "students": [join(REFERENCES_DIR,"studentid_group.csv")],
}

DATASETS = ["gapfill_lang", "assessments_language", "assessements_math", "gp", "numbers"]

DIRS =  {
    "from": RAW_DIR,
    "to": CLEAN_DIR,
    "old": ARCHIVED_DIR,
    "ref": REFERENCES_DIR
}

