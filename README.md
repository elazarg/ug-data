# UG-data
This project is about publishing Technion UG courses information in a machine-friendly manner. 

The code here is not important. Really. It's all about the data.
[`course_list.json`](course_list.json) is a valid [JSON](https://en.wikipedia.org/wiki/JSON#Example) file containing information about courses in the Technion. Please take a look at it: as a JSON file, it's human-readable.

It is also machine-readable, of course. To read this file and use it in your program, simply load it as a JSON file. For example, in Python your code can be:

```python
with open('course_list.json', encoding='utf8') as f:
    courses = json.load(f)
```        
so `courses` will be a dictionary mapping course ids (strings, e.g "234123") to a dictionary.
Similar functions exists for any other programming language you'd like to use,
such as [Ruby](https://hackhands.com/ruby-read-json-file-hash/).

Note - the file is `utf-8`, not `ascii`.

As can be seen from the code, the data was extracted directly from the [UG-site](https://ug3.technion.ac.il/rishum/search), but this is not an official project, in any sense; the data might contain errors.
