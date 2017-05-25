# -*- coding: utf-8 -*-
"""
Created on Tue May 31 11:42:13 2016

@author: Gordon Gibb and Jeremy Novell
"""

import Tkinter as Tk
import ttk
import tkMessageBox
import tkFileDialog
from CGLtk import ScrolledText
import chimera
import os
import Tetr
import time
from chimera.baseDialog import ModelessDialog






        
#abstract class containing code common to the Tetr and Lev00        
class LevGUI(ModelessDialog):

    def fillInUI(self, parent):
        self.parent=parent
        
        self.timestamp=time.time()
        
        self.prevtext=""
        
        row = 0
        
        #allow window (and things within it) to be resizable
        parent.rowconfigure(0,weight=1)
        parent.columnconfigure(0,weight=1)
        
        #if the window is clicked on, the entry widget is given focus
        parent.bind("<Button-1>", self.focus_callback)
       
        
#################### Create console output widget and label (LHS of window) #####################
        
        #put them in their own frame (LHS column of window)
        consoleFrame=Tk.Frame(parent)
        consoleFrame.grid(row=0,column=0,padx=5,sticky=Tk.W+Tk.E+Tk.N+Tk.S)
        
        consoleFrame.columnconfigure(0,weight=1) #make resizable in the x direction
        
        #working directory label:
        self.wdirlabel=Tk.Label(consoleFrame,text="wkdir= '?'")
        self.wdirlabel.grid(row=row,column=0,sticky=Tk.W)
        row+=1
        
       
        consolerow=row
        
        #text output widget (with scrollbar)
        scrollbar=Tk.Scrollbar(consoleFrame)
        t=Tk.Text(consoleFrame,wrap=Tk.WORD,width=80, height=45,yscrollcommand=scrollbar.set)
        t.config(font=('courier', 12, 'normal'))
        t.grid(row=row,column=0, sticky=Tk.W+Tk.E+Tk.N+Tk.S)
        consoleFrame.rowconfigure(row,weight=1) #make resizable in the y direction
        
        scrollbar.grid(row=row, column=1, sticky='ns')
        scrollbar.config(command=t.yview)
        
        self.outText = t
        
        #allow a button press to focus the text box (allows selection of text from concole output) 
        t.bind('<ButtonPress>', lambda e,t=t: t.focus(),
                   add = True)

        # set the initial text
        self.updateText(self.App+" starting...\n")
        
        

        
#################### text entry widget (bottom of screen) #####################

        #entry widget at the bottom left
        Tk.Label(parent, text=self.App+" Input:").grid(row=row, sticky=Tk.W,padx=5)
        row += 1
        self.entry = Tk.Entry(parent)
        self.entry.config(relief=Tk.SUNKEN,font=('courier', 12, 'normal'))
        self.entry.grid(row=row,column=0, sticky=Tk.W+Tk.E,columnspan=1,padx=5)
        
        #enter button at bottom right
        Tk.Button(parent,text="<- Enter Command",command=self._updateInput).grid(row=row,column=1, sticky=Tk.W+Tk.E,padx=5)
        
        # Tell the entry widget to watch the input
        self.consoleInput = Tk.StringVar()
        self.entry["textvariable"] = self.consoleInput
        self.entry.focus_set()

        # Get a callback when return key is pressed

        self.entry.bind('<Key-Return>', self._updateInput)
    
    
#################### Create options frame (RHS of window) #####################
        
        optionsFrame=Tk.Frame(parent)
        optionsFrame.grid(row=0,column=1,sticky=Tk.N,padx=5)
        
        optionsrow=0
        
        #add some vertical space (in this case just some blank space)
        Tk.Label(optionsFrame,text=" ").grid(row=optionsrow)
        
        optionsrow+=1
        
