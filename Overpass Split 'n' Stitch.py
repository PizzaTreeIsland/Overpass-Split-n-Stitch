import tkinter as tk
import tkintermapview
import math
from tkinter import filedialog
import overpy
import geojson
#import threading

#Defining globally used variables and assigning default values
root = tk.Tk()
boundarysouth = 20
boundarywest = -10
boundarynorth = 60
boundaryeast = 40
oldboundarysouth = 20
oldboundarywest = -10
oldboundarynorth = 60
oldboundaryeast = 40
globalsearch = tk.IntVar(root)
inputsouth = tk.DoubleVar(root)
inputwest = tk.DoubleVar(root)
inputnorth = tk.DoubleVar(root)
inputeast = tk.DoubleVar(root)
inputsouth.set(boundarysouth)
inputwest.set(boundarywest)
inputnorth.set(boundarynorth)
inputeast.set(boundaryeast)
segments = tk.IntVar()
segments.set(100)
segmentcoords = []
showsegments = tk.IntVar()
showsegments.set(1)
moreoptions = tk.IntVar()
moreoptions.set(0)
querytextinput=tk.StringVar()


def runquery(): #runs query
    global querytext
    global querytextinput
    global moreoptionscheckbox
    global moreoptions
    global globalsearchcheckbox
    global inputnorthspinbox
    global inputsouthspinbox
    global inputwestspinbox
    global inputeastspinbox
    global segmentnumberspinbox
    global showsegmentscheckbox
    global runbutton
    global globalsearch

    # select output file path
    file_path = ""
    file_path = filedialog.asksaveasfilename(title="Select path for geojson output file", filetypes=[("GeoJSON", "*.geojson")], defaultextension=".geojson")
    if file_path == "":
        return 0

    #deactivate input ui elements
    moreoptionscheckbox.config(state="disabled")
    querytext.config(state="disabled")
    globalsearchcheckbox.config(state="disabled")
    inputnorthspinbox.config(state="disabled")
    inputsouthspinbox.config(state="disabled")
    inputwestspinbox.config(state="disabled")
    inputeastspinbox.config(state="disabled")
    segmentnumberspinbox.config(state="disabled")
    showsegmentscheckbox.config(state="disabled")
    runbutton.config(state="disabled")

    # creates empty FeatureCollection to add features for each segment to
    feature_collection = geojson.FeatureCollection([])

    def executequery():
        # Helper function to convert Overpass node to GeoJSON feature
        def node_to_feature(node):
            return geojson.Feature(
                id=node.id,
                geometry=geojson.Point((float(node.lon), float(node.lat))),
                properties=node.tags
            )

        # Helper function to convert Overpass way to GeoJSON feature
        def way_to_feature(way):
            coordinates = [(float(node.lon), float(node.lat)) for node in way.nodes]
            return geojson.Feature(
                id=way.id,
                geometry=geojson.LineString(coordinates),
                properties=way.tags
            )

        # Helper function to convert Overpass relation to GeoJSON feature
        def relation_to_feature(relation):
            # This example handles only multipolygon type of relations
            polygons = []
            for member in relation.members:
                if isinstance(member, overpy.Way):
                    coordinates = [(float(node.lon), float(node.lat)) for node in member.nodes]
                    polygons.append(coordinates)
            return geojson.Feature(
                id=relation.id,
                geometry=geojson.MultiPolygon([polygons]),
                properties=relation.tags
            )

        #run actual query for each segment:
        for segment in segmentcoords:
            # discriminates wether or not the moreoptions option is checked or not, in order to assemble the query text accordingly.
            # then assembles query text string for individual segment
            if moreoptions.get() == 0:
                querytextstring = str("[bbox:" + str(segment[0]) + "," + str(segment[1]) + "," + str(segment[2]) + "," + str(segment[3]) + "][out:json];"+"\n"+querytext.get("1.0","end"))
            else:
                querytextstring = str("[bbox:" + str(segment[0]) + "," + str(segment[1]) + "," + str(segment[2]) + "," + str(segment[3]) + "][out:json]"+"\n"+querytext.get("1.0","end"))

            #runs query with querytextstring
            api = overpy.Overpass()
            queryresponse = api.query(querytextstring)

            # Convert elements to GeoJSON features
            features = []

            # Add nodes
            for node in queryresponse.nodes:
                features.append(node_to_feature(node))

            # Add ways
            for way in queryresponse.ways:
                features.append(way_to_feature(way))

            # Add relations
            for relation in queryresponse.relations:
                features.append(relation_to_feature(relation))

            #add to featurecollection:
            feature_collection.features.extend(features)

    executequery()#this could be replaced by the following lines to outsource the ressource hungry query process to its own thread

    #querythread=threading.Thread(target=executequery)
    #querythread.start()
    #querythread.join()


    #save featurecollection as geojson file
    with open(file_path, 'w') as f:
        geojson.dump(feature_collection, f)

    #show window "done"
    donewindow = tk.Toplevel()
    donewindow.title("Done!")
    donewindow.iconbitmap("Icon.ico")
    tk.Label(donewindow, text="The query results were saved as geojson file. ", wraplength=400).pack(padx=10, pady=10)
    tk.Button(donewindow, text='OK', command=donewindow.destroy).pack(padx=10, pady=10)


    #reactivate input ui elements
    moreoptionscheckbox.config(state="normal")
    querytext.config(state="normal")
    globalsearchcheckbox.config(state="normal")
    if globalsearch.get() == 0:
        inputnorthspinbox.config(state="normal")
        inputsouthspinbox.config(state="normal")
        inputwestspinbox.config(state="normal")
        inputeastspinbox.config(state="normal")
    segmentnumberspinbox.config(state="normal")
    showsegmentscheckbox.config(state="normal")
    runbutton.config(state="normal")



