BUILDDIR = build/
TESTDIR = test/
SRCDIR = src/
# Objects
OBJS = $(addprefix $(BUILDDIR)/, )
TESTOBJS = $(addprefix $(BUILDDIR)/, )
# Headers
INCLUDEPATH = include/
INCLUDE = -I$(INCLUDEPATH)
HEADERS = $(addprefix $(INCLUDEPATH)/, )
# Compiler settings
CXX = g++
CFLAGS = -fPIC -c -std=c++17 $(INCLUDE) -flto -O3 -march=native
LFLAGS = -shared -flto -O3 -march=native
TESTLFLAGS = -flto -O3 -march=native
EXECLFLAGS = -flto -O3 -march=native

$(TESTDIR)/test: $(BUILDDIR)/test.o $(HEADERS) $(OBJS)
	$(CXX) $(BUILDDIR)/test.o $(OBJS) $(TESTLFLAGS) -o $(TESTDIR)/test

$(BUILDDIR)/test.o: $(TESTDIR)/test.cpp $(HEADERS)
	$(CXX) $(CFLAGS) $(TESTDIR)/test.cpp -o $(BUILDDIR)/test.o

.PHONY: clean
clean:
	rm $(OBJS) $(TESTOBJS) $(TESTDIR)/test

.PHONY: install
install:
	sudo ln -snf $(CURDIR)/$(INCLUDEPATH) /usr/local/include/test_cpp_proj

.PHONY: uninstall
uninstall:
	sudo rm /usr/local/include/test_cpp_proj
