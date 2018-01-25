# Plugin for soving pipe networks using hardy cross method
Installation
    Download this folder and copy it to QGIS plugins directory.
    
This plugin is used to solve pipe networks(lines and polylines) using hardy cross method (https://en.wikipedia.org/wiki/Hardy_Cross_method). 
	The sample data is also included in this repository. 
	For the plugin to work properly on a vector layer, the layer must contain atleast three attributes ie."name","FLOW","k", and the direction of the line plays an important role
	Where
	
	-name: name of the segment. The dead ends must be named with "O". The direction of the line and the naming must match.That is, OA is not equal as AO,where OA represent flow from O to A while AO is the counterwise.
	-FLOW: the flow value
	-k-head loss per unit flow
Select the layer on which the plugin should run and click the plugin's icon or Plugins->HardyCross->Solve for active layer
