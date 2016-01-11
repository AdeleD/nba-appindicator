# NBA AppIndicator for Ubuntu Unity

**An Application Indicator for Ubuntu to display NBA games results from last night.**

## Install

Open a terminal and run this command into the directory of your choice:

```
$ git clone git@github.com:AdeleD/nba-appindicator.git
```

Then, inside the nba-appindicator folder, run:

```
$ cd nba-appindicator
$ make
```

## To launch NBA AppIndicator at startup

Go to Ubuntu "Startup Applications" menu.

Click the "Add" button. Enter a name and into the "Command" input field, the path to the installation folder and the `bin/nbaindicator` file.

Example:

```
Command: /home/adele/nba-appindicator/bin/nbaindicator
```

Click the "Save" button.

That's it!
