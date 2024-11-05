from majors.major_data import parse_catalog, complie_majors
from courses.course_data import parse_courses
import json

file = open("compileconfig.json", 'r')
config = json.load(file)

if config['config']['get_majors'] == True:
    parse_catalog(config['links']['majors'])

if config['config']['plot_major_retrieval'] == True:
    complie_majors()

if config['config']['plot_course_retrieval'] == True:
    parse_courses(config['links']['courses'])

file.close()