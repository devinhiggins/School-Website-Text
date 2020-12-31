import tkinter as tk
import pandas as pd
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
import pandas as pd
import csv
import bs4
import requests


class Validator(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        global driver,confirmed
        driver = webdriver.Firefox()
        confirmed = 'no'
        
        #separate the window into two halves
        left_frame = tk.Frame(self)
        left_frame.pack(side = 'left',
                        padx=10,
                        pady=10)
    
        right_frame = tk.Frame(self)
        right_frame.pack(side='left',
                         padx=10,
                         pady=10)
        
        #left frame
        entry_label = tk.Label(left_frame,
                               text='Input csv file:')
        entry_label.grid(row=0,
                         column=0)
        global entry
        entry = tk.Entry(left_frame)
        entry.insert(0,
                     "NationalDone.csv")
        entry.grid(row=0,
                   column=1)
        confirm_button = tk.Button(left_frame,text = 'Confirm',
                                   height=1,width=8, 
                                   command = lambda: self.confirm_click())
        confirm_button.grid(row=1,
                            column=1)
        
        #right frame
        global query_label
        query_label = tk.Label(right_frame,
                               text = 'Query String')
        query_label.grid(row=0,
                         column=0,
                         columnspan =3)
        global yes_button,no_button
        yes_button = tk.Button(right_frame,
                               text = 'Yes',
                               height=1,
                               width=8,
                               command = lambda: self.append_click('yes'))
        yes_button.grid(row=1,
                        column=1)
        no_button = tk.Button(right_frame,text = 'No',
                              height=1,
                              width=8,
                              command = lambda: self.append_click('no'))
        no_button.grid(row=2,
                       column=1)
        quit_button = tk.Button(right_frame,
                                text = 'Quit',
                                height=1,
                                width=8,
                                command = lambda: self.quit_click())
        quit_button.grid(row=3,
                         column=1)
    
    def confirm_click(self):
        global confirmed, index, entry, driver,query_label
        confirmed = 'yes'
        index = 0
        
        file = entry.get()
        input_csv = pd.read_csv(file, header=None)
        
        global school,city,zipcode,URL,query
        school = input_csv[0]
        city = input_csv[1]
        zipcode = input_csv[2].astype(str)
        URL = input_csv[3]
        query = school + ',' + city + ',' + zipcode
        
        driver.get('{}'.format(URL[index]))
        query_label.config(text='{}'.format(query[index]))
        
    def append_csv(self,prediction):
        global index
        
        if prediction == 'TP':
            with open('TruePositive.csv', 'a', newline='') as f1:
                writer = csv.writer(f1)
                writer.writerow([school[index], city[index], zipcode[index], URL[index]])  
        elif prediction == 'FP':
            with open('FalsePositive.csv', 'a', newline='') as f2:
                writer = csv.writer(f2)
                writer.writerow([school[index], city[index], zipcode[index],'NA' ])
        
        if index < len(URL) - 1:
                index += 1
                driver.get('{}'.format(URL[index]))
                query_label.config(text='{}'.format(query[index]))
                return index
            
        if (index + 1) >= len(URL):  # this is a check if there are any more entries
                tk.messagebox.showinfo('Attention', 'No more entries, closing program')
                self.quit_click()
        
    def google_navigation(self,boolean):
        global yes_button,no_button, google_urls, google_index
        
        if boolean == 'yes':
            URL[index] = google_urls[google_index]
            self.append_csv('TP')
            yes_button.configure(command=lambda: self.append_click('yes'))
            no_button.configure(command=lambda: self.append_click('no'))
            
        elif boolean == 'no':
            if google_index < len(google_urls) - 1:
                google_index += 1
                driver.get(google_urls[google_index])
            else:
                tk.messagebox.showinfo('Attention','No more alternate entries')
                self.append_csv('FP')
                yes_button.configure(command=lambda: self.append_click('yes'))
                no_button.configure(command=lambda: self.append_click('no'))
        
    def append_click(self,boolean):
        global index
        
        if confirmed == 'no':
            tk.messagebox.showinfo('Attention','Confirm input first')
        
        else:
            if boolean =='yes':
                self.append_csv('TP')
            elif boolean == 'no':               
                page = requests.get('https://www.google.com/search?q={}'.format(query[index])).content
                soup = bs4.BeautifulSoup(page,'html.parser')
                global google_urls,google_index
                google_urls = []
                links = [a.get('href') for a in soup.find_all('a', href=True)]
                for i in links:
                    if 'https' in i and 'google' not in i:
                        #only extracts external links
                        i = i.replace('/url?q=','').split('&',1)[0]
                        google_urls.append(i)
                google_urls = list(dict.fromkeys(google_urls))
                google_index = 0
                tk.messagebox.showinfo('Attention','Showing alternate entries')
                driver.get(google_urls[google_index])
                global yes_button,no_button
                yes_button.configure(command=lambda: self.google_navigation('yes'))
                no_button.configure(command=lambda: self.google_navigation('no'))

    def quit_click(self):
        self.destroy()
        global driver
        driver.quit()
        
                    
root = Validator()
root.title('Validator')
root.mainloop()