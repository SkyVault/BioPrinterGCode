#!/usr/bin/env python

import pickle
import Tkinter as tk
from Tkinter import LEFT, Grid, Frame

from functools import *
from ntpath import basename
import os.path

FONT = 32
SAVE = "save"

ToSave = {}

if os.path.isfile(SAVE):
    with open(SAVE, 'rb') as f:
        ToSave = pickle.load(f)
else:
    ToSave = {
        "outfile": "zamboni_1.ngc",
        "template": "zamboni.ngc_template"
    }
    with open(SAVE, 'wb') as f:
        pickle.dump(ToSave, f, protocol=pickle.HIGHEST_PROTOCOL)

print(ToSave)

def Save():
    with open(SAVE, 'wb') as f:
        pickle.dump(ToSave, f, protocol=pickle.HIGHEST_PROTOCOL)

class FrameGroup(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.all_instances = []
        self.counter = 0

    def Add(self):
        self.counter += 1
        name = "Frame %s" % self.counter 
        subframe = Subframe(self, name=name)
        subframe.pack(side="left", fill="y")
        self.all_instances.append(subframe)

    def Remove(self, instance):
        # don't allow the user to destroy the last item
        if len(self.all_instances) > 1:
            index = self.all_instances.index(instance)
            subframe = self.all_instances.pop(index)
            subframe.destroy()

    def HowMany(self):
        return len(self.all_instances)

    def ShowMe(self):
        for instance in self.all_instances:
            print(instance.get())


class Subframe(tk.Frame):
    def __init__(self, parent, name):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.e1 = tk.Entry(self)
        self.e2 = tk.Entry(self)
        self.e3 = tk.Entry(self)
        label = tk.Label(self, text=name, anchor="center")
        add_button = tk.Button(self, text="Add", command=self.parent.Add)
        remove_button = tk.Button(self, text="Remove", command=lambda: self.parent.Remove(self))

        label.pack(side="top", fill="x")
        self.e1.pack(side="top", fill="x")
        self.e2.pack(side="top", fill="x")
        self.e3.pack(side="top", fill="x")
        add_button.pack(side="top")
        remove_button.pack(side="top")


def makeFilepathInput(parent, default_path="C:/"):
    frame = Frame(parent)

    outvar = tk.StringVar()
    outvar.set(default_path)
    entry = tk.Entry(frame, textvariable=outvar)
    entry.config(font=("Courier", FONT))
    entry.pack(side="left")

    def test():
        print("Hello")

    open_dialog = tk.Button(frame, text="...", command=test)
    open_dialog.config(font=("Courier", FONT / 2))
    open_dialog.pack(side="left")

    return (frame, outvar)

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()

    def createWidgets(self, varmap, content):
        self.content = content
        self.varmap = varmap
        
        # Create the export filepath entry
        # self.filepathoutvar = tk.StringVar()
        # self.filepathoutvar.set("zambonie_1.ngc")
        # self.filepathoutentry = tk.Entry(self, textvariable=self.filepathoutvar)
        # self.filepathoutentry.grid(row=0, column=1)
        # self.filepathoutentry.config(font=("Courier", FONT))

        self.filepathoutentry, self.filepathoutvar = makeFilepathInput(self, default_path=ToSave["outfile"])
        self.filepathoutentry.grid(row=0, column=1)

        self.filepathentry, self.filepathvar = makeFilepathInput(self, default_path=ToSave["template"])
        self.filepathentry.grid(row=0, column=0)

        self.stringvars = {}

        # Create the different inputs for the variables
        index = 0
        for key in varmap:
            name = varmap[key][0]
            default = varmap[key][1]

            v = tk.StringVar()
            v.set(default)
            e = tk.Entry(self, textvariable=v)
            e.config(font=("Courier", FONT))

            l = tk.Label(self, text=name[1:])
            l.config(font=("Courier", FONT))
            l.grid(row=index+1, column=0)

            e.grid(row=index+1, column=1)
            self.stringvars[key] = v
            index += 1

        index += 1

        self.generateButton = tk.Button(self, text="Generate", command=self.generatePart)
        self.generateButton.grid(row=index, column=0) 
        self.generateButton.config(font=("Courier", FONT))

        self.btn_frame = Frame(self)
        self.btn_frame.grid(column=1, row=index)

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
        values = []
        for val in self.stringvars:
            values.append(self.stringvars[val].get())

        newcontent = self.content.format(*values)
        with open(self.filepathoutvar.get(), "w") as f:
            f.write(newcontent)
        

def run():
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
            
            index = line.find("(")
            if index >= 0 and line[index] is '(':
                index+=1
                while end < len(line) and line[end] is not ')':
                    end+=1
                the_default = line[index:end]
            
            varmap[numbers] = (name, the_default)
            numbers += 1
        lines[line_number] = line
        line_number += 1

    # Merge all of the changed lines into the content
    content = reduce(lambda a, b: a+b, lines)

    # Start the application
    app = Application()
    app.createWidgets(varmap, content)
    app.master.title('Generator')
    app.mainloop()

# Entry point
if __name__=='__main__':
    run()