#--------frame for view options (ball and stick, wireframe etc)---------

        viewFrame=Tk.Frame(optionsFrame,relief=Tk.GROOVE,borderwidth=1)
        viewFrame.grid(row=optionsrow,column=0,sticky=Tk.W+Tk.E)
        
        options = [
            ("Stick",0),
            ("Ball and Stick",1),
            ("Wireframe",2),
            ("Sphere",3)
        ]
        
        self.voption=Tk.IntVar()
        self.voption.set(0) #set initial view option 
        
        framecol=0
        framerow=0
        
        
        Tk.Label(viewFrame, text="Display Options:").grid(row=framerow, sticky=Tk.W)
        
        for txt,val in options:
            framerow+=1
            Tk.Radiobutton(viewFrame,text=txt,padx=20,variable=self.voption,
                           command=self.SetViewOption,value=val).grid(row=framerow, column=framecol,sticky=Tk.W)
        
       
        
        self.showAtom=Tk.IntVar()
        self.showNumber=Tk.IntVar()
        
        framerow+=1
        Tk.Checkbutton(viewFrame,text="Show Numbers" ,variable=self.showNumber,command=self.UpdateLabels).grid(row=framerow,column=framecol,sticky=Tk.W)
        
        framerow+=1
        Tk.Checkbutton(viewFrame,text="Show Species" ,variable=self.showAtom,command=self.UpdateLabels).grid(row=framerow,column=framecol,sticky=Tk.W)
        
        
        if self.App=="Lev00":
            
            framerow+=1
            
            ttk.Separator(viewFrame,orient=Tk.HORIZONTAL).grid(row=framerow,sticky=Tk.W+Tk.E)
            
            framerow+=1
            
            Tk.Label(viewFrame, text="File Display:").grid(row=framerow, sticky=Tk.W)
            
            lev00options = [
                ("Full Structure",0),
                ("Density",1)
                ]
            
            self.levvoption=Tk.IntVar()
            self.levvoption.set(0)
            
            self.lev00radio=[]
            for txt,val in lev00options:
                framerow+=1
                self.lev00radio.append(Tk.Radiobutton(viewFrame,text=txt,padx=20,variable=self.levvoption,
                            command=self.SetLev00ViewOption,value=val))
                self.lev00radio[-1].grid(row=framerow, column=framecol,sticky=Tk.W)
            
            self.lev00radio[1].config(state=Tk.DISABLED)
            
        
        
        optionsrow +=1
        Tk.Label(optionsFrame,text=" ").grid(row=optionsrow) #blank space
        
        
#--------frame for axis options---------        
        
        optionsrow+=1
        
        axisFrame=Tk.Frame(optionsFrame,relief=Tk.GROOVE,borderwidth=1)
        axisFrame.grid(row=optionsrow,sticky=Tk.W+Tk.E)
        
        axisRow=0
        Tk.Label(axisFrame,text="Axis Options:").grid(row=axisRow)
        
        axisRow+=1
        self.axisshow=Tk.IntVar()
        Tk.Checkbutton(axisFrame,text="Toggle Axis",variable=self.axisshow,command=self.axis_toggle).grid(row=axisRow,columnspan=2,sticky=Tk.W)
        
        axisRow+=1
        Tk.Label(axisFrame,text="x-coord:").grid(row=axisRow,column=0,sticky=Tk.E)
        self.xaxis=Tk.Text(axisFrame,width=6,height=1)
        self.xaxis.grid(row=axisRow,column=1)
        self.xaxis.insert(Tk.END,"0.0")
        
        axisRow+=1
        Tk.Label(axisFrame,text="y-coord:").grid(row=axisRow,column=0,sticky=Tk.E)
        self.yaxis=Tk.Text(axisFrame,width=6,height=1)
        self.yaxis.grid(row=axisRow,column=1)
        self.yaxis.insert(Tk.END,"0.0")
        
        axisRow+=1
        Tk.Label(axisFrame,text="z-coord:").grid(row=axisRow,column=0,sticky=Tk.E)
        self.zaxis=Tk.Text(axisFrame,width=6,height=1)
        self.zaxis.grid(row=axisRow,column=1)
        self.zaxis.insert(Tk.END,"0.0")
        
        axisRow+=1
        Tk.Label(axisFrame,text="Size:").grid(row=axisRow,column=0,sticky=Tk.E)
        self.saxis=Tk.Text(axisFrame,width=6,height=1)
        self.saxis.grid(row=axisRow,column=1)
        self.saxis.insert(Tk.END,"5.0")
        
        axisRow+=1
        Tk.Button(axisFrame,text="Update",command=self.make_axis).grid(row=axisRow,sticky=Tk.W+Tk.E,column=0)
        
        Tk.Button(axisFrame,text="Reset",command=self.reset_axis).grid(row=axisRow,sticky=Tk.W+Tk.E,column=1)
        
        axisRow +=1
        self.lattice=Tk.IntVar()
        self.LatVecButton=Tk.Checkbutton(axisFrame,text="Toggle Vectors (Vs)",variable=self.lattice,command=self.ToggleLatticeVectors)
        self.LatVecButton.grid(row=axisRow,sticky=Tk.W,columnspan=2)
        self.LatVecButton.config(state=Tk.DISABLED)
        
        optionsrow +=1
        
        Tk.Label(optionsFrame,text=" ").grid(row=optionsrow) #blank space
        
        
