#!/usr/bin/env python

import pickle
import Tkinter as tk
import tkFileDialog
import tkMessageBox
import os.path
import os
import sys
import csv

from tkinter_utils import *

from Tkinter import LEFT, Grid, Frame, Y, RIGHT, BOTH

from functools import *
from ntpath import basename

FONT = 16
SAVE = "save"

ToSave = {}

def Confirm(msg):
    result = tkMessageBox.askquestion("Reset to default values?", "Are You Sure?", icon='warning')
    return result == "yes"

# Loading the save file
if os.path.isfile(SAVE):
    with open(SAVE, 'rb') as f:
        ToSave = pickle.load(f)
else:
    ToSave = {
        "outfile": "zamboni_1.ngc",
        "template": "zamboni.ngc_template",
        "csv": "log.csv",
    }
    with open(SAVE, 'wb') as f:
        pickle.dump(ToSave, f, protocol=pickle.HIGHEST_PROTOCOL)

print(ToSave)

def Save():
    with open(SAVE, 'wb') as f:
        pickle.dump(ToSave, f, protocol=pickle.HIGHEST_PROTOCOL)

def makeFilepathInput(parent, path_change, label="DEFAULT", default_path="C:/"):
    frame = Frame(parent)

    label = tk.Label(frame, text=label)
    label.pack(side="top")

    outvar = tk.StringVar()
    outvar.set(default_path)
    entry = tk.Entry(frame, textvariable=outvar)
    entry.config(font=("Courier", FONT))
    entry.pack(side="left", expand=1)

    def open_dialog():
        result = tkFileDialog.askopenfilename(initialdir="", title="Select file", filetypes=(("GCode files", "*.ngc"), ("all files", "*.*")))
        if (result != ""):
            path_change(result)

    open_dialog = tk.Button(frame, text="...", command=open_dialog)
    open_dialog.config(font=("Courier", FONT / 2))
    open_dialog.pack(side="left")

    return (frame, outvar)

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def createWidgets(self, varmap, content):
        self.content = content
        self.varmap = varmap

        def outfile_pathchange(newpath):
            ToSave["outfile"] = newpath
            Save()
            self.filepathoutvar.set(newpath)

        def templatefile_pathchange(newpath):
            ToSave["template"] = newpath
            Save()
            self.filepathvar.set(newpath)
            for v in self.variable_fields:
                v.pack_forget()
            self.variable_fields = []
            
            # Restart
            python = sys.executable
            os.execl(python, python, * sys.argv)

        self.filepathoutentry, self.filepathoutvar = makeFilepathInput(self, outfile_pathchange, default_path=ToSave["outfile"], label="output file")
        self.filepathoutentry.grid(row=0, column=1)

        self.filepathentry, self.filepathvar = makeFilepathInput(self, templatefile_pathchange,  default_path=ToSave["template"], label="template file")
        self.filepathentry.grid(row=0, column=0)

        self.stringvars = {}

        self.input_fields_frame = VerticalScrolledFrame(self)
        self.input_fields_frame.grid(row=1, column=0, columnspan=2)

        def generateInputFields():
            self.variable_fields = []
            for key in varmap:
                name = varmap[key][0]
                default = varmap[key][1]
                docstring = varmap[key][2]

                # sub = Frame(self.input_fields_frame)
                sub = Frame(self.input_fields_frame.interior)
                
                if docstring is not "":
                    CreateToolTip(sub, docstring)

                v = tk.StringVar()
                v.set(default)
                e = tk.Entry(sub, textvariable=v)
                e.config(font=("Courier", FONT))

                # Make the names look prettier
                new_name = ' '.join(name[1:].split('_'))
                new_name = new_name.title()

                l = tk.Label(sub, text=new_name)
                l.config(font=("Courier", FONT))
                self.stringvars[key] = v

                e.pack(side="right", fill="both")
                l.pack(side="right", fill="both")
                sub.pack(side="top", anchor="w", fill="both")
                self.variable_fields.append(sub)

        generateInputFields()
        generateInputFields()

        self.lbtn_frame = Frame(self)
        self.lbtn_frame.grid(row=2, column=0)

        self.generateButton = tk.Button(self.lbtn_frame, text="Generate", command=self.generatePart)
        self.generateButton.config(font=("Courier", FONT))
        self.generateButton.pack(side="left")
        
        def restart():
            if not Confirm(""): return
            # Restart
            python = sys.executable
            os.execl(python, python, * sys.argv)

        resetButton = tk.Button(self.lbtn_frame, text="Default", command=restart)
        resetButton.config(font=("Courier", FONT))
        resetButton.pack(side="left")

        self.btn_frame = Frame(self)
        self.btn_frame.grid(column=1, row=2)

        self.decButton = tk.Button(self.btn_frame, text="-", command= lambda: self.addFileName(-1))
        self.decButton.config(font=("Courier", FONT))
        self.decButton.pack(side="left")

        self.incButton = tk.Button(self.btn_frame, text="+", command= lambda: self.addFileName(1))
        self.incButton.config(font=("Courier", FONT))
        self.incButton.pack(side="left")

        self.quitButton = tk.Button(self.btn_frame, text='Quit', command=self.quit)
        self.quitButton.config(font=("Courier", FONT))
        self.quitButton.pack(side="left")


    def addFileName(self, val):
        path = self.filepathoutvar.get()
        name, ext = basename(path).split('.')

        name, num = name.split('_')

        num = int(num)
        num += val
        self.filepathoutvar.set("{}_{}.{}".format(name, num, ext))
        ToSave["outfile"] = self.filepathoutvar.get()
        Save()


    def generatePart(self):
        Save()
        values = []
        for val in self.stringvars:
            values.append(self.stringvars[val].get())

        newcontent = self.content.format(*values)
        with open(self.filepathoutvar.get(), "w") as f:
            f.write(newcontent)
        
        names = [self.varmap[_n][0] for _n in self.varmap]

        the_list = []

        if os.path.isfile(ToSave["csv"]):
            with open(ToSave["csv"], 'rb') as f:
                reader = csv.reader(f)
                the_list = list(reader) 
    
        if len(the_list) == 0 or the_list[0][0] != names[0]:
            the_list.insert(0, names)            

        # Log to csv file
        with open(ToSave["csv"], "wb+") as f:
            writer = csv.writer(f)
            for row in the_list:
                writer.writerow(row)
            writer.writerow(values)

