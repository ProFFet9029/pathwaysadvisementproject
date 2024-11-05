import requests
from bs4 import BeautifulSoup
import json

# pull all majors from USM catalog
def parse_catalog(url):
    offered_courses = dict()
    current = 'none'
    
    # fetch catalog offered courses
    response = requests.get(url)
    
    # Parse HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # extract catalog links and headers above the links
    links = soup.find_all(lambda tag: (tag.name == 'a') or (tag.name == 'p' and tag.get('style') == 'padding-left: 30px'))
    
    # parse all majors into a json file
    for link in links:
        if link.name == 'p':
            if 'Bachelor' in link.text:
                current = 'major'
            else:
                current = 'other'
        elif link.name == 'a':
            href = link.get('href')
            if 'poid' and 'returnto=2243' in href and current == 'major':
                offered_courses[link.text] = f"https://catalog.usm.edu/{href}"
    
    # dump to file
    out = open("majors/parsed_majors.json", "w")
    json.dump(offered_courses, out, indent = 4)
    out.close

# get catalog links to each major's degree requirements and semester guide
def complie_majors():
    file = open("majors/parsed_majors.json", "r")
    
    data = json.load(file)
    majors = list(data.keys())
    urls = list(data.values())
    
    direct_links = dict()
    
    for url, major in zip(urls, majors):
        # check each major page and extract requirements and semester guide links
        response = requests.get(url)
                    
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a')
        
        direct_links[major] = dict()    
        ignore = '/content.php?catoid=35&navoid=2240'        
        for link in links:
            href = link.get('href')
            if 'Degree Requirements' in link.text and ignore != href:
                direct_links[major]["Degree Requirements"] = f"https://catalog.usm.edu/{href}"
            elif 'Semester Guide' in link.text and ignore != href:
                direct_links[major]['Semester Guide'] = f"https://catalog.usm.edu/{href}"
        
        if not direct_links[major]:
            direct_links[major]["Degree Requirements"] = url
            direct_links[major]['Semester Guide'] = url
        
    out = open("majors/major_paths.json", "w")
    json.dump(direct_links, out, indent = 4)
    out.close()
        
    file.close()

# ai utility
# extract plain text from semester guide and degree requirements urls 
def major_info(url: str):  
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    target_div = soup.find('div', class_ = 'custom_leftpad_20')
    if target_div:
            # Get the plain text content
            plain_text = target_div.get_text(separator = '\n', strip = False)
            
            file = open("reference.txt", 'w')
            file.write(plain_text)
            file.close()
            
            return plain_text
    else:
        return False

# parse_catalog("https://catalog.usm.edu/content.php?catoid=35&navoid=2243")
# complie_catalog()