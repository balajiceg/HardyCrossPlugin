#pipeline
from PyQt4.QtCore import QVariant
from itertools import cycle
from qgis.core import *
from qgis.utils import *
import random


uniquePts=[]
sets=[]
loops=[]
lines=[]
def get_points(l):
    geom = l.geometry()
    return geom.asPolyline()
def compare(s, t):
    t = list(t)   # make a mutable copy
    try:
        for elem in s:
            t.remove(elem)
    except ValueError:
        return False
    return not t

def compare_similar(s, t):
    t = list(t)   # make a mutable copy
    try:
        for elem in s:
            t.remove(elem)
    except ValueError:
        return False
    return not t


def get_line(p1,p2):
    for line in lines:
        x=get_points(line)
        if x[0]==p1 and x[-1]==p2:return line,-1
        elif x[-1]==p1 and x[0]==p2:return line,1

def start_search(tmp,p,initial):
    i=uniquePts.index(p)
    #print 'I'+str(i)
    tmp.append(p)
    pts=sets[i]
    j=0
    while len(pts)>0 and j<len(pts):
        #print j
        point=pts[j]
        if point==initial:
            if len(tmp)<2:
                j+=1
                continue
            if len(loops)<1:
                tmp.append(point)
                pts.pop(j)
                return True
            for loop in loops:
                tmp.append(point)
                if not compare(loop,tmp):
                    pts.pop(j)
                    return True
                else:
                    for s in sets:random.shuffle(s)
                    return False
        if point not in tmp:
            if start_search(tmp,point,initial):
                pts.pop(j)
                return True
            else:
                return False
        else: 
            j+=1


