# TrioCAD - Tool for developing motion paths of machine effectors working in 2D space

A software project for creating two-dimensional motion paths and generating the TrioBASIC code for them, which is the basic programming language of TrioMotion motion controllers. An important element of the program is the possibility of creating drawings in an external CAD software and subsequent import of files in DXF format.

## Application presentation

<img src=https://user-images.githubusercontent.com/101074920/157502105-062b88f4-3e76-4e77-920f-e63582f5b676.png width="900"><br>

## An object representing the path of the movement

<img src=https://user-images.githubusercontent.com/101074920/157678700-f1d946d7-c239-43f5-bf66-40d39b73158a.png width="500"><br>

## Display modes

<img src=https://user-images.githubusercontent.com/101074920/157678399-eec681e7-9f0c-4113-a02f-b1a09ba449a2.png width="900"><br>

## Ways to create polylines (motion paths):
- manual creation based on adding points by consecutive mouse clicks on the drawing field
- manual creation based on adding points using a special window <br>

<img src=https://user-images.githubusercontent.com/101074920/157498513-4c9fa48e-c7d0-4f35-97ee-fd94f6191d79.png width="500"><br>
- creating with a table of points <br>

<img src=https://user-images.githubusercontent.com/101074920/157498551-344e1349-bd80-481e-b614-535188965c8f.png width="500"><br>
- DXF files interpretation <br>

<img src=https://user-images.githubusercontent.com/101074920/157498998-727cd90a-373e-437a-87c1-0cca547f2117.png width="900"><br>

## Drawing assistance

The program has several facilities related to drawing directly by selecting positions with the mouse cursor. The first thing is the cursor position information, which we can get in two ways:
- by reading it from the coordinate axes,
- by reading it directly from the bottom toolbar.
The option to put a grid on the drawing area is also helpful in the above. The size of its field can be freely modified depending on our needs. <br>
The second thing is the implemented drawing assistant with three functions:
- snapping to a polyline point,
- orthogonal drawing,
- snap to a grid point. <br>
Each of the functions can work alone or we can combine them freely.

## Polyline modifications
- using the end of line handle

<img src=https://user-images.githubusercontent.com/101074920/157500760-99847eda-5d9c-4ed0-8a6c-f00d9ef4b728.png width="900"><br>
- using ine center handle

<img src=https://user-images.githubusercontent.com/101074920/157501822-4ba5a612-c7cd-46e7-9330-e892fe064903.png width="900"><br>
The red circles presented in the picture above indicate that it is not possible to make rounding with a given radius

## Delete individual lines
<img src=https://user-images.githubusercontent.com/101074920/157502777-c7d586e3-37e9-4f0d-bb09-f972ed723829.png width="900"><br>

## Layers

The program supports the creation of motion paths using layers. <br>

<img src=https://user-images.githubusercontent.com/101074920/157509356-04593ae0-f45f-46b8-b7a7-e32f557beb76.png width="900"><br>

## Showcase the use of the application

1. Creation of a motion path in TrioCAD and generation of the corresponding motion code

<img src=https://user-images.githubusercontent.com/101074920/157524024-225f8242-debb-4812-8788-fe193740ba6e.png width="900"><br>

2. Use of the generated motion code in the Motion Perfect motion program (TrioMotion motion controller software)

<img src=https://user-images.githubusercontent.com/101074920/157524037-9e32c7d4-59b9-4018-935f-d2d6c54f2d7c.png width="900"><br>

3. Presentation of the motion simulation resulting from the previously generated code on the MotionPerfect oscilloscope

<img src=https://user-images.githubusercontent.com/101074920/157524048-b30ea930-5e8b-4a00-ac5c-a298f3bddc52.png width="900"><br>
