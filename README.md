# mini-python-to-java-compiler

A university course project created by Daniel Lee, Victor Ma, and Takafumi Murase
for the purpose of learning about compilers.

This compiler takes a formatted Python file as input and outputs a compilable
Java file that performs the same functions as the input file.

Note that due to time constraints and the nature of the project, the compilier
can only recognize a subset of the Python language (denoted as Mini Python)
that contains the following:

- integer, float, boolean, string, list, tuple
- if, elif, else statements
- while loops
- function definitions
- No classes, “None” type, re-declaring variable types are permitted
- Scopes are defined using semicolons and hashtags
