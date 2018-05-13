# Automatically generated Makefile. DO NOT MODIFY.
# Generated on 2018-05-12 18:36:04.185508

.PHONY: clean

build/test.o: test/test.cpp include/header1.hpp include/header2.hpp include/nestedHeader.hpp
	g++ -fPIC -c -O3 -flto -march=native -std=c++17 test/test.cpp -o build/test.otest -Iinclude

build/source1.o: src/source1.cpp include/header1.hpp include/nestedHeader.hpp
	g++ -fPIC -c -O3 -flto -march=native -std=c++17 src/source1.cpp -o build/source1.osrc -Iinclude

build/source2.o: src/source2.cpp include/header2.hpp include/nestedHeader.hpp
	g++ -fPIC -c -O3 -flto -march=native -std=c++17 src/source2.cpp -o build/source2.osrc -Iinclude

test/test: build/test.o build/source1.o build/source2.o
	g++ -fPIC -c -O3 -flto -march=native -std=c++17 build/test.o build/source1.o build/source2.o -o test/test

clean:
	rm -rf build/* test/test

