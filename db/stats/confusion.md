
l = ["a", "b", "c"]
chapter = [1, 2, 3]
couples = itertools.product(l, repeat=2)
couples = [
    ("a", "a"), ("a", "b"), ("a", "c"), 
    ("b", "a"), ("b", "b"), ("b", "c"),
    ("c", "a"), ("c", "b"), ("c", "c")
]
[(chapter,couple) for couple in couples for chapter in chapters]
chapter_couples = [
    (1, ("a", "a")), (1,("a", "b")), (1,("a", "c")), 
    (1,("b", "a")), (1,("b", "b")), (1,("b", "c")),
    (1,("c", "a")), (1,("c", "b")), (1,("c", "c")),
    (2, ("a", "a")), (2,("a", "b")), (2,("a", "c")), 
    (2,("b", "a")), (2,("b", "b")), (2,("b", "c")),
    (2,("c", "a")), (2,("c", "b")), (2,("c", "c")),
    (3, ("a", "a")), (3,("a", "b")), (3,("a", "c")), 
    (3,("b", "a")), (3,("b", "b")), (3,("b", "c")),
    (3,("c", "a")), (3,("c", "b")), (3,("c", "c"))
]


itertools.product(itertools.product(l, repeat=2))


1. Optimize the insertion
- sort False
- insert_many with bulk_insert
- batch size of 1000

2. Solve the confusion on numbers
setting CV in 'N'
to allow merge