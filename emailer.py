from bs4 import BeautifulSoup
import requests
import re
import csv
import webbrowser
import thread
import time
from selenium import webdriver

accepted_tlds = ["com", "net", "org", "co"]
keywords = ""
domain_name = ""
searches = ""
searches_per_day = ""


EMAIL = "smartin@nametailor.com"
FIRST_NAME = "Scott "
LAST_NAME = "Martin"
PHONE = "203-693-1112"


def get_links(search_term, num_results):
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


def get_emails(domain_list):
  num_emails = 0
  emails = []
  for domain in domain_list:
    print domain
    found_emails = search_for_email(domain)
    print found_emails
    if len(found_emails) == 0:
      found_emails = search_for_email(domain + "/contact")
      print found_emails
    if len(found_emails) == 0:
      found_emails = search_for_email(domain + "/about")
      print found_emails
    if len(found_emails) == 0:
      found_emails = search_for_email(domain + "/contact-us")
      print found_emails
    if len(found_emails) == 0:
      print "Additional----"
      found_emails = search_for_contact_link(domain)
      print found_emails
    if len(found_emails) > 0:
      emails.append(found_emails)
      num_emails += 1
  return num_emails, emails


def search_for_email(domain):
  found_emails = []
  try:
    page = requests.get("http://" + domain, timeout=3)
    if page.status_code == "400":
      return []
    found_emails = re.findall(r'[A-Za-z0-9_]+@[A-Za-z0-9_]+\.[a-zA-Z]+', page.text)
  except:
    return []
  return found_emails

def search_for_contact_link(domain):
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
    results = search_for_email(link)
    if len(results) == 0:
      if "http://" not in link:
        link = "http://" + link
      # Go to contact page
      thread.start_new_thread(send_contact_form, (link,))
    return results
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
        input_box.send_keys(EMAIL)
        email_filled = True
      elif "first" in attribute_text and not name_filled:
        input_box.send_keys(FIRST_NAME)
      elif "last" in attribute_text and not name_filled:
        input_box.send_keys(LAST_NAME)
        name_filled = True
      elif "name" in attribute_text and not name_filled:
        input_box.send_keys(FIRST_NAME + LAST_NAME)
        name_filled = True
      elif "phone" in attribute_text:
        input_box.send_keys(PHONE)
        phone_filled = True



        # Fill by type of input
  for input_box in inputs:
    type = input_box.get_attribute('type')
    print type
    if type == "email" and not email_filled:
      input_box.send_keys(EMAIL)
      email_filled = True
      continue
    if type == "tel" and not phone_filled:
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
        inputs[0].send_keys(FIRST_NAME + LAST_NAME)
        inputs[1].send_keys(EMAIL)
        input_box.click()
      print "Guessing..."


def send_contact_form(link):
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


if __name__ == "__main__":
  global parsed_emails


  #Import top million sites.
  with open('top-1m.csv', 'rb') as f:
    reader = csv.reader(f)
    top_million_sites = []
    for line in reader:
      top_million_sites.append(line[0])
    top_million_sites = set(top_million_sites)




  keywords = raw_input("Keywords >>>")
  price = raw_input("Price >>>")
  searches = raw_input("Searches per month>>>")
  searches_per_day = str(int(round(int(searches)/30)))
  domain_name = keywords.title().strip().replace(" ", "") + ".com"
  domains = get_links(keywords, int(raw_input("Results to scrape>>>")))
  small_businesses = []
  for domain in domains:
    if domain not in top_million_sites:
      small_businesses.append(domain)

  num_emails, emails = get_emails(small_businesses)

  print "v----Success rate"
  print float(num_emails) / float(len(small_businesses))
  final_list = []
  for email in emails:
    final_list.extend(list(set([e.lower() for e in email if e.split(".")[-1] in accepted_tlds])))

  print final_list

  # Write csv file with scraped emails.
  with open('emails.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Name", "Stage", "Deal Size", "Notes", "Domain", "Keywords", "Searches", "Searches/Day"])
    for email in final_list:
      writer.writerow([email, "Lead", price, "", domain_name, keywords.strip(), searches, searches_per_day])