def moreoptionshelp():
    helpwindow = tk.Toplevel()
    helpwindow.title("Add more options")
    helpwindow.iconbitmap("Icon.ico")
    tk.Label(helpwindow, text="Removes the semicolon at the end of the query settings block so you can add more options in square brackets and then close the statement with a semicolon yourself. ", wraplength=400).pack(padx=10, pady=10)
    tk.Button(helpwindow, text='OK', command=helpwindow.destroy).pack(padx=10, pady=10)


def segmentation():
    global boundarysouth
    global boundarywest
    global boundarynorth
    global boundaryeast
    global segments
    global segmentcoords
    global map
    #factorize the desired number of segments, optimize for difference between factors being minimal to avoid long, narrow bboxes (for no particular reason other than beauty of mind and a good gui experience when displaying progress or other info in segments later on
    n = segments.get()
    min_difference = float('inf')  # Initialize with a large value

    # Iterate through potential factors up to the square root of n
    for i in range(1, int(math.sqrt(n)) + 1):
        if n % i == 0:
            # i is a factor, n/i is the corresponding pair factor
            pair_factor = n // i
            difference = abs(i - pair_factor)

            # Update if we found a pair with smaller difference
            if difference < min_difference:
                min_difference = difference
                longsegments = i
                latsegments = pair_factor


    #find segment edge lenghts:
    longsegmentsize = (boundarynorth-boundarysouth)/longsegments
    latsegmentsize = (boundaryeast-boundarywest)/latsegments


    #calculate individual bbox corners
    segmentcoords=[]
    boundarysouthclamped=max(boundarysouth, -89.99999) #workaround for possible bug (https://github.com/TomSchimansky/TkinterMapView/issues/142). Excludes south pole from search bbox. But let's be honest, were you really searching on the south pole?
    i = 0
    for long in range(longsegments):
        for lat in range(latsegments):
            #append this structure to segmentcoords: [south, west, north, east]
            segmentcoords.append([boundarysouthclamped + long * longsegmentsize, boundarywest + lat * latsegmentsize,
                                  boundarysouthclamped + (long + 1) * longsegmentsize,
                                  boundarywest + (lat + 1) * latsegmentsize])
            i += 1
    #overwrites northern and eastern boundry values with set bbox values to avoid either propagated rounding errors or, more likely, deviations caused by the hacky south border clamping workaround
    #adjusting east border:
    for long in range(longsegments):
        segmentcoords[long * latsegments + (latsegments - 1)][3] = boundaryeast
    #adjusting north border:
    for lat in range(latsegments):
        segmentcoords[(longsegments - 1) * latsegments + lat][2] = boundarynorth
    refreshgui()

