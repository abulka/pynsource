J=tests/testing-generate-java
D=tests/testing-generate-delphi
python pynsource.py -j $J/java-out $J/python-in/*.py
python pynsource.py -d $D/delphi-out $D/python-in/*.py
