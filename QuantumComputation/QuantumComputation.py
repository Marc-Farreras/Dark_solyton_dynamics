# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 19:24:43 2020

@author: josep
"""

import kivy
import numpy as np

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.input.motionevent import MotionEvent
from kivy.graphics import *
from kivy.factory import Factory
from kivy.uix.scatter import Scatter
from functools import partial

from QiskitConverter import QiskitConverter
import importlib

from qiskit import * 
import matplotlib.pyplot as plt 
from qiskit.visualization import plot_histogram, plot_bloch_multivector,plot_state_qsphere, plot_state_city,plot_state_hinton
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg


global matrix
global row_name
global multigates

File = open("QiskitCircuit.py","w")
File.close()

import QiskitCircuit

matrix =np.empty((0,0), dtype="<U5")
row_name=[]
gates_list=['H', 'X', 'CX', 'CCX', 'SWAP', 'T', 'Y', 'RESET']
gates_2={'CX': 2, 'CCX': 3, 'SWAP': 2}
pressed=''
multigates=[]


cellsize=50
space=5
    

class Gate_mouse(Button):
    def __init__ (self, **kwargs):
        global pressed
        super(Gate_mouse, self).__init__(**kwargs)
        #self.text= pressed
        self.opacity=0.6
        self.size_hint=(None,None)
        self.size=(cellsize*0.9, cellsize*0.9)
    

class Gate_circuit(Button):
    
    def __init__ (self, **kwargs):
        super(Gate_circuit, self).__init__(**kwargs)
        self.always_release=True
        self.opacity=0.8
        self.size_hint=(0.9, 0.9)
        self.size=(cellsize/2., cellsize/2.)
        self.background_down = self.background_normal
        self.halign='center'
        self.bind(
            on_press=self.create_clock,
            on_release=self.delete_clock)
        
    def create_clock(self,  *args):
        global callback
        global cgrid
        
        callback = partial(self.long_press)
        Clock.schedule_once(callback, 0.3)
        
        

    def delete_clock(self,  *args):
        global callback
        global pressed
        global cgrid
        
        Clock.unschedule(callback)
        if pressed != 'multigate':
            pressed=''
        cgrid.remove_widget(cgrid.scatter)
        
        
    def long_press(self, *largs):
        global cgrid
        global matrix
        global pressed
        global gates_2
        global rowsconnected
        global multigate
        global prev
        
        
        if matrix[self.matrix[0],self.matrix[1]]=='':
            return
            
        
        if pressed=='multigate':
            
            cgrid.rows[0].cols[0].deletecurrent()
            if self.matrix[0] in rowsconnected and self.matrix[1]== multigate[1]:
                return
        
        posx=self.x-cgrid.scroll.parent.scroll_x*(cgrid.scroll.width-cgrid.scroll.parent.width)
        posy=self.y-cgrid.scroll.parent.scroll_y*(cgrid.scroll.height-cgrid.scroll.parent.height)+cgrid.scroll.parent.y    
        
        if matrix[self.matrix[0],self.matrix[1]] in gates_2:
            for i in multigates:
                if i[-1]==self.matrix[1] and self.matrix[0] in i:
                    prev= i[:]
                    i.pop(-1)
                    pressed =  matrix[prev[0]][self.matrix[1]] 
                    for j in i:
                        cgrid.rows[j].cols[prev[-1]].remove_widget(cgrid.rows[j].cols[prev[-1]].gate)
                        matrix[j][self.matrix[1]]=''
                    cgrid.rows[prev[0]].cols[prev[-1]].canvas.before.remove_group('multigate')
                        
                    multigate=(prev[0], prev[-1], pressed, gates_2[pressed])
                    prev.pop(-1)
                    pressed = 'dragmulti'
                    multigates.remove(i)
                    
                    cgrid.scatter =Gate_mouse(text=multigate[2],pos=(posx,posy))
                    cgrid.add_widget(cgrid.scatter)
                        
        else:
            pressed=self.text
            try: 
                self.parent.remove_widget(self)
            except:
                pass
            matrix[self.matrix[0],self.matrix[1]]=''
            
       
            cgrid.scatter =Gate_mouse(text=pressed, pos=(posx,posy))
            cgrid.add_widget(cgrid.scatter)
        
        
    def on_touch_move(self, touch):
        cgrid.scatter.center=touch.pos
        
    


class Gate_panel(Button):
    def __init__ (self, **kwargs):
        super(Gate_panel, self).__init__(**kwargs)
        self.always_release=True
        self.bind(on_press=self.press)
        self.bind(on_release=self.release)
        self.size_hint=(None,None)
        self.size= (cellsize,cellsize)
        self.background_down = self.background_normal

    def press(self, *args):
        global pressed
        global cgrid
        if pressed=='multigate':
            cgrid.rows[0].cols[0].deletecurrent()
            
        pressed=self.text
        cgrid.scatter =Gate_mouse(pos=(-100,-100))
        cgrid.add_widget(cgrid.scatter)

    def release(self, *args):
        global pressed
        pressed=''
        cgrid.remove_widget(cgrid.scatter)
        
    def on_touch_move(self, touch):
        cgrid.scatter.center=touch.pos
    
    

class GatesGrid(GridLayout):
    def __init__(self, **kwargs):
        super(GatesGrid, self).__init__(**kwargs)
        self.rows=1
        self.spacing=10,10
      
        for i in gates_list:
            self.add_widget(Gate_panel(text=i))
            
        

class CCell(FloatLayout):
    def __init__ (self, **kwargs):
        super(CCell, self).__init__(**kwargs)
        
        
    
    def on_touch_up(self, touch):
        global currentcell
        global matrix
        global row_name
        global pressed
        global multigate
        global rowsconnected
        global prev
        global multigates
        global canvascell
     
        scrollview=self.parent.parent.parent
        floatlay=self.parent.parent
        refx=self.x-scrollview.scroll_x*(floatlay.width-scrollview.width)
        refy=self.y-scrollview.scroll_y*(floatlay.height-scrollview.height)+scrollview.y
        
        
        if (refy < touch.y <refy+cellsize) and (refx < touch.x <refx+cellsize):  
            if pressed != '':
                row=matrix.shape[0]-self.parent.parent.children.index(self.parent)-1
                col=matrix.shape[1]-self.parent.children.index(self)-1  
                
                if pressed == 'multigate':
                    self.secondclick(row,col)
                    
                            
                elif pressed in gates_2:
                    if currentcell != '':
                        self.remove_widget(self.gate)
                    gate=Gate_circuit(text=(pressed), pos=(self.x+0.05*cellsize, self.y+0.05*cellsize))
                    currentcell= pressed
                    self.gate=gate
                    self.add_widget(self.gate)
                    self.gate.matrix=(row,col)
                    multigate=(row, col, pressed, gates_2[pressed])
                    rowsconnected=[row]
                    Clock.schedule_once(lambda dt:self.multigate(), 0)
                    
                    canvascell=cgrid.rows[row].cols[col]
                    with canvascell.canvas.before:
                        Color(0,0,0,0.5)
                        canvascell.rect=Rectangle(group='multigate',size=canvascell.size,pos=canvascell.pos)
                    
                elif pressed == 'dragmulti':
                    for i in prev:
                        if matrix[i][col] != '':
                            cgrid.rows[i].cols[col].remove_widget(cgrid.rows[i].cols[col].gate)
                        if prev.index(i)==0:
                            gatetext=multigate[2]
                        else:
                            if multigate[2] in ('SWAP'):
                                pref=''
                            else:
                                pref='--'
                            gatetext=pref+multigate[2]
                        gate=Gate_circuit(text=gatetext, pos=(cgrid.rows[i].cols[col].x+0.05*cellsize, cgrid.rows[i].cols[col].y+0.05*cellsize))
                        matrix[i][col]= multigate[2]
                        
                        cgrid.rows[i].cols[col].gate=gate
                        cgrid.rows[i].cols[col].add_widget(cgrid.rows[i].cols[col].gate)
                        cgrid.rows[i].cols[col].gate.matrix=(i,col)
                    currentcell=multigate[2]
                    prev.append(col)
                    multigates.append(prev)
                    
                    cgrid.rows[prev[0]].cols[prev[-1]].multigate_lines(prev)
                    
                
                else:
                    if currentcell != '':
                        self.remove_widget(self.gate)
                    gate=Gate_circuit(text=pressed, pos=(self.x+0.05*cellsize, self.y+0.05*cellsize))
                    currentcell= pressed
                    self.gate=gate
                    
                    self.add_widget(self.gate)
                    self.gate.matrix=(row,col)

        
        super(CCell, self).on_touch_up(touch)
    
    def multigate_lines(self, gaterows):
        global cgrid
        with self.canvas.before:
            Color(0,0,0,0.5)
            self.rect=Rectangle(group='multigate',size=self.size,pos=self.pos)
            for i in gaterows[1:-1]:
                canvascell2=cgrid.rows[i].cols[gaterows[-1]]
                self.rect=Rectangle(group='multigate',size=canvascell2.size,pos=canvascell2.pos)
                self.line=Line(
                    points= (self.x+self.width/2., self.y+self.height/2.,
                             canvascell2.x+canvascell2.width/2., canvascell2.y+canvascell2.height/2.),
                    width= 1.5, cap= 'none', group='multigate')
               
    def multigate(self):
        global pressed
        pressed='multigate'
    
    def deletecurrent(self, *args):
        global rowsconnected
        global matrix
        global cgrid
        global multigate
        global pressed
        global canvascell
        
        for i in rowsconnected:
            cgrid.rows[i].cols[multigate[1]].remove_widget(cgrid.rows[i].cols[multigate[1]].gate)
            #print('before:',matrix[i][col])
            matrix[i][multigate[1]]=''
            #print(matrix[i][col])
        pressed=''
        canvascell.canvas.before.remove_group('multigate')
        
        
    def secondclick(self, row, col):
        global multigate
        global cgrid
        global matrix
        global currentcell
        global pressed
        global rowsconnected
        global canvascell
        
        if (multigate[1]!=col) or (row in rowsconnected):
            Clock.schedule_once(lambda dt:self.deletecurrent(), 0.05)
            
        else:
            if currentcell != '':
                self.remove_widget(self.gate)
            rowsconnected.append(row)
            if multigate[2] in ('SWAP'):
                pref=''
            else:
                pref='--'
            gate=Gate_circuit(text=(pref+multigate[2]),pos=(self.x+0.05*cellsize, self.y+0.05*cellsize))
            currentcell= multigate[2]
            
            self.gate=gate
            self.add_widget(self.gate)
            self.gate.matrix=(row,col)
            
            pressed=''
            
            multigate=(multigate[0], multigate[1], multigate[2],multigate[3]-1)
            
            with canvascell.canvas.before:
                    Color(0,0,0,0.5)
                    canvascell.rect=Rectangle(group='multigate',size=canvascell.size,pos=self.pos)
                    canvascell.line=Line(
                    points= (canvascell.x+canvascell.width/2., canvascell.y+canvascell.height/2.,
                             self.x+self.width/2., self.y+self.height/2.),
                    width= 1.5, cap= 'none', group='multigate')
            
            if multigate[3] > 1:
                self.multigate()
                
            else:
                rowsconnected.append(col)
                multigates.append(rowsconnected)
                
            
            
            
                    
       
                

class CRow(FloatLayout):
    global matrix
    def __init__(self, **kwargs):
        global row_num
        super(CRow, self).__init__(**kwargs)
        self.cols=[]
        row_num=matrix.shape[0]
        self.reini(-1)
        
    def refresh_row(self, num):
        global currentcell
        global matrix
        global multigates
        global cgrid
        
        self.clear_widgets()
        self.reini(num)
        for i in range(len(self.cols)):
            self.add_widget(self.cols[i])
            if matrix[num][i] != '':
                    self.cols[i].remove_widget(self.cols[i].gate)
                    if matrix[num][i] in gates_2:
                        for j in multigates:
                            if j[-1]==i and num in j:
                                if j.index(num)==0:
                                    gatetext=matrix[num][i]
                                  
                                    cgrid.rows[num].cols[i].canvas.before.remove_group('multigate')
                                    cgrid.rows[num].cols[i].multigate_lines(j)
                                else:
                                    if matrix[num][i] in ('SWAP'):
                                        pref=''
                                    else:
                                        pref='--'
                                    gatetext=pref+matrix[num][i]
                    else:
                        gatetext=matrix[num][i]
                        currentcell=matrix[num][i]
                    self.cols[i].gate=Gate_circuit(text=gatetext, pos=(self.cols[i].x+0.05*cellsize, self.y+0.05*cellsize))

                    self.cols[i].add_widget(self.cols[i].gate)
                    self.cols[i].gate.matrix=(num, i)
        return matrix
    
    def add_cell(self):
        self.cols.append(CCell(size_hint= (None, None), size= (cellsize,cellsize), pos_hint= {"y":0}, pos=(self.x+cellsize*(len(self.cols)+0.5)+70,0)))
        self.add_widget(self.cols[-1])
        
    def remove_cell(self):
        if len(self.cols) != 0:
            self.remove_widget(self.cols[-1])
            self.cols.pop(-1)
            
    def delete(self):
        global row_name
        global matrix
        global cgrid
        
        if pressed=='multigate':
            cgrid.rows[0].cols[0].deletecurrent()
        num=row_name.index(self.name_label.text)
        
        row_name.pop(num)
        for i in range(len(row_name)-num):
            if row_name[i+num] == ('q'+str(i+num+1)):
                row_name[i+num] = ('q'+str(i+num))
        
        for i in multigates:
            for j in range(len(i)-1):
                if i[j]==num:
                    col=i[-1]
                    for k in range(len(i)-1):
                        
                        matrix[i[k]][col]=''
                        cell=cgrid.rows[i[k]].cols[col]
                        cell.remove_widget(cell.gate)
                    cgrid.rows[i[0]].cols[col].canvas.before.remove_group('multigate')
    
        
        matrix=np.delete(matrix, num, axis=0)
        self.parent.parent.parent.rows.pop(num)
        self.parent.remove_widget(self)
        
        Clock.schedule_once(lambda dt:cgrid.refresh(), 0)
        
        
    def reini(self, num):
        global row_name
        qname=row_name[num]
        self.name_label=Label(text=qname,
                              color=(0,0,0,1),
                              halign='left',
                              texture_size=(30,30),
                              text_size=(40, None), 
                              pos_hint={"center_y":0.5}, 
                              pos= (25,0))
        self.add_widget(self.name_label)
        self.add_widget(Button(text="X", 
                               size_hint= (None, None), 
                               size= (self.height/2. , self.height/2.),
                               pos_hint= {"center_y": 0.5},
                               pos= (10,0),
                               on_release= lambda a:self.delete()))
        

class CGrid(FloatLayout):
    grid = ObjectProperty(None)
    scroll=ObjectProperty(None)
    
    def __init__(self, **kwargs):
        global cgrid
        super(CGrid, self).__init__(**kwargs)
        self.rows=[]
        for i in range(2):
            Clock.schedule_once(lambda dt:self.add_row(), 0.5)
        for i in range(12):
            Clock.schedule_once(lambda dt:self.add_col(), 0.5)
        Clock.schedule_once(lambda dt:self.resize_scroll(), 1.2)
            
        Window.bind(on_resize=Clock.schedule_once(lambda dt:self.resize_scroll(), 0))
        Window.bind(on_resize=Clock.schedule_once(lambda dt:self.set_scroll(), 0))
        cgrid=self
        
    def on_touch_up(self, touch):
        global matrix
        global currentcell
        if self.collide_point(*touch.pos):
            for i in range(matrix.shape[0]):
                for j in range(matrix.shape[1]):
                    currentcell=matrix[i][j]
                    self.rows[i].cols[j].on_touch_up(touch)
                    matrix[i][j]=currentcell
        root.sm.screen1.QiskitConv()
                    
                    
            #super(CGrid, self).on_touch_up(touch)
            
        
    def add_col(self): #Adds column to matrix and rows
        global matrix
        matrix=np.append(matrix, np.empty((matrix.shape[0],1), str), axis=1)
        for i in range(matrix.shape[0]):
            self.rows[i].add_cell()
        self.resize_scroll()
        return matrix

    def refresh(self): #Refresh buttons
        self.resize_scroll()
        for i in range(matrix.shape[0]):
            self.rows[i].pos= (0, self.scroll.y+(cellsize+space)*(matrix.shape[0]-i-1))
            self.rows[i].refresh_row(i)
        root.sm.screen1.QiskitConv()
            
    
    def remove_col(self): #Remove column from matrix and rows
        global matrix
        if matrix.shape[1] != 0:
            matrix=np.delete(matrix, -1, axis=1)
        for i in range(matrix.shape[0]):
            self.rows[i].remove_cell()
        self.resize_scroll()
        return matrix
    
    def add_row(self): #Add row
        global matrix
        global row_name
        matrix=np.append(matrix, np.empty((1,matrix.shape[1]), str), axis=0)
        row_name.append('q'+str(len(row_name)))
        self.rows.append(CRow(pos= (0, self.scroll.y-(cellsize+space)*(matrix.shape[0]-1))))
        self.scroll.add_widget(self.rows[-1])
        for i in range(matrix.shape[1]):
            self.rows[-1].add_cell()
        self.refresh()
        Clock.schedule_once(lambda dt:self.refresh(), 0)
    
    def resize_scroll(self, *args):
        self.scroll.size=(cellsize*(matrix.shape[1]+1.5)+70,(cellsize+space)*(matrix.shape[0]+0.5))
    
    def set_scroll(self): #Necessary to avoid problems when resizing
        self.scroll.parent.scroll_x=0.0
        self.scroll.parent.scroll_y=1.0
    
    def resize_panels(self, prob, gates):
        width=0.7 if prob else 1
        height=0.62 if gates else 0.92
        self.parent.parent.size_hint=(width, height)
        Clock.schedule_once(lambda dt:self.resize_scroll(), 0)
        Clock.schedule_once(lambda dt:self.set_scroll(), 0)

    def add_element2(self, *args):
        global pressed
        global matrix
        global multigates
       # print(root.sm.screen1.problabel.text)
        print(probabilities)
        print(matrix)
        print(multigates)
       
class WindowManager(ScreenManager):
    screen1 = ObjectProperty(None)
    pass 

class QComp(App):
    def build(self):
        global root
        root=self
        self.sm = WindowManager()
        return self.sm
        



class Screen1(Screen):
    problabel = ObjectProperty(None)
    plotbox = ObjectProperty(None)
    
    
    def QiskitConv(self, *args):
        global matrix
        global multigates
        global row_name
        global gates_2
        global results
        global state
        global probabilities
        
        
        QiskitConverter(matrix, multigates, row_name, gates_2)
        importlib.reload(QiskitCircuit)
        
        results=QiskitCircuit.GetStatevector()
        
        self.problabel.text, probabilities=(GetResults(results))
        self.plotbox.clear_widgets()
        
        
        plt.barh(list(probabilities.keys()), list(probabilities.values()))
        plt.xlim(0,100)
        self.plotbox.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        plt.close()
        
        
    def ShowQSpehre(self):
        plot=plot_state_qsphere(results)
        plt.show(plot)
        
    def ShowBlochSpheres(self):
        plot=plot_bloch_multivector(results)
        plt.show(plot)
        
    def ShowDensityMatrix(self):
        plot=plot_state_city(results)
        plt.show(plot)
        
    def ShowDensityMatrix2D(self):
        plot=plot_state_hinton(results)
        plt.show(plot)
        
    def ShowHistogram(self):
        plot=plot_histogram(probabilities)
        plt.show(plot)
    

def GetResults(args):

    results=args
    probtext='|'+' '.join(reversed(row_name))+'>:  Prob, Phase\n\n'
    probabilities={}

    for i in range(len(results)):
        state = str(np.binary_repr(i, width=matrix.shape[0]))
        angle=np.angle(results[i])
        
        if abs(results[i]) > 0.001:
            probabilities[state]=np.absolute(results[i])**2*100
            ratio=(angle/np.pi).as_integer_ratio()
            if (abs(angle)>0.00001) and (abs(ratio[1])<10):
                if ratio[0]==1:
                    phase='pi'
                elif ratio[0]==-1:
                    phase='-pi'
                else:
                    phase=str(ratio[0])+'pi'
                if ratio[1]==1:
                    pass
                else:
                    phase=phase + '/'+str(ratio[1])
            elif (abs(angle)>0.00001):
                phase='{0:.3g}'.format(np.angle(results[i]))
            else:
                phase='0'
            probtext=probtext+'|'+state+'>'+':  '+'{0:.3g}'.format(np.absolute(results[i])**2*100)+'%, '\
            +phase+'\n'
            
    return probtext, probabilities
    
    

class Screen2(Screen):
    pass


        

if __name__ =='__main__':
    QComp().run()