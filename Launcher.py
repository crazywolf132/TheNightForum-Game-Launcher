#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tkinter as Tk
import os, time, urllib2, urllib, shutil, zipfile, subprocess, webbrowser, socket
from os.path import expanduser

## These 10 variables are here because it allows for all the classes
## to look at them and edit them without having to create a loop of
## one class calling another which then calls that same class again... (its hard to explain the loop).
configs = {}
props = {}
game_configs = {}
grannyCounter = 0
errorFrameRunning = 0
keeper = []
gameMode = False
LauncherNeedsUpdate = False
GameNeedsUpdate = False
OnlineVersion = ""

########################################################################
## This is the main class (in the way that this is the main frame and the first to ever get called.
## This class is responsible for showing users the main menu aswell as getting everything setup for show.
class Start(object):
    #----------------------------------------------------------------------
    ## In every class, this function is required... This is to get everything setup internally inside the class.
    def __init__(self, parent):
        ## This line here ↓ is for taking the frame generated in the starting function (VERY BOTTOM OF THE FILE!)..
        ## And using it inside of the class, as it was passed through as an "object" (as stated in the class calling above)
        self.root           = parent
        ## We are now adding the name to the frame "TNF Game Launcher"
        self.root.title("TNF Game Launcher")
        ## We are setting up "self.frame" as a Frame to the parent which was established just above.
        self.frame          = Tk.Frame(parent)
        ## Now we are setting up the packing of the frame so that it is all centered inside the frame
        ## and everything inside the center column is being expanded by 1 column (1 extra column wider...)
        self.frame.pack(anchor=Tk.CENTER, expand=1)
        ## This function ↓ is for determining what to display on the screen. This is called multiple times, as it is using
        ## the "draw" function to display multiple views on the same frame by removing them and then loading the correct
        ## ones according to ↓ variable.
        self.frameState     = 0
        #----------------------------------
        ## Calling the "configs" variable here by using the "global" so we can also write to it if we need to.
        global configs
        global props
        ## Setting up "self.configs" to point towards the global "configs" variable, so then the code it neater...
        ## and has less lines (as i won't have to make a global call to "configs" all the time)
        self.configs        = configs
        ## Now creating a few local variables to save alot of re-writing of the exact same thing.
        ## A good example of this, is the "self.path" and the "self.confFile". It saves re-writing the whole path of the
        ## files and folders all the time.
        ## The "self.props" dictionary is just a local version (local, as in... inside the code) of the config file...
        ## That gets generated every single time the program is started (and only run at start)... It is so it can create
        ## a config file if none was found. It also contains the default variables of the config file.
        self.props          = props
        self.path           = "{0}/{1}".format(expanduser("~"), "TNFLauncher")
        self.confFile       = "{0}/{1}/{2}".format(self.path, "configs", "launcher.conf")
        ## This ↓ "pageNum" variable is here to allow the "draw" function know what page to draw for both the settings
        ## and the tutorial system. This is a variable that is used by different methods and should never start at 0, as
        ## there is no such thing as a zero'th page in a book.
        self.pageNum        = 1
        #----------------------------------
        ## These next 2 lines are just calling the 2 other classes, "Thinking" and "Logger", and setting them to local
        ## variables (only for use inside this class) to make it easier to refer to them in the future code inside of this
        ## class. The "Thinking" class is the biggest and most complex class, as it is like the Brain of the whole project
        ## hence the name "Thinking"...
        self.core           = Thinking()
        self.log            = Logger()
        #----------------------------------
        ## Here we are just packing the frame so then everything can be visible on the screen.
        self.frame.pack()
        ## Here ↓  we are launching the startup function. This will only ever be called once as it is in the opening
        ## "__init__" function of this class...
        self.startup()
        ## Last but not least, we are calling the draw function to display the screen to the user.
        self.draw()

    ## This is where the magic begins. The main-screen of the launcher and whats on it is all being controlled by
    ## this one simple and beautiful function.
    #----------------------------------------------------------------------
    def draw(self):
        ## We are going to run a "grannyCheck" to make sure everything is ok, before we do anything with the frames.
        ## (Makes sure that the files are still there, and that the config files were not touched without us doing it.)
        self.core.grannyCheck()
        ## If the "frameState" is set to "-1" it means that the player is new, and we are going to send them to the
        ## tutorial screen... as that is what the config is saying...
        if self.frameState == -1:
            ## Creating all the required fields to display on the screens.
            Welcome = Tk.Label(self.frame, text="Welcome to...")
            TNF = Tk.Label(self.frame, text="TNF Game Launcher!")
            NextBtn = Tk.Button(self.frame, text="Next →", command=lambda:self.showFrame(5))
            SkipBtn = Tk.Button(self.frame, text="Skip", command=lambda:self.showFrame(0))
            msg = Tk.Text(self.frame, borderwidth=3, width=35, height=11, relief="sunken")
            ## here ↓, im adding the text that will go into the field. This text is returned from the "self.show_tut"
            ## function, where we are requesting the line of "Intro"
            msg.insert(Tk.END,str(self.show_tut("Intro")))
            ## This little line here ↓ is used to disable the box from any editing by the user.
            msg.config(font=("consolas", 12), wrap='word', state=Tk.DISABLED)

            ## Here we are assigning all the fields to the set positions in the grid.
            Welcome.grid(row=0, column=0, sticky=Tk.NSEW)
            TNF.grid(row=1, column=0, sticky=Tk.NSEW)
            ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
            self.fill_empty(2, 0)
            msg.grid(row=3, column=0, sticky=Tk.NSEW)
            ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
            self.fill_empty(4, 0)
            ## We are now adding the "Next" and "Skip" buttons to the frame for the player to be able to click...
            NextBtn.grid(row=5, column=0, sticky=Tk.NSEW)
            SkipBtn.grid(row=6, column=0, sticky=Tk.NSEW)

        ## This here ↓ checks if "self.frameState" = 0, if it does... we will show the user the waiting frame...
        ## This frame rarely ever gets called. It should only ever be called if the launcher is performing a large task that takes time...
        if self.frameState == 0:
            ## With this ↓ we are logging that we have switched to the "Initialising Frame", AKA: Waiting frame...
            self.log.record("Initialising Loading frame", "info")
            ## Currently, with this ↓ line of code, we are adding the Tkinter Label that says "Please Wait..."
            wait = Tk.Label(self.frame, text="Please Wait...", font="Helvetica 16 bold")
            ## We are now adding that "wait" variable (which is the Tkinter Label) to the frame at row 1, column 1
            wait.grid(row=1,column=1,sticky=Tk.NSEW)
        ## This here ↓ checks if "self.frameState" = 1, if it does... we will show the user the Main Frame...
        ## This main frame is where all the fun happens. This should be first screen the users see's when using the app every time...
        ## thought, this screen will change depending on if the user is new, or if they are in the settings panel or not...
        elif self.frameState == 1:
            ## We are now going to log that we are on the main screen.
            self.log.record("Loading MainFrame", "info")
            ## We are assigning the variable "Logo" to the Tkinter Label that says "TNF Launcher"
            Logo = Tk.Label(self.frame, text="TNF Launcher", font="Helvetica 20 bold")
            ## ↓ This is going to check if there are any games installed on the system by checking the "configs" variable...
            ## If this = "1", it means that there are some games installed, otherwise... if it = "0"... this means there are none installed.
            if configs['GotGames'] == "1":
                ## If there are some games installed, we want to add a "Games" button and assign it to the "Play" variable.
                ## When this button is pressed we want to run the "self.showFrame(2)" function. This will mean that we launch
                ## a frame from the "OtherFrame" class when the user clicks this button.
                Play = Tk.Button(self.frame, text="Games", command=lambda:self.showFrame(2))
            ## We are now going to add the "Add" button, and assign it to the variable "Add".
            ## When this button is pressed, we are going to run the command "self.showFrame(1)". This will mean that we launch
            ## a frame from the "OtherFrame" class when the user clicks this button.
            Add = Tk.Button(self.frame, text="Add", command=lambda:self.showFrame(1))
            ## With this ↓ code, we are checking if the variable/setting "DevMode" has been assigned inside of the "configs" variable.
            ## If it has, we are going to check to see if the value of it is = 1... if it is, we are going to run the
            ## if statement to then add another button to the field. Otherwise, if it is anything else... we will ignore it
            if int(configs['DevMode']) == 1:
                ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
                self.fill_empty(4, 0)
                ## We are now adding the "Create" button and assigning it to the variable "Create". When this button
                ## is pressed, we are going to run the command "self.showFrame(4)". This will mean that when the user
                ## clicks the button... we will run the "OtherFrame" class to display the correct frame.
                Create = Tk.Button(self.frame, text="Create", command=lambda:self.showFrame(4))
                ## We are now assigning the button to row 5, column 0 in the on-screen grid.
                Create.grid(row=5, column=0, sticky=Tk.NSEW)
            ## With this code ↓ we are now creating a "Settings" button and assigning it to the variable "Settings".
            ## When this button is pressed/clicked... the command "self.showFrame(3)" will be run. This will execute
            ## the "OtherFrame" class and get it to display to us the correct frame we require.
            Settings = Tk.Button(self.frame, text="Settings", command=lambda:self.showFrame(3))
            ## We are now adding the most important button of all. The "Quit" button, we are then assigning it to the
            ## variable "Quit". When this button is pressed, it runs the "self.shutdown" command. This means that it
            ## will kill all the frames currently running and stop the application.
            Quit = Tk.Button(self.frame, text="Quit", command=self.shutdown)

            ## Now we are getting into the fun stuff! We are finally assigning most of the fields to their placement on
            ## screen with the "grid" method. This is required to show all the elements on the screen.
            ## Below ↓ we are adding the "Logo" field which we set above. This is going to go to row 0, column 0 in the on-screen grid.
            Logo.grid(row=0,column=0, sticky=Tk.NSEW)
            ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
            self.fill_empty(1, 0)
            ## Right below ↓ us here is the if statement to work out if we have any games at all. If we do, we will run
            ## the statement, otherwise we will ignore it and skip to below.
            if int(configs['GotGames']) == 1:
                ## According to this, we have some games. Therefore we will need to show the "Play" feild on the screen.
                ## We are going to be displaying this field at row 2, column 0 in the on-screen grid.
                Play.grid(row=2,column=0, sticky=Tk.NSEW)
            ## We are now passed the if-statement, so this means that this field will be added regardless of if we have
            ## any games or not. We are now adding the "Add" feild, and we are placing it at row 3, column 0 of the on-screen grid.
            Add.grid(row=3,column=0, sticky=Tk.NSEW)
            ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
            self.fill_empty(6, 0)
            ## Here ↓ we are adding the "Settings" field to the on-screen grid at the location row 7, column 0.
            ## The reason for the massive jump in numbers is to compencate for the posibility of the "Create" field being added.
            ## Even if the "Create" field is not added... We still keep it at row 7, as it will just move up as there is nothing in the way.
            Settings.grid(row=7, column=0, sticky=Tk.NSEW)
            ## We are now going to add the "Quit" field to the on-screen grid at lication row 8, column 0.
            ## Much like the above "Settings" feild... we have a high number for the row... as it will just move up if there is nothing in the way.
            Quit.grid(row=8, column=0, sticky=Tk.NSEW)

        ## Now, we are going to start checking if "self.frameState" = 2. If it does, we are going to display the "Settings Frame" to the user.
        elif self.frameState == 2:
            ## First of all, we start off by logging what is happening. We say "Settings Frame started..."
            ## so then in the log, if there is an error... we can try to re-create the issue to then fix it.
            self.log.record('Settings Frame started...', 'info')
            ## We now start by making a few internal variables that are only avaliable to this class.
            ## The reason why most of the lists start with 'No'... is because in a list, that first item is at position 0...
            ## and in binary. 0 means off, and 1 means on. So... making it 0, makes it easier to remember what it means
            ## if you latter read through the code...
            ## "self.opt" is a "StringVar"... which means it holds a string.
            self.opt = Tk.StringVar()
            ## "self.options" is a list. This holds all the possible options to go into "self.opt"
            self.options = ["Errors Only", "Warnings Only", "Info Only", "Debug Only", "Errors and Warnings", "Warnings and Info", "Game info only", "All"]
            ## "self.devString" is a "StringVar"... which means it holds a string.
            self.devString = Tk.StringVar()
            ## "self.devoption" is a list. This holds all the possible options to go into "self.devString"
            self.devoption = ['No', 'Yes']
            ## "self.GrannyHolder" is a "StringVar"... which means it holds a string.
            self.GrannyHolder = Tk.StringVar()
            ## "self.GrannyOptions" is a list. This holds all the possible options to go into "self.GrannyHolder"
            self.GrannyOptions = ['No', 'Yes']
            ## "self.VersionHolder" is a "StringVar"... which means it holds a string.
            self.VersionHolder = Tk.StringVar()
            ## "self.VersionOps" is a list. This holds all the possible options to go into "self.VersionHolder".
            self.VersionOps = ['Decide at the time', 'Latest']
            ## "self.KeepVersionsHolder" is a "StringVar"... which means its holds a string.
            self.keepVersionsHolder = Tk.StringVar()
            ## "self.keepVersionsOps" is a list. This holds all the possible options to go into "self.keepVersionsHolder"
            self.keepVersionsOps = ['No', 'Yes']
            ## "self.BackupOptHolder" is a "StringVar"... which means it holds a string.
            self.BackupOptHolder = Tk.StringVar()
            ## "self.BackupOptOps" is a list. This holds all the possible options to go into "self.BackupOptHolder"
            self.BackupOptOps = ['No', 'Yes']
            ## "self.BackupIntHolder" is a "StringVar"... which means it holds a string.
            self.BackupIntHolder = Tk.StringVar()
            ## "self.BackupIntOps" is a list. This holds al teh possible options to go into "self. BackupIntHolder"
            self.BackupIntOps = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

            ## We are now going to do some searching to set the "StringVar" variables to the current setting
            ## that is saved in the config file. This is good as when the user looks at the page, they can see
            ## all the current settings and not have to change every single setting each time...
            ## We are now searching for the "Logging" field in the "configs" variable... and we are going
            ## to get the returned value of that, and assign it to the variable "num"
            num = int(configs['Logging'])
            ## We are now going to set "self.opt" to the item in "self.options" that is at the position of
            ## the returned number that is assigned to "num"
            self.opt.set(self.options[num])
            ## We are now searching for the "DevMode" field in the "configs" variable... and we are going
            ## to get the returned value of that, and assign it to the variable "num"
            num = int(configs['DevMode'])
            ## We are now going to set "self.devString" to the item in "self.devoption" that is at the the possition of
            ## the returned number that is assigned to "num"
            self.devString.set(self.devoption[num])
            ## We are now searching for the "GrannyChecker" field in the "configs" variable... and we are going
            ## to get the returned value of that, and assign it to the variable "num"
            num = int(configs['GrannyChecker'])
            ## We are now going to set "self.GrannyHolder" to the item in "self.GrannyOptions" that is at the position of
            ## the returned number that is assigned to "num"
            self.GrannyHolder.set(self.GrannyOptions[num])
            ## We are now searching for the "GetVersion" field in the "configs" variable... and we are going
            ## to get the returned value of that, and assign it to the variable "num"
            num = int(configs['GetVersion'])
            ## We are now going to set "self.VersionHolder" to the item in "self.VersionOps" that is at the position of
            ## the returned number that is assigned to "num"
            self.VersionHolder.set(self.VersionOps[num])
            ## We are now searching for the "KeepVersions" field in the "configs" variable... and we are going
            ## to get the returned value of that, and assign it to the variable "num"
            num = int(configs['KeepVersions'])
            ## We are now going to set "self.keepVersionHolder" to the item in "self.keepVersionsOps" that is at the position
            ## of the returned number that is assigned to "num"
            self.keepVersionsHolder.set(self.keepVersionsOps[num])
            ## We are now searching for the "Backups" field in the "configs" variable... and we are going
            ## to get the returned value of that, and assign it to the variable "num"
            num = int(configs['Backups'])
            ## We are now going to set "self.BackupOptHolder" to the item in "self.BackupOptOps" that is at the position
            ## of the returned number that is assigned to "num"
            self.BackupOptHolder.set(self.BackupOptOps[num])
            ## We are going to do something different now. As we have decided that the Backup Variable and the Backup Timer variable
            ## are going to be related. When the "self.BackupOptHolder" is = 0, then the "self.BackupIntHolder" is going to be equal to 0
            if self.BackupOptHolder == "0":
                ## This will only run if "self.BackupOptHolder" is = 0.
                ## As it is clearly = 0, we are going to set "self.BackupIntHolder" to that of whatever is at position 0
                ## in the "self.BackupIntOps" list.
                self.BackupIntHolder.set(self.BackupIntOps[0])
            ## We are now searching for the "BackupInt" field in the "configs" variable... and we are going to
            ## get the returned value of that, and assign it to the variable "num"
            num = int(configs['BackupInt'])
            ## We are now going to set "self.BackupIntHolder" to the item in "self.BackupIntOps" that is at the position of
            ## the returned number that is assigned to "num"
            self.BackupIntHolder.set(self.BackupIntOps[num])

            ## Here is where the fun begins. We start to render the pages on the screen aswell as the other info.
            ## We are now making a "Logo" variable outside of any of the pages as this will show up on all the pages.
            Logo = Tk.Label(self.frame, text="Launcher - Settings", font="Helvetica 20 bold")
            ## We are now checking to see if "self.pageNum" is = 1. If it is, then we are going to load the first page.
            ## self.pageNum should always be = 1 on first launch as it is manually defined above in the __init__ function.
            if self.pageNum == 1:
                ## We are now rendering the first page. Everything inside of here is just setting up the
                ## variables to have Tkinter widgest assigned to. So then they can be latter drawn on screen.
                ## The reason why I did not add the code that adds all of these to the on-screen grid, to here... is
                ## because it makes it rather messier and harder to read and edit than if it were in a seperate place.

                ## I feel i dont need explain what this is doing, as it is just assigning tkinter widgets to variable names.
                LoggingTitle = Tk.Label(self.frame, text="Logging Level:")
                LoggingOptions = Tk.OptionMenu(self.frame,self.opt,*self.options)
                DeveloperTitle = Tk.Label(self.frame, text="Developer Mode:")
                DeveloperOptions = Tk.OptionMenu(self.frame,self.devString,*self.devoption)
                GrannyCheckTitle = Tk.Label(self.frame, text="Granny Checks:")
                GrannyCheckOptions = Tk.OptionMenu(self.frame,self.GrannyHolder,*self.GrannyOptions)
                VersionTitle = Tk.Label(self.frame, text="Version to get:")
                VersionOptions = Tk.OptionMenu(self.frame,self.VersionHolder,*self.VersionOps)

            ## This ↓ is now checking if the "self.pageNum" is = 2.... If so, we will load the 2nd page.
            ## If it is anything else than one of these 2 pages... it will not load anything. It will just show a blank screeen.
            elif self.pageNum == 2:
                ## This page is also just loading the tkinter widgets and adding them to variable names to latter be
                ## added to the page (down below)...
                KeepTitle = Tk.Label(self.frame, text="Keep All Versions:")
                KeepOptions = Tk.OptionMenu(self.frame, self.keepVersionsHolder,*self.keepVersionsOps)
                BackUpTitle = Tk.Label(self.frame, text="Enable Backups?")
                BackUpOps = Tk.OptionMenu(self.frame,self.BackupOptHolder,*self.BackupOptOps)
                BackUpTimeTitle = Tk.Label(self.frame, text="Backup Intervals:")
                BackUpTimeOps = Tk.OptionMenu(self.frame,self.BackupIntHolder,*self.BackupIntOps)

            ## These next 4 items are just Tkinter Button Widgets being assigned to the variables.
            ## The reason why these are not placed inside one the "self.pageNum" arguements... is because it is going
            ## to be displayed on all the pages regardless... This will always be true, unless stated otherwise.
            NextPage = Tk.Button(self.frame, text="Next Page →", command=lambda:self.changePage(self.pageNum+1))
            BackPage = Tk.Button(self.frame, text="← Previous Page", command=lambda:self.changePage(self.pageNum-1))
            SaveBtn = Tk.Button(self.frame, text="Save", command=lambda:self.saveConfig())
            BackBtn = Tk.Button(self.frame, text="Back", command=lambda:self.showFrame(0))
            #--------------------------------------------------------#

            ## We are now going to start adding all these variables to the on-screen grid...
            ## Adding "Logo" to position row=0,column=0
            Logo.grid(row=0, column=0, sticky=Tk.NSEW)
            ## If we are currently on pageNum 1, we will load the items in the if statement.
            if self.pageNum == 1:
                ## Going to start drawing all the required fields to be displayed on the first page.
                #--------------------------------------------------------#
                ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
                self.fill_empty(1, 0)
                #--------------------------------------------------------#
                ## Here ↓ we are adding both "LoggingTitle" and "LoggingOptions" so they can both be rendered together on the screen.
                ## These are both together so then they can be easily seen by the user of which ones the title corresponds to
                LoggingTitle.grid(row=2, column=0, sticky=Tk.NSEW)
                LoggingOptions.grid(row=3, column=0, sticky=Tk.NSEW)
                #--------------------------------------------------------#
                ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
                self.fill_empty(4, 0)
                #--------------------------------------------------------#
                ## Here ↓ we are adding both "DeveloperTitle" and "DeveloperOptions"... These are both in the same area together, so then
                ## the user will be able to see what the title corresponds with.
                DeveloperTitle.grid(row=5, column=0, sticky=Tk.NSEW)
                DeveloperOptions.grid(row=6, column=0, sticky=Tk.NSEW)
                #--------------------------------------------------------#
                ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
                self.fill_empty(7, 0)
                #--------------------------------------------------------#
                ## Here ↓ we are adding both "GrannyCheckTitle" and "GrannyCheckOptions"... These are both in the same area together, so then
                ## the user will be able to see what the title corresponds with.
                GrannyCheckTitle.grid(row=8, column=0, sticky=Tk.NSEW)
                GrannyCheckOptions.grid(row=9, column=0, sticky=Tk.NSEW)
                #--------------------------------------------------------#
                ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
                self.fill_empty(10, 0)
                #--------------------------------------------------------#
                ## Here ↓ we are adding both "VersionTitle" and "VersionsOptions"... These are both in the same area together, so then
                ## the user will be able to see what the title corresponds with.
                VersionTitle.grid(row=11, column=0, sticky=Tk.NSEW)
                VersionOptions.grid(row=12, column=0, sticky=Tk.NSEW)
                #--------------------------------------------------------#
            ## Here we are just checking if the pageNum is = 2, as it isnt = 1... If it doesnt = 1 or 2... then it will be ignored and show nothing.
            elif self.pageNum == 2:
                # --------------------------------------------------------#
                ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
                self.fill_empty(1, 0)
                # --------------------------------------------------------#
                ## Here ↓ we are adding both "KeepTitle" and "KeepOptions"... These are both in the same area together, so then
                ## the user will be able to see what the title corresponds with.
                KeepTitle.grid(row=2, column=0, sticky=Tk.NSEW)
                KeepOptions.grid(row=3, column=0, sticky=Tk.NSEW)
                # --------------------------------------------------------#
                ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
                self.fill_empty(4, 0)
                # --------------------------------------------------------#
                ## Here ↓ we are adding both "BackUpTitle" and "BackUpOps"... these are both in the same area together, so then
                ## the user will be able to see what the title corresponds with.
                BackUpTitle.grid(row=5, column=0, sticky=Tk.NSEW)
                BackUpOps.grid(row=6, column=0, sticky=Tk.NSEW)
                ## Here ↓ we are adding both "BackUpTimeTitle" abd "BackUpTimeOps"... these are both in the same area together, so then
                ## the user will be able to see what the title corresponds with.
                BackUpTimeTitle.grid(row=7, column=0, sticky=Tk.NSEW)
                BackUpTimeOps.grid(row=8, column=0, sticky=Tk.NSEW)

                # --------------------------------------------------------#

            ## We are now rendering everything that will be at the bottom of the screen.
            ## These are not in the the pageNum sections as they will be persistent at the bottom of the page.
            ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
            self.fill_empty(13, 0)
            #--------------------------------------------------------#
            ## Here ↓ we are adding the "Next Page" button. This will be visible on every page except the last page...
            ## Which just so happens to be the second page. HAHAHA... soz, ran out of ideas for settings.
            if self.pageNum < 2:
                ## If the self.pageNum is lower than 2, we will display the NextPage button, otherwise we will skip it.
                NextPage.grid(row=14, column=0, sticky=Tk.NSEW)
            ## Here ↓ we are adding the "Back Page" button. This will only be visible if the self.pageNum is greater than 1...
            if self.pageNum > 1:
                ## Adding the BackPage button now...
                BackPage.grid(row=15, column=0, sticky=Tk.NSEW)

            #--------------------------------------------------------#
            ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
            self.fill_empty(16, 0)
            #--------------------------------------------------------#
            ## Now adding the "Save" and "Back" buttons to the screen so the user can save and leave the settings page.
            SaveBtn.grid(row=17, column=0, sticky=Tk.NSEW)
            BackBtn.grid(row=18, column=0, sticky=Tk.NSEW)
            #--------------------------------------------------------#
        ## Checking if "self.frameState" is = 3. If it is... we are going to display the "Next Page" for the tutorial screen.
        elif self.frameState == 3:
            ## First we are going to log what is happening so if for some reason there is a major error... we are going to be able
            self.log.record("Showing next page of guide!", "info")
            ## For convience so we can see where abouts the error is... we are going to say what page we are currently on...
            self.log.record("Current page is {0}".format(self.pageNum), "info")
            ## We are now going to render the fields onto the screen... But first, we must assign
            ## the Tkinter widgets to variables...
            Logo = Tk.Label(self.frame, text="TNF - Tutorial", font="Helvetica 16 bold")
            ## We are adding a "Next" button that executes the "self.changePage(self.pageNum+1" command when clicked.
            ## This will increase the pageNum counter... so then we can see the next page.
            NextBtn = Tk.Button(self.frame, text="Next Page →", command=lambda:self.changePage(self.pageNum+1))
            ## We are now adding a "Back" button that executes the "self.changePage(self.pageNum-1)" command when clicked.
            ## This will decrease the pageNum counter... so then we can see the previous page.
            BackBtn = Tk.Button(self.frame, text="← Previous Page", command=lambda:self.changePage(self.pageNum-1))
            ## This "Finished" button executes the "self.finished_tut()" function that resets the "pageNum" counter
            ## when clicked. This will only be visible on the final frame...
            FinishBtn = Tk.Button(self.frame, text="Finished!", command=lambda:self.finished_tut())
            ## We are now starting a check to see what page we need to load...
            if self.pageNum == 1:
                ## We are now displaying the First Page...
                ## We are just loading the Sub-Title and setting it to say "Adding new games..."
                Title = Tk.Label(self.frame, text="Adding new games...")
                ## Here ↓ we are loading a text-box that is disabled from user editing...
                ## We are also inserting the text from "self.show_tut("Adding")"....
                info = Tk.Text(self.frame, borderwidth=3, width=35, height=11, relief="sunken")
                info.insert(Tk.END, str(self.show_tut("Adding")))
                info.config(font=("consolas", 12), wrap='word', state=Tk.DISABLED)

            ## We are now checking if the pageNum is = 2...
            elif self.pageNum == 2:
                ## We are now just loadin the Sub-Title and setting it to say "Game code..."
                Title = Tk.Label(self.frame, text="Game code...")

                ## Here we are doing some sneaky little trick to see if there are any games manually installed already.
                ## As this is the "FirstTime" screen... there shouldnt be... but if there is... we will display a message
                ## saying that they must already know how to add games. Otherwise, we will show them how to add games...
                ## Along with a text box so they must add atleast one game first.
                if configs['GotGames'] == "1":
                    ## If the user already has games, we will show them "self.show_tut("GotGames")"....
                    info = Tk.Text(self.frame, borderwidth=3, width=35, height=5, relief="sunken")
                    info.insert(Tk.END, str(self.show_tut("GotGames")))
                else:
                    ## If the user does not already have games... we will show them "self.show_tut("Add")"...
                    info = Tk.Text(self.frame, borderwidth=3, width=35, height=15, relief="sunken")
                    info.insert(Tk.END, str(self.show_tut("Add")))
                ## Here we are just setting the text field to always be disabled from user interaction.
                ## We have it here and not in both of the if-else statements... is so it can apply
                ## to either one... and it takes up less lines of code.
                info.config(font=("consolas", 12), wrap='word', state=Tk.DISABLED)

                ## Here we are just setting up the "Add Game" button, but only if there are zero games detected in the system.
                if configs['GotGames'] == "0":
                    AddBtn = Tk.Button(self.frame, text="Add Game", command=lambda:self.showFrame(1))
                    AddBtn.grid(row=5, column=0, sticky=Tk.NSEW)

            elif self.pageNum == 3:
                Title = Tk.Label(self.frame, text="Managing games...")

                info = Tk.Text(self.frame, borderwidth=3, width=35, height=17, relief="sunken")
                info.insert(Tk.END, str(self.show_tut("Managing")))
                info.config(font=("consolas", 12), wrap='word', state=Tk.DISABLED)

            elif self.pageNum == 4:
                Title = Tk.Label(self.frame, text="Settings...")

                info = Tk.Text(self.frame, borderwidth=3, width=35, height=15, relief="sunken")
                info.insert(Tk.END, str(self.show_tut("Settings")))
                info.config(font=("consolas", 12), wrap='word', state=Tk.DISABLED)

            Logo.grid(row=0, column=0, sticky=Tk.NSEW)
            Title.grid(row=1, column=0, sticky=Tk.NSEW)
            ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
            self.fill_empty(2, 0)
            info.grid(row=3, column=0, sticky=Tk.NSEW)
            ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
            self.fill_empty(4,0)
            if self.pageNum == 2:
                ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
                self.fill_empty(6, 0)
            if self.pageNum == 4:
                FinishBtn.grid(row=7, column=0, sticky=Tk.NSEW)
            else:
                NextBtn.grid(row=7, column=0, sticky=Tk.NSEW)
            if not self.pageNum == 1:
                BackBtn.grid(row=8, column=0, sticky=Tk.NSEW)

        else:
            self.log.record("Could not find a 'Frame_State'", "warning")

    ## This method is used at startup... and statup only...
    ## It is going to setup everything the launcher needs for the launcher to run...
    #----------------------------------------------------------------------
    def startup(self):

        self.core.makeFolders(self.path)
        self.loadProps()
        self.loadConfig()
       # self.log.record("Starting startup sequence.", "info")
        self.core.configs = self.configs
        self.gamesList = self.core.games_w_folders
        self.core.upGrannyCounter()
        self.core.grannyCheck()
        res = self.core.checkLauncherUpdates(configs['Version'])
        if res == True:
            self.showFrame(6)
        if configs['FirstTime'] == "0":
            self.frameState = 1
        else:
            self.frameState = -1
        self.log.load()
        self.log.record("Done with startup sequence.", "info")
        self.refresh()
        self.gamesList = self.core.games_w_folders

    ## This method here takes everything out of the window... and then loads
    ## all the new elements onto the screen. Hence, refreshing it...
    #----------------------------------------------------------------------
    def refresh(self):
        self.log.record("Removing everything off the screen to load the new menu items!", "info")
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.draw()

    ## Well, this method is for when you have "finished_tut"...
    ## It finishes the tutorial...
    #----------------------------------------------------------------------
    def finished_tut(self):
        self.pageNum = 1
        self.showFrame(0)

    ## This is the method that creates its own back-up config that can be loaded
    ## if there is no config present.
    #----------------------------------------------------------------------
    def loadProps(self):
        #self.log.record("Loading default properties.", "info")
        self.props['Version'] = '1.4'
        self.props['FirstTime'] = '1'
        self.props['ErrorFrame'] = '1'
        self.props['Logging'] = '7'
        self.props['DevMode'] = '0'
        self.props['GrannyChecker'] = '1'
        self.props['GetVersion'] = '0'
        self.props['GotGames'] = '0'
        self.props['KeepVersions'] = '0'
        self.props['Backups'] = '0'
        self.props['BackupInt'] = '0'

    ## This method loads the config... if you didnt get that... there is something wrong.
    ## It reads the file... and writes it the "config" dictionary.
    #----------------------------------------------------------------------
    def loadConfig(self):
        if os.path.isfile("{0}/{1}".format(self.path, "configs/launcher.conf")):
            holder = {}
            with open(self.confFile, 'r') as _in:
                for line in _in:
                    line = line.strip("\n")
                    (key, val) = line.split("=")
                    holder[str(key)] = val
            for x in holder:
                x_old = x
                c = x[0]
                x = c.upper()+x[1:]
                configs[x] = holder[x_old]
        else:
            self.core.makeConfig()
            self.loadConfig()
        #self.log.record("Loading config.", "info")

    ## This function does exactly what it says... Saves the config.
    ## It does it by reading the loaded config that is in memory... and saving
    ## it to the file.
    #----------------------------------------------------------------------
    def saveConfig(self):
        global configs
        configs['Logging'] = self.options.index(self.opt.get())
        configs['DevMode'] = self.devoption.index(self.devString.get())
        configs['GrannyChecker'] = self.GrannyOptions.index(self.GrannyHolder.get())
        configs['GetVersion'] = self.VersionOps.index(self.VersionHolder.get())
        configs['KeepVersions'] = self.keepVersionsOps.index(self.keepVersionsHolder.get())
        self.log.record("Saving config.", "info")
        results = []
        with open(self.confFile, 'w') as out:
            for line in configs:
                results.append('{0}={1}\n'.format(line, configs[line]))
            for _line in results:
                out.write(_line)

    ## This is a very small fucntion... to shutdown the launcher. Duh.
    #----------------------------------------------------------------------
    def shutdown(self):
        self.frame.quit()

    ## This function is used to change the Page that is currently loaded
    ## by changing the variable "pageNum"
    #----------------------------------------------------------------------
    def changePage(self, pageNum):
        self.log.record("Changing Page.", "info")
        self.pageNum = pageNum
        self.refresh()
        self.show()

    ## This method is used to change the frame and framestate used in the "draw"
    ## functoin. It also takes a message that could be used within the different
    ## frames. EG. A waiting message, A game code. etc.
    #----------------------------------------------------------------------
    def showFrame(self, frameName):
        self.log.record("Switching frames.", "info")
        if frameName == 0:
            if configs['FirstTime'] == "1":
                configs['FirstTime'] = "0"
            self.log.record("Switching back to 'Main Frame'", "info")
            self.frameState = 1
            self.refresh()
            self.show()
        elif frameName == 1:
            self.log.record("Switching to 'Add Game'", "info")
            subFrame = OtherFrame(self, "Add Game", 1, "", "")
        elif frameName == 2:
            self.log.record("Switching to 'All Games'", "info")
            subFrame = OtherFrame(self, "", 2, "", "")
        elif frameName == 3:
            self.log.record("Switching to 'Settings Frame'", "info")
            self.frameState = 2
            self.refresh()
            self.show()
        elif frameName == 4:
            self.log.record("Switching to the 'Developer' Frame", "info")
            subFrame = OtherFrame(self, "Developer Mode", 4, "", "main")
        elif frameName == 5:
            self.log.record("Woo, the user wants to read more of the guide!", "info")
            self.frameState = 3
            self.refresh()
            self.show()
        elif frameName == 6:
            self.log.record("Showing the Update Frame", "info")
            subFrame = OtherFrame(self, "", 5, "", "")
            self.hide()

    ## This small but functional method is used to create blank rows in the
    ## on-screen grid. It allows for good styling throughout the whole
    ## Draw method.
    #----------------------------------------------------------------------
    def fill_empty(self,row,column):
        empty = Tk.Label(self.frame)
        empty.grid(row=row,column=column)
        return empty

    ## This method is used to show the selected pages from the online tutorial.
    ## It loads it from the file, splits it... then returns it back to whatever called it.
    #----------------------------------------------------------------------
    def show_tut(self,page):
        self.log.record("Loading the '{0}' page of the tutorial.".format(page), "info")
        path = "{0}/{1}/{2}".format(self.path, "configs", "tut.info")
        temp = {}
        holder = {}
        _temp = ""
        with open(path, 'r') as _in:
            for line in _in:
                line = line.strip("\n")
                (key, val) = line.split("=")
                temp[str(key)] = val
        for x in temp:
            x_old = x
            c = x[0]
            x = c.upper() + x[1:]
            holder[x] = temp[x_old]
        try:
            _temp = holder[str(page)]
            return _temp.replace("$x", "\n")
        except:
            self.log.record("For some reason could not find '{0}' page of the tutorial...".format(page), "error")
            return "Sorry, having a slight issue loading this page at current."

    ## This is used to hide the whole frame. It makes everything invisible
    ## to the user, so then u can see the other frames. It can be used in
    ## the "Refresh" function to remove everything off the screen then
    ## reload it all.
    #----------------------------------------------------------------------
    def hide(self):
        self.log.record("Hiding Main Fame", "info")
        self.root.withdraw()

    ## This method is used to intially show the frames. It draws it onto the screen
    ## then used the "Draw" method to display all the elements onto it.
    #----------------------------------------------------------------------
    def show(self):
        self.core.loadGames()
        self.gamesList = self.core.games_w_folders
        self.log.record("Showing Main Current frame.", "info")
        self.refresh()
        self.root.update()
        self.root.deiconify()