def refreshgui():
    global boundarysouth
    global boundarywest
    global boundarynorth
    global boundaryeast
    global inputsouth
    global inputwest
    global inputnorth
    global inputeast
    global querybboxlabel
    global globalsearch
    global segmentcoords
    global moreoptions

    #set spinbox labels to adjusted values
    inputsouth = tk.DoubleVar(root)
    inputwest = tk.DoubleVar(root)
    inputnorth = tk.DoubleVar(root)
    inputeast = tk.DoubleVar(root)
    inputsouth.set(boundarysouth)
    inputwest.set(boundarywest)
    inputnorth.set(boundarynorth)
    inputeast.set(boundaryeast)

    inputnorthspinbox.config(textvariable=inputnorth)
    inputsouthspinbox.config(textvariable=inputsouth)
    inputeastspinbox.config(textvariable=inputeast)
    inputwestspinbox.config(textvariable=inputwest)


    #adjust label text for query beginning
    if moreoptions.get() == 0:
        querybboxlabel.config(text="[bbox:" + str(boundarysouth) + "," + str(boundarywest) + "," + str(boundarynorth) + "," + str(boundaryeast) + "]" + "\n" + "[out:json];", justify="left")
    else:
        querybboxlabel.config(text="[bbox:" + str(boundarysouth) + "," + str(boundarywest) + "," + str(boundarynorth) + "," + str(boundaryeast) + "]" + "\n" + "[out:json]", justify="left")

    #Refresh bbox visualisation in map view, depending on wether or not segments are supposed to be shown
    map.delete_all_polygon()
    if showsegments.get() == 1:
        i=0
        bboxes = {}
        for segment in enumerate(segmentcoords):
            bboxes[f'bbox{i + 1}'] = map.set_polygon(
                [(segment[1][2], segment[1][1]), (segment[1][2], segment[1][3]), (segment[1][0], segment[1][3]),
                 (segment[1][0], segment[1][1]), (segment[1][2], segment[1][1])])
    else:
        bboxvis = map.set_polygon(
            [(boundarynorth, boundarywest), (boundarynorth, boundaryeast), (max(boundarysouth, -89.99999), boundaryeast),
             (max(boundarysouth, -89.99999), boundarywest), (boundarynorth, boundarywest)]) #clamps south value to avoid possible bug (https://github.com/TomSchimansky/TkinterMapView/issues/142)

def getbbox():
    global boundarysouth
    global boundarywest
    global boundarynorth
    global boundaryeast

    global map
    #sets bbox limits to input parameters, checks for north > south and east > west as well as value being within map limits
    boundarynorth = max(min(90, max(-90, float(inputnorth.get()))),boundarysouth)
    boundarysouth = min(max(-90, min(90, float(inputsouth.get()))), boundarynorth)
    boundaryeast = max(min(180, max(-180, float(inputeast.get()))), boundarywest)
    boundarywest = min(max(-180, min(180, float(inputwest.get()))), boundaryeast)

    # Reset map zoom to boxvis
    map.fit_bounding_box((min(boundarynorth + 0.174533, 89.9), max(boundarywest - 0.174533, -179.9)),
                         (max(boundarysouth - 0.174533, -89.9), min(boundaryeast + 0.174533, 179.9)))
    # sets viewing bbox to selected bbox with margin around, clamped to global maximum in case of bboxes near map borders

    #refreshing gui
    segmentation()
    refreshgui()

