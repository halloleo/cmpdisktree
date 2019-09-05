# cmpdisktree - Compare the directories as macOS disk structures
              
      ___                      
     /\__\            _____              ___     
    /:/  /           /::\  \           /\__\    
   /:/  /           /:/\:\  \         /:/  /    
  /:/  /  ___      /:/  \:\__\       /:/__/     
 /:/__/  /\__\    /:/__/ \:|__|     /::\  \     
 \:\  \ /:/  /    \:\  \ /:/  /    /:/\:\  \    
  \:\  /:/  /      \:\  /:/  /     \/__\:\  \   
   \:\/:/  /        \:\/:/  /           \:\  \  
    \::/  /          \::/  /             \:\__\  
     \/__/   mp       \/__/   isk         \/__/ ree


## The Problem

* Symlinks with non-existing target give error in diff, but shouldn't. They
  should only check whether the target string is the same.

## Footnotes to the help screen:

(*) `--relative-fs-top`: This makes exclusion patterns with demand to match the 
    beginning of a path name match in the middle of  a path name as well.

(**) `--output-path`: If a file path is given, use the file as error log file 
    and write, if applicable, the OK log to `cmp-ok.log` in the same directory

## Credits

Thanks to [Kent Nassen](http://www-personal.umich.edu/~knassen/figfonts/isometric2.flf) for the ASCII art