#-------frame for console display options ------------
        optionsrow+=1
        
        toptFrame=Tk.Frame(optionsFrame,relief=Tk.GROOVE,borderwidth=1)
        toptFrame.grid(row=optionsrow,sticky=Tk.W+Tk.E)
        
        Tk.Label(toptFrame,text=self.App+" console:").grid(row=0,sticky=Tk.W)
        
        dispoptions = [
            ("Latest output",0),
            ("All output",1),
        ]
        
        self.DispOption=Tk.IntVar()
        self.DispOption.set(0) #set initial view option 
        
        framecol=0
        framerow=0
        
        for txt,val in dispoptions:
            framerow+=1
            Tk.Radiobutton(toptFrame,text=txt,padx=20,variable=self.DispOption,
                           command=self.SwitchConsoleView,value=val).grid(row=framerow, column=framecol,sticky=Tk.W)
        
        
        optionsrow+=1
        Tk.Label(optionsFrame,text=" ").grid(row=optionsrow) #blank space
#--------frame for atom selections---------  
        
        if self.App=="Tetr":
            optionsrow+=1
            
            #get selected atoms
            
            selectionFrame=Tk.Frame(optionsFrame,relief=Tk.GROOVE,borderwidth=1)
            selectionFrame.grid(row=optionsrow,sticky=Tk.W+Tk.E)
            
            Tk.Label(selectionFrame,text="Atom Selection:").grid(row=0,columnspan=2,sticky=Tk.W)
            Tk.Button(selectionFrame,text="Get Selection",command=self.GetSelection).grid(row=1,column=0, sticky=Tk.W+Tk.E)
            Tk.Button(selectionFrame,text="?",command=self.selectionHelp).grid(row=1,column=1, sticky=Tk.W+Tk.E)
            
            
            optionsrow +=1
            
            Tk.Label(optionsFrame,text=" ").grid(row=optionsrow)
        
