[![DOI](https://zenodo.org/badge/827412848.svg)](https://doi.org/10.5281/zenodo.14674093)


# OSM Map Matching

A [QGIS](https://qgis.org)-plugin for matching a route with the [OpenStreetMap](https://www.openstreetmap.org) road network. The output is a linestring that can be optionally exported as a ESRI Shapefile or into a SQLite database.

## What's New in Version 1.1

- Optionally, the output can be stored in an SQLite database.
- Various minor bug fixes and improvements.

## Dependencies

The plugin uses the following modules: modules networkx, geopy and python-heapq

### Installing External Python Modules for QGIS

To extend the functionality of QGIS with additional Python modules, you may need to install them in the environment where QGIS’s Python interpreter can access them. Follow these instructions for each platform:

#### 1. **Windows**
   - **Locate the QGIS Python Directory**: Find the QGIS installation folder, typically located in `C:\Program Files\QGIS <version>`.
   - **Open OSGeo4W Shell**: Launch the "OSGeo4W Shell" from your QGIS installation folder or Start Menu. This shell is configured to use QGIS’s Python environment.
   - **Install the Module**: In the OSGeo4W Shell, use `pip` to install the desired module:
     ```shell
     pip install <module_name>
     ```

#### 2. **macOS**
   - **Locate QGIS Python Path**: By default, QGIS on macOS includes its own Python installation. You’ll need to identify the correct Python path, which is usually in `/Applications/QGIS.app/Contents/MacOS/bin/python3`.
   - **Use Terminal to Install Modules**:
     - Open the Terminal application.
     - Run the following command to install the module within QGIS’s Python environment:
       ```shell
       /Applications/QGIS.app/Contents/MacOS/bin/pip3 install <module_name>
       ```

#### 3. **Linux**
   - **Open Terminal**: Linux installations usually have QGIS set up with the system Python, so you can use your system's default `pip` command.
   - **Install Module**:
     - Use the following command in Terminal:
       ```shell
       sudo pip3 install <module_name>
       ```
     - Alternatively, if you prefer not to use `sudo`, you can use `pip install --user <module_name>` to install it locally for the user.


## Installation

* Download the file [osm_map_matching.zip](osm_map_matching.zip)
* From the "Plugin" menu, open "Manage and Install Plugins..."
* Click on "Install from ZIP"
* Select the zip file you just downloaded and press "Install Plugin"

## How to run

### Add a point vector layer to the current QGIS project

You can use a GPS track in any format that is supported by QGIS. Select the item to import, this must be a sequence of Point (see the figure)

![Select Vector](pictures/how_to_use_select_item.png)

### Open the plugin

On the "Plugin" menu, click on "Analyze" under the "OSM map matching" sub-menu. 

![Analyze Window](pictures/how_to_use_analyze_window.png)

Choose a vector layer of points from those loaded in the project, or select a file that contains one.

Set the "Max distance" parameter to specify the maximum allowable distance between an input point and the map element to which it is mapped.

Set the 'Minimum loop size' parameter for the cleaning phase. This parameter defines the minimum length of loops that will be retained in the output path. During this phase, all loops shorter than the specified value are removed from the solution. The output path is scanned multiple times to ensure all short loops are eliminated. This process can be time consuming but can be interrupted by pressing the 'Cancel' button.

Choose an optional ESRI Shapefile for the output or a SQLite database.

## How to use the output

Upon completion of the algorithm, the new layer containing the output is loaded. This is a vector layer consisting of consecutive lines. Each line represents a segment of the route as a sequence of points, with additional fields detailing the segment's attributes, which are derived from OSM data. 

To better understand what the plugin produces, it is helpful to look at the Attribute Table of the layer. To do this, select the layer, right-click to open the context menu, and choose "Open Attribute Table".

![Attribute Table](pictures/how_to_use_attribute_table.jpg)

Each row describes a line feature in the vector layer. The column information is sourced from OpenStreetMap. Some rows may contain more information than others, depending on the accuracy of the data from the source. However, the "highway" column is always present; it identifies the type of road, street, or path. These data can be used to analyze or to represent the original track in a more informative way.

### Example: Statistics on the lengths of various types of roads, ways, and paths

To generate statistics on the lengths of different types of roads or paths traversed by a route, start by adding a field to the attribute table that contains the length of each line. Then, use the "Statistics by categories" algorithm integrated into QGIS. The following animation illustrates the process in detail.

![Statistics](pictures/how_to_use_statistics.gif)

## How to use the SQLite database

It is possible to store the outputs in an SQLite database with the SpatiaLite extension. The database collects the outputs from multiple runs of the algorithm on various input vectors. Each input vector of points represents an activity to which a name and type (Bike, Run, Walk, etc.) can be assigned.

## Database Schema

### Table: `activities`

This table stores metadata about the activities.

| Column Name     | Data Type | Description                                 |
|-----------------|-----------|---------------------------------------------|
| `id`            | INTEGER   | Primary key, auto-incremented.              |
| `activity_name` | TEXT      | Name of the activity (e.g., "Morning Run"). |
| `activity_type` | TEXT      | Type of activity (e.g., "bike", "run").     |

### Table: `linestrings`

This table stores the geometries and additional information derived from OSM tags.

| Column Name     | Data Type | Description                                              |
|-----------------|-----------|----------------------------------------------------------|
| `activityid`    | INTEGER   | Foreign key referencing `id` in the `activities` table. |
| `geometry`      | LINESTRING| The geometry representing the line (from OSM way).       |
| `osm_tag_1`     | TEXT      | A field derived from an OSM tag (example).               |
| `osm_tag_2`     | TEXT      | Another field derived from an OSM tag (example).         |

**Relationships**:

- The `activityid` field in `linestrings` establishes a relationship with the `id` field in `activities`.
- This allows associating multiple linestring geometries and their OSM tag-derived attributes with a single activity.

### Example Workflow with SQLite

It is possible to use an SQLite database to store outputs from multiple executions and run SQL queries to analyze the results. Below is an example illustrated with an animated GIF:

1. **Create a New SQLite Database**:  
   Start a new SQLite database to collect the execution data.

2. **Run Multiple Executions in Batch Mode**:  
   Open the plugin and use batch mode to execute multiple runs and store the results in the database.

3. **Filter Data with an SQL Query**:  
   Use the following query to select only activities of a specific type, for example, "Run":

   ```sql
   SELECT l.* 
   FROM linestrings l
   JOIN activities a ON l.activityid = a.id
   WHERE a.activity_type = 'Run'
   
4. **Load the Results as a Layer**:
    Use the query results to create a new layer. This layer can then be visualized, analyzed, or further processed according to your needs.

![SQLite](pictures/sqlite.gif)
