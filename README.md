# UG-data
This project is about publishing Technion UG courses information in a machine-friendly manner. 

The code here is not important. Really. It's all about the data.
[`course_list.json`](course_list.json) is a valid [JSON](https://en.wikipedia.org/wiki/JSON#Example) file containing information about courses in the Technion. Please take a look at it: as a JSON file, it's human-readable. Another interesting files are [`reverse_kdam.json`](reverse_kdam.json) and [`reverse_adjacent.json`](reverse_adjacent.json).

JSON is also machine-readable, of course. To read this file and use it in your program, simply load it as a JSON file. For example, in Python your code can be:

```python
with open('course_list.json', encoding='utf8') as f:
    courses = json.load(f)
```        
so `courses` will be a dictionary mapping course ids (strings, e.g "234123") to a dictionary.
Similar functions exists for any other programming language you'd like to use,
such as [Ruby](https://hackhands.com/ruby-read-json-file-hash/).

Note - the file is `utf-8`, not `ascii`.

As can be seen from the code, the data was extracted directly from the [UG-site](https://ug3.technion.ac.il/rishum/search), but this is not an official project, in any sense; the data might contain errors.

Example for a single fetch:

```
$ python3 ug_fetch.py 234123
{
  "id": "234123",
  "points": "4.5",
  "name": "מערכות הפעלה",
  "lecture": "2",
  "tutorial": "2",
  "lab": "3",
  "project": "6",
  "kdam": [
    [
      "234218",
      "234118"
    ]
  ],
  "no_more": [
    "236364",
    "234120",
    "234119",
    "046210",
    "046209"
  ],
  "site": "http://www.cs.technion.ac.il/~cs234123/index.html",
  "syllabus": "הקורס מציג את הנושאים המרכזיים של מערכות הפעלה מודרניות, ובפרט: תהליכים וחוטים: זימון והחלפת הקשר, תיאום: בעיית הקטע הקריטי, סמפורים ומשתני תנאי, פסיקות, ניהול זיכרון: דפדוף, זיכרון וירטואלי, מערכת הקבצים. במסגרת התרגול, הסטודנטים יכנסו לעומקה של מערכת הפעלה מתקדמת."
}
```