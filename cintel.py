# Copyright (c) 2014 Jiri Ohnheiser

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import sublime
import sublime_plugin


import os
import re
import subprocess
import traceback
import time


from cintel.all_views_autocomplete import *

def get_settings():
    """Load settings.

    :returns: dictionary containing settings
    """
    return sublime.load_settings("cintel.sublime-settings")


def get_setting(key, view, default=None):
    """Load individual setting.

    :param key: setting key to get value for
    :param default: default value to return if no value found

    :returns: value for ``key`` if ``key`` exists, else ``default``
    """


    if view != None:
        if view.settings().get('cintel') != None:
            if key in view.settings().get('cintel'):
                return view.settings().get('cintel')[key];    

    return get_settings().get(key, default)

setting = get_setting








"""Autocomplete commands"""

# import smartcomplete

class smartItem():
    name = ""
    filename = ""
    line = 0
    text = ""
    kind = ""
    inherits = []
    arguments = []
    inClass = ""
    inEnum = ""
    retInstanceOf = ""
    retPointer = 0 #0-Instance 1-Pointer
    isContainerWithType = ""
    template = ""
    templatePointer = 0 #0-Instance 1-Pointer
    indexInFile = 0
    access = 0  #0-public, 1-protected, 2-private
    functionParameters = []

    isGlobal = False



    def __init__(self):
        self.inherits = []
        self.arguments = []
        self.functionParameters = []


    def printf(self):
        print("name          :", self.name)
        print("filename      :", self.filename)
        print("line          :", self.line)
        print("text          :", self.text)
        print("kind          :", self.kind)
        print("inherits      :", str(self.inherits))
        print("arguments     :", str(self.arguments))
        print("inClass       :", self.inClass)
        print("inEnum        :", self.inEnum)
        print("instanceOf    :", self.retInstanceOf + " /p=" + str(self.retPointer))
        print("template      :", self.template + " /p=" + str(self.templatePointer))
        print("isContainer   :", self.isContainerWithType)
        print("indexInFile   :", self.indexInFile)
        print("access        :", self.access)
        print("Num of f-param:", str(len(self.functionParameters)))



