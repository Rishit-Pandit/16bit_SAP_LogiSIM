from lexer import hexer, parser

code = """

let x = 10;
let y = 12;
out(y);
x = add(x, y);
out(x);
del x;
del y;
let a = 20;
out(a);
a = sub(a, 12);
out(a);
del a;
let x = 0;
x = divf(29, 3);
out(x);
push(1);
push(2);
push(3);
push(4);
push(5);
push(6);
push(7);
push(8);
push(9);
push(10);
push(11);
push(12);
push(13);
push(14);
pop();
pop(x);
out(x);
x = divf(30, 3);
out(x);

"""

code = hexer(parser(code))
print(code)

with open("Program_RAM", "w") as file:
	rows = len(code)//16 + 1
	file.writelines("v3.0 hex words plain\n")
	for i in range(rows):
		file.writelines(" ".join(code[16*i:16*(i+1)]) + "\n")