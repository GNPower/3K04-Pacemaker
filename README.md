<img src="DCM/flaskapp/static/logo.png" height="120" width="120">

# 3k04 Pacemaker Project
This is the Github repository for our 3K04 Pacemaker Group

### Getting Started
- Clone this repository to your working environment on your computer
	- If you are using command line copy this text:  
	git clone https://github.com/GNPower/3K04-Pacemaker.git  
	- If you are using an IDE, you can google how to clone a repo using that IDE
- Checkout your branch to begin development
	- If you are using command line copy this text:  
	git fetch origin  
	git checkout -b dev origin/{YOUR_NAME_HERE}  
	- You are now setup to develop on your branch (which is called 'dev' on your local machine)
	- If you are using an IDE, you can google how to checkout a branch using that IDE
- Take a look through the files to get a feel for how everyhting is set up
	- ~/3K04-Pacemaker is the base directory for this project
	- ~/3K04-Pacemaker/DCM is the base directory for the GUI and other DCM stuff
	- ~/3K04-Pacemaker/Simulink is the base directory for all Matlab Simulink models
- Each base directory contains a .gitignore
	- The base gitignore by default ignores all project and build files from some common IDEs like Visual Studio (Code), Eclipse, IntelliJ, NetBeans
	- If you are using a different IDE please add its .gitignore configuration to the base .gitignore
	- If you wan to ignore any additional files, add that file to the closest .gitignore (i.e. if you are ignoring something in "3K04-Pacemaker/DCM"  add it to the  "3K04-Pacemaker/DMC/.gitignore"  and not the  "3K04-Pacemaker/.gitignore")
    
# Project Description