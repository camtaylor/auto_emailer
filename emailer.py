from bs4 import BeautifulSoup
import requests
import re
import csv
import os

accepted_tlds = ["com", "net", "org", "co"]
keywords = ""
domain_name = ""
searches = ""
searches_per_day = ""


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
      results = search_for_email(link)
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


  # Write headers for csv file with scraped emails.
  with open('emails.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Name", "Stage", "Deal Size", "Notes", "Domain", "Keywords", "Searches", "Searches/Day"])

  final_list = []
  for marketed_domain in domain_list:
    keywords = marketed_domain[0]
    searches = marketed_domain[1]
    searches_per_day = str(int(round(int(searches) / 30)))
    domain_name = keywords.title().strip().replace(" ", "") + ".com"
    domains = get_links(keywords, 180)
    small_businesses = []
    for domain in domains:
      if domain not in top_million_sites:
        small_businesses.append(domain)

    num_emails, emails = get_emails(small_businesses)

    print "v----Success rate"
    print float(num_emails) / float(len(small_businesses))
    for email in emails:
      final_list.extend(list(set([e.lower() for e in email if e.split(".")[-1] in accepted_tlds])))

    print final_list

    # Append csv file with scraped emails.
    with open('emails.csv', 'a') as csvfile:
      writer = csv.writer(csvfile)
      for email in final_list:
        writer.writerow([email, "Lead","", "", domain_name, keywords.strip(), searches, str(int(round(int(searches)/30)))])