#--------frame for reset controls---------
        
        optionsrow +=1
        
        resetFrame=Tk.Frame(optionsFrame,relief=Tk.GROOVE,borderwidth=1)
        resetFrame.grid(row=optionsrow,sticky=Tk.W+Tk.E)
        
        
        Tk.Label(resetFrame,text="Restart "+self.App+":").grid(row=0,column=0,columnspan=2,sticky=Tk.W)
        Tk.Button(resetFrame,text="Restart",command=self.reset_app).grid(row=1,column=0,sticky=Tk.W+Tk.E)
        Tk.Button(resetFrame,text="?",command=self.resetHelp).grid(row=1,column=1, sticky=Tk.W+Tk.E)
        resetFrame.columnconfigure(0,weight=1)
        resetFrame.columnconfigure(1,weight=1)
        
   
   
   
   
    def CheckSelectionFile(self,force=False):
        if self.App == "Tetr":
            file=self.wkdir+"/tetr.slc"
        else:
            file=self.wkdir+"/lev00.slc"
            
        print("Checking for selection file")
        if os.path.isfile(file):
            print("selection file exists!")
            
            if self.timestamp < os.stat(file).st_mtime or force:
                if not force:
                    self.timestamp = os.stat(file).st_mtime
                
                #read file
                f=open(file,"r")

                atoms=[]

                for line in f:
                    line=line.split()
                    for item in line:
                        atoms.append(int(item))
                    
                print(atoms)
                
                f.close()
                #put selection into tetr
                
                self.ChimeraInterface.SetSelection(atoms)
   
   
    def unfinished(self,e=None):
        print("Nothing to see here... yet")
        
        
    def checkVectorsToggle(self):
        filename=self.wkdir+"/vectors.vct"
        
        if os.path.isfile(filename):
            if self.latvectime < os.stat(filename).st_mtime:
                
                self.latvectime = os.stat(filename).st_mtime
                
                self.LatVecButton.config(state=Tk.NORMAL)
                
                self.lattice.set(1)
                
                self.ToggleLatticeVectors()
           
        

        
    def ToggleLatticeVectors(self,e=None):
        if self.lattice.get() == 1:
            filename=self.wkdir+"/vectors.vct"
            
            if not os.path.isfile(filename):
                tkMessageBox.showwarning("Warning","No vectors file (vectors.vct) present. Create this using the 'Vs' option in "+self.App)
                self.lattice.set(0)
                return
            
            f=open(filename,"r")
            
            nvec=int(f.readline())
            vectors=[]
            for i in range(nvec):
                line=f.readline()
                entries=line.split()
                vect=[]
                for entry in entries:
                    num=float(entry)
                    print(entry,num)
                    vect.append(num)
                vectors.append(vect)

            f.close()
            
            f=open(self.appdir+"/lattice.bild","w")
            
            try:
                v=vectors[0]
                f.write(".color 0 1 1\n")
                f.write(".arrow 0.0 0.0 0.0 "+str(v[0])+" "+str(v[1])+" "+str(v[2])+'\n')

                v=vectors[1]
                f.write(".color 1 1 0\n")
                f.write(".arrow 0.0 0.0 0.0 "+str(v[0])+" "+str(v[1])+" "+str(v[2])+'\n')
                
                v=vectors[2]
                f.write(".color 1 0 1\n")
                f.write(".arrow 0.0 0.0 0.0 "+str(v[0])+" "+str(v[1])+" "+str(v[2])+'\n')
                
                v=vectors[3]
                f.write(".color 1 0.64 0\n")
                f.write(".arrow 0.0 0.0 0.0 "+str(v[0])+" "+str(v[1])+" "+str(v[2])+'\n')
                
                v=vectors[4]
                f.write(".color 0.58 0 0.82\n")
                f.write(".arrow 0.0 0.0 0.0 "+str(v[0])+" "+str(v[1])+" "+str(v[2])+'\n')
                
                v=vectors[5]
                f.write(".color 0.2 1 0.8\n")
                f.write(".arrow 0.0 0.0 0.0 "+str(v[0])+" "+str(v[1])+" "+str(v[2])+'\n')
            except:
                pass
            
            f.close()
            
            print("Lattice vectors written to file")
            
            self.ChimeraInterface.ShowLattice(True)
            
        else:
            self.ChimeraInterface.ShowLattice(False)
        
    def SwitchConsoleView(self,e=0):
        if self.DispOption.get() == 0: #latest output
            text = self.prevtext
            self.displayText(text)
            self.toption=0
        else:
            text= self.fulltext
            self.toption=1
            self.displayText(text)
        
    #replaces text in the tetr console/terminal with "text"
    def displayText(self,text):
        self.outText.config(state = Tk.NORMAL) #allow modification of the text
        self.outText.delete(1.0,Tk.END)
        self.outText.insert(Tk.END, text)
        self.outText.config(state = Tk.DISABLED) #disable modification of the text
        self.outText.see(Tk.END)

    
    
    def UpdateLabels(self,e=None):
        num=self.showNumber.get()
        spec=self.showAtom.get()
        print("Atom Number=",num)
        print("Atom Species=",spec)
        self.ChimeraInterface.UpdateLabels(num,spec)
        
        
    
    #gives focus to the entry widget
    def focus_callback(self,e):
        self.entry.focus_set()
        
        
        
    #gets the view option selection and sends it to the chimera interface    
    def SetViewOption(self):
        print("View Option=",self.voption.get())
        self.ChimeraInterface.SetViewOption(self.voption.get())
    
    #gets the atom selections from chimera and pastes the text into the input box 
    def GetSelection(self):
        
        length=self.getmaxlen()
        if length <=0:
            length=1000
            print("Warning cannot find length - resorting to default of 1000")
        
        text=self.ChimeraInterface.GetSelection()
        if text==None:
            tkMessageBox.showwarning("Warning","No atoms in selection")
        elif len(text) > length:
            tkMessageBox.showwarning("Warning","The size of the selection string is too big to be input into tetr. Please make a smaller selection.")
        else:
            self.consoleInput.set(text)
    
    #find the length of input lines in real8.inc in the tetr source directory
    def getmaxlen(self):

        file = self.rootdir+"/real8.inc"
        f=open(file,"r")

        n=0
        length=-1
        for line in f:
            n+=1
            pos=line.find("LENG2=")
            if pos >=0: #if we found this in a line...
                ln=line[pos+6:-1]
                for i in range(len(ln)): #read in number till the end of the number
                    if not ln[i].isdigit():
                        break
                num=ln[0:i]
                length=int(num)
                break

        f.close()

        print "line length=",length
        return length

    
    #puts up a dialogue offering help with the selection feature
    def selectionHelp(self):
        tkMessageBox.showinfo("Selection Help",('Use the "Get Selection" button to paste atoms selected in the Chimera GUI into Tetr:\n'
            '- Make your selection in Chimera\n'
            '- In Tetr select "T. Tag atoms"\n'
            '- click "Get Selection"\n'
            '- Hit Return or "Enter Command"\n\n'
            'You may then apply the operation of your choosing to these selected atoms in Tetr.'))
    
    #gets text in the input field and puts it into tetr/lev00
    def _updateInput(self, event=0):
        
        inString = self.consoleInput.get()
        try:
            self.ChimeraInterface.setInput(inString)
        except IOError:
            tkMessageBox.showerror("Error","The "+self.App+" process has ended (user-exited or crashed). Please restart "+self.App+" via the 'Restart' button.")
            return
        #self._updateText(inString + "\n")
        self.fulltext+=inString+"\n"
        self.consoleInput.set("")
        self.prevtext=""
        
        time.sleep(self.pausetime) #wait for tetr/lev00 to do its thing
        #try:
            #outputText = self.ChimeraInterface.getOutput()
        #except IOError:
            #tkMessageBox.showerror("Error","The "+self.App+" process has ended (user-exited or crashed). Please restart "+self.App+" via the 'Restart' button.")
            #return
        #self.updateText(outputText) #update tetr/lev00 output text
        #if self.App == "Lev00":
            #val = self.levvoption.get()
            #self.ChimeraInterface.refreshGeom(opt=val)
            #if val == 0:
                #self.CheckSelectionFile()
            #self.CheckforCube()
        #else:
            #self.ChimeraInterface.refreshGeom() #update model in chimera
            #self.CheckSelectionFile()
        #self.UpdateLabels() #re-apply labels if they are on
        #if self.App == "Tetr":
            
    
    
    def timer(self):
        
        try:
            outputText = self.ChimeraInterface.getOutput()
        except IOError:
            tkMessageBox.showerror("Error","The "+self.App+" process has ended (user-exited or crashed). Please restart "+self.App+" via the 'Restart' button.")
            return
        except:
            print("SOMETHING IS WRONG")
            return
        
        if outputText != "":
            self.updateText(outputText) #update tetr/lev00 output text
        
        if self.App == "Lev00":
            val = self.levvoption.get()
            self.ChimeraInterface.refreshGeom(opt=val)
            if val == 0:
                self.CheckSelectionFile()
            self.CheckforCube()
        else:
            self.ChimeraInterface.refreshGeom() #update model in chimera
            self.CheckSelectionFile()
        self.checkVectorsToggle()
        self.UpdateLabels() #re-apply labels if they are on
        
        self.parent.after(500,self.timer)
    



    def updateText(self, text):
        self.fulltext+=text
        self.prevtext+=text
       
        if self.toption==0:
            self.displayText(self.prevtext)
        else:
            self.displayText(self.fulltext)
        
    
        
        
    #Create the axis file to be displayed in Chimera
    def make_axis(self):
        axisfile=self.appdir+"/axis.bild"
        
        #check for ".Tetr/.Lev00 directory" - if it isn't there, make it'
        if not (os.path.isdir(self.appdir)):
            print "Making ",self.appdir
            os.mkdir(self.appdir)
        
        #get values from the text fields
        x=self.xaxis.get("1.0",Tk.END)
        y=self.yaxis.get("1.0",Tk.END)
        z=self.zaxis.get("1.0",Tk.END)
        l=self.saxis.get("1.0",Tk.END)
        
        #try to parse these strings into floats. Display an error if not
        try:
            xs=float(x)
            ys=float(y)
            zs=float(z)
            ls=float(l)
        except ValueError:
            print "Invalid option"
            tkMessageBox.showerror("Error","Invalid number in field. Please try again, or press 'Reset' to reset the axis values")
            return
        
        #produce axis file
        print "Opening ",axisfile
        f=open(axisfile,"w")
        #f.write(".sphere "+str(xs)+" "+str(ys)+" "+str(zs)+" "+str(0.5)+"\n") #uncomment to display ball in axis
        f.write(".font SERIF 50 bold\n")
        f.write(".color 1 0 0\n")
        f.write(".arrow "+str(xs)+" "+str(ys)+" "+str(zs)+" "+str(ls+xs)+" "+str(ys)+" "+str(zs)+"\n")
        f.write(".cmov "+str(ls+xs)+" "+str(ys)+" "+str(zs)+"\nx\n")

        
        f.write(".color 0 1 0\n")
        f.write(".arrow "+str(xs)+" "+str(ys)+" "+str(zs)+" "+str(xs)+" "+str(ls+ys)+" "+str(zs)+"\n")
        f.write(".cmov "+str(xs)+" "+str(ls+ys)+" "+str(zs)+"\ny\n")
        
        f.write(".color 0 0 1\n")
        f.write(".arrow "+str(xs)+" "+str(ys)+" "+str(zs)+" "+str(xs)+" "+str(ys)+" "+str(ls+zs)+"\n")
        f.write(".cmov "+str(xs)+" "+str(ys)+" "+str(ls+zs)+"\nz\n")
        
        f.close()
        
        print "File written"
        
        #display new axis
        if self.axisshow.get() == 1:
            self.ChimeraInterface.ShowAxis(True)
        else:
            tkMessageBox.showwarning("Warning","You need to toggle 'Show Axis' to on in order to view the axis")
    
    #reset the axis text fields to default
    def reset_axis(self):
        self.xaxis.delete(1.0,Tk.END)
        self.xaxis.insert(Tk.END,"0.0")
        
        self.yaxis.delete(1.0,Tk.END)
        self.yaxis.insert(Tk.END,"0.0")
        
        self.zaxis.delete(1.0,Tk.END)
        self.zaxis.insert(Tk.END,"0.0")
        
        self.saxis.delete(1.0,Tk.END)
        self.saxis.insert(Tk.END,"5.0")
        
        if self.axisshow.get() == 1:
            self.ChimeraInterface.ShowAxis(True)
    
    #toggle the axis on/off
    def axis_toggle(self):
        val=self.axisshow.get()
        
        if val==1: #show the axis
            self.make_axis()
            self.ChimeraInterface.ShowAxis(True)
        else:
            self.ChimeraInterface.ShowAxis(False)
            
            
            
    def getShell(self):
        configfile=self.appdir+"/shell.dat"
        
        if os.path.isfile(configfile):
            f=open(configfile,"r")
            myshell=f.read()
            if os.path.isfile(myshell):
                self.myshell=myshell
                return
            else:
                self.chooseShell()
                return
        else:
            self.chooseShell()
        
        
    def chooseShell(self):
        win=Tk.Toplevel(self.parent)
        
        win.title("Test program")
        self.label=Tk.Label(win,text="Please choose the shell you would like to execute "+self.App+" in:")
        
        options = [
                ("/bin/sh",0),
                ("/bin/bash",1),
                ("/bin/csh",2),
                ("/bin/tcsh",3)
            ]
            
        option=Tk.IntVar()
        option.set(0) #set initial view option 
        
        row=0
        
        self.label.grid(row=row,sticky=Tk.W)
        
        
        for txt,val in options:
            row+=1
            Tk.Radiobutton(win,text=txt,padx=20,variable=option,
                            command=None,value=val).grid(row=row,sticky=Tk.W)
        row+=1
        
        Tk.Button(win,text="Confirm",command=lambda: self.setShell(option.get(),win)).grid(row=row)
        
        win.transient(self.parent)
        win.grab_set()
        self.parent.wait_window(win)
        
    def setShell(self,val,win):
        if val==0:
            self.myshell="/bin/sh"
        elif val==1:
            self.myshell="/bin/bash"
        elif val==2:
            self.myshell="/bin/csh"
        elif val==3:
            self.myshell="/bin/tcsh"
        else:
            self.myshell=None
       
       
        print "You chose ",self.myshell

        configfile=self.appdir+"/shell.dat"

        f=open(configfile,"w")
        f.write(self.myshell)
        f.close()

        win.destroy()
       
       
       
       
    
    
    
            
    #try to find the Tetr/Lev00 root directory. If not, ask the user to give it        
    def getappdir(self):
        
        if self.App=="Tetr":
            #check for HOME_TETR environment variable
            home_tetr=os.environ.get("HOME_TETR")
            
            if home_tetr != None:
                print "$HOME_TETR defined as: ",home_tetr
                if os.path.isfile(home_tetr+"/tetr"):
                    print "$HOME_TETR/tetr exists! Using it"
                    self.rootdir=home_tetr
                    return
                else:
                    print "$HOME_TETR/tetr does not exist"
            else:
                print "$HOME_TETR not defined in enviroment"
        
        
        
         # if the tetr/lev00 root file exists, use the path in it, else prompt the user
        configfile=self.appdir+"/"+self.App.lower()+"_root.dat"
        
        if not os.path.isfile(configfile):
            print("not a file")
            self.SetRoot()
        else:
            f=open(configfile)
            rootdir=f.read()
            f.close()
            if os.path.isfile(rootdir+"/"+self.App.lower()):
                self.rootdir=rootdir
            else:
               print("can't find exec")
               self.SetRoot()
        
        
        print self.App+" Root directory=",self.rootdir
        
    #prompt the user to provide the tetr/lev00 executable's directory
    def SetRoot(self):
        self.rootdirwin=Tk.Toplevel(self.parent)
        Tk.Label(self.rootdirwin,text="Please provide the path to the "+self.App+" executable\n(You should only have to do this once)").grid(row=0,column=0)
        Tk.Button(self.rootdirwin,text="Choose path",command=self.ChooseRoot).grid(row=1,column=0)
        
        self.rootdirwin.transient(self.parent)
        self.rootdirwin.grab_set()
        self.parent.wait_window(self.rootdirwin)
   
    #selection window for tetr/lev00 root. Checks if tetr/lev00 executable exists in that location 
    def ChooseRoot(self):
        self.rootdir=tkFileDialog.askdirectory(title="Please select the path to "+self.App)
        
        while not os.path.isfile(self.rootdir+"/"+self.App.lower()):
            tkMessageBox.showwarning("Warning","Cannot find "+self.App+" in:\n'"+self.rootdir+"'\nPlease try again")
            self.rootdir=tkFileDialog.askdirectory(title="Please select the path to "+self.App)
            
        f=open(self.appdir+"/"+self.App.lower()+"_root.dat","w")
        f.write(self.rootdir)
        f.close()
        self.rootdirwin.destroy()
    
    #ask the user to set the working directory. Choose from the previously used one, or choose a new one
    def getWorkingDir(self):
        
        dirfile = self.appdir+"/wkdir.dat"
        
        self.wkdirwin=Tk.Toplevel(self.parent)
        self.wkdirwin.title("Please choose your working directory")
        
        oldbut=Tk.Button(self.wkdirwin,text="Use previous directory",command=self.UseOldPath)
        newbut=Tk.Button(self.wkdirwin,text="Choose new directory",command=self.UseNewPath)
        
        if os.path.isfile(dirfile):
            f=open(dirfile,"r")
            self.olddir=f.read()
            f.close()
            message = "Your previous working directory was:\n'"+self.olddir+"'"
        else:
            message = "Please choose a working directory"
            oldbut.configure(state="disabled")
            
        Tk.Label(self.wkdirwin,text=message).grid(row=0,columnspan=2,padx=10,pady=10)
        oldbut.grid(row=1,column=0,padx=10,pady=10)
        newbut.grid(row=1,column=1,padx=10,pady=10)
        
        self.wkdirwin.transient(self.parent)
        self.wkdirwin.grab_set()
        self.parent.wait_window(self.wkdirwin)
            
    # sets the working directory to the previously used one    
    def UseOldPath(self):
        self.wkdir=self.olddir
        print "Working directory=",self.wkdir
        self.wkdirwin.destroy()
        
    #sets the working directory to a user selected one    
    def UseNewPath(self):
        string=tkFileDialog.askdirectory(title="Please Choose "+self.App+"'s working directory")
        if string != "":
            self.wkdir=string
            dirfile = self.appdir+"/wkdir.dat"
            f=open(dirfile,"w")
            f.write(self.wkdir)
            f.close()
            print "Working directory=",self.wkdir
            self.wkdirwin.destroy()
        
    #kill window and resets everything - currently not used    
    def Destroy(self):
        self.parent.destroy()
        self.destroy()
    
    #kills the tetr/Lev00 process and starts a new one
    def reset_app(self):
        answer = tkMessageBox.askquestion("Resetting "+self.App, "Are you sure you want to proceed? \nAny unsaved work will be lost")
        if answer == "yes":
            self.ChimeraInterface.CloseModels()
            self.ChimeraInterface = None
            self.fulltext=""
            self.prevtext=""
            self.latvectime=time.time()
            self.lattice.set(0)
            self.LatVecButton.config(state=Tk.DISABLED)
            self.updateText(self.App+" starting...\n")
            self.getWorkingDir()
            if self.App=="Tetr":
                self.ChimeraInterface = Tetr.Tetr(self.rootdir,self.wkdir,self.myshell)
            else:
                self.ChimeraInterface = Tetr.Lev00(self.rootdir,self.wkdir,self.myshell)
                self.lev00radio[1].config(state=Tk.DISABLED)
                self.levvoption.set(0)
            time.sleep(self.pausetime)
            self.updateText(self.ChimeraInterface.getOutput())
            self.ChimeraInterface.refreshGeom()
            self.SetViewOption()
            self.axis_toggle()
            self.ToggleLatticeVectors()
            self.wdirlabel.config(text="wkdir= '"+self.wkdir+"'")
            self.UpdateLabels()
            self.timer()
            
    
    #produces a dialogue that offers help on the reset button
    def resetHelp(self):
            tkMessageBox.showinfo("Resetting "+self.App,"This command resets "+self.App+" by closing and re-opening "+self.App+". Any unsaved progress will be lost")
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
class TetrDialog(LevGUI):
    name = "tetr ui"
    buttons = ("Close")
    title = "Enter Tetr Commands"
    

    def __init__(self, sessionData=None, *args, **kw):
        self.pausetime=0.5 #time to wait between submitting a command and checking for output/refreshing the text (seconds)
        dir, file = os.path.split(__file__)
        icon = os.path.join(dir, 'TetrLogo.tiff')
        chimera.tkgui.app.toolbar.add(icon,
                              lambda d=chimera.dialogs.display,
                              n=TetrDialog.name: d(n),
                              'Run Tetr', None)
        self.App="Tetr"
        self.fulltext=""
        self.toption=0
        ModelessDialog.__init__(self, *args, **kw)
        print "In init"
        
        self.latvectime=time.time()
        
        self.home=os.path.expanduser("~")
        self.appdir=self.home+"/.Tetr"
        
        #check for ~/.Tetr. If it doesn't exist, create it
        if not (os.path.isdir(self.appdir)):
            print "Making ",self.appdir
            os.mkdir(self.appdir)
            
        self.getShell()    
        
        #Look for the tetr root directory. Prompt user if necessary
        self.getappdir()
        
        #Ask user to select the working directory
        self.getWorkingDir()
        
        # Create tetr process
        self.ChimeraInterface = Tetr.Tetr(self.rootdir,self.wkdir,self.myshell)
        
        self.wdirlabel.config(text="wkdir= '"+self.wkdir+"'")
        
        # Create variable to store Tetr output
        self.ChimeraInterfaceOutput = Tk.StringVar()
        
        time.sleep(self.pausetime)
        
        
        
        #Update the tetr text on screen
        self.updateText(self.ChimeraInterface.getOutput())
        
        #load 'geom.xyz'
        self.ChimeraInterface.refreshGeom()
        
        #set view options to those selected in the GUI
        self.SetViewOption()
        
        self.timer()
        
    def fillInUI(self,parent):
        LevGUI.fillInUI(self,parent)
        
        
        
        
            
            
            
            
