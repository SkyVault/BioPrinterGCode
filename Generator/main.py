#!/usr/bin/env python
import tkinter as tk

from functools import *


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()

    def createWidgets(self, varmap, content):
        FONT = 32
        self.content = content
        self.varmap = varmap
        
        # Create the export filepath entry
        self.filepathvar = tk.StringVar()
        self.filepathvar.set("temp.ngc")
        self.filepathentry = tk.Entry(self, textvariable=self.filepathvar)
        self.filepathentry.grid(row=0, column=0)
        self.filepathentry.config(font=("Courier", FONT))

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

        self.quitButton = tk.Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(row=index, column=1)
        self.quitButton.config(font=("Courier", FONT))

    def generatePart(self):
        values = []
        for val in self.stringvars:
            values.append(self.stringvars[val].get())

        newcontent = self.content.format(*values)
        with open(self.filepathvar.get(), "w") as f:
            f.write(newcontent)
        

def run():
    lines = ""
    content = ""
    
    varmap = {}

    with open("zamboni.ngc_template", "r") as f:
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
