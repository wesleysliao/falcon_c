
all: example lib/falcon_c.so

lib/falcon_c.so: falcon_c.cpp falcon_c.h
	g++ -shared -lnifalcon falcon_c.cpp -o lib/falcon_c.so

example: bin/main.o bin/falcon_c.o
	g++ -lnifalcon -o example bin/main.o bin/falcon_c.o

bin/falcon_c.o: falcon_c.cpp falcon_c.h
	g++ -c falcon_c.cpp  -lnifalcon -o bin/falcon_c.o

bin/main.o: main.cpp falcon_c.h
	g++ -c main.cpp  -o bin/main.o


clean:
	rm -f bin/falcon_c.o bin/main.o example lib/falcon_c.so
