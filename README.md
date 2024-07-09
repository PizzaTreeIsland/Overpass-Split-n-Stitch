# Overpass-Split-n-Stitch
A simple UI tool that makes it easy to run overpass API queries on a large BBox by splitting it up into smaller areas and joining the resulting geojson file(s). 

![Pasted image 20240709204544](https://github.com/PizzaTreeIsland/Overpass-Split-n-Stitch/assets/163044645/82acce18-54a5-439a-bbed-3d850fe7232c)


---
## Table of contents
- [Usage](#usage)
	- [Prerequisites](#prerequisites)
	- [How to run](#how-to-run)
	- [Configuration options](#configuration-options)
- [Possible future features](#possible-future-features)
---
## Usage
### Prerequisites
This tool uses the [overpy](https://github.com/DinoTools/python-overpy) library to run the queries, the [tkintermapview](https://github.com/TomSchimansky/TkinterMapView) library to draw the map and bbox segmentation as well as the [geojson](https://github.com/jazzband/geojson) library to handle the result files. 
### How to run
Compile and run ```Overpass split 'n' stitch.py```. 

Paste your overpass query into the field on the left, adjust your bbox and hit Run! A file dialog will appear. Choose the path where you want the resulting geojson file to be saved. After the query has completed, a noice will appear and you can quit the tool and open the results file you saved earlier, for example using the [JOSM editor](https://github.com/JOSM) or [QGIS](https://github.com/qgis/QGIS).
### Configuration options
#### Adding more query parameters
If you want to add more query parameters, such as a timeout, you can select the "Add more options" checkbox, thus removing the semicolon at the end of the preset query header and therefore not terminating it. You have to add this semicolon after your custom parameters. 

![Pasted image 20240709204725](https://github.com/PizzaTreeIsland/Overpass-Split-n-Stitch/assets/163044645/049d66c4-c8c0-4852-9ede-fdbffa505624)

#### Custom bbox or global search
You can customize the borders of your rectangular bbox using the according options. You can also check "global search" to search globally. 

![Pasted image 20240709205046](https://github.com/PizzaTreeIsland/Overpass-Split-n-Stitch/assets/163044645/9efdb240-4225-4633-b0fe-ea8320957aa5)

Note that in any case, results south of -89.99999° will be ignored because of [a possible bug in a used library](https://github.com/TomSchimansky/TkinterMapView/issues/142). I hope you don't want to search anything about 4 feet around the south pole. 
#### Segment number
You can set the number of segments to influence the individual segment size. Uncheck "Show segmentation" if you're using a large number and the visualisation bogs down your computer.

![Pasted image 20240709205435](https://github.com/PizzaTreeIsland/Overpass-Split-n-Stitch/assets/163044645/6fda212e-7489-41a0-93fb-ec910c71c390)


--- 
## Possible future features
This is an early version of the Overpass Split 'n' Stitch tool. It works well enough for what I need it for personally, which is why I chose to publish it now, but it is very much unpolished and I will try to get around to some issues. Here are some of my ideas for future versions: 
### Adding options for using your own overpass instance
For particularly large queries, it would be nice if you could usse this tool to query a self hosted version of the overpass api. But it seems [there isn't support for that yet in ther overpy library](https://github.com/DinoTools/python-overpy/issues/78). [This other overpass wrapper](https://github.com/mvexel/overpass-api-python-wrapper) has an easy option for that, but doesn't just easily pass through the query, which is why I ultimately opted against using that one. 
### Making this a commandline tool
I prefer looking at pretty pictures rather than working with the naked numbers, especially when it comes to geocoordinates and maps. However, I know people like command line tools and I consider removing all the gui elements and just packing the bbox segmentation function into its own command line tool. 
### Display query results in preview map
To make it more complete and easy to use just like the overpass turbo website. Run huge queries and look at the results in just one window, so you don't even have to figure out what to do with the resulting geojson file and how to open it. 
### Show progress intuitively
So far, all the input options go inactive and nothing happens for a while until all the queries are finished. That is ok if you know what's going on, but I would like to add a "everything is fine" communication of some kind for confused users. I dream of multi-colored progress bars showing succesful, unsuccesful and currently pending segments. 

![Pasted image 20240709212230](https://github.com/PizzaTreeIsland/Overpass-Split-n-Stitch/assets/163044645/c3a168a8-42a3-4c5f-9adb-81c484120f1a)


### Add more options to the tile view
The tile view is a great opportunity to show each tiles progress for each tile. 
### Error handling for query issues or timeouts
This one is a big oversight. If you have a typo in your query, the program just stops. Error handling should be somewhat easy to implement in the future and is necessary for dealing with unsuccesful segments. 
###  Implement dynamic segment size
It doesn't make any sense to have the same segment size over oceans and in city centers. Options for dynamic tile sizes based on node density would be very useful, but that is above my paygrade at this point. 
### Handle aborting file path selection
When running the query, don't abort in the file dialog. Just don't. Yet. 


If you're interested in any of these issues or other possible features feel free to contribute, open an issue or write me on Mastodon! 

--- 
