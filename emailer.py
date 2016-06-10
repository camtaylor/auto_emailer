from bs4 import BeautifulSoup
import requests
import re
import csv
import webbrowser
import form_filler


accepted_tlds = ["com", "net", "org", "co"]

def get_links(search_term, num_results):
  page = requests.get("https://www.google.com/search?q={}&num={}".format(search_term, num_results))
  soup = BeautifulSoup(page.content, "lxml")
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
  soup = BeautifulSoup(page, "lxml")
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
      form_filler.send_contact_form(link)
    return results
  else:
    return ""


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
