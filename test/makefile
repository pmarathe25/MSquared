# Automatically generated Makefile. DO NOT MODIFY.
# Generated on 2018-05-12 19:48:45.329737

.PHONY: clean test

build/test.o: test/test.cpp include/nestedHeader.hpp include/header1.hpp include/header2.hpp
	g++ -fPIC -c -O3 -flto -march=native -std=c++17 test/test.cpp -o build/test.o -Iinclude

build/source1.o: src/source1.cpp include/nestedHeader.hpp include/header1.hpp
	g++ -fPIC -c -O3 -flto -march=native -std=c++17 src/source1.cpp -o build/source1.o -Iinclude

build/source2.o: src/source2.cpp include/header2.hpp include/nestedHeader.hpp
	g++ -fPIC -c -O3 -flto -march=native -std=c++17 src/source2.cpp -o build/source2.o -Iinclude

test/test: build/test.o build/source1.o build/source2.o
	g++ -O3 -flto -march=native build/test.o build/source1.o build/source2.o -o test/test

clean:
	rm -rf build/* test/test

test: test/test
	test/test