def setglobalsearch():
    global oldboundarysouth
    global oldboundarywest
    global oldboundarynorth
    global oldboundaryeast
    global boundarysouth
    global boundarywest
    global boundarynorth
    global boundaryeast
    global showsegments
    global map


    if globalsearch.get() == 1:
        #save old bbox limits to variable so they can be restored when globalsearch is unchecked again
        oldboundarysouth = boundarysouth
        oldboundarywest = boundarywest
        oldboundarynorth = boundarynorth
        oldboundaryeast = boundaryeast
        #set bbox limits to world wide

        boundarysouth = -90
        boundarywest = -180
        boundarynorth = 90
        boundaryeast = 180
        #deactivate bbox selector elements
        inputnorthspinbox.config(state="disabled")
        inputsouthspinbox.config(state="disabled")
        inputeastspinbox.config(state="disabled")
        inputwestspinbox.config(state="disabled")
        #reposition map view and remove bbox
        map.fit_bounding_box((89.9, -179.9), (-89.9, 179.9))
        map.delete_all_polygon()
    else:
        #reactivate bbox selector elements
        inputnorthspinbox.config(state="normal")
        inputsouthspinbox.config(state="normal")
        inputeastspinbox.config(state="normal")
        inputwestspinbox.config(state="normal")
        #Restore bbox size from last selection
        boundarysouth = oldboundarysouth
        boundarywest = oldboundarywest
        boundarynorth = oldboundarynorth
        boundaryeast = oldboundaryeast
        #reset mapview to bbox
        map.fit_bounding_box((min(boundarynorth + 0.174533, 89.9), max(boundarywest - 0.174533, -179.9)), (max(boundarysouth - 0.174533,-89.9), min(boundaryeast + 0.174533,179.9)))
        # sets viewing bbox to selected bbox with margin around, clamped to global maximum in case of bboxes near map borders
        if showsegments.get() == 0:
            bboxvis = map.set_polygon(
                [(boundarynorth, boundarywest), (boundarynorth, boundaryeast), (max(boundarysouth, -89.99999), boundaryeast),
                 (max(boundarysouth, -89.99999), boundarywest), (boundarynorth, boundarywest)]) #clamps south value to avoid possible bug (https://github.com/TomSchimansky/TkinterMapView/issues/142)
    segmentation()
    refreshgui()

#defining gui elements
root.title("Overpass Split 'n' Stitch")
root.iconbitmap("Icon.ico")
queryframe = tk.Frame(root)
rightframe = tk.Frame(root)
parametersframe = tk.Frame(rightframe)
progressframe = tk.Frame(root)
mapframe = tk.Frame(rightframe)

#filling queryframe
querybeginningframe = tk.Frame(queryframe)
querybboxlabel = tk.Label(querybeginningframe, text="[bbox:"+str(boundarysouth)+","+str(boundarywest)+","+str(boundarynorth)+","+str(boundaryeast)+"]"+"\n"+"[out:json];", justify="left")
moreoptionscheckbox = tk.Checkbutton(querybeginningframe, text="Add more options", command=refreshgui, variable=moreoptions)
moreoptionshelp = tk.Button(querybeginningframe, command=moreoptionshelp, text="?", activebackground="light grey", width=1, height=1, bd=0)
querytext = tk.Text(queryframe, height=10, width=40)
querybboxlabel.pack(side="left")
moreoptionshelp.pack(side="right")
moreoptionscheckbox.pack(side="right")
querybeginningframe.pack(fill="x", expand=False)
querytext.pack(fill="both", expand=True)


