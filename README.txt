Replication Kit for the Paper "Are there any Unit Tests? An Empirical Study on Open Source Python Projects"

Contents:
1) Used version of the vcsSHARK
	- located in “vcsSHARK”
2) Used version of the testImpSHARK
	- located in “testImpSHARK”
3) Analysis implementations
	- located in “testImpSHARK/testimpshark/analysis”
4) Raw Data CSV Files
	- located in “testImpSHARK/testimpshark/analysis/data
5) Raw MongoDB
	- located in “mongo_backup”


Usage:
1) Usage instructions for the vcsSHARK is given on its github homepage (http://ftrautsch.github.io/vcsSHARK/index.html) or directly in the “vcsSHARK/pyvcsshark/main.py” file

2) Usage instructions for the testImpSHARK:
	- if only one revision should be analyzed use “testImpSHARK/main.py” 
	- if all revisions should be analyzed use “testImpSHARK/execution.py”
	- in both files concrete instructions can be found

3) Each analysis file is commented. For some of them (rq1_boxplot.py and rq4.py the connection to the MongoDB must be changed). For the R files, the path to the data must be adapted. Otherwise, the files can be directly executed.

4) The MongoDB can be restored via:
mongorestore --gzip --archive=smartshark040816.gz --db smartshark --host <HOST> --port <PORT> --username <USERNAME> --password <PASSWORD> --authenticationDatabase <AUTHENTICATION_DATABASE> 


Tests:
1) The tests can be run directly via the unittest framework of python: e.g., python -m unittest tests/test_common.py
