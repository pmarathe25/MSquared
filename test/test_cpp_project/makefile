# Automatically generated Makefile. DO NOT MODIFY.
# Generated on 2018-05-12 18:16:01.118645

.PHONY: clean

build/test.o: test/test.cpp include/header1.hpp include/header2.hpp include/nestedHeader.hpp
	g++ -fPIC -c -O3 -flto -march=native -std=c++17 test/test.cpp -o build/test.o

test/test: build/test.o
	g++ -fPIC -c -O3 -flto -march=native -std=c++17 build/test.o -o test/test

clean:
	rm -rf build/* test/test