#filling parametersframe with bboxselectorframe, segmentationframe and map
bboxselectorframe = tk.Frame(parametersframe)
explainertext = tk.Label(bboxselectorframe, text="Adjust bbox or select global search")
globalsearchcheckbox = tk.Checkbutton(bboxselectorframe, text="Global search", variable=globalsearch, command=setglobalsearch)

inputnorthframe = tk.Frame(bboxselectorframe)
inputnorthlabel = tk.Label(inputnorthframe, text="North:")
inputnorthspinbox = tk.Spinbox(inputnorthframe, from_=-90, to=90, command=getbbox, textvariable=inputnorth)
inputnorthspinbox.bind("<Return>", lambda event: getbbox())
inputnorthlabel.pack(side="left")
inputnorthspinbox.pack(side="right")

inputsouthframe = tk.Frame(bboxselectorframe)
inputsouthlabel = tk.Label(inputsouthframe, text="South:")
inputsouthspinbox = tk.Spinbox(inputsouthframe, from_=-90, to=90, command=getbbox, textvariable=inputsouth)
inputsouthspinbox.bind("<Return>", lambda event: getbbox())
inputsouthlabel.pack(side="left")
inputsouthspinbox.pack(side="right")

inputwestframe = tk.Frame(bboxselectorframe)
inputwestlabel = tk.Label(inputwestframe, text="West:")
inputwestspinbox = tk.Spinbox(inputwestframe, from_=-180, to=180, command=getbbox, textvariable=inputwest)
inputwestspinbox.bind("<Return>", lambda event: getbbox())
inputwestlabel.pack(side="left")
inputwestspinbox.pack(side="right")

inputeastframe = tk.Frame(bboxselectorframe)
inputeastlabel = tk.Label(inputeastframe, text="East:")
inputeastspinbox = tk.Spinbox(inputeastframe, from_=-180, to=180, command=getbbox, textvariable=inputeast)
inputeastspinbox.bind("<Return>", lambda event: getbbox())
inputeastlabel.pack(side="left")
inputeastspinbox.pack(side="right")

explainertext.pack(anchor="nw")
inputnorthframe.pack(anchor="ne")
inputsouthframe.pack(anchor="ne")
inputwestframe.pack(anchor="ne")
inputeastframe.pack(anchor="ne")
globalsearchcheckbox.pack(anchor="nw")
bboxselectorframe.pack(side="left", padx=5, pady=5)

segmentationframe = tk.Frame(parametersframe)
segmentationlabel = tk.Label(segmentationframe, text="Number of segments:")
segmentnumberspinbox = tk.Spinbox(segmentationframe, from_=2, to="+inf", textvariable=segments, command=segmentation)
segmentnumberspinbox.bind("<Return>", lambda event: segmentation())
segmentationlabel.pack()
segmentnumberspinbox.pack()
showsegmentscheckbox = tk.Checkbutton(segmentationframe, variable=showsegments, command=refreshgui, text="Show segmentation")
showsegmentscheckbox.pack()
segmentationframe.pack(side="right", padx=5, pady=5)


map = tkintermapview.TkinterMapView(mapframe, height=500, width=600)
segmentation()
map.fit_bounding_box((min(boundarynorth + 0.174533, 89.9), max(boundarywest - 0.174533, -179.9)),
                     (max(boundarysouth - 0.174533, -89.9), min(boundaryeast + 0.174533, 179.9))) #sets vewing box to bbox with margin, clamped down for bboxes near map borders
map.pack(side="bottom")



#filling progressframe
runbutton = tk.Button(progressframe, text="Run", command=runquery)
runbutton.pack(side="right")


#packing gui window
progressframe.pack(side="bottom", anchor="s", fill="x", padx=10, pady=20)
queryframe.pack(side="left", padx=10, pady=10, fill="both", expand=True)
parametersframe.pack(side="top", padx=10, pady=10, fill="both", expand=True)
mapframe.pack(side="bottom", padx=10, pady=10)
rightframe.pack(fill="both", side="right")

root.mainloop()