class Lev00Dialog(LevGUI):
    name="lev00 ui"
    buttons=("Close")
    title="Enter Lev00 Commands"
    
    
    def __init__(self,sessionData=None, *args, **kw):
        
        self.pausetime=0.5 #time to wait between submitting a command and checking for output/refreshing the text (seconds)
        
        self.starttime=time.time()
        self.latvectime=time.time()
        
        dir, file = os.path.split(__file__)
        icon = os.path.join(dir, 'Lev00Logo.tiff')
        chimera.tkgui.app.toolbar.add(icon,
                              lambda d=chimera.dialogs.display,
                              n=Lev00Dialog.name: d(n),
                              'Run Lev00', None)
        
        
        self.App="Lev00"
        self.fulltext=""
        self.toption=0
        ModelessDialog.__init__(self, *args, **kw)
        print "In init"
        
        self.home=os.path.expanduser("~")
        self.appdir=self.home+"/."+self.App
        
        #check for ~/.Lev00. If it doesn't exist, create it
        if not (os.path.isdir(self.appdir)):
            print "Making ",self.appdir
            os.mkdir(self.appdir)
            
        self.getShell()    
        
        #Look for the Lev00 root directory. Prompt user if necessary
        self.getappdir()
        #self.rootdir="/Users/ggibb2/Projects/CP2k/lev00_3.49"
        
        #Ask user to select the working directory
        self.getWorkingDir()
        
        # Create lev00 process
        self.ChimeraInterface = Tetr.Lev00(self.rootdir,self.wkdir,self.myshell)
        
        self.wdirlabel.config(text="wkdir= '"+self.wkdir+"'")
        
        # Create variable to store Lev00 output
        self.ChimeraInterfaceOutput = Tk.StringVar()
        
        time.sleep(self.pausetime)
        
        #Update the Lev00 text on screen
        self.updateText(self.ChimeraInterface.getOutput())
        
        #load 'geom.xyz'
        self.ChimeraInterface.refreshGeom()
        
        #set view options to those selected in the GUI
        self.SetViewOption()
        
        self.timer()
        
        
    def fillInUI(self,parent):
        LevGUI.fillInUI(self,parent)
        
    def SetLev00ViewOption(self,e=None):
        val = self.levvoption.get()
        
        self.ChimeraInterface.refreshGeom(opt=val,force=True)
        if val==0:
            self.CheckSelectionFile(force=True)
            
    
    #enables the cube file vewing option when a new cube file has been created
    def CheckforCube(self):
        cubeFile=self.wkdir+"/gOpenMol.cube"
        if (os.path.isfile(cubeFile)):
                mTime = os.stat(cubeFile).st_mtime
                if mTime > self.starttime:
                    print "New cube file!"
                    self.lev00radio[1].config(state=Tk.NORMAL)
                    self.levvoption.set(1)
                    self.ChimeraInterface.refreshGeom(opt=1,force=True)
                    self.starttime=mTime
                else:
                    print "No new Cube file!"
            
            
            
            

chimera.dialogs.register(TetrDialog.name, TetrDialog)
chimera.dialogs.register(Lev00Dialog.name,Lev00Dialog)