########################################################################
class OtherFrame(Tk.Toplevel):
    #----------------------------------------------------------------------
    def __init__(self, parent, frameName, frameState, frameSize, message):
        global game_configs
        self.parent         = parent
        self.name           = frameName
        self.log            = Logger()
        self.core           = Thinking()
        self.gameConfigs    = game_configs
        self.frame_state    = frameState
        self.code           = ""

        if not message == "":
            self.message = message
        Tk.Toplevel.__init__(self)
        if not frameSize == "":
            self.geometry(str(frameSize))
        self.title(str(self.name))
        self.drawFrame()


    ## This is the method used to acutally draw all the elements on the screen after
    ## sorting through what is needed, and what is not. This used the "self.frameState"
    ## variable to declare which "framstate" to use.
    #----------------------------------------------------------------------
    def drawFrame(self):
        self.core.grannyCheck()
        self.log.record("Loading Selected Frame.", "info")
        if self.frame_state == 0:
            self.closeFrame()
        elif self.frame_state == 1:
            """ This is the Add Game Frame """
            self.log.record("Loading 'Add Game Frame'", "info")
            self.gameCode = Tk.StringVar()

            Logo = Tk.Label(self, text="TNF Launcher", font="Helvetica 16 bold")
            info = Tk.Label(self, text="Please enter the 5 digit code below.")
            code = Tk.Entry(self, textvariable=self.gameCode)
            Enter = Tk.Button(self, text="Enter!", command=lambda:self.addGame(self.gameCode.get()))

            Logo.grid(row=0, column=1, sticky=Tk.NSEW)
            info.grid(row=1, column=1, sticky=Tk.NSEW)
            code.grid(row=2, column=1, sticky=Tk.NSEW)
            Enter.grid(row=3, column=1, sticky=Tk.NSEW)
        elif self.frame_state == 2:
            """ This is the Frame to display All Games """
            self.log.record("Loading the 'All Games' frame.", "info")
            self.core.grannyCheck()
            self.gameList = self.core.games_w_folders
            _counter = 0
            _line = 0
            _row = 1
            _column = 0
            if not len(self.gameList) == 0:
                Title = Tk.Label(self, text="All your games", font="Helvetica 16 bold")
                Title.grid(row=0, column=0, sticky=Tk.NSEW)
                for i in range(len(self.gameList)):
                    G = Tk.Button(self, text=str(self.gameList[_counter]), command=lambda x=i: self.changeFrame(3,"{0}".format(self.gameList[x])))
                    G.grid(row=_row, column=_column, sticky=Tk.NSEW)
                    if _row % 20 == 0:
                        _column += 1
                        _row = 0
                    _counter += 1
                    _row += 1
            else:
                self.log.record("User has been able to access games window when there are no games!", "warning")
                Title = Tk.Label(self, text="No games installed!", font="Helvetica 16 bold")
                CloseBtn = Tk.Button(self, text="Close", command=lambda:self.closeFrame())
                Title.grid(row=0,column=0,sticky=Tk.NSEW)
                CloseBtn.grid(row=1, column=0, sticky=Tk.NSEW)
        elif self.frame_state == 3:
            """ This is the Game Frame """
            _tokens = self.message.split("$x")
            self.message = _tokens[0]
            self.core.loadGame(self.message)
            self.VersionHolder = Tk.StringVar()
            gotten = self.core.loadVersionList(self.message)
            VersionsOps = gotten.split(",")
            self.VersionHolder.set("Latest")
            update = self.core.checkGameUpdates(self.message)
            try:
                if _tokens[1] == "false":
                    update = False
            except:
                pass
            if update == False:

                self.log.record("Loading {0}'s frame!'".format(self.message), "info")
                Title = Tk.Label(self, text=self.message.upper(), font="Helvetica 16 bold")
                Version = Tk.Label(self, text="Latest Version: {0}".format(self.gameConfigs['Latest_Version']))
                VersionsChoice = Tk.OptionMenu(self, self.VersionHolder,*VersionsOps)
                playBtn = Tk.Button(self, text="Play Game", command=lambda:self.playGame(self.message))
                updateBtn = Tk.Button(self, text="Force Update", command=lambda:self.forceUpdate(self.message))
                uninstallBtn = Tk.Button(self, text="Uninstall", command=self.delGame)

                Title.grid(row=0, column=1, sticky=Tk.NSEW)
                Version.grid(row=1, column=1, sticky=Tk.NSEW)
                VersionsChoice.grid(row=2, column=1, sticky=Tk.NSEW)
                playBtn.grid(row=3, column=0, sticky=Tk.NSEW)
                updateBtn.grid(row=3, column=1, sticky=Tk.NSEW)
                uninstallBtn.grid(row=3, column=2, sticky=Tk.NSEW)
            else:
                self.log.record("We have detected that there is an update... Just going to workout if we are allowed to auto-update...", "warning")
                if str(self.gameConfigs['Auto_Update']).strip() == "true":
                    holder = self.message
                    self.log.record("We are allowed to do self update...", "info")
                    ## Going to auto-update to the latest version... Download the new version...
                    self.changeFrame(-2, "Please wait, we are updating the game!")
                    returned = self.core.versionGrabber(holder, "version")
                    self.core.downloadLink(holder, returned.strip())
                    self.core.updateGameConfig(holder, "Latest_Version", returned.strip())
                    self.changeFrame(3, holder)
                elif self.gameConfigs['Auto_Update'].strip() == "false":
                    self.log.record("We are NOT allowed to do self update... :(", "info")
                    self.holder = self.message
                    self.core.GameNeedsUpdate = True
                    self.core.LauncherNeedsUpdate = False
                    self.changeFrame(5, "")

        elif self.frame_state == 4:
            """ This is the Developer frame """
            self.core.findDevFolders()
            Logo = Tk.Label(self, text="TNF Launcher", font="Helvetica 16 bold")
            devTitle = Tk.Label(self, text="Dev - Mode")
            Logo.grid(row=0,column=0,sticky=Tk.NSEW)

            if self.message == "main":
                workSpacesBtn = Tk.Button(self, text="Current Work Spaces - {0}".format(self.core.amountDevFolders), command=lambda:self.changeFrame(4, "current"))
                MakeNewBtn = Tk.Button(self, text="Make new", command=lambda:self.changeFrame(4, "new"))

                devTitle.grid(row=1,column=0,sticky=Tk.NSEW)
                ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
                self.fill_empty(2, 0)
                workSpacesBtn.grid(row=3,column=0,sticky=Tk.NSEW)
                MakeNewBtn.grid(row=4,column=0,sticky=Tk.NSEW)

            if self.message == "new":
                NewName = Tk.Label(self, text="New Name")
                CreateBtn = Tk.Button(self, text="Create")
                devTitle.grid(row=1,column=0,sticky=Tk.NSEW)
                ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
                self.fill_empty(2, 0)
                NewName.grid(row=3, column=0, sticky=Tk.NSEW)
                CreateBtn.grid(row=4, column=0, sticky=Tk.NSEW)

            if self.message == "current":
                ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
                self.fill_empty(0, 1)
                devTitle.grid(row=0,column=2,sticky=Tk.NSEW)
                ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
                self.fill_empty(2, 0)
                ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
                self.fill_empty(3, 0)
                ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
                self.fill_empty(5, 0)
                _counter = 0
                _row = 1
                _column = 0
                for i in range(len(self.core.dev_folders)):
                    G = Tk.Button(self, text=str(self.core.dev_folders[_counter]), command=lambda x=i: self.changeFrame(3,"{0}".format(self.core.dev_folders[x])))
                    G.grid(row=_row, column=_column, sticky=Tk.NSEW)
                    if _row % 20 == 0:
                        _column += 1
                        _row = 0
                    _counter += 1
                    _row += 1

        elif self.frame_state == 5:
            """ This is the Update-Avaliable Frame"""
            self.log.record("Loaded the update avaliable frame!", "info")
            Title = Tk.Label(self, text="There is an update!", font="Helvetica 20 bold")
            WouldTitle = Tk.Label(self, text="Would you like to download it?")
            YesBtn = Tk.Button(self, text="Yes", command=lambda:self.doUpdate("true"))
            NoBtn = Tk.Button(self, text="No", command=lambda:self.doUpdate("false"))
            Title.grid(row=0, column=1, sticky=Tk.NSEW)
            WouldTitle.grid(row=1, column=1, sticky=Tk.NSEW)
            YesBtn.grid(row=2, column=0, sticky=Tk.NSEW)
            NoBtn.grid(row=2, column=2, sticky=Tk.NSEW)

            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=1)
            self.columnconfigure(2, weight=1)
        elif self.frame_state == 6:
            """ This is the Multiple-Versions-Found Frame"""
            self.log.record("Loaded the Multiple-Versions-Found Frame", "info")

            _tokens = self.message.split("$x")
            _list = _tokens[1].split("$i")
            VersionHolder = Tk.StringVar()
            VersionOps = _list
            del VersionOps[-1]
            VersionHolder.set(VersionOps[-1])


            Title = Tk.Label(self, text=_tokens[0], font="Helvetica 16 bold")
            Opts = Tk.OptionMenu(self,VersionHolder,*VersionOps)
            Btn = Tk.Button(self, text="Get!", command=lambda:self.getGameVersion(_tokens[-1], VersionHolder.get()))

            Title.grid(row=0, column=0, sticky=Tk.NSEW)
            Opts.grid(row=1, column=0, sticky=Tk.NSEW)
            Btn.grid(row=2, column=0, sticky=Tk.NSEW)
        elif self.frame_state == -1:
            """ This is the Error Frame """
            self.log.record("Loading the error frame!", "info")
            errorLabel = Tk.Label(self, text="Error!", font="Helvetica 16 bold")
            errorMsg = Tk.Label(self, text=self.message)
            okBtn = Tk.Button(self, text="Ok", command=self.closeFrame)

            errorLabel.grid(row=0,column=0, sticky=Tk.NSEW)
            errorMsg.grid(row=0,column=1, sticky=Tk.NSEW)
            okBtn.grid(row=1,column=1, sticky=Tk.NSEW)
        elif self.frame_state == -2:
            """ This is the Waiting Frame """
            self.log.record("Loading the 'Waiting' frame.", "info")
            Wait = Tk.Label(self, text=self.message, font="Helvetica 16 bold")
            if self.message == "Done!":
                Btn = Tk.Button(self, text="Ok", command=self.closeFrame)
                Btn.grid(row=1,column=0,sticky=Tk.NSEW)
            Wait.grid(row=0,column=0,sticky=Tk.NSEW)

        elif self.frame_state == -3:
            """ THIS IS THE ERROR REPORTING FRAME! """
            self.log.record("Loading the Error Reporting Frame!", "info")
            errorLabel = Tk.Label(self, text="Critical Error Occured!", font="Helvetica 16 bold")

            errorMsg = Tk.Text(self, borderwidth=3, relief="sunken")
            ## Going to display everything up untill the last 4 lines...
            ## As those last 4 lines are logging the opening of the error frame...
            self.errorMessage = keeper
            for line in self.errorMessage:
                errorMsg.insert(Tk.END,str(line))
            errorMsg.config(font=("consolas", 12), undo=True, wrap='word', state=Tk.DISABLED)

            errorMsg.grid(row=2, column=1, sticky="nsew", padx=2, pady=2)

            scrollb = Tk.Scrollbar(self, command=errorMsg.yview)
            scrollb.grid(row=2, column=2, sticky='nsew')
            errorMsg['yscrollcommand'] = scrollb.set

            ForumBtn = Tk.Button(self, text="Forum", command=lambda: webbrowser.open_new_tab("http://thenightforum.com/"))
            PasteBinBtn = Tk.Button(self, text="PasteBin", command=lambda: self.pasteBin(self.errorMessage))
            GithubBtn = Tk.Button(self, text="Github", command=lambda: webbrowser.open_new_tab("https://github.com/TheNightForum/TheNightForum.github.io/issues"))
            IgnoreBtn = Tk.Button(self, text="Ignore", command=self.ignoreError)

            errorLabel.grid(row=0, column=1, sticky=Tk.NSEW)
            ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
            self.fill_empty(1,0)
            ## Here ↓ we are making an empty space to make it look cleaner and easier to read... by using the "fill_empty" function.
            self.fill_empty(3,0)
            ForumBtn.grid(row=4, column=0, sticky=Tk.NSEW)
            PasteBinBtn.grid(row=5, column=0, sticky=Tk.NSEW)
            GithubBtn.grid(row=4, column=2, sticky=Tk.NSEW)
            IgnoreBtn.grid(row=5, column=2, sticky=Tk.NSEW)

    ## This method is used when playing games as it generates the required path
    ## by grabbing the data from the options menu (The dropdown box that displays
    ## what version you are playing....) it also grabs the currently loaded game.
    ## It then sends everything it needs to the "Thinking" class...
    # ----------------------------------------------------------------------
    def playGame(self, code):
        if self.VersionHolder.get() == "Latest":
            version = self.gameConfigs['Latest_Version'].strip()
        else:
            version = str(self.VersionHolder.get())
        if 'Game_Folder' in self.gameConfigs:
            path = "{0}/{1}/{2}/{3}/{4}/{5}".format(self.core.path, "games", code, version, self.gameConfigs['Game_Folder'].strip(), self.gameConfigs['Launch_File'].strip())
        else:
            path = "{0}/{1}/{2}/{3}/{4}".format(self.core.path, "games", code, version, self.gameConfigs['Launch_File'].strip())
        self.core.startGame(code, path)

    ## This method is also used by the drawFrame method to forcefully update
    ## the game that is currently loaded. These methods are here because they
    ## display another frame eg. The waiting frame... so they can install without
    ## it looking like the project has crashed.
    # ----------------------------------------------------------------------
    def forceUpdate(self, code):
        self.changeFrame(-2, "Please wait whilst we Force Update {0}".format(code.upper()))
        path = "{0}/{1}/{2}/".format(self.core.path, "games", code)
        returned = self.core.versionGrabber(code, "version")
        if os.path.exists("{0}{1}".format(path, returned.strip())):
            shutil.rmtree("{0}{1}".format(path, returned.strip()))
        self.core.downloadLink(code, returned.strip())
        self.core.updateGameConfig(code, "Latest_Version", returned.strip())
        self.changeFrame(3, code)

    ## This method is used by the drawFrame function when adding games. It takes
    ## the input from the tkinter entry field... then it sorts out whether or not
    ## the game is already installed, by calling the "Thinking" class....
    #----------------------------------------------------------------------
    def addGame(self, code):
        self.log.record("About to try and add a game!", "info")
        self.core.grannyCheck()
        if len(code) > 5:
            self.log.record("Code is longer than 5 characters!", "warning")
            self.changeFrame(-1, "Sorry, code must be no more than 5 characters long!")
        elif len(code) == 0:
            self.log.record("Code was empty.", "warning")
            self.changeFrame(-1, "Please enter a code!")
        else:
            self.log.record("Code was a good length.", "info")
            result = self.core.checkIfInstalled(code)
            if result == "got":
                self.log.record("'{0}' is already installed!".format(code.upper()), "warning")
                returned = self.core.versionGrabber(code, "versions.list")
                if not returned == "":
                    _list = returned.split("\n")
                    path = "{0}/{1}/{2}/".format(self.core.path, "games", code)
                    returned = ""
                    for item in _list:
                        item = item.strip()
                        if not os.path.exists("{0}{1}".format(path, item)):
                            if returned == "":
                                returned += "{0}".format(item)
                            else:
                                returned += "$i{0}".format(item)
                        else:
                            pass
                    self.changeFrame(6,"We have found multiple versions of the game.\nWhich one would you like?$x{0}$x{1}".format(returned, code))
                else:
                    self.changeFrame(-1, "Sorry, this game is already installed.")
            elif result == True:
                self.log.record("Going to install '{0}'".format(code.upper()), "info")
                self.changeFrame(-2, "Please wait whilst we install your game!")
                ## Here we are going to check if there are multiple versions of the game...
                ## What we will do is, we will consault the "version.list" file... if it exsists... then there are more versions...
                returned = self.core.versionGrabber(code, "version")
                self.core.downloadLink(code, returned.strip())
                self.log.record("Game installed!", "info")
                self.changeFrame(-2, "Done!")
            elif result == False:
                self.log.record("Game code is invalid.", "warning")
                self.changeFrame(-1, "Sorry, That game code is invalid.")

    ## This method is used to get specific versions of games.... It generates a
    ## link and a path and sends it off to the "thinking" class to then download
    ## and put in the correct directory...
    # ----------------------------------------------------------------------
    def getGameVersion(self, code, version):
        self.changeFrame(-2, "Please wait whilst we install your game!")
        self.core.downloadLink(code, version.strip())
        self.log.record("Game installed!", "info")
        self.changeFrame(-2, "Done!")

    ## This function is used to delete a game. It grabs the game that is currently
    ## loaded and then it changes the frame so the user knows what is happening
    ## all the whilst it is sending off information to the "Thinking" class to then
    ## go throught the files and delete them.
    #----------------------------------------------------------------------
    def delGame(self):
        code = self.message
        self.log.record("Pressed button to delete '{0}'".format(code.upper()), "info")
        self.changeFrame(-2, "Please wait whilst we uninstall '{0}'".format(code.upper()))
        result = self.core.deleteGame(code)
        if not result == "Done!":
            self.changeFrame(-1, result)
        else:
            self.changeFrame(-2, result)

    ## This method is used to change the frame and framestate used in the "draw"
    ## functoin. It also takes a message that could be used within the different
    ## frames. EG. A waiting message, A game code. etc.
    #----------------------------------------------------------------------
    def changeFrame(self, frameState, msg):
        self.log.record("Changing frame to code: {0}".format(frameState), "info")
        if not frameState == 0:
            self.message =  msg
            self.frame_state = frameState
            self.refresh()
            self.show()

    ## This function is used to take the error message from the Error Frame
    ## and upload it to pastebin. After it is done with that, it then opens
    ## the newly created pastebin lik into a new tab...
    # ----------------------------------------------------------------------
    def pasteBin(self, msg):
        _string = ""
        for line in msg:
            _string += line
        pastebin_vars = {'api_dev_key': 'da53f47febdf5bbe0923770027c9733e', 'api_option': 'paste'}
        pastebin_vars['api_paste_code'] = str(_string)
        response = urllib2.urlopen('http://pastebin.com/api/api_post.php', urllib.urlencode(pastebin_vars))
        url = response.read()
        webbrowser.open_new_tab(url)

    ## This is the important function of finding out what system needs an
    ## update... Either Launcher or Game... It then displays the correct screen
    ## and handles the whole update proccess for you...
    # ----------------------------------------------------------------------
    def doUpdate(self, response):
        global LauncherNeedsUpdate
        if response == "true":
            self.log.record("User chose to do update...", "info")
            ## Working out if it is the launcher or a game that is being updated...
            if LauncherNeedsUpdate == True and GameNeedsUpdate == False:
                self.log.record("Its the Launcher that needs the update...", "info")
                ## This means that it is an update for the Launcher, and not a Game
                LauncherNeedsUpdate = False
                self.core.selfModify("", "", 1)
                self.core.selfModify("Version",str(urllib2.urlopen("https://raw.githubusercontent.com/TheNightForum/TheNightForum.github.io/master/VERSION").read().strip()),3)
                self.closeFrame()
            elif self.core.LauncherNeedsUpdate == False and self.core.GameNeedsUpdate == True:
                ## This means that it is an update for a game, and not for the Launcher
                self.log.record("Its the Game that needs the update...", "info")
                returned = self.core.versionGrabber(self.holder, "version")
                self.core.downloadLink(self.holder, returned.strip())
                self.core.updateGameConfig(self.holder, "Latest_Version", returned.strip())
                self.changeFrame(3, self.holder)
        elif response == "false":
            if self.core.LauncherNeedsUpdate == False and self.core.GameNeedsUpdate == True:
                self.changeFrame(3, "{0}$x{1}".format(self.holder, "false"))
        else:
            ## This means that the response was other than 'True' or 'False'
            pass

    ## This is the function that is used by the Error Frame to ignore the
    ## the error and just continue on like nothing is wrong.
    #----------------------------------------------------------------------
    def ignoreError(self):
        global errorFrameRunning
        errorFrameRunning = 0
        self.closeFrame()

    ## This small but functional method is used to create blank rows in the
    ## on-screen grid. It allows for good styling throughout the whole
    ## Draw method.
    #----------------------------------------------------------------------
    def fill_empty(self,row,column):
        empty = Tk.Label(self)
        empty.grid(row=row,column=column)
        return empty

    ## This is used to hide the whole frame. It makes everything invisible
    ## to the user, so then u can see the other frames. It can be used in
    ## the "Refresh" function to remove everything off the screen then
    ## reload it all.
    #----------------------------------------------------------------------
    def hide(self):
        self.withdraw()

    ## This function has the important role of taking everything off the screen
    ## and then loading everything new onto it. It invokes the "Draw" function
    ## striaght after it removes all of the Tkinter widgets.
    #----------------------------------------------------------------------
    def refresh(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.drawFrame()

    ## This method is used to intially show the frames. It draws it onto the screen
    ## then used the "Draw" method to display all the elements onto it.
    #----------------------------------------------------------------------
    def show(self):
        self.update()
        self.deiconify()

    ## This is used to take the user back to his/her original screen.
    ## It kills this screen and then loads the previous one that was used...
    ## The parent. If there is no parent present... it will just close this
    ## whole frame...
    #----------------------------------------------------------------------
    def closeFrame(self):
        self.destroy()
        if not self.parent == None:
            self.parent.show()

########################################################################
class Thinking():
    ## This is used to initialise the "Thinking" class... and setup
    ## some very basic variables...
    #----------------------------------------------------------------------
    def __init__(self):
        """ This class is for handling the core of the launcher."""
        global configs
        global game_configs
        global grannyCounter
        self.log                = Logger()
        self.configs            = configs
        self.gameConfigs        = game_configs
        self.frame_state        = 0
        self.baseUrl            = "http://thenightforum.github.io/"
        self.path               = "{0}/{1}".format(expanduser("~"), "TNFLauncher")
        self.confFile = "{0}/{1}/{2}".format(self.path, "configs", "launcher.conf")
        self.games_w_folders    = ""
        self.defaultConfigFile  = {'Version':'1.0', 'Game_Folder':'bin', 'Launch_File':'game.jar', 'Auto_Update':'true', 'Version_Url':'Default'}
        self.loadGames()
        self.LauncherNeedsUpdate = False
        self.GameNeedsUpdate    = False

    ## This function has the role of searching through the whole games
    ## directory and add it to a public list to then be used by other functions...
    #----------------------------------------------------------------------
    def loadGames(self):
        if os.path.exists("{0}/{1}".format(self.path, "games")):
            try:
                self.games_w_folders    = os.listdir("{0}/{1}".format(self.path, "games"))
                num                     = self.games_w_folders.index(".DS_Store")
                del self.games_w_folders[num]
            except:
                pass

    ## This is used to go to the public repo and collect a list of all the different
    ## versions of games there are, that are avaliable to download.
    # ----------------------------------------------------------------------
    def loadVersionList(self, code):
        stringList = ""
        for item in os.listdir("{0}/{1}/{2}/".format(self.path, "games", code)):
            if os.path.isdir("{0}/{1}/{2}/{3}".format(self.path, "games", code, item)):
                if item == self.gameConfigs['Latest_Version'].strip():
                    if stringList == "":
                        stringList += "{0}".format(str("Latest"))
                    else:
                        stringList += ",{0}".format(str("Latest"))
                else:
                    if not item == "DATA":
                        if stringList == "":
                            stringList += "{0}".format(str(item))
                        else:
                            stringList += ",{0}".format(str(item))

        return str(stringList)

    ## This method is very simple, but very important... It checks to see if the
    ## game is actually installed.... so we can either get the latest game, or
    ## make the user choose a version of the game to download.
    #----------------------------------------------------------------------
    def checkIfInstalled(self, code):
        self.log.record("Checking if '{0}' is already installed.".format(code.upper()), "info")
        games = os.listdir("{0}/{1}".format(self.path, "games"))
        for game in games:
            if game == code:
                return "got"
        else:
            result = self.checkUrl(code)
            return result

    ## THis is checking if the url is present for the code that is provided...
    ## if it returns false, we either wont install the game... or we will delete
    ## the one that is already installed...
    #----------------------------------------------------------------------
    def checkUrl(self, code):
        self.log.record("Checking URL for '{0}'".format(code.upper()), "info")
        self.GameURL = "{0}/Games/{1}/".format(self.baseUrl, code)
        self.GameCode = code
        try:
            urllib2.urlopen("{0}{1}".format(self.GameURL, "version"))
            self.log.record("Found the game!", "info")
            return True
        except urllib2.HTTPError, e:
            self.log.record("HTTP ERROR: Could not find address!", "warning")
            return False
        except urllib2.URLError, e:
            self.log.record("URL ERROR: Could not find address!", "warning")
            return False

    ## This is the exact same as the method above, but is used to determine if
    ## any url provided is valid. It will take any url provided to it... and
    ## check to see if it returns a 404 error.
    # ----------------------------------------------------------------------
    def checkUrlItem(self, webURL):
        self.log.record("Checking if '{0}' is a URL.".format(webURL.upper()), "info")
        try:
            urllib2.urlopen("{0}".format(webURL))
            self.log.record("URL exists!", "info")
            return True
        except:
            self.log.record("URL ERROR: Could not find address!", "warning")
            return False

    ## This is used to grab all the different versions of games avaliable to
    ## the user to download and install.
    # ----------------------------------------------------------------------
    def versionGrabber(self, code, file):
        URL = "{0}/Games/{1}/{2}".format(self.baseUrl, code, file)
        result = self.checkUrlItem(URL)
        if result == True:
            return urllib2.urlopen(URL).read().strip()
        else:
            ## Returning nothing so then it can make the check easier...
            return ""

    ## This is the important function that creats the download link for the
    ## game and then downloads it to the temp folder... and preped to be installed
    # ----------------------------------------------------------------------
    def downloadLink(self, code, version):
        self.log.record("Beginning game download...", "info")
        response = urllib2.urlopen("{0}/Games/{1}/{2}.zip".format(self.baseUrl, code, version))
        zipcontent= response.read()
        with open("{0}/{1}/{2}.zip".format(self.path, "temp", version), 'w') as f:
            f.write(zipcontent)
        self.log.record("Done.", "info")
        self.unZipGame(code, version)
        if not os.path.exists("{0}/{1}/{2}/{3}".format(self.path, "games", code, "DATA")):
            os.mkdir("{0}/{1}/{2}/{3}".format(self.path, "games", code, "DATA"))
        if not os.path.exists("{0}/{1}/{2}/{3}".format(self.path, "games", code, "config.properties")):
            with open("{0}/{1}/{2}/{3}".format(self.path, "games", code, "config.properties"), 'w') as out:
                try:
                    data = urllib2.urlopen("{0}/Games/{1}/{2}".format(self.baseUrl, code, "config.properties")).read()
                    out.write(data)
                except:
                    self.log.record("For some reason this game did not have any config.properties in the repo... Going to make the default...", "warning")
                    self.defaultConfig(code)

        if not os.path.exists("{0}/{1}/{2}/{3}/{4}".format(self.path, "games", code, version, "config.properties")):
            with open("{0}/{1}/{2}/{3}/{4}".format(self.path, "games", code, version, "config.properties"), 'w') as out:
                out.write("#Please do not modify this file by hand!")
                out.write("Current_Path={0}".format("{0}/{1}/{2}/{3}/".format(self.path, "games", code, version)))
                out.write("DATA_Path={0}".format("{0}/{1}/{2}/{3}/".format(self.path, "games", code, "DATA")))
        else:
            with open("{0}/{1}/{2}/{3}/{4}".format(self.path, "games", code, version, "config.properties"), 'a') as out:
                out.write("Current_Path={0}".format("{0}/{1}/{2}/{3}/".format(self.path, "games", code, version)))
                out.write("DATA_Path={0}".format("{0}/{1}/{2}/{3}/".format(self.path, "games", code, "DATA")))

    ## This function has the amazing ability to unzip the downloaded games...
    ## and put them into their required paths so they are setup and ready to play.
    #----------------------------------------------------------------------
    def unZipGame(self, code, version):
        self.log.record("Unzipping game.", "info")
        path = "{0}/{1}/{2}.zip".format(self.path, "temp", version)
        zip_ref = zipfile.ZipFile(path, 'r')

        zip_ref.extractall("{0}/{1}/{2}/{3}".format(self.path, "games", code, version))
        zip_ref.close()
        try:
            self.log.record("Trying to delete game zip!", "info")
            os.remove(path)
            self.log.record("Done!", "info")
        except:
            self.log.record("Could not delete game zip!", "error")

    ## UnZipItem is the exact same as the method above, just it has the ability
    ## to unzip any item provided... and put it into the path provided.
    # ----------------------------------------------------------------------
    def unZipItem(self, item, location):
        path = "{0}/{1}/{2}.zip".format(self.path, "temp", item)
        zip_ref = zipfile.ZipFile(path, 'r')
        zip_ref.extractall("{0}".format(location))
        zip_ref.close()
        try:
            self.log.record("Trying to delete '{0}' zip!".format(item), "info")
            os.remove(path)
            self.log.record("Done!", "info")
        except:
            self.log.record("Could not delete '{0}' zip!".format(item), "error")

    ## Make config file for the launcher when it detects that the launcher.config
    ## file does not exist. It creates it so then the launcher can function properly.
    # ----------------------------------------------------------------------
    def makeConfig(self):
        results = []
        with open(self.confFile, 'w') as _out:
            for line in props:
                results.append('{0}={1}\n'.format(line, props[line]))
            for _line in results:
                _out.write(_line)
        with open("{0}/{1}/{2}.info".format(self.path, "configs", "tut"), 'w') as out:
            data = urllib2.urlopen("http://repo.zectr.com/Releases/Programs/TNFLauncher/info/tut.info").read()
            out.write(data)

    ## This function is only used when the launcher has detected that the home
    ## folder for the launcher has been deleted mid-way through running...
    ## It re-creats all the folders and config files... so the launcher can keep
    ## on running.
    # ----------------------------------------------------------------------
    def remake(self):
        self.makeFolders(self.path)
        self.makeConfig()

    ## Granny checker is the biggest and most important function of them all.
    ## It constantly goes through all the important files that are in the home
    ## folder of the launcher and checks to see if they are the same as the ones
    ## loaded into memory. If they are different, it will re-load them back to the
    ## same state loaded into memory. It also goes through all the games in the
    ## "games.list" file and makes sure they are actually installed into the "games"
    ## folder. Along with that it also regularly checks to see if they are still avaliable
    ## online, if they are not... then they are deleted.
    #----------------------------------------------------------------------
    def grannyCheck(self):
        """
        This method is here to perform checks throughout the use of the launcher
        to make sure we are not letting just any random stick their fingers into
        our files and edit stuff to break us.
        """
#        self.log.record("Running Granny Check", "info")
        if os.path.exists(self.path):
            pass
        else:
            self.remake()
            self.log.record("Sorry, for some reason the core folder was deleted... so we just remade it... we are back now...", "warning")
        if len(self.games_w_folders) > 0:
            if not configs['GotGames'] == "1":
                self.selfModify("GotGames", "1", 3)
        else:
            if not configs['GotGames'] == "0":
                self.selfModify("GotGames", "0", 3)

        results = []
        temp = {}
        try:
            with open ("{0}/{1}".format(self.path, "configs/launcher.conf"), 'r') as check:
                for line in check:
                    holder = {}
                    with open("{0}/{1}".format(self.path, "configs/launcher.conf"), 'r') as _in:
                        for line in _in:
                            line = line.strip("\n")
                            (key, val) = line.split("=")
                            holder[str(key)] = val
                    for x in holder:
                        x_old = x
                        c = x[0]
                        x = c.upper()+x[1:]
                        temp[x] = holder[x_old]
        except:
            self.log.record("Something went wrong when trying to read the config file!", "error")
            if os.path.exists(self.path):
                pass
            else:
                self.log.record("Oh no... Something went Major wrong... The Home-Dir of the launcher is gone!", "error")

        for key in set(configs.keys()).union(temp.keys()):
            if key not in configs or key not in temp:
                self.rewrite()
                continue
            if not configs[key] == temp[key]:
                self.rewrite()
                continue
        if configs['GrannyChecker'] == 1:
            try:
                with open ("{0}/{1}".format(self.path, "configs/game.list"), 'r') as check:
                    for line in check:
                        line = line.strip("\n")
                        path = "{0}/{1}/{2}".format(self.path, "games", line)
                        if os.path.exists(path):
                            results.append(line)
                        else:
                            pass

                with open ("{0}/{1}".format(self.path, "configs/game.list"), 'w') as check:
                    for line in results:
                        check.write("{0}\n".format(line))
            except:
                if os.path.exists("{0}/{1}/{2}".format(self.path, "configs", "games.list")):
                    self.log.record("Something went wrong with opening the games.list file!", "error")
                else:
                    pass

            for game in self.games_w_folders:
                for line in results:
                    if game == line:
                        break
                else:
                    if os.path.isdir("{0}/{1}/{2}".format(self.path, "games", game)):
                        self.log.record("Found a new game that was not listed!", "warning")
                        results.append(game)
                        self.saveGamesList(game)
                    else:
                        self.log.record("Found a file in the games directory... Going to remove it.", "warning")
                        try:
                            os.remove("{0}/{1}/{2}".format(self.path, "games", game))
                        except:
                            self.log.record("Tried to remove file in games directory... but couldnt.", "error")

            if grannyCounter % 5 == 0:
                self.log.record("Now running a check to make sure that all games here are on the webserver!", "warning")
                _list = []
                for game in self.games_w_folders:
                    self.log.record("Checking '{0}'...".format(game.upper()), "info")
                    result = self.checkUrl(game)
                    if result == True:
                        self.log.record("Found the game... all is good!", "info")
                        pass
                    elif result == False:
                        try:
                            host = socket.gethostbyname("www.github.com")
                            s = socket.create_connection((host, 80), 2)
                            self.log.record("Didn't find the game... Removing...", "warning")
                            _list.append(game)
                        except:
                            self.log.record("No internet connection, could not check the Versions!", "warning")
                            pass

                for game in _list:
                    path = "{0}/{1}/{2}".format(self.path, "games", game)
                    shutil.rmtree(path, ignore_errors=True, onerror=None)
                    self.log.record("Removed '{0}'...".format(game.upper()), "info")
                    num = self.games_w_folders.index(game)
                    del self.games_w_folders[num]

        self.log.record("Upping Granny Counter by 1", "info")
        self.upGrannyCounter()

    ## This method is only ever used by the "grannyCheck" function to up the counter.
    ## The counter is used to determine how often it is going to run through and check
    ## the validity of the games that are installed.
    #----------------------------------------------------------------------
    def upGrannyCounter(self):
        global grannyCounter
        grannyCounter = grannyCounter + 1

    ## This is used to re-write the launcher.config file... It is so it can update
    ## the launcher file when needed without tripping out the grannyCheck function.
    #----------------------------------------------------------------------
    def rewrite(self):
        results = []
        try:
            with open("{0}/{1}".format(self.path, "configs/launcher.conf"), 'w') as out:
                for line in configs:
                    results.append('{0}={1}\n'.format(line, configs[line]))
                for _line in results:
                    out.write(_line)
        except:
            self.log.record("Don't know what, but something went wrong...", "error")

    ## This function is used by the developer mode to find the created workspaces...
    ## So then it can load it all into a list and display on-screen.
    #----------------------------------------------------------------------
    def findDevFolders(self):
        self.dev_folders = os.listdir("{0}/{1}".format(self.path, "dev"))
        num = self.dev_folders.index(".DS_Store")
        del self.dev_folders[num]
        self.amountDevFolders = len(self.dev_folders)

    ## This method is used to add new games to the "games.list" file...
    ## It is only ever used if a game is found in the "games" folder... that
    ## looks like a game...
    #----------------------------------------------------------------------
    def saveGamesList(self, game):
        self.log.record("Adding {0} to the games list.".format(game), "info")
        try:
            with open("{0}/{1}".format(self.path, "configs/game.list"), 'a') as out:
                out.write(str(game)+"\n")
        except:
            self.log.record("Could not add game to games list!", "error")
            ## Going to manually make file by 'writing' it to the file...
            try:
                with open("{0}/{1}".format(self.path, "configs/game.list"), 'w') as out:
                    out.write(str(game)+"\n")
            except:
                pass

    ## This is used to generate all the required folders on startup for the
    ## launcher to then use. It runs regarless if it is the first time to run...
    ## As there is no telling if a folder will be deleted at any time by accident.
    #----------------------------------------------------------------------
    def makeFolders(self, path):
        #self.log.record("Making all required folders for the launcher.", "info")
        self.path = path
        folders = ["/games", "/configs", "/temp", "/logs/games", "/logs/launcher", "/dev"]
        for folder in folders:
            path = self.path + folder
            if os.path.exists(path):
                #self.log.record("{0} already exists... moving onto next folder.".format(folder), "info")
                pass
            else:
                #self.log.record("Making {0} folder.".format(folder), "info")
                os.makedirs(path)
        self.folderCheckRun = True

    ## This function is used to update a selcted part of a games config.
    ## It could be any value... as it will search through the file... edit it...
    ## then replace the contents of the file with the newly created config that is in memory.
    # ----------------------------------------------------------------------
    def updateGameConfig(self, code, item, value):
        self.log.record("Asked to update {0}'s config file.".format(code), "info")
        self.log.record("Replacing {0}'s value with '{1}'".format(item, value), "info")
        temp = []
        holder = []
        _string = ""
        with open("{0}/{1}/{2}/config.properties".format(self.path, "games", code), 'r') as _in:
            for line in _in:
                line = line.strip()
                temp.append(line)
        holder.append(temp[0])
        del temp[0]
        holder.append(temp[0])
        del temp[0]
        for entity in temp:
            if _string == "":
                _string += "{0}\n".format(holder[0])
                _string += "{0}\n".format(holder[1])
            _tokens = entity.split("=")
            if _tokens[0] == item:
                _tokens[1] = value
            _string += "{0}={1}\n".format(_tokens[0], _tokens[1])
        with open("{0}/{1}/{2}/config.properties".format(self.path, "games", code), 'w') as out:
            out.write(_string)

    ## This function is used to start the selected game that the user has chosen
    ## in the menu. It also grabs the path of the folder and game that is given
    ## by the "OtherFrame" class.
    #----------------------------------------------------------------------
    def startGame(self, code, path):
        global gameMode
        path = path.strip()
        if os.path.exists(path):
            game = ['java', '-jar']
            game.append(path)
            self.log.record("", "game")
            gameMode = True
            for output_line in self.run_command(list(game)):
                #if "Exception" in output_line or "ERROR":
                #    self.log.record(output_line, "error")
                #else:
                self.log.log(output_line)

        else:
            self.log.record("Path to game is: {0}".format(path), "warning")
            self.log.record("Could not find {0}'s game file!".format(code.upper()), "error")

    ## This function is used to go through all the folders and delete anything
    ## that is related to the game that is provided to the function.
    #----------------------------------------------------------------------
    def deleteGame(self, code):
        self.log.record("Requested to delete {0}".format(code.upper()), "info")
        path = "{0}/{1}/{2}".format(self.path, "games", code)
        if os.path.exists(path):
            self.log.record("Found the folder to delete...", "info")
            try:
                shutil.rmtree(path, ignore_errors=True, onerror=None)
                num = self.games_w_folders.index(code)
                del self.games_w_folders[num]
                self.log.record("'{0}' is now uninstalled!".format(code.upper()), "info")
                return "Done!"
            except:
                self.log.record("Had in issue uninstalling '{0}'".format(code.upper()), "error")
                return "Had a slight issue removing the game!"
                self.grannyCheck()
        else:
            self.log.record("Could not even find '{0}', is it installed?", "error")
            num = self.games_w_folders.index(code)
            del self.games_w_folders[num]
            self.grannyCheck()
            return "Could not find game to delete."

    ## This method here is used to check if there are any new updates avaliable
    ## for the game that is provided to the function.
    #----------------------------------------------------------------------
    def checkGameUpdates(self, code):
        self.log.record("Looking for new game version!", "info")

        ## Loading the needed details...
        try:
            self.VUrl = self.gameConfigs['Version_Url'].strip()
            self.AUpdate = self.gameConfigs['Auto_Update'].strip()
        except:
            self.log.record("Had an issue with loading the required data to check for game updates...", "error")
            self.defaultConfig(code)
            self.VUrl = "Default"
            self.AUpdate = "True"
            self.Fversions = "Default"


        ## Checking
        if self.VUrl == "Default":
            self.VUrl = "{0}Games/{1}/version".format("https://raw.githubusercontent.com/TheNightForum/TheNightForum.github.io/master/", code)
        self.log.record("Checking '{0}' for new version.".format(str(self.VUrl)), "info")

        ## Getting online version num
        try:
            self.onlineGameVersion = urllib2.urlopen(str(self.VUrl)).read().strip()
        except:
            self.log.record("Could not find online version of '{0}'".format(code.upper()), "warning")
            self.grannyCounter = 5

        ## Comparing the versions...
        try:
            if self.gameConfigs['Latest_Version'].strip() > self.onlineGameVersion:
                # TODO: Something is wrong, we need to fix this, lets self-modify the games config file...
                self.log.record("Online version number of '{0}' is less than local version".format(code.upper()), "warning")
                return True
            elif self.gameConfigs['Latest_Version'].strip() < self.onlineGameVersion:
                self.log.record("New version of '{0}' found.".format(code.upper()), "warning")
                return True
            else:
                self.log.record("Could not find an update for '{0}'.".format(code.upper()), "info")
                return False
        except:
            try:
                host = socket.gethostbyname("www.github.com")
                s = socket.create_connection((host, 80), 2)
                self.log.record("Had an issue with comparing game versions...", "error")
                return False
            except:
                self.log.record("No internet connection, could not check the Versions!", "warning")
                return False

    ## This function is used to create the config file for any games that do not
    ## already have a config file. It essentially puts the default information
    ## into the file for the launcher to read.
    #----------------------------------------------------------------------
    def defaultConfig(self, code):
        self.log.record("Making default config for '{0}'".format(code.upper()), "info")
        path = "{0}/{1}/{2}/{3}".format(self.path, "games", code, "config.properties")
        if os.path.exists(path):
            os.remove(path)
        results = []
        with open(path, 'w') as out:
            for line in self.defaultConfigFile:
                results.append('{0}={1}\n'.format(line, self.defaultConfigFile[line]))
            results.insert(0,"#Please do not manually edit this file!\n")
            results.append('Latest_Version={0}\n'.format(self.versionGrabber(code, "version")))
            for _line in results:
                out.write(_line)

    ## This function is used to download the updates for the game in question.
    ## It just downloads the new file, unzips it... and changes the "Latest_Version"
    ## to the current game version just downloaded.
    # ----------------------------------------------------------------------
    def downloadUpdate(self, code):
        path = "{0}/{1}/{2}".format(self.path, "games", code)
        if configs['KeepVersions'] == "1":
            print("")
        else:
            print("")

    ## This function is used to backup all the games, files... on a regular
    ## occurance to the "backup" folder.
    # ----------------------------------------------------------------------
    def backupFiles(self, code):
        self.log.record("Starting Backup for '{0}'".format(code.upper()), "info")
        path = "{0}/{1}/{2}/{3}".format(self.path, "games", code, "DATA")
        backupDir = "{0}/{1}/{2}/{3}".format(self.path, "backups", code, "DATA")
        if os.path.exists(backupDir):
            ## Delete the folder...
            shutil.rmtree(backupDir)
        shutil.copytree(path, backupDir)

    ## This is used to load the config of all the game that is being played.
    ## It does this so it can check for updates and stuff.
    #----------------------------------------------------------------------
    def loadGame(self, code):
        self.log.record("Loading everything for the game ({0})".format(code.upper()), "info")
        path = "{0}/{1}/{2}/{3}".format(self.path, "games", code, "config.properties")
        _string = ""
        if os.path.exists(path):
            self.log.record("Found {0}'s' properties file for the launcher.".format(code.upper()), "info")
            holder = {}
            with open(path, 'r') as _in:
                for line in _in:
                    if line.startswith("#"):
                        pass
                    else:
                        line = line.strip("\n")
                        (key, val) = line.split("=")
                        holder[str(key)] = val
            for x in holder:
                x_old = x
                c = x[0]
                x = c.upper()+x[1:]
                self.gameConfigs[x] = holder[x_old]
        else:
            self.log.record("For some reason, this game does not have a config file!", "warning")

    ## This function does as it says. Checks for launcher updates...
    #----------------------------------------------------------------------
    def checkLauncherUpdates(self, local):
        global LauncherNeedsUpdate
        self.log.record("Checking Launcher for updates!", "info")
        try:
            data = str(urllib2.urlopen("https://raw.githubusercontent.com/TheNightForum/TheNightForum.github.io/master/VERSION").read().strip("\n"))
        except:
            self.log.record("Could not grab the onlive version at current time. Please try again latter. Maybe Check internet", "warning")
            data = local
        global OnlineVersion
        OnlineVersion = data
        self.onlineVersion = float(OnlineVersion)
        self.localVersion = float(local)
        if self.onlineVersion > self.localVersion:
            self.log.record("There is a new version avaliable!", "info")
            LauncherNeedsUpdate = True
            return True
        elif self.localVersion > self.onlineVersion:
            self.log.record("Local Version number is bigger than online... Going to do a fresh reinstall...", "warning")
            LauncherNeedsUpdate = True
            return True
        else:
            self.log.record("No new updates found for the Launcher", "info")
            return False

    ## this function is used to actually launch the game from the command line
    ## and pipe the messages back to the logger. For monitoring.
    #----------------------------------------------------------------------
    def run_command(self, command):
        p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
        return iter(p.stdout.readline, b'')

    ## This method is used to modify its own code to update it to the latest
    ## version online, without stopping the launcher. It is efficent in the
    ## way it loads everything to memory before it re-writes it...
    #----------------------------------------------------------------------
    def selfModify(self, tochange, changeto, mode):
        self.log.record("Requested to self Modify file!", "info")
        if mode == 1:
            self.log.record("Self Modifying own file!", "warning")
            data = urllib2.urlopen("{0}{1}.py".format("https://raw.githubusercontent.com/TheNightForum/TheNightForum.github.io/master/Launcher/", OnlineVersion)).read()
            with open("main.py", 'w') as out:
                for line in data:
                    out.write(line)
            self.log.record("Update complete.", "info")
        elif mode == 0:
            self.log.record("Requested to replace the value of '{0}' to '{1}'".format(tochange, changeto), "warning")
            res = []
            with open("main.py", 'r') as _in:
                self.log.record("Searching for '{0}' in own file...".format(tochange), "info")
                for line in _in:
                    if line.startswith('        ' + str(tochange)):
                        line.strip("\n")
                        tokens = line.split(" = ")
                        res = tokens[1][1:-2]
                        self.log.record("Found!", "info")
                        break
            with open("main.py") as f:
                self.log.record("Replacing with '{0}'".format(changeto), "info")
                newText = f.read().replace(res, changeto, 1)

            with open("main.py", 'w') as out:
                self.log.record("Starting to write change to own file!", "warning")
                out.write(newText)
            self.log.record("Self-Modification Complete", "info")
        elif mode == 2:
            """ This mode is for self modifying game files... (eg. Config files)"""
        elif mode == 3:
            """ This mode is for editing the config file one line at a time..."""
            res = []
            path = "{0}/{1}/{2}".format(self.path, "configs", "launcher.conf")
            with open(path, 'r') as _in:
                self.log.record("Searching for '{0}' in launcher configs...", "info")
                for line in _in:
                    if line.startswith(str(tochange)):
                        line.strip("\n")
                        tokens = line.split("=")
                        res = tokens[1][1:-2]
                        self.log.record("Found!", "info")
                        break
            with open(path) as f:
                self.log.record("Replacing with '{0}'".format(str(changeto)), "info")
                newText = f.read().replace(res, changeto, 1)

            with open(path, 'w') as out:
                self.log.record("Starting to write changes to launcher.conf", "warning")
                out.write(newText)
            ## Also manually adding it to the 'loaded' config, so it wont trip the Granny Checker.
            configs[str(tochange)] = str(changeto)
            self.log.record("Modification Complete", "info")


########################################################################
class Logger():
    def __init__(self):
        global configs
        """
        Logging levels...
        0 = Errors
        1 = Warnings
        2 = Info
        3 = Debug
        4 = Errors and Warnings
        5 = Warnings and Info
        6 = Game info only.
        7 = All
        """
        global gameMode
        self.info       = "  INFO        |  "
        self.warning    = "  WARNING     |  "
        self.error      = "  ERROR!      |  "
        self.debug      = "  -DEBUG-     |  "
        self.empty      = "              |  "
        self.last       = ""
        self.path       = "{0}/{1}".format(expanduser("~"), "TNFLauncher")
        self.gameMode   = gameMode
        self.saved      = False
        self.lvl        = ""
        self.check()

        if self.gameMode == True:
            self.path = "{0}/logs/games".format(self.path)
        else:
            self.path = "{0}/logs/launcher".format(self.path)

    ## This method is used to check if there any log files in the system
    ## from the last time the user used it...
    #----------------------------------------------------------------------
    def check(self):
        if os.path.exists("{0}/{1}".format(self.path, "error.log")):
            with open("{0}/{1}".format(self.path, "error.log"), "w") as out:
                out.write("BEGGING!")

    ## This function is used to load the logging level from the launcher configs.
    #----------------------------------------------------------------------
    def load(self):
        self.lvl        = configs['Logging']
        self.record("Loaded the config for logging.", "info")

    ## This is the actual function that prints everything to the console
    ## and monitors it all for errors.
    #----------------------------------------------------------------------
    def log(self, _string):
        global keeper
        keeper.append("{0}\n".format(_string))
        print(_string)
        with open("{0}/{1}".format(self.path, "error.log"), 'a') as out:
            out.write("{0}\n".format(_string))

    ## This is the function that generates the "Error Frame" for use by the user.
    #----------------------------------------------------------------------
    def errorFrame(self):
        global errorFrameRunning
        if errorFrameRunning == 0:
            frame = OtherFrame(None, "ERROR!", -3, "", "no")
            errorFrameRunning += 1
        else:
            pass

    ## This is the method that is refered to by all the other classes to log.
    ## This logs everything and displays everything accordingly... due to the
    #----------------------------------------------------------------------
    def record(self, msg, Status):
        Status = Status.lower()
        if Status == "start":
            self.log(self.empty + "*"*22)
            self.log(self.empty + "Begging of TNF Laucnher.")
            self.log(self.empty + "*"*22)
            self.log(self.empty)
        elif Status == "game":
            self.log(self.empty)
            self.log(self.empty)
            self.log(self.empty + "*"*22)
            self.log(self.empty + "Begging of Game.")
            self.log(self.empty + "*"*22)
            self.log(self.empty)
            self.log("_"*66)
        elif Status == "info":
            if int(configs['Logging']) == 7 or int(configs['Logging']) == 2 or int(configs['Logging']) == 5:
                if self.last == "info":
                    self.log("{0}{1}".format(self.empty, msg))
                else:
                    self.last = "info"
                    self.log("{0}{1}".format(self.info, msg))
            else:
                pass
        elif Status == "error":
            if int(configs['Logging']) == 7 or int(configs['Logging']) == 0 or int(configs['Logging']) == 4:
                self.last = "error"
                self.log("{0}{1}".format(self.error, msg))
                self.errorFrame()

            else:
                pass
        elif Status == "warning":
            if int(configs['Logging']) == 5 or int(configs['Logging']) == 7 or int(configs['Logging']) == 1 or int(configs['Logging']) == 4:
                self.last = "warning"
                self.log("{0}{1}".format(self.warning, msg))
            else:
                pass
        elif Status == "debug":
            if int(configs['Logging']) == 7 or int(configs['Logging']) == 3:
                self.last = "debug"
                self.log("{0}{1}".format(self.debug, msg))
            else:
                pass
        elif Status == "gameLog":
            if int(configs['Logging']) == 7 or int(configs['Logging']) == 6:
                self.last = "game"
                self.log(str(msg))


#----------------------------------------------------------------------
if __name__ == "__main__":
    ## THis is starting the Logger...
    log = Logger()
    ## This is loading the "Start" message...
    log.record("", "start")
    ## This is starting the tkinter frame...
    root = Tk.Tk()
    ## Now editing the frame...
    root.geometry("800x600")
    root.borderwidth = 0
    root.highlightthickness = 0
    ## loading the variable "app" with the Start class...
    app = Start(root)
    ## running the app....
    root.mainloop()