def extractVariables():
    lines = ""
    content = ""
    
    varmap = {}

    with open(ToSave["template"], "r") as f:
        lines = f.readlines() 
        f.seek(0)
        content = f.read()

    # Get the variables to change

    # Moves the index until the first non whitespace character
    def skipWhitespace(line, index):
        while index < len(line) and line[index] in "\n\t\r ":
            index += 1
        return index
    
    # Moves the index to the first non whitespace character
    def skipTillWhitespace(line, index):
        while index < len(line) and line[index] not in "\n\t\r ":
            index += 1
        return index

    numbers = 0
    line_number = 0
    for line in lines:
        # If we find the variable 
        if line.startswith('#') and line.find("?") >= 0:
            index = 1
            end = index
            assert(line[index] == '<')

            # Extract the variables name
            index += 1
            while end < len(line) and line[end] is not '>':
                end+=1

            name = (line[index:end])

            # Change the question mark to the {N} syntax
            curly = line.find("?")
            part_1 = line[:curly]
            part_2 = line[curly+1:]
            line = part_1 + "{" + str(numbers) + "}" + part_2
            
            # Find the default value if it exists
            index = line.find("}") + 1
            index = skipWhitespace(line, end + 1)
            end = curly
            the_default = 0
            the_comment = ""
            
            index = line.find("(")
            if index >= 0 and line[index] is '(':
                index+=1
                while end < len(line) and line[end] is not ')':
                    end+=1
                the_default = line[index:end]

                index = end + 1
                index = skipWhitespace(line, index)
                if index is not len(line):
                    if line[index] is not '(':
                        print("Malformed documentation comment for {}".format(name))
                    else:
                        index += 1
                        end = index
                        while end < len(line) and line[end] is not ')':
                            end+=1
                        the_comment = line[index:end]
        
            varmap[numbers] = (name, the_default, the_comment)
            numbers += 1

        lines[line_number] = line
        line_number += 1

    # Merge all of the changed lines into the content
    content = reduce(lambda a, b: a+b, lines)
    return (varmap, content)

def run():
        varmap, content = extractVariables()

        # Start the application
        app = Application()
        app.createWidgets(varmap, content)
        app.master.title('Generator')
        app.mainloop()

# Entry point
if __name__=='__main__':
    run()
