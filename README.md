# Jarvis backend
backend part of wildberries business analytics system 

## Build
to build the last realesed version (or version, that you set in your builder/build.properties) you need to run in terminal:


python builder/build.py

## Publishing
for publishing realese version you need to check version in build.properties and run:
python builder/publish.py 

or

python builder/publish_with_comment.py "Your comment" 

#### Custom (test) versions
if you need to build some custom version you need to set version of your custom component from as example "0.0.1" -> "0.0.1a"
and rebuild it in project which use it
