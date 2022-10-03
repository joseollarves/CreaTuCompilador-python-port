# Python port of the compiler created by the user <a href="https://github.com/t-edson">T-edson</a>

Original sources:

- <https://github.com/t-edson/CreaTuCompilador>

- <http://blogdetito.com/2019/01/05/crea-tu-propio-compilador-casero-parte-1/>

## Important Notes

- The compiler is not finished. For some problems with Python i couldnt recreate all the functions that were on the original compiler.

- The comments on the program and pages above are mostly in Spanish.

- The core logic of the Python compiler is mostly the same as the original compiler.

- The original compiler was wrote in <a href="https://www.freepascal.org/docs.html">Pascal</a>.

## Problems Encountered

- The first and most important one is that if you try to create some sentences before assigning a value to a variable, the compiler will just stop there
  pretending that it already finished reading all the lines. Generating an error of this nature:

- I cant tell if there are other mistakes besides this one, because all the tests in the page work just fine except for the ones that casually have the
  case above.

## F.A.Q

1. How does it work?

    - The compiler is for a fictional language called Titan and is oriented to learn how to create a compiler.

    - If you want to test it yourself just follow the tests in the 2nd url above.

2. Why create a port of a specific compiler and why in Python?

    - It was for an assignment in my University and they only let me port it to Python or Java.

3. Are you going to finish it some day?

    - Probably not, it was a very difficult task to barely make it function. However if you want to fix it go ahead and try.
