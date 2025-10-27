# 16bit SAP chipset in LogiSIM
This chipset is based on the Simple as Possible architecture and was designed in LogiSIM. It has 3 general purpose registers, an arithmetic unit, flags for the ALU that are used for conditional jumps, a separate address register for sub-routines, a stack with a pointing register, and an output register. The project also has a program part which is a simple lexer and assembler that converts a python-like syntax into intsructions for the RAM and stores them in a binary file.  

![/Circuit Diagram](/SAP.png)

## Making the chip work
First the `SAP.circ` file needs to be opened in LogiSIM and secondly the `Control_ROM` and `Program_RAM` need to be loaded from the provided instruction sets and demo code. Select the desired clock speed in the `Simulate` tab from the top, then click the Reset button on the circuit and start the clock cycling. The curcuit will run according to the demo code and enter the `HALT` state after completing the entire program. To reset the system just click on the `Reset` button while the clock signal is low.

## Writing Programs
To write custom programs for the chip just modify the `code` string in the `demo.py` file and run the file, it will modify the `Program_RAM` file and then just load it into in the RAM in the circuit. The coding guidelines are as follows:
- `let <var> = <value>;`                                for creating variables and initializing
- `<var> = <opperation>(<var/value>, <var/value>);`     for conducting opperations and storing their values
- `del <var>;`                                          for freeing up memory
- `out(<var>);`                                         for loading the value of var in the output register
- `push(<var/value>);`                                  for pushing data onto the stack
- `pop(<var/empty>);`                                   for retrieving or rejecting data from stack

The opperations are add(x, y), sub(x, y), mul(x, y), divf(x, y) and they do x+y, x-y, x*y, x/y respectively. The stack is used for multiplication and division when available, otherwise memory is used.
