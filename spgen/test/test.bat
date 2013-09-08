python ..\spgen.py -l cpp -g .\test01.spg
cl /Fo.\gen\ /EHsc Test01.cpp /link /out:.\gen\test01.exe
gen\test01
