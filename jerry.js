var fso = new ActiveXObject(“Scripting.FileSystemObject”);
var f = fso.OpenTextFile("COM3:", ForWriting, false, TriStateFalse);
f.write("\x02306E303030303030303030303832\x03");

