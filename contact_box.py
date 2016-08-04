from bs4 import BeautifulSoup
import requests
import re
import csv
import webbrowser
import thread
import time
from selenium import webdriver
from selenium.webdriver.support.select import Select
import os



"""
  Program to fill contact boxes for nametailor domain selling. This is achieved through a combination
  of selenium and beautiful soup.
"""


EMAIL = "smartin@nametailor.com"
FIRST_NAME = "Scott "
LAST_NAME = "Martin"
PHONE = "203-693-1112"

thread_count = 0
MAX_THREADS = 3

def clear_input(input):
  try:
    input.clear()
  except Exception as e:
    print e


def get_links(search_term, num_results):
  """
  Function to get the links of search results from google.

  :param search_term:
  :param num_results:
  :return: list of links
  """
  page = requests.get("https://www.google.com/search?q={}&num={}".format(search_term, num_results))
  soup = BeautifulSoup(page.content)
  links = soup.findAll("a")
  domain_list = []
  for link in soup.find_all("a", href=re.compile("(?<=/url\?q=)(htt.*://.*)")):
    scraped_list =  re.split(":(?=http)", link["href"].replace("/url?q=", ""))
    if len(scraped_list) > 1:
      scraped_list.pop(0)
    domain = re.findall(r'(?<=http://)([^\.]+\.)([^/]+)', scraped_list[0])
    if domain and "." in domain[0][1]:
      domain_list.append(domain[0][1])
    elif domain:
      domain_list.append(domain[0][0] + domain[0][1])

  return list(set(domain_list))

def search_for_contact_link(domain):
  global thread_count
  try:
    page = requests.get("http://" + domain, timeout=1).text
  except:
    return ""
  soup = BeautifulSoup(page)
  links = soup.findAll('a', href=True, text=re.compile('Contact.*', re.IGNORECASE))
  if len(links) > 0 and len(links[0]) > 0:
    link = links[0]['href']
    if "http://" in link:
      link = link.replace("http://", "")
    if link[0] == "/":
      link = domain + link
    else:
      link = domain + "/" + link
    if "http://" not in link:
      link = "http://" + link
    # Go to contact page
    while thread_count > MAX_THREADS:
      continue
    thread_count += 1
    try:
      # thread.start_new_thread(send_contact_form, (link,))
      send_contact_form(link)

    except Exception as e:
      print e
      thread_count -= 1
    print thread_count

    return link
  else:
    return ""

def fill_form(form):

  name_filled = False
  email_filled = False
  message_filled = False
  phone_filled = False

  email = """Hello,

  I am contacting you because I thought you might be interested in knowing that we are selling our domain {} ; the search term " {} " receives an average of  {} exact-match searches per month (roughly {} per day) on Google alone and owning this domain would be an asset to your marketing efforts.

  85% of people search online for local services.
  94% of those people don't go beyond the first search page.

  If you are interested or have any questions about the domain please don't hesitate to ask.""".format(domain_name,
                                                                                                       keywords,
                                                                                                       searches,
                                                                                                       searches_per_day)

  message_box = form.find_element_by_tag_name('textarea')
  if message_box:
    message_box.send_keys(email)
    message_filled = True
  inputs = [input for input in form.find_elements_by_tag_name('input') if input.get_attribute('type') != "hidden"]
  labels = form.find_elements_by_tag_name('label')
  selects = [input for input in form.find_elements_by_tag_name('select')]
  for select in selects:
    options = [x for x in select.find_elements_by_tag_name("option")]
    options[-1].click()



  num_inputs = len(inputs)
  num_labels = len(labels)
  # One label to each input
  if not num_labels > num_inputs:
    for index, label in enumerate(labels):
      label_text = label.get_attribute('innerHTML').lower()
      print label_text
      if "mail" in label_text:
        inputs[index].send_keys(EMAIL)
        email_filled = True
      elif "first" in label_text:
        inputs[index].send_keys(FIRST_NAME)
      elif "last" in label_text and not name_filled:
        inputs[index].send_keys(LAST_NAME)
        name_filled = True
      elif "name" in label_text and not name_filled:
        inputs[index].send_keys(FIRST_NAME + LAST_NAME)
        name_filled = True
      elif "phone" in label_text:
        inputs[index].send_keys(PHONE)
        phone_filled = True


  attributes = ['placeholder', 'innerHTML', 'value']
  for attribute in attributes:
    for input_box in inputs:
      attribute_text = input_box.get_attribute(attribute)
      print attribute_text
      if not attribute_text:
        continue
      attribute_text = attribute_text.lower()

      if "mail" in attribute_text and not email_filled:
        clear_input(input_box)
        input_box.send_keys(EMAIL)
        email_filled = True
      elif "first" in attribute_text and not name_filled:
        clear_input(input_box)
        input_box.send_keys(FIRST_NAME)
      elif "last" in attribute_text and not name_filled:
        clear_input(input_box)
        input_box.send_keys(LAST_NAME)
        name_filled = True
      elif "name" in attribute_text and not name_filled:
        clear_input(input_box)
        input_box.send_keys(FIRST_NAME + LAST_NAME)
        name_filled = True
      elif "phone" in attribute_text:
        clear_input(input_box)
        input_box.send_keys(PHONE)
        phone_filled = True



        # Fill by type of input
  for input_box in inputs:
    type = input_box.get_attribute('type')
    print type
    if type == "email" and not email_filled:
      clear_input(input_box)
      input_box.send_keys(EMAIL)
      email_filled = True
      continue
    if type == "tel" and not phone_filled:
      clear_input(input_box)
      input_box.send_keys(PHONE)
      phone_filled = True
      continue
    if type == "radio" or type == "checkbox":
      input_box.click()
    if type == "submit" and message_filled and name_filled and email_filled:
      input_box.click()
      time.sleep(3)
      driver.close
      print "Found button"
    elif type == "submit":
      if not name_filled:
        clear_input(inputs[0])
        inputs[0].send_keys(FIRST_NAME + LAST_NAME)
        clear_input(inputs[1])
        inputs[1].send_keys(EMAIL)
        input_box.click()
      print "Guessing..."


def send_contact_form(link):
  global thread_count
  print link
  driver = webdriver.Firefox()
  driver.get(link)
  try:
    form = driver.find_element_by_xpath("//form[1]")
    if form:

      fill_form(form)
  except Exception as e:
    print e
    print "Failed"
    driver.close()
  thread_count -= 1


if __name__ == "__main__":

  #Import top million sites.
  with open('top-1m.csv', 'rb') as f:
    reader = csv.reader(f)
    top_million_sites = []
    for line in reader:
      top_million_sites.append(line[0])
    top_million_sites = set(top_million_sites)

  csv_option = raw_input("Read from domains.csv? (y/n): ")
  domain_list = []
  if "y" in csv_option:
    with open('domains.csv', 'rb') as f:
      reader = csv.reader(f)
      for line in reader:
        keywords = line[0]
        searches = line[1]
        domain_list.append([keywords, searches])
  else:
    keywords = raw_input("Keywords >>>")
    searches = raw_input("Searches per month>>>")
    domain_list.append([keywords, searches])


  for marketed_domain in domain_list:
    keywords = marketed_domain[0]
    searches = marketed_domain[1]
    searches_per_day = str(int(round(int(searches)/30)))
    domain_name = keywords.title().strip().replace(" ", "") + ".com"
    domains = get_links(keywords, 160)
    for domain in domains:
      if domain not in top_million_sites:
        search_for_contact_link(domain)
    if thread_count > 0:
      time.sleep(5)
    print "--------Finished--------"
    os.system("pkill firefox-bin")

