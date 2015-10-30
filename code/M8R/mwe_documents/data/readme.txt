This is the location of the experiment code.

First you must run the experiment using:

scons

You can "lock" or save the results using:

scons lock

This allows you to use the figures generated from a Result() call in a document

Next you need to create a SConstruct file in a folder where your document is

Then you need to make a .tex file that contains paper content

Then you MUST create a link within the folder containing the .tex file.
The link must link to the folder where the experiment was conducted.
In this case, that folder is this folder.

ln -s ../data/ .
