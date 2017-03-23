# -*- coding: utf-8 -*-
"""
Created on Tue May 31 11:42:13 2016

@author: Gordon Gibb and Jeremy Novell
"""

import Tkinter as Tk
import tkMessageBox
import tkFileDialog
from CGLtk import ScrolledText
import chimera
import os
import Tetr
import time
from chimera.baseDialog import ModelessDialog

pausetime=0.5 #time to wait between submitting a Tetr command and checking for output/refreshing the text (seconds)

class TetrDialog(ModelessDialog):
    name = "tetr ui"
    buttons = ("Close")
    title = "Enter Tetr Commands"

    def __init__(self, sessionData=None, *args, **kw):
        ModelessDialog.__init__(self, *args, **kw)
        print "In init"
        
        self.home=os.path.expanduser("~")
        self.tetrdir=self.home+"/.Tetr"
        tetrfile=self.tetrdir+"/tetr_root.dat"
        
        #check for ~/.Tetr. If it doesn't exist, create it
        if not (os.path.isdir(self.tetrdir)):
            print "Making ",self.tetrdir
            os.mkdir(self.tetrdir)
        
        #Look for the tetr root directory. Prompt user if necessary
        self.getTetrDir()
        
        #Ask user to select the working directory
        self.getWorkingDir()
        
        # Create tetr process
        self.tetr = Tetr.Tetr(self.rootdir,self.wkdir)
        
        # Create variable to store Tetr output
        self.tetrOutput = Tk.StringVar()
        
        time.sleep(pausetime)
        
        #Update the tetr text on screen
        self._updateText(self.tetr.getOutput())
        
        #load 'geom.xyz'
        self.tetr.refreshGeom()
        
        #set view options to those selected in the GUI
        self.SetViewOption()

    def fillInUI(self, parent):
        self.parent=parent
        row = 0
        
        #allow window (and things within it) to be resizable
        parent.rowconfigure(0,weight=1)
        parent.columnconfigure(0,weight=1)
       
        
#################### Create tetr output widget and label (LHS of window) #####################
        
        #put them in their own frame (LHS column of window)
        tetrFrame=Tk.Frame(parent)
        tetrFrame.grid(row=0,column=0,padx=5,sticky=Tk.W+Tk.E+Tk.N+Tk.S)
        
        tetrFrame.columnconfigure(0,weight=1) #make resizable in the x direction
        
        
        #label for the tetr output
        Tk.Label(tetrFrame, text="Tetr Output:").grid(row=row,column=0, sticky=Tk.W)
        row += 1
        tetrrow=row
        
        #tetr text output widget (with scrollbar)
        scrollbar=Tk.Scrollbar(tetrFrame)
        t=Tk.Text(tetrFrame,wrap=Tk.WORD,width=80, height=45,yscrollcommand=scrollbar.set)
        t.config(font=('courier', 12, 'normal'))
        t.grid(row=row,column=0, sticky=Tk.W+Tk.E+Tk.N+Tk.S)
        tetrFrame.rowconfigure(row,weight=1) #make resizable in the y direction
        
        scrollbar.grid(row=row, column=1, sticky='ns')
        scrollbar.config(command=t.yview)
        
        self.outText = t
        
        #allow a button press to focus the text box (allows selection of text from tetr output) 
        t.bind('<ButtonPress>', lambda e,t=t: t.focus(),
                   add = True)

        # set the initial text
        self._updateText("Tetr starting...")
        
        
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
        Tk.Checkbutton(axisFrame,text="Show Axis",variable=self.axisshow,command=self.axis_toggle).grid(row=axisRow,columnspan=2,sticky=Tk.W)
        
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
        
        optionsrow +=1
        
        Tk.Label(optionsFrame,text=" ").grid(row=optionsrow) #blank space
        
        
        
#--------frame for atom selections---------  
        
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
        
        
        Tk.Label(resetFrame,text="Restart Tetr:").grid(row=0,column=0,columnspan=2,sticky=Tk.W)
        Tk.Button(resetFrame,text="Restart",command=self.reset_tetr).grid(row=1,column=0,sticky=Tk.W+Tk.E)
        Tk.Button(resetFrame,text="?",command=self.resetHelp).grid(row=1,column=1, sticky=Tk.W+Tk.E)
        resetFrame.columnconfigure(0,weight=1)
        resetFrame.columnconfigure(1,weight=1)
        
        
