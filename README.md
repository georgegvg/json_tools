# json_tools

Search for a regular expressions in Json or Yaml files

## Install
pip3 install pyyaml

sudo python3 setup.py install

## Usage

json_tools FILE_OR_DIR_PATH REG_EXP

if FILE_OR_DIR_PATH is a directory, all *.json, *.yaml and *.yml files in this directory and its subdirectories
will be searched.

## Output

The search is structural, the output matches both keys and values, and returns the matched key or value, as well as the path to this key.

### For Example

```
json_tools example.json ".*arkup*.| *.itle.*|.*ML.*"

----------------------------------------
example.json
Matched Keys
----------------------------------------
glossary.title
glossary.GlossDiv.title
----------------------------------------
Matched Values (Path: value)
----------------------------------------
glossary.GlossDiv.GlossList.GlossEntry.Acronym: "SGML"
glossary.GlossDiv.GlossList.GlossEntry.GlossDef.GlossSeeAlso[0]: "GML"
glossary.GlossDiv.GlossList.GlossEntry.GlossDef.GlossSeeAlso[1]: "XML"
glossary.GlossDiv.GlossList.GlossEntry.GlossDef.para: "A meta-markup language, used to create markup languages such as DocBook."
glossary.GlossDiv.GlossList.GlossEntry.GlossSee: "markup"
glossary.GlossDiv.GlossList.GlossEntry.GlossTerm: "Standard Generalized Markup Language"
glossary.GlossDiv.GlossList.GlossEntry.ID[0]: "SGML"
glossary.GlossDiv.GlossList.GlossEntry.ID[1]: "SGML2"
glossary.GlossDiv.GlossList.GlossEntry.SortAs: "SGML"
----------------------------------------
```