def pipe_run():
	global sets,uniquePts,loops,lines
	uniquePts=[]
	sets=[]
	loops=[]
	lines=[]
	layer = iface.activeLayer()
	n=2
	no_itr=5
	#for rr in range(50):
	#    random.seed(rr)
	no_itr+=1
	if not layer.isValid():
	    print "Layer failed to load!"
	random.seed(3)    
	layer.startEditing()    
	init_index=layer.dataProvider().fieldNameIndex('initial')

	if init_index==-1:    
	    res = layer.dataProvider().addAttributes([QgsField('initial',QVariant.Double)])

	for i in range(1,no_itr):
	    init_index=layer.dataProvider().fieldNameIndex('itr'+str(i))
	    if init_index==-1:    
		layer.dataProvider().addAttributes([QgsField('itr'+str(i),QVariant.Double)])


	layer.updateFields()

	init_index=layer.dataProvider().fieldNameIndex('initial')
	iter = layer.getFeatures()

	
	points=[]
	for feature in iter:
	    # retrieve every feature with its geometry and attributes
	    # fetch geometry
	    geom = feature.geometry()
	    lines.append(feature)
	    x = geom.asPolyline()
	    points.append(x[0])
	    points.append(x[-1])
	#print points
	
	endPts=[]
	for i in points:
	  if points.count(i)==1:
	    endPts.append(i)
	    continue
	  if i not in uniquePts:
	    uniquePts.append(i)

	
	for i in uniquePts:
	    temp=[]
	    for l in lines:
		if str(l['name']).upper().find('O')!=-1:continue
		geom = l.geometry()
		x = geom.asPolyline()
		if i in x:
		    if i==x[0]:
		        temp.append(x[-1])
		    else:
		        temp.append(x[0])
		    #temp.append(l)
	    sets.append(temp)

	#random.seed(9)
	for s in sets:random.shuffle(s)

	
	for set,pt in zip(sets,uniquePts):
	    ii=0
	    while (len(set)>0 and ii<len(set)):
		tmp=[]
		#print 'i='+str(ii)
		temp_p=[set[ii]]
		temp_p=temp_p.pop()
		if start_search(tmp=tmp,p=set[ii],initial=pt):
		    set.pop(ii)
		    loops.append([]+tmp)
		    continue
		ii+=1
		
	sum=0


	dup_loops=loops[:]
	    
	for i in dup_loops:
	    q1=QgsGeometry.fromPolygon([i])
	    for j in dup_loops:
		if i!=j:
		    q2=QgsGeometry.fromPolygon([j])
		    if q1.contains(q2):
		        if not q1.disjoint(q2):
		            try:loops.remove(i)
		            except :pass
		            break

	#for i in loops:
	#    print len(i)
	   
	sets=[]
	for i in uniquePts:
	    temp=[]
	    for l in lines:
		geom = l.geometry()
		x = geom.asPolyline()
		if i in x:
		    temp.append(l)
	    sets.append(temp+[i])

	sets.sort(key = len)
	uniquePts=[]
	len_sets=[]
	for set in sets:
	    uniquePts.append(set.pop())
	    len_sets.append(len(set))

	min_len=min(len_sets)
	last_index=len(len_sets) - len_sets[::-1].index(min_len)

	for i in range(1,last_index):
	    if len(sets[i])!=min_len:break
	    for l in sets[i]:
		if str(l['name']).upper().find('O')>=0:
		    if get_points(l)[-1]==uniquePts[i]:
		        sets.insert(0,sets.pop(i))
		        uniquePts.insert(0,uniquePts.pop(i))
		        
	    
	    

	layer.startEditing()
	for set,p in zip(sets,uniquePts):
	    plus_flows=minus_flows=0
	    nopu=nomu=0
	    
	    for line in set:
		if get_points(line)[0]==p:
		    try:minus_flows+=line['FLOW']
		    except:nomu+=1
		else:
		    try:plus_flows+=line['FLOW']
		    except:nopu+=1
	    try:
		assumed=(plus_flows-minus_flows)/(nomu-nopu)
	    except ZeroDivisionError:pass  
	    for line in set:
		    if line['FLOW']==None:
		        layer.changeAttributeValue(line.id(),init_index, assumed)
		        line['FLOW']=assumed
		        line['initial']=assumed
		    else:
		        layer.changeAttributeValue(line.id(),init_index, line['FLOW'])
		        line['initial']=line['FLOW']

	layer.commitChanges()        

	dup_loops=loops[:]

	pairs=[]
	while dup_loops:
	    loop1=dup_loops.pop(0)
	    for loop2 in loops:
		broke=False
		if loop1==loop2:
		    continue
		similar=[]
		for i in loop1:
		    if i in loop2:
		        similar.append(i)
		if similar.__len__()>1:
		    for pair in pairs:
		        if compare(pair['similar'],similar):
		            broke=True
		            break
		    if not broke:
		        pairs.append({'similar':similar,'pair':[loop1,loop2]})

	layer.updateFields()
	layer.startEditing() 

	str1='initial'
    	
    	
	for it in range(1,no_itr):
	    str2='itr'+str(it)
	    if it!=1:
		str1='itr'+str(it-1)
		
	    for pair in pairs:
		similar=pair['similar']
		similar_line,dir_sim=get_line(similar[0],similar[1])
		
		#first loop
		loop=pair['pair'][0]
		cyc=cycle(loop)
		cur_pt=[]
		nxt_pt=[]
		Hl=dir_sim*(similar_line[str1]**n)*similar_line['k']
		Hlqa=abs(Hl/similar_line[str1])
		edges=[similar_line]
		dir=[dir_sim]
		while cur_pt!=similar[1]:cur_pt=cyc.next()
		
		if cyc.next()==similar[0]:loop.reverse()
		
		cyc=cycle(loop[:])
		cur_pt=[]
		while cur_pt!=similar[1]:cur_pt=cyc.next()
		
		while nxt_pt!=similar[0]:
		    nxt_pt=cyc.next()
		    l,d=get_line(cur_pt,nxt_pt)
		    edges.append(l)
		    dir.append(d)
		    Hl+=d*(l[str1]**n)*l['k']
		    Hlqa+=abs((d*(l[str1]**n)*l['k'])/l[str1])
		    
		    cur_pt=nxt_pt
		
		delt1=-Hl/(n*Hlqa)
		
		
		#second loop
		loop=pair['pair'][1]
		cyc=cycle(loop)
		cur_pt=[]
		nxt_pt=[]
		dir_sim*=-1
		Hl=dir_sim*(similar_line[str1]**n)*similar_line['k']
		Hlqa=abs(Hl/similar_line[str1])
		edges1=[similar_line]
		dir1=[dir_sim]
		while cur_pt!=similar[1]:cur_pt=cyc.next()
		if cyc.next()==similar[0]:loop.reverse()
		cyc=cycle(loop[:])
		cur_pt=[]
		while cur_pt!=similar[1]:cur_pt=cyc.next()
		
		while nxt_pt!=similar[0]:
		    nxt_pt=cyc.next()
		    l,d=get_line(cur_pt,nxt_pt)
		    d=d*-1
		    edges1.append(l)
		    dir1.append(d)
		    Hl+=d*(l[str1]**n)*l['k']
		    Hlqa+=abs((d*(l[str1]**n)*l['k'])/l[str1])
		    cur_pt=nxt_pt
		
		delt2=-Hl/(n*Hlqa)
		
		if layer.dataProvider().fieldNameIndex(str2)==-1:
		    layer.dataProvider().addAttributes([QgsField(str2,QVariant.Double)])
		    layer.updateFields()
		print ('del1:'+str(delt1),'del2:'+str(delt2))
		init_index=layer.dataProvider().fieldNameIndex(str2)
		
		value=abs(dir[0]*edges[0][str1]+delt1-delt2)
		value2=abs(dir1[0]*edges1[0][str1]-delt1+delt2)
		layer.changeAttributeValue(edges[0].id(),init_index,value)
		edges[0][str2]=value
		
		edges1.pop(0)
		edges.pop(0)
		dir.pop(0)
		dir1.pop(0)
		
		for line,d in zip(edges,dir):
		    value=abs(d*line[str1]+delt1)
		    layer.changeAttributeValue(line.id(),init_index,value)
		    line[str2]=value
		    
		for line,d in zip(edges1,dir1):
		    value=abs(d*line[str1]+delt2)
		    layer.changeAttributeValue(line.id(),init_index,value)
		    line[str2]=value
		layer.updateFields()
        	
		

	layer.commitChanges()        

	print("done")
        
        
        
        
        
        
        
        
        
