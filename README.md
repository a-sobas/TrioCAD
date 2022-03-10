# TrioCAD - Tool for developing motion paths of machine effectors working in 2D space

This paper describes the implementation of software for creating 
two-dimensional motion paths and the generation of TrioBASIC code for them, which is the basic programming language of TrioMotion motion controllers. An important element of the program is also enabling the creation of drawings in external CAD software and the subsequent import of files saved in the DXF format. 

## Podstawowe informacje

<img src=https://user-images.githubusercontent.com/101074920/157502105-062b88f4-3e76-4e77-920f-e63582f5b676.png width="900"><br>

## Obiekt reprezentujący ścieżkę ruchu

<img src=https://user-images.githubusercontent.com/101074920/157498038-6aafda43-9685-460e-9b3f-8e501aea7fb0.jpg width="500"><br>

## Istnieją cztery sposoby tworzenia polilinii:
•	tworzenie manualne oparte o dodawanie punktów poprzez kolejne kliknięcia myszy na polu rysunkowym,
•	tworzenie manualne oparte o dodawanie punktów za pomocą specjalnego okna,

<img src=https://user-images.githubusercontent.com/101074920/157498513-4c9fa48e-c7d0-4f35-97ee-fd94f6191d79.png width="500"><br>

•	tworzenie za pomocą tabeli punktów,
<img src=https://user-images.githubusercontent.com/101074920/157498551-344e1349-bd80-481e-b614-535188965c8f.png width="500"><br>

•	interpretacja plików DXF.
<img src=https://user-images.githubusercontent.com/101074920/157498998-727cd90a-373e-437a-87c1-0cca547f2117.png width="500"><br>

## Wspomaganie rysowania

Program posiada kilka ułatwień związanych z rysowaniem bezpośrednio poprzez wybieranie pozycji za pomocą kursora myszy. Pierwszą rzeczą jest kwestia informacji o pozycji kursora, którą możemy zdobyć na dwa sposoby:
•	odczytując ją z osi współrzędnych,
•	odczytując ją bezpośrednio z dolnego paska narzędzi.
Pomocnym w powyższym jest również możliwość opcji naniesienia siatki na pole rysunkowe. Wielkość jej pola możemy dowolnie modyfikować w zależności od naszych potrzeb. Drugą rzeczą jest natomiast zaimplementowany asystent rysowania posiadający trzy funkcje:
•	przyciąganie do punktu polilinii,
•	rysowanie ortogonalne,
•	przyciąganie do punktu siatki.
Każda z funkcji może działać samotnie lub możemy je dowolnie łączyć.


## Modyfikacja linii
<img src=https://user-images.githubusercontent.com/101074920/157500760-99847eda-5d9c-4ed0-8a6c-f00d9ef4b728.png width="500"><br>

<img src=https://user-images.githubusercontent.com/101074920/157501822-4ba5a612-c7cd-46e7-9330-e892fe064903.png width="500"><br>

## Usuwanie linii

<img src=https://user-images.githubusercontent.com/101074920/157502777-c7d586e3-37e9-4f0d-bb09-f972ed723829.png width="500"><br>

## Warstwy

<img src=https://user-images.githubusercontent.com/101074920/157509356-04593ae0-f45f-46b8-b7a7-e32f557beb76.png width="500"><br>

## Wykorzystanie 

<img src=https://user-images.githubusercontent.com/101074920/157524024-225f8242-debb-4812-8788-fe193740ba6e.png width="500"><br>

<img src=https://user-images.githubusercontent.com/101074920/157524037-9e32c7d4-59b9-4018-935f-d2d6c54f2d7c.png width="500"><br>

<img src=https://user-images.githubusercontent.com/101074920/157524048-b30ea930-5e8b-4a00-ac5c-a298f3bddc52.png width="500"><br>
