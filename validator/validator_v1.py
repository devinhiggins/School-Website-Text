from os.path import join
from tkinter import messagebox, Tk, Label
from tkinter.ttk import Button
from selenium import webdriver
import pandas as pd
import csv

root = Tk()

# input_name = input('Enter CSV input: ')
input_dir = '/Users/jhp/MSU/project/schooltext/jhp/data/national_dump'
input_name = 'NationalDone.csv'
input_csv = pd.read_csv(join(input_dir, input_name), header=None)

school = input_csv[0]
city = input_csv[1]
zipcode = input_csv[2].astype(str)
urls = input_csv[3]
query = school + ',' + city + ',' + zipcode

index = 0
driver = webdriver.Firefox()
driver.get('{}'.format(urls[index]))


def append_records(filename, output_dir=input_dir):
    with open(join(output_dir, filename), 'a', newline='') as fw:
        writer = csv.writer(fw)
        writer.writerow([school[index], city[index], zipcode[index], urls[index]])


def next_url():
    global index
    if index < len(urls) - 1:  # continue as normal if in parameter
        index += 1  # update index we are on
        query_label.config(text='{}'.format(query[index]))
        driver.get('{}'.format(urls[index]))
        return index  # remember our index

    if (index + 1) >= len(urls):  # this is a check if there are any more entries
        messagebox.showinfo('Attention', 'No more entries, closing program')
        quit_click()


def yes_click():
    append_records('TruePositive.csv')
    next_url()


def no_click():
    append_records('FalsePositive.csv')
    next_url()


def quit_click():  # closes out the application
    root.destroy()
    driver.quit()


query_label = Label(root, text='{}'.format(query[index]))  # reads query label
query_label.pack()

yes_button = Button(root, text='Yes', command=yes_click)
yes_button.pack()

no_button = Button(root, text='No', command=no_click)
no_button.pack()

quit_button = Button(root, text='Quit', command=quit_click)
quit_button.pack()

root.mainloop()
