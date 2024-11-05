import requests
from bs4 import BeautifulSoup
import json
import re

# get coid, course name, and general number from course description catalog
def parse_courses(url: str):
    page_count = get_page_count(url)
    
    course_links = dict()
    for page in range(1, page_count + 1):
        # append page filter to extract all course data
        filter = f'&filter%5Bcpage%5D={page}'
        
        response = requests.get(url + filter)
        soup = BeautifulSoup(response.content, "html.parser")
            
        content = soup.select('a[aria-expanded^="false"]')
        
        # extract and store course prefix, course number, and coid
        for line in content:
            link = line.get('href')
            coid = re.search(r'coid=(\d+)', str(link))
            parse = re.match(r"([A-Z]+) (\d+[A-Z]?)\s*-\s*(.+)", line.text)
            
            if parse and coid:
                if parse.group(1) not in course_links.keys():
                    course_links[parse.group(1)] = dict()
                
                course_links[parse.group(1)][parse.group(2)] = {
                    "name" : parse.group(3), 
                    "coid" : coid.group(1)
                }
    
    # store all parsed data
    file = open('courses/course_paths.json', 'w')
    json.dump(course_links, file, indent = 4)
    file.close()

# get page count for usm course description catalog
def get_page_count(url: str):
    # get and parse url info
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    pages = soup.select('a[aria-label^="Page"]')
    
    # iterate through page data and extract highest page number
    page_count = 0
    for page in pages:
        try:
            current = int(page.text)
            page_count = current if current > page_count else page_count
        except ValueError:
            pass
    
    return page_count

def semester_offerings(semester: str, year: str):
    file = open(f'{semester}_{year}_offerings.txt', 'r')
    
    course_paths = open('course_paths.json' , 'r')
    paths = json.load(course_paths)
    course_paths.close()
    
    err_list = []
    out = open('2025_offerings_details.csv', 'w')
    for line in file:
        course = re.match(r"([A-Z]+) (\d+[A-Z]?)", line.strip())
        
        if course:
            try:
                coid = paths[course.group(1)][course.group(2)]['coid']
                url = f"https://catalog.usm.edu/preview_course_nopop.php?catoid=35&coid={coid}"
            
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                targets = soup.find_all("p")
                
                for target in targets:
                    if line.strip() in target.text:
                        out.write(course.group(1) + ',' + course.group(2) + ',' + f"\"{target.text}\"" + '\n')
            
            except KeyError:
                err_list.append(line.strip())
            
    print(err_list)
    out.close()
    file.close()

def extract_info(info: str):
    # Extract course prefix, number, and title
    course_info = re.search(r"([A-Z]+) (\d+[A-Z]?) - (.+?)\s*(\d+(?:-\d+)?\s*hrs?\.)", info)
    course_prefix = course_info.group(1) if course_info else "N/A"
    course_number = course_info.group(2) if course_info else "N/A"
    course_title = course_info.group(3) if course_info else "N/A"
    course_hours = course_info.group(4) if course_info else "Not specified"

    # Extract prerequisites (if any)
    prerequisites = re.search(r"Prerequisite\(s\):\s*(.+?)(?=\s*Corequisite|\.|$)", info)
    prerequisites = prerequisites.group(1).strip() if prerequisites else "None"

    # Extract corequisites (if any)
    corequisites = re.search(r"Corequisite\(s\):\s*(.+?)(?=Prerequisite|\.|$)", info)
    corequisites = corequisites.group(1).strip() if corequisites else "None"

    # Extract description (everything following course hours, prerequisites, and corequisites)
    description_start = info.find(course_hours) + len(course_hours)
    description_text = info[description_start:]
    # Remove 'Prerequisite(s)' and 'Corequisite(s)' sections from the description
    description_text = re.sub(r"(Prerequisite\(s\):.+?\.|Corequisite\(s\):.+?\.)", "", description_text).strip()
    
    # Print or store the parsed information
    print("Course Prefix:", course_prefix)
    print("Course Number:", course_number)
    print("Course Title:", course_title)
    print("Course Hours:", course_hours)
    print("Prerequisites:", prerequisites)
    print("Corequisites:", corequisites)
    print("Description:", description_text)
    print("\n" + "-"*40 + "\n")    
    
semester_offerings('spring', '2025')