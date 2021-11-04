CC=g++
CFLAGS=-c -fPIC
INCDIR=/usr/include
LIBDIR=/usr/lib
SRC=src/frame.cpp src/speechPlayer.cpp src/speechWaveGenerator.cpp
OBJ=frame.o speechPlayer.o speechWaveGenerator.o
TARGET=libspeechplayer.so
HEADER=speechPlayer.h

all: $(TARGET)

frame.o: src/frame.cpp src/frame.h
	$(CC) $(CFLAGS) src/frame.cpp

speechPlayer.o: src/speechPlayer.cpp src/speechPlayer.h
	$(CC) $(CFLAGS) src/speechPlayer.cpp

speechWaveGenerator.o: src/speechWaveGenerator.cpp src/speechWaveGenerator.h
	$(CC) $(CFLAGS) src/speechWaveGenerator.cpp

$(TARGET): $(OBJ)
	$(CC) -shared -Wl,-soname,$(TARGET) $(OBJ) -o $(TARGET)

install: $(TARGET) include/$(HEADER)
	cp include/$(HEADER) $(INCDIR)
	cp $(TARGET) $(LIBDIR)

uninstall:
	rm -f $(INCDIR)/$(HEADER)
	rm -f $(LIBDIR)/$(TARGET)

clean:
	rm -f $(OBJ) $(TARGET)