class SmartAutocompleteCtags():
    items = []
    hashed = {}
    byFile = {}
    numberOfItemsInFile = {}
    byParentClass = {}
    onlyClasses = {}
    globalVariables = {}
    initialized = False
    rebuilding = False
    timeOfLastRefresh = 0

    internalLibNames = ["stl_containers"]

    listOfBasicTypes = set(["void", "char", "bool", "boolean","short", "short int", "short int", "signed short", 
        "signed short int", "unsigned short", "unsigned short int", "unsigned short int", 
        "int", "int", "signed", "signed int", "unsigned", "unsigned int", 
        "unsigned int", "long", "long int", "long int", "signed long", 
        "signed long int", "unsigned long", "unsigned long int", "unsigned long int", 
        "long long", "long long int ", "long long int", "signed long long", "signed long long int", 
        "unsigned long long", "unsigned long long int ", "unsigned long long int", "float", "double", "long double"])
    # listOfBasicTypes = set(["void"])
    
    def __init__(self):
        self.items = []

    def clearMemory(self):
        self.items = []
        self.hashed = {}
        byFile = {}
        self.numberOfItemsInFile = {}
        self.byFile = {}
        self.byParentClass = {}
        self.globalVariables = {}
        self.initialized = False
        self.onlyClasses = {}
    
    def init(self, view, pathToTagsToLoad):


        try:
            fileHandle = open(pathToTagsToLoad)
        except:
            print ("CINTEL: cannot open: "+pathToTagsToLoad)
            return False





        for line in fileHandle:
            #clean data
            if line[0] == '!':
                continue
            try:
                item = self.getItemFromLine(line)
            except:
                print ("CINTEL ERROR: Problem with parsing line\n" + line + "\n" + traceback.format_exc() )
                continue
            
            #-----------------------
            #add them to caches
            self.items.append(item)

            #global
            if item.kind == "variable" or item.isGlobal == True:
                self.globalVariables[item.name] = item

            if item.kind == "class" or item.kind == "struct":
                self.onlyClasses[item.name] = item

            #class members
            if item.inClass != "" and item.kind != "function":
                if item.inClass in self.byParentClass:
                  # self.byParentClass[item.inClass].append(item);
                  self.byParentClass[item.inClass][item.name]  = item;
                else:
                  self.byParentClass[item.inClass]  = {};
                  self.byParentClass[item.inClass][item.name]  = item;

            #class members, special case for functions, where they are only
            #implemented in class - therefore function = prototype
            if item.inClass != "" and item.kind == "function":
                if item.inClass in self.byParentClass:
                    if not (item.name in self.byParentClass[item.inClass]):
                        self.byParentClass[item.inClass][item.name]  = item;
                else:
                  self.byParentClass[item.inClass]  = {};
                  self.byParentClass[item.inClass][item.name]  = item;


            #hashed by name
            if item.name in self.hashed:
              self.hashed[item.name].append(item);
            else:
              self.hashed[item.name]  = [item];


            #by filename - for searching functions
            if item.filename in self.byFile:
              self.byFile[item.filename].append( item )
              self.numberOfItemsInFile[item.filename] = self.numberOfItemsInFile[item.filename] + 1
            else:
              self.byFile[item.filename]  = [ item ]
              self.numberOfItemsInFile[item.filename] = 1

            item.indexInFile = self.numberOfItemsInFile[item.filename] - 1


        self.initialized = True
        # i = 0
        # for item in self.items:
        #     i = i + 1
        #     print ("ID: ", i)
        #     item.printf()

        print("------------DONE------------")
        print("- items:   ", len(self.items))
        print("- files:   ", len(self.byFile))
        print("- classes: ", len(self.onlyClasses))
        # print("----------------------------")
        # self.hashed["CQueue"][0].printf()
        # print("------------")
        # self.hashed["syn"][1].printf()

        # print ( self.byFile.keys() )
        # print (self.byFile["test.cc"])

        fileHandle.close()
        return True

    # def deleteTabs(self, line):
    #     start = line.find("/^")
    #     end   = line.find("$/;")

    #     print ("deleteTabs = " + str(start) +","+ str(end))
    #     for x in range(start,end):
    #         print("X = " + str(x) + " = '" + line[x] + "'")
    #         if line[x] == '\t':
    #             line[x:x+1] = ' '





    def getItemFromLine(self, line):
        # print ("\n1:" + line)
        line = re.sub(r"(/\^.*?)\t\t*(.*\$/;\")", "\\1 \\2", line, count=5)
        line = re.sub("(/\^.*?)\t\t*(.*\$/;\")", "\\1 \\2", line, count=5)
        line = re.sub("(/\^.*?)\t\t*(.*\$/;\")", "\\1 \\2", line, count=5)
        line = re.sub("(/\^.*?)\t\t*(.*\$/;\")", "\\1 \\2", line, count=5)
        # print ("2:" + line)
        # self.deleteTabs(line)
        line = re.sub("/\^\s*", "", line)
        line = re.sub("\$/;\"", "", line)



        splited = line.split('\t')
        item = smartItem()

        # print ("3:" + line)
        #load basic stuff
        item.name = splited[0]
        item.filename = splited[1]
        item.text = re.sub(r"\\/", "/", splited[2])
        text = re.sub( r"//.*", "", item.text)
        text = text.strip()
        item.kind = splited[3]
        item.line = int( splited[4].strip().replace("line:", "") )

                  
        
        #search for special properties
        if len(splited) > 5:
            if splited[5][0:4] == "inherits"[0:4]:
                item.inherits.append( splited[5].strip().replace("inherits:", "") )
                # print (item.name+ " - "+ item.inherits[0])
            if splited[5][0:4] == "class"[0:4]:
                item.inClass = splited[5].strip().replace("class:", "")
                # print (item.name+ " - "+ item.inClass)
            if splited[5][0:4] == "struct"[0:4]:
                item.inClass = splited[5].strip().replace("struct:", "")
            if splited[5][0:4] == "union"[0:4]:
                item.inClass = splited[5].strip().replace("union:", "").split("::")[0]
                # print (item.name+ " - "+ item.inClass)
            if splited[5][0:4] == "enum"[0:4]:
                item.inenum = splited[5].strip().replace("enum:", "")
                # print (item.name+ " - "+ item.inenum)
            
            if len(splited) > 6:
                if splited[5][0:4] == "access"[0:4]:
                    tmpaccess = splited[5].strip().replace("access:", "")
                    if tmpaccess == "private":
                        item.access = 2
                    elif tmpaccess == "protected":
                        item.access = 1


        #Template class
        if item.kind == "class" or item.kind == "struct":
            item.retInstanceOf = item.name
            temp = text.strip()
            if temp.find("<") != -1:
                tempInside = re.sub(".*<[\s]*[^\s]*[\s]*", "", temp)
                tempInside = re.sub(">.*", "", tempInside)
                item.template = tempInside

        

        #searching for retInstanceOf
        if item.kind == "member" or item.kind == "variable" or item.kind == "local":
            temp = re.sub("=.*", "", text)
            temp = temp.strip()
            temp = temp.strip(";")
            temp = temp.strip()
            if temp.find("<") != -1:
                #templates, thing will go ugly
                tempInside = re.sub(".*<", "", temp)
                tempInside = re.sub(">.*", "", tempInside)

                #temporary solution, will take only last one
                tempInside = tempInside.split(",")[-1]

                item.templatePointer = self.getPointerOrNot(tempInside)
                tempInside = re.sub("&|\*", "", tempInside)
                tempInside = tempInside.strip()
                
                temp = re.sub("[\s]*<.*", "", temp)
                temp = re.sub(".*?::", "", temp)

                # print ("TEM: ", temp  + " = " + tempInside)
                item.template = tempInside
                item.retInstanceOf = temp

                pass
            else:
                if temp.find("[") != -1:
                    item.isContainerWithType = "array"
                    temp = temp.replace("\[.*\]", "")
                item.retPointer = self.getPointerOrNot(temp)
                temp = re.sub("&|\*", "", temp)
                temp = temp.strip()


                tmpSplited = temp.split()
                item.retInstanceOf = tmpSplited[0]
                #print ("VAR: ", tmpSplited)


        if item.kind == "function" or item.kind == "prototype":
            # print("FUN1: "+ item.text)
            temp = re.sub("[^\s]*[\s]*\(.*", "", text)
            temp = re.sub(".*?[^:]::", "",  temp)
            temp = re.sub("static", "",  temp)
            temp = temp.strip()

            item.retPointer = self.getPointerOrNot(temp)
            temp = re.sub("&|\*", "", temp)
            temp = temp.strip()


            item.retInstanceOf = temp
            # print("FUN2: "+ temp + "\n")

            if item.inClass == "":
                item.isGlobal = True;
            pass

        #create parameters items of function
        if item.kind == "function":
            temp = re.sub(".*\(", "", text)
            temp = re.sub("\).*", "",  temp)
            params = temp.split(",")
            # print("FuncP: "+item.name+' = ' +str(params))
            for param in params:
                if param == '':
                    continue
                aaa = self.getTemplateFromText(param)
                if aaa[0] == '':
                    continue
                parItem = smartItem()
                parItem.retInstanceOf = aaa[0]
                parItem.name = aaa[1]
                parItem.retPointer = aaa[2]
                parItem.kind = "local"
                parItem.line = item.line
                parItem.filename = item.filename
                item.functionParameters.append(parItem)



        return item
        #TODO parse function parameters
        #if item.kind == "function":
        #   temp = item.text.strip()
        #   temp = temp.strip(";")
        #   temp = temp.strip()
        #
        #   self.arguments = ???


    def getTemplateFromText(self, text):
        temp = re.sub("=.*", "", text)
        temp = temp.strip()
        isPointer = self.getPointerOrNot(temp)
        temp = re.sub("&|\*", "", temp)
        

        splited = temp.split()
        # print (str(splited))

        if len(splited) < 2:
            return ["", "", 0]

        if len(splited) > 2:
           splited[0] = " ".join(splited[0:-1])
           # print("XA:" + text)
           # print("XB:" + splited[0])

        # print ("TEM: ", text  + " = " + tempInside)
        return [splited[0], splited[-1], isPointer]

    def getPointerOrNot(self, text):
        if text.find("*") != -1:
            return 1;
        return 0


    def getSmartAutocomplete(self, view, prefix, locations):
        if self.initialized == False:
            self.rebuild(view)
        if self.initialized == False:
            return []

        lineForCompletion = ""
        ret = []

        rowcol = view.rowcol(view.sel()[0].begin())

        lineForCompletion = view.substr(view.line(view.sel()[0])) [0:rowcol[1]]

        #todo in while
        lineForCompletion = re.sub('\([^\(]*\)', '()', lineForCompletion)
        lineForCompletion = re.sub('\([^\(]*\)', '()', lineForCompletion)
        lineForCompletion = re.sub('\([^\(]*\)', '()', lineForCompletion)
        lineForCompletion = re.sub('\([^\(]*\)', '()', lineForCompletion)

        lineForCompletion = lineForCompletion.split(",")[-1]
        lineForCompletion = lineForCompletion.split(";")[-1]
        lineForCompletion = lineForCompletion.split("<")[-1]
        lineForCompletion = lineForCompletion.split("=")[-1]
        lineForCompletion = re.sub('^.*-[^>]', '', lineForCompletion)
        lineForCompletion = re.sub('^.*[^-]>', '', lineForCompletion)

        lineForCompletion = re.sub('^.*return', '', lineForCompletion)
        while lineForCompletion.count ('(') > lineForCompletion.count (')'):
            lineForCompletion = re.sub('^.*?\(', '', lineForCompletion)
        lineForCompletion = lineForCompletion.strip()

        #default value
        queryType = 0
        addThis = False

        if setting('inClass_autocomplete', view):
            queryType = 2

        if len(lineForCompletion) > 0:
            if lineForCompletion[-1] == "." and len(lineForCompletion) > 1:
                lineForCompletion = lineForCompletion[:-1]
                queryType = 1
            if lineForCompletion[-2:] == "->" and len(lineForCompletion) > 2:
                lineForCompletion = lineForCompletion[:-2]
                queryType = 1
            if re.search('#include[\s]*"|<', lineForCompletion) is not None:
                queryType = 3

        #if nothing fits, cancel
        if queryType == 0:
            return []

        #Cleanup the arrays
        lineForCompletion = re.sub('\[.*?\]', '.operator []', lineForCompletion)

        #divide into items
        items1 = re.split("[.]|->|", lineForCompletion)
        items = []
        for i in items1:
            i = re.sub('\(.*\)', '', i)
            items.append(i)
            #TODO dont delete typecast

        filename = view.file_name();
        folderpath = view.window().folders()[0]

        folder = setting('default_path', view)
        folder = re.sub("^[.]/?", "/", folder)
        folder = re.sub("[/]*?$", "/", folder)
        folder = re.sub("^/?", "/", folder)
        filename = filename.replace(folderpath, '').replace(folder, "").strip("/")
        print ("CString: " + lineForCompletion)
        # print ("rowcol: " + str(rowcol[0]))
        print ("items: " + str(items) )
        # print ("file_name(): " + filename )
        # print ("folder_name(): " + view.window().folders()[0] )
        print ("queryType: " + str(queryType) )

        lastItem = None
        firstParrent = None
        #dry autocomplete
        if queryType == 2:
            lastItem = self.SearchForParrentFunction(filename, rowcol[0])
            if lastItem != None:
                if lastItem.inClass in self.onlyClasses:
                    lastItem = self.onlyClasses[lastItem.inClass]
                else:
                    lastItem = None

        #search through line
        if queryType == 1:
            parrentFunction = self.SearchForParrentFunction(filename, rowcol[0])
            firstParrent = self.searchForLocalVariable(items[0], filename, rowcol[0])

            #try this pointer
            if items[0] == "this":
                lastItem = self.SearchForParrentFunction(filename, rowcol[0])
                if lastItem.inClass in self.onlyClasses:
                    lastItem = self.onlyClasses[lastItem.inClass]
                else:
                    lastItem = None

            #Search in Function parameters
            if firstParrent == None:
                if parrentFunction != None:
                    print ("Searching in Function parameters of: " + parrentFunction.name)
                    for par in parrentFunction.functionParameters:
                        print ("  +- " + par.name)
                        if par.name == items[0]:
                            firstParrent = par
            
            #if nothing found, lets look in class (and inherited classes)
            if firstParrent == None:
                if parrentFunction != None:
                    if parrentFunction.inClass != "":
                        firstParrent = self.recursiveSearchForWordInClasses(items[0], parrentFunction.inClass)
                        pass

            #Try GLOBAL
            if firstParrent == None:
                if items[0] in self.globalVariables:
                    firstParrent = self.globalVariables[items[0]]

            #Recursive search through line for completion to the last item
            if firstParrent != None:
                print("---------------Found firstParrent = " + firstParrent.name)
                # firstParrent.printf()
                if parrentFunction != None:
                    print("Fun txt: ", parrentFunction.text)
                    print("Fun inh: ", parrentFunction.inClass)

                lastItem = self.recursiveSearchOptions(items[1:], firstParrent)

        #Gather all possibilities for autocomplete
        if ( queryType == 1 or  queryType == 2 )and lastItem != None:
            print("---------------LAST ITEM")
            lastItem.printf()
            print("---------------Results")
            ret = []

            listOfInheritedObjects = self.getAllInheritedClasses(lastItem.retInstanceOf)
            print ("Iherited are: ", str(listOfInheritedObjects))

            for oneClass in listOfInheritedObjects:
                print (" *CLASS: " + oneClass )
                if oneClass in self.byParentClass:
                    ret.append(("---" + oneClass + "---", ""))
                    for i in self.byParentClass[oneClass].values():
                        name = i.name
                        print("+- ", i.text + " :" + i.retInstanceOf + " /" + str(i.retPointer))
                        if i.isContainerWithType == "array":
                            name = name +"[]"
                        if i.kind == "prototype" or i.kind == "function":
                            name = name + "()"

                        # if i.retInstanceOf in self.listOfBasicTypes:
                            # name = name + ";"
                        elif i.retPointer == 1 or self.testTemplatedForPointer(i, lastItem):
                            name = name + "->"
                        else:
                            name = name + "."

                        if addThis == True:
                            ret.append( ( i.text, "his->"+name) )
                            # ret.append( ( i.text, name) )
                        else:
                            ret.append( ( i.text, name) )
        elif queryType == 3:
            print("----INCLUDE----")
            ret = []

            for fname in sorted(self.byFile.keys()):
                if fname.endswith(".h") or fname.endswith(".hpp"):
                    ret.append((fname, fname))
        else:
            if lastItem == None:
                print("------NONE-----")


        if setting('inClass_add_sublime_tags', view):
            if queryType == 2:
                print("--------------------------xxx--------------------------")
                if setting('inClass_add_sublime_tags_all_opened', view):
                    allauto = AllAutocomplete.getAutocomplete( view, prefix, locations, True)
                else:
                    allauto = AllAutocomplete.getAutocomplete( view, prefix, locations, False)
                ret.append(("---Others---", ""))
                ret = ret + allauto
                print (allauto)
        rret = (ret, sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)
        return rret
        # return ret


    def getAllInheritedClasses(self, firstClassName):
        print("getAllInheritedClasses: " + firstClassName)
        ret = [firstClassName]
        if firstClassName in self.onlyClasses:
            for x in self.onlyClasses[firstClassName].inherits:
                ret = ret + self.getAllInheritedClasses(x)


        return ret


    def testTemplatedForPointer(self, item, parrent):
        if parrent.templatePointer != 1:
            return False
        if self.hashed[parrent.retInstanceOf][0].template == item.retInstanceOf:
            # print ("    MATCH")
            return True
        else:
            # print ("    NO")
            return False


    def recursiveSearchOptions(self, items, parrent):
        print("recursiveSearchOptions in Class" + str(items) + " parent=" + parrent.text)
        if len(items) < 1:
            return parrent

        if parrent.retInstanceOf in self.onlyClasses:
            if items[0] in self.byParentClass[parrent.retInstanceOf]:
                print ("  +-Item: " + self.byParentClass[parrent.retInstanceOf][items[0]].text)

                print ("    return=" + self.byParentClass[parrent.retInstanceOf][items[0]].retInstanceOf )
                print ("    templa=" + self.onlyClasses[parrent.retInstanceOf].template )
                print ("    inTemp=" + parrent.template )


                if self.onlyClasses[parrent.retInstanceOf].template == self.byParentClass[parrent.retInstanceOf][items[0]].retInstanceOf and parrent.template in self.onlyClasses:
                    print ("    MATCH = " + self.onlyClasses[parrent.template].text)
                    return self.recursiveSearchOptions(items[1:], self.onlyClasses[parrent.template])
                print ("    NO")
                
                return self.recursiveSearchOptions(items[1:], self.byParentClass[parrent.retInstanceOf][items[0]])
            else:
                print("  +-Trying inherited of:" + parrent.retInstanceOf + ", they are " +str(self.onlyClasses[parrent.retInstanceOf].inherits))
                for inherited in self.onlyClasses[parrent.retInstanceOf].inherits:
                    ret = self.recursiveSearchOptions(items, self.onlyClasses[inherited])
                    if ret != None:
                        return ret

        if items[0] == 'operator []':
            return self.recursiveSearchOptions(items[1:], parrent)


        return None



    def recursiveSearchForWordInClasses(self, item, where):
        print("recursiveSearchForWordInClasses: " + where)
        if item in self.byParentClass[where]:
            print ("  found:" + self.byParentClass[where][item].name)
            return self.byParentClass[where][item]

        # do not know how this should work, but it does not
        if self.hashed[where][0].inherits != []:
            for x in self.hashed[where][0].inherits:
                print ( "  and: "+x)
                ret = self.recursiveSearchForWordInClasses(item, x)
                if ret != None:
                    return ret
        
        inherited = self.getAllInheritedClasses(where)
        for x in inherited:
            if x in self.byParentClass:
                if item in self.byParentClass[x]:
                    print ("  found:" + self.byParentClass[x][item].name)
                    return self.byParentClass[x][item]
            
        if item.find("::") != -1:
            s = item.split("::")
            print("  Testing Class::Function")
            if s[1] in self.byParentClass[s[0]]:
                print ("  found:" + self.byParentClass[s[0]][s[1]].name)
                return self.byParentClass[s[0]][s[1]]

        print ("  not found in ")
        return None

                


    # Returns Parrent Function
    def SearchForParrentFunction(self, file, line):
        state = 0
        if not (file in self.byFile):
            return None
        for item in reversed(self.byFile[file]):
            # print(str(item))
            # item.printf()
            if state == 0:
                if item.line <= line:
                    state = 1
            if state == 1:
                if item.kind == "function":
                    return item
            if state == 2:
                break;
        return None

    def searchForLocalVariable(self, name, file, line):

        state = 0
        if not (file in self.byFile):
            return None
        for item in reversed(self.byFile[file]):
            # print(str(item))
            # item.printf()
            if state == 0:
                if item.line <= line:
                    state = 1
            if state == 1:
                if item.name == name:
                    return item
                if item.kind == "function":
                    state = 2
            if state == 2:
                break;
        return None


    def getPath(self, view):
        if not (view.window().folders()):
            print ("CINTEL: Not a project with folders!")
            return None
        folder = setting('default_path', view)

        # print("A> " + folder)
        folder = re.sub("^[.]/?", "/", folder)
        folder = re.sub("[/]*?$", "/", folder)
        folder = re.sub("^/?", "/", folder)
        # print("B> " + folder)

        tags_path = view.window().folders()[0] + folder #+  setting('tag_file', view)

        # print("CINTEL: Path: " + tags_path)
        if not (os.path.exists(tags_path)):
            print("CINTEL: Path does not exist: "+tags_path)
            return None


        return tags_path

    def rebuild(self, view):
        if self.rebuilding == True:
            return
        if self.timeOfLastRefresh+2 > time.time():
            return
        self.rebuilding = True
        print("\n---------REBUILDING---------")
        self.timeOfLastRefresh = time.time()
        startTime = time.time()


        self.clearMemory()
        #program BODY
        try:
            tags_path = self.getPath(view)
            if tags_path == None:
                raise Exception('Path Error')
            # print("running program")
            command = "ctags -R -f "+setting('tag_file', view)+" --fields=nkKisa --c++-kinds=+lp --c-kinds=+lp --sort=no --languages=c,c++ --totals=yes"
            # command = "touch .tags"
            p = subprocess.Popen(command.split(), cwd=tags_path)
            p.wait()

            self.init(view, tags_path+setting('tag_file', view))
        except Exception as err:
            print ("CINTEL ERROR: Creating tags failed\n" + traceback.format_exc() )



        #external Libs from CINTEL
        libs = []
        for lib in self.internalLibNames:
            if(setting(lib, view)):
                libs.append(lib+".h")
        try:
            cmd = "ctags -R -f .tags --fields=nkKisa --c++-kinds=+lp --c-kinds=+lp --sort=no --languages=c,c++ --totals=yes " + " ".join(libs)
            from os.path import dirname, realpath
            packageDirectory = dirname(realpath(__file__)) + "/headers"
            proc = subprocess.Popen(cmd.split(), cwd=packageDirectory)
            proc.wait()
            self.init(view, packageDirectory+"/.tags")
        except Exception as err:
            print ("CINTEL ERROR: Internal LIBS\n" + traceback.format_exc() )


        #user defined files
        userlibs = setting("external", view)
        print ("userlibs = " + str(userlibs))
        for item in userlibs:
            try:
                libDirectory = ""
                projectPath = self.getPath(view)
                filePath = item
                if item[0] != '/':
                    filePath = projectPath + item
                tagFileName = setting('tag_file', view) + re.sub(r"[\s]+|[.]*\\|[.]*/|[.][.]*|[*]|/|\\","." ,item) + ".tags"
                cmd = "ctags -R -f "+tagFileName+" --fields=nkKisa --c++-kinds=+lp --c-kinds=+lp --sort=no --languages=c,c++ --totals=yes " + " "+filePath+""
                proc = subprocess.Popen(cmd.split(), cwd=projectPath)
                proc.wait()
                self.init(view, projectPath+tagFileName)
            except Exception as err:
                print ("CINTEL ERROR: External LIBS\n" + traceback.format_exc() )
                
        print("- rebuild time was: %.2f s" % (time.time() - startTime) )
        print("----------------------------")

        self.rebuilding = False



smComplete = SmartAutocompleteCtags() 



class RebuildCommand(sublime_plugin.TextCommand):
    def run(self, edit):  
        smComplete.rebuild(self.view)
      

class CustomactionCommand(sublime_plugin.TextCommand):
    def run(self, edit):  
        cmd = get_setting("custom_action",self.view)
        for item in cmd:
            print("1 = " + str(item))
            subprocess.call(item, shell=True)
            print("2 = " + str(item.split()))

      

        

      


class CTagsAutoComplete(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if setting('enabled', view):
            print("\n\n\n-------------------------Start of Completion----")
            ret = smComplete.getSmartAutocomplete(view, prefix, locations)
            print("-------------------------End of Completion------")
            return ret
        else:
            return []


    def on_post_save(self, view):
        if setting('enabled', view):
            if setting('auto_rebuild_on_save', view):
                print("CINTEL: on_post_save")
                smComplete.rebuild(view)

    def on_post_save_asyn(self, view):
        # print("CINTEL: on_post_save_asyn")
        # if setting('enabled', view):
        #     if setting('auto_rebuild_on_save', view):
        #         smComplete.rebuild(self.view)
        pass

















