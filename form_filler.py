from selenium import webdriver


EMAIL = "smartin@nametailor.com"
FIRST_NAME = "Scott "
LAST_NAME = "Martin"
PHONE = "203-693-1112"
MESSAGE = "HELLO THIS IS AN EXAMPLE"


def fill_form(form):

  name_filled = False
  email_filled = False
  message_filled = False


  message_box = form.find_element_by_tag_name('textarea')
  if message_box:
    message_box.send_keys(MESSAGE)
    message_filled = True
  inputs = [input for input in form.find_elements_by_tag_name('input') if input.get_attribute('type') != "hidden"]
  labels = form.find_elements_by_tag_name('label')
  print len(inputs)
  print len(labels)
  for input_box in inputs:
    type = input_box.get_attribute('type')
    print type
    if type == "hidden":
      continue
    if type == "email":
      input_box.send_keys(EMAIL)
      email_filled = True
    if type == "tel":
      input_box.send_keys(PHONE)
    if type == "submit":
      print "BUTTON FOUND--->"

    print input_box.get_attribute('placeholder')
    print input_box.get_attribute('innerHTML')
    print input_box.get_attribute('value')


def send_contact_form(link):
  print link
  driver = webdriver.Firefox()
  driver.get(link)
  try:
    form = driver.find_element_by_xpath("//form[1]")
    if form:
      fill_form(form)
  except Exception:
    print "Failed"
    driver.close()
