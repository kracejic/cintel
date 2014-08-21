CIntel
======

CIntel is plugin for SublimeText3 which handles smart auto complete features for C++. It is a quick hack which I put together to be able to work with C++ in SublimeText. I have not invested much time into it yet. The code is not optimized and not at all pretty. It is really only patched together. But it works for me most of the time now. Also I made it to comply with my style of work, so you mileage may vary.

Plugin makes refresh of its database every time you save a file. During this refresh ctags is executed for all of your source files. This can be time consuming for bigger projects. It could be slow on non SSD disks or bigger projects. On project with 88 files and 15000 lines it takes on my PC about 300ms. The process of searching of suggestions is quite quick.

I would be happy to accept any pull requests which will not break work flow. 

Please make not, that this plugin is in pre-alpha phase and things will break down. Also it is no case ready for production environment.

This plugin is inpired by https://github.com/SublimeText/CTags


Installation
-----------
### Linux
You must have installed ctags. On ubuntu:
sudo apt-get install exuberant-ctags

### Windows
You must have installed ctags and have it on your PATH.

Features
--------
 * smart auto complete for class members
 * smart auto complete is aware of class inherited members
 * initial template support
 * include auto complete - in #include ""
 * snippets
 * limited stl container support

Planned Features
----------------
 * better template processing
 * per file refreshing of DB (performance)
 * fill switch with all cases of enum

Known Bugs
----------
 * the function and variable definitions must be on one line (even the template)
 * in template CIntel only works with the last type
 * does not suggest global variables and functions
 * all members are treated as public

Snippets
--------
| trigger word| description|
| :-------------: |:-------------|
| construct | constructor and destructor implementation |
| cclass | Class creation |
| csingletonclass | quick singleton class |
| cc | Translates itself to FILENAME:: , useful for implementation of class functions|
| cfun | Class member function implementation void FILENAME::FOO(void){}|
| //- | commented horizontal line |
| name | namespace|
| forrange | range based for from C++11 |
| funct | function |
| switch | |
| try | |
| while | |



Example projects settings
-------------------------
By default CIntel is disabled. You have to enable it in project specific settings.

```json
{
    "folders":
    [
        {
            "folder_exclude_patterns":
            [
                "build"
            ],
            "file_exclude_patterns":
            [
                ".tags"
            ],
            "follow_symlinks": true,
            "path": "."
        }
    ],
    "settings":
    {
        "cintel":
        {
            "default_path" : "source",
            "enabled" : true,
            "auto_rebuild_on_save" : true,

        }
    }
}
```

Support
-------
Please add some source code part which on which I can reconstruct your problem. Do not forget to specify line. But in the best case, fix it and send me pull request since I do not have much time to spent. :)

License
-------
MIT
