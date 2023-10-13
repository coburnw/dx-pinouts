# dx-pinouts
Pinout Generator for Microchip's DX Series Chips

### dependencies.  
* [drawsvg](https://github.com/cduck/drawsvg) SVG drawing library
* [v-pallete](https://github.com/villoro/vpalette) Simplifies color selection
* *pillow* Used for calculating actual string length given a specific font.
* *requests* for downloading fonts

### install
In a new project folder:
* create a new python venv and activate
* pip install dependencies
* install [m-dfp](http://github.com/coburnw/m-dfp.git) (Microchip-DFP parsing library)
* install [pinout-overview-lib](http://github.com/coburnw/pinout-overview-lib.git)
* git clone github.com/coburnw/dx-pinouts
* cd dx-pinouts
* edit da.json to reflect file paths or desired variants
* python pinout.py

### configuration
dx_functions.py contains both style and the parsing methods for adapting 
the definitions found in the DFP to a visual item displayed on the page.   

