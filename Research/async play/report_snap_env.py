import sys, os
try:
    import wx
except:
    print("can't import wx")
else:
    print("import wx succeeded OK")

print("sys.path")
print(sys.path)
print()

print("\n".join(sys.path))
print()

print("os.getcwd()")
print(os.getcwd())
print()

print("os.listdir()")
print(os.listdir())
print()