#################### Tetr text entry widget (bottom of screen) #####################

        #entry widget at the bottom left
        Tk.Label(parent, text="Tetr Input:").grid(row=row, sticky=Tk.W,padx=5)
        row += 1
        self.entry = Tk.Entry(parent)
        self.entry.config(relief=Tk.SUNKEN,font=('courier', 12, 'normal'))
        self.entry.grid(row=row,column=0, sticky=Tk.W+Tk.E,columnspan=1,padx=5)
        
        #enter button at bottom right
        Tk.Button(parent,text="<- Enter Command",command=self._updateInput).grid(row=row,column=1, sticky=Tk.W+Tk.E,padx=5)
        
        # Tell the entry widget to watch the input
        self.tetrInput = Tk.StringVar()
        self.entry["textvariable"] = self.tetrInput

        # Get a callback when return key is pressed

        self.entry.bind('<Key-Return>', self._updateInput)
        
        
        
        
    #gets the view option selection and sends it to the chimera interface    
    def SetViewOption(self):
        print("View Option=",self.voption.get())
        self.tetr.SetViewOption(self.voption.get())
    
    #gets the atom selections from chimera and pastes the text into the tetr input box 
    def GetSelection(self):
        text=self.tetr.GetSelection()
        if text==None:
            tkMessageBox.showwarning("Warning","No atoms in selection")
        elif len(text) > 200:
            tkMessageBox.showwarning("Warning","The size of the selection string is too big to be input into tetr. Please make a smaller selection.")
        else:
            self.tetrInput.set(text)
    
    #puts up a dialogue offering help with the selection feature
    def selectionHelp(self):
        tkMessageBox.showinfo("Selection Help",('Use the "Get Selection" button to paste atoms selected in the Chimera GUI into Tetr:\n'
            '- Make your selection in Chimera\n'
            '- In Tetr select "T. Tag atoms"\n'
            '- click "Get Selection"\n'
            '- Hit Return or "Enter Command"\n\n'
            'You may then apply the operation of your choosing to these selected atoms in Tetr.'))
    
    #gets text in the input field and puts it into tetr
    def _updateInput(self, event=0):
        
        inString = self.tetrInput.get()
        self.tetr.setInput(inString)
        #self._updateText(inString + "\n")
        self.tetrInput.set("")
        
        time.sleep(pausetime) #wait for tetr to do its thing
        
        outputText = self.tetr.getOutput()
        self._updateText(outputText) #update tetr output text
        self.tetr.refreshGeom() #update model in chimera
        

    #def _processTetrOutput(self, text):
        #for line in iter(text.readline, b''):
            #pass

    def _updateText(self, text):
        self.outText.config(state = Tk.NORMAL) #allow modification of the text
        self.outText.delete(1.0,Tk.END) #this line clears any previous text - comment out to append new test instead
        self.outText.insert(Tk.END, text)
        self.outText.config(state = Tk.DISABLED) #disable modification of the text
        self.outText.see(Tk.END)

    #Create the axis file to be displayed in Chimera
    def make_axis(self):
        axisfile=self.tetrdir+"/axis.bild"
        
        #check for ".Tetr directory" - if it isn't there, make it'
        if not (os.path.isdir(self.tetrdir)):
            print "Making ",self.tetrdir
            os.mkdir(self.tetrdir)
        
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
        
        f.write(".color 1 0 0\n")
        f.write(".arrow "+str(xs)+" "+str(ys)+" "+str(zs)+" "+str(ls+xs)+" "+str(ys)+" "+str(zs)+"\n")
        
        f.write(".color 0 1 0\n")
        f.write(".arrow "+str(xs)+" "+str(ys)+" "+str(zs)+" "+str(xs)+" "+str(ls+ys)+" "+str(zs)+"\n")
        
        f.write(".color 0 0 1\n")
        f.write(".arrow "+str(xs)+" "+str(ys)+" "+str(zs)+" "+str(xs)+" "+str(ys)+" "+str(ls+zs)+"\n")
        
        f.close()
        
        print "File written"
        
        #display new axis
        if self.axisshow.get() == 1:
            self.tetr.ShowAxis(True)
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
            self.tetr.ShowAxis(True)
    
    #toggle the axis on/off
    def axis_toggle(self):
        val=self.axisshow.get()
        
        if val==1: #show the axis
            self.make_axis()
            self.tetr.ShowAxis(True)
        else:
            self.tetr.ShowAxis(False)
            
    #try to find the tetr root directory. If not, ask the user to give it        
    def getTetrDir(self):
        
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
        
        
        
        
        # if the tetr root file exists, use the path in it, else prompt the user
        if not os.path.isfile(tetrfile):
            self.SetTetrRoot()
        else:
            f=open(tetrfile)
            rootdir=f.read()
            f.close()
            if os.path.isfile(rootdir+"/tetr"):
                self.rootdir=rootdir
            else:
               self.SetTetrRoot()
        
        
        print "Tetr Root directory=",self.rootdir
        
    #prompt the user to provide the tetr directory
    def SetTetrRoot(self):
        self.rootdirwin=Tk.Toplevel(self.parent)
        Tk.Label(self.rootdirwin,text="Please provide the path to the tetr executable\n(You should only have to do this once)").grid(row=0,column=0)
        Tk.Button(self.rootdirwin,text="Choose path",command=self.chooseTetrRoot).grid(row=1,column=0)
        
        self.rootdirwin.transient(self.parent)
        self.rootdirwin.grab_set()
        self.parent.wait_window(self.rootdirwin)
   
    #selection window for tetr root. Checks if tetr executable exists in that location 
    def chooseTetrRoot(self):
        self.rootdir=tkFileDialog.askdirectory(title="Please select the path to tetr")
        
        while not os.path.isfile(self.rootdir+"/tetr"):
            tkMessageBox.showwarning("Warning","Cannot find tetr in:\n'"+self.rootdir+"'\nPlease try again")
            self.rootdir=tkFileDialog.askdirectory(title="Please select the path to tetr")
            
        f=open(self.tetrdir+"/tetr_root.dat","w")
        f.write(self.rootdir)
        f.close()
        self.rootdirwin.destroy()
    
    #ask the user to set the working directory. Choose from the previously used one, or choose a new one
    def getWorkingDir(self):
        
        dirfile = self.tetrdir+"/wkdir.dat"
        
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
            
    # sets the tetr working directory to the previously used one    
    def UseOldPath(self):
        self.wkdir=self.olddir
        print "Tetr working directory=",self.wkdir
        self.wkdirwin.destroy()
        
    #sets the tetr working directory to a user selected one    
    def UseNewPath(self):
        self.wkdir=tkFileDialog.askdirectory(title="Please Choose Tetr's working directory")
        dirfile = self.tetrdir+"/wkdir.dat"
        f=open(dirfile,"w")
        f.write(self.wkdir)
        f.close()
        print "Tetr working directory=",self.wkdir
        self.wkdirwin.destroy()
        
    #kill window and resets everything - currently not used    
    def Destroy(self):
        self.parent.destroy()
        self.destroy()
    
    #kills the tetr process and starts a new one
    def reset_tetr(self):
        answer = tkMessageBox.askquestion("Resetting Tetr", "Are you sure you want to proceed? \nAny unsaved work will be lost")
        if answer == "yes":
            self.tetr.CloseModels()
            self.tetr = None
            self._updateText("Tetr starting...")
            self.getWorkingDir()
            self.tetr = Tetr.Tetr(self.rootdir,self.wkdir)
            time.sleep(pausetime)
            self._updateText(self.tetr.getOutput())
            self.tetr.refreshGeom()
            self.SetViewOption()
            self.axis_toggle()
    
    #produces a dialogue that offers help on the reset button
    def resetHelp(self):
            tkMessageBox.showinfo("Resetting Tetr","This command resets Tetr by closing and re-opening Tetr. Any unsaved progress will be lost")
            

chimera.dialogs.register(TetrDialog.name, TetrDialog)

dir, file = os.path.split(__file__)
icon = os.path.join(dir, 'ExtensionUI.tiff')
chimera.tkgui.app.toolbar.add(icon,
                              lambda d=chimera.dialogs.display,
                              n=TetrDialog.name: d(n),
                              'Run Tetr', None)
