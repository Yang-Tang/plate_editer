#!/usr/bin/env python

import string
import wx
ROW_NAMES = list(string.ascii_uppercase)
COLUMN_NAMES = map(str, range(1, 100))

class Sample(object):
    def __init__(self, name):
        self.name = name
        self.group = None
        self.wells = set()
        
    def getName(self):
        return self.name
    
    def isControl(self):
        return self.getGroup().isControl()
    
    def setGroup(self, group):
        self.group = group
        return self
        
    def getGroup(self):
        return self.group
    
class SampleList(object):
    def __init__(self, name, start, n):
        self.samples = []
        for i in range(start, start + n):
            sample = Sample(name + '_' + str(i))
            self.samples.append(sample)
            
    def getSamples(self):
        return self.samples
    
    def subset(self, start, n = 1):
        tmp = []
        for i in range(start, start + n):
            try:
                tmp.append(self.samples[i - 1])
            except IndexError:
                break
        return tmp

class Group(object):
    def __init__(self, name):
        self.name = name
        self.samples = []
        self.treatment = {}
        self.control = False
        
    def addSample(self, sample):
        if not sample in self.samples:
            self.samples.append(sample)
            sample.group = self
        return self
            
    def addSampleList(self, list_of_samples):
        for sample in list_of_samples:
            self.addSample(sample)
        return self
        
    def getName(self):
        return self.name
    
    def getSample(self, sample_name):
        for sample in self.samples:
            if sample.getName() == sample_name:
                return sample
        else:
            return None
    
    def getSamples(self):
        return self.samples
    
    def setTreatment(self, treatment, value):
        self.treatment[treatment] = value
        return self
    
    def isControl(self):
        return self.control

class Detector(object):
    def __init__(self, name):
        self.name = name
        self.value = None
        self.control = False
        self.wells = set()
        
    def getName(self):
        return self.name
    
    def setValue(self, value):
        self.value = value
        return self
        
    def getValue(self):
        return self.value

    def isControl(self):
        return self.control
    
class Well(object):
    def __init__(self, address, plate):
        self.address = address
        self.omit = False
        self.plate = plate
        self.samples = set()
        self.detectors = set()
        self.ui = Well_ui(self.plate.ui, self.plate, self)
        print 'well inited!'
#
    def addSample(self, sample):
        self.samples.add(sample)
        sample.wells.add(self)
        return self
    def addDetector(self, detector):
        self.detectors.add(detector)
        detector.wells.add(self)
        return self
    def removeSample(self, sample):
        self.samples.discard(sample)
        sample.wells.discard(self)
        return self
    def removeDetector(self, detector):
        self.detectors.discard(detector)
        detector.wells.discard(self)
        return self
    def clearSamples(self):
        for sample in self.samples:
            sample.wells.discard(self)
        self.samples.clear()
        return self
    def clearDetectors(self):
        for detector in self.detectors:
            detector.wells.discard(self)
        self.detectors.clear()
        return self
    def clearAll(self):
        self.clearSamples()
        self.clearDetectors()
        return self
    def copySamplesTo(self, new_well):
        new_well.clearSamples()
        for sample in self.samples:
            new_well.addSample(sample)
        return self
    def copyDetectorsTo(self, new_well):
        new_well.clearDetectors()
        for detector in self.detectors:
            new_well.addDetector(detector)
        return self
    def copyAllTo(self, new_well):
        self.copySamplesTo(new_well)
        self.copyDetectorsTo(new_well)
        return self
    def moveSamplesTo(self, new_well):
        new_well.clearSamples()
        for sample in self.samples:
            new_well.addSample(sample)
        self.clearSamples()
        return self
    def moveDetectorsTo(self, new_well):
        new_well.clearDetectors()
        for detector in self.detectors:
            new_well.addDetector(detector)
        self.clearDetectors()
        return self
    def moveAllTo(self, new_well):
        self.moveSamplesTo(new_well)
        self.moveDetectorsTo(new_well)
        return self
    def getSampleNames(self):
        tmp = ''
        for i in self.samples:
            tmp += i.getName() + ';'
        if tmp == '':
            tmp = 'NA'
        return tmp
    def getGroupNames(self):
        tmp = ''
        for i in self.samples:
            tmp += i.getGroup().getName() + ';'
        if tmp == '':
            tmp += 'NA'
        return tmp
    def getDetectorNames(self):
        tmp = ''
        for i in self.detectors:
            tmp += i.getName() + ';'
        if tmp == '':
            tmp += 'NA'
        return tmp
    def getDetectorValues(self):
        tmp = ''
        for i in self.detectors:
            tmp += i.getName() + ':' + str(i.getValue()) + ';'
        if tmp == '':
            tmp = 'NA'
        return tmp
    def offset(self, n_rows, n_columns):
        r = ROW_NAMES.index(self.address[0])
        c = COLUMN_NAMES.index(self.address[1:])
        try:
            new_address = ROW_NAMES[r + n_rows] + COLUMN_NAMES[c + n_columns]
        except IndexError:
            return None
        return self.plate.getWell(new_address)

class Plate(object):
    def __init__(self, name = 'Plate', n_rows = 8, n_columns = 12):
        self.name = name
        self.n_rows = n_rows
        self.n_columns = n_columns
        self.ui = Plate_ui(None, self)
        self.wells = {}
        self.grid = wx.GridSizer(self.n_rows, self.n_columns, 1, 1)
        n = 0
        for j in range(self.n_rows):
            for i in range(self.n_columns):
                address = ROW_NAMES[j] + COLUMN_NAMES[i]
                well = Well(address, self)
                self.wells[address] = well
                self.grid.Add(well.ui, 1, wx.EXPAND|wx.ALL, 0)
                n += 1
                #self.ui.gauge.SetValue(n)
        print 'Plate inited!'

    def getName(self):
        return self.name
    def getNrows(self):
        return self.n_rows
    def getNcols(self):
        return self.n_columns
    def getRow_names(self):
        return ROW_NAMES[:self.n_rows]    
    def getColumn_names(self):
        return COLUMN_NAMES[:self.n_columns]    
    def getWell(self, address):
        return self.wells.get(address.upper(), None)    
    def wellInPlate(self, well):
        return well.plate == self    
    def rangeInPlate(self, myRange):
        return myRange.plate == self
    def initui(self):

        self.ui.vbox.Add(self.grid, proportion = 1, flag=wx.EXPAND|wx.ALL, border = 10)

        #self.ui.SetSizer(vbox)

        self.ui.SetSizer(self.ui.vbox)
        self.ui.SetSize((self.n_columns * 75, self.n_rows * 60))
        self.ui.SetTitle(self.name)
        self.ui.Centre()
        self.ui.Show()
        self.over_well = None
        self.start_well = None
        self.selected_rng = None

class Range(object):
    def __init__(self, start_well, end_well):
        self.plate = start_well.plate
        self.wells = set()
        column_names = self.plate.getColumn_names()
        row_names = self.plate.getRow_names()
        i1 = column_names.index(start_well.address[1:])
        i2 = column_names.index(end_well.address[1:])
        j1 = row_names.index(start_well.address[0])
        j2 = row_names.index(end_well.address[0])
        i0 = min(i1, i2)
        j0 = min(j1, j2)
        self.start_well = self.plate.getWell(row_names[j0] + column_names[i0])
        self.n_rows = abs(j1 - j2) + 1
        self.n_columns = abs(i1 - i2) + 1
        self.column_names = column_names[i0 : (i0 + self.n_columns)]
        self.row_names = row_names[j0 : (j0 + self.n_rows)]
        for i in range(self.n_columns):
            for j in range(self.n_rows):
                well = self.start_well.offset(j, i)
                self.wells.add(well)

    def getPlate(self):
        return self.plate
    def getRow_names(self):
        return self.row_names    
    def getColumn_names(self):
        return self.column_names    
    def getWell(self, address):
        return self.plate.wells.get(address.upper(), None)    
    def getStartWell(self):
        return self.start_well
    
    def wellInRange(self, well):
        return well in self.wells
    
    def rangeInRange(self, myRange):
        if myRange.plate <> self.plate:
            return False
        for well in myRange.wells:
            if not self.wellInRange(well):
                return False
        return True
    
    def show(self, item = 'address'):
        output = '' + chr(9) + chr(9).join(self.getColumn_names()) + chr(10)
        for j in range(self.n_rows):
            output += self.getRow_names()[j] + chr(9)
            for i in range(self.n_columns):
                well = self.start_well.offset(j, i)
                if item.lower() == 'address':
                    output += well.address
                elif item.lower() == 'sample':
                    output += well.getSampleNames() 
                elif item.lower() == 'group':
                    output += well.getGroupNames() 
                elif item.lower() == 'detector':
                    output +=  well.getDetectorNames() 
                elif item.lower() == 'value':
                    output +=  well.getDetectorValues() 
                output += chr(9)
            output += chr(10)
        return output
    
    def offset(self, n_rows, n_columns):
        start_well = self.getStartWell().offset(n_rows, n_columns)
        end_well = self.getStartWell().offset(self.n_rows - 1, self.n_columns - 1).offset(n_rows, n_columns)
        if start_well == None:
            return None
        elif end_well == None:
            return None
        else:
            return Range(start_well, end_well)
        
    def autoFill(self, item = 'sample', entry = [], index = 0, n_row = 2, n_column = 2, direction = 1, s_shape = False):
        x = self.n_columns / n_column
        y = self.n_rows / n_row
        if direction == 1:
            for i in range(x):
                for j in range(y):
                    well = self.getStartWell().offset(j*n_row, i*n_column)
                    for m in range(n_column):
                        for n in range(n_row):
                            if item.lower() == 'sample':
                                well.offset(n, m).addSample(entry[index % len(entry)])
                            elif item.lower() == 'detector':
                                well.offset(n, m).addDetector(entry[index % len(entry)])
                    index += 1
        elif direction == 2:
            for j in range(y):
                for i in range(x):
                    well = self.getStartWell().offset(j*n_row, i*n_column)
                    for m in range(n_column):
                        for n in range(n_row):
                            if item.lower() == 'sample':
                                well.offset(n, m).addSample(entry[index % len(entry)])
                            elif item.lower() == 'detector':
                                well.offset(n, m).addDetector(entry[index % len(entry)])
                    index += 1
        return index

    def copyTo(self, new_range, item = 'all'):
        tmp_plate = Plate('tmp', self.plate.n_rows, self.plate.n_columns)
        address0 = self.getStartWell().address
        address1 = new_range.getStartWell().address
        j = ROW_NAMES.index(address1[0]) - ROW_NAMES.index(address0[0])
        i = COLUMN_NAMES.index(address1[1:]) - COLUMN_NAMES.index(address0[1:])
        for well in self.wells:
            if item.lower() == 'all':
                well.copyAllTo(tmp_plate.getWell(well.address))
            elif item.lower() == 'sample':
                well.copySamplesTo(tmp_plate.getWell(well.address))
            elif item.lower() == 'detector':
                well.copyDetectorsTo(tmp_plate.getWell(well.address))
        for well in self.wells:
            new_well = new_range.plate.getWell(well.address).offset(j, i)
            if new_well <> None:
                tmp_plate.getWell(well.address).copyAllTo(new_well)
                
    def moveTo(self, new_range, item = 'all'):
        tmp_plate = Plate('tmp', self.plate.n_rows, self.plate.n_columns)
        address0 = self.getStartWell().address
        address1 = new_range.getStartWell().address
        j = ROW_NAMES.index(address1[0]) - ROW_NAMES.index(address0[0])
        i = COLUMN_NAMES.index(address1[1:]) - COLUMN_NAMES.index(address0[1:])
        for well in self.wells:
            if item.lower() == 'all':
                well.moveAllTo(tmp_plate.getWell(well.address))
            elif item.lower() == 'sample':
                well.moveSamplesTo(tmp_plate.getWell(well.address))
            elif item.lower() == 'detector':
                well.moveDetectorsTo(tmp_plate.getWell(well.address))
        for well in self.wells:
            new_well = new_range.plate.getWell(well.address).offset(j, i)
            if new_well <> None:
                tmp_plate.getWell(well.address).copyAllTo(new_well)
                
    def clear(self, item = 'all'):
        for well in self.wells:
            if item.lower() == 'all':
                well.clearAll()
            elif item.lower() == 'sample':
                well.clearSamples()
            elif item.lower() == 'detector':
                well.clearDetectors()

#UI
class Well_ui(wx.Panel):
    def __init__(self, parent, plate, well, over_color = '#F5F5F5', active_color = '#FFF8DC', inactive_color = 'white'):
        super(Well_ui, self).__init__(parent)
        self.plate = plate
        self.well = well
        self.active = False
        self.over_color = over_color
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.color = self.inactive_color
        self.SetBackgroundColour(self.color)
        self.mouseover = False
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftdown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftup)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeydown)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyup)
        font9 = wx.Font(9, wx.MODERN, wx.SLANT, wx.NORMAL, False, u'Consolas')
        font8 = wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.t1 = wx.StaticText(self, label=self.well.address, pos = (1, 0))
        self.t1.SetFont(font9)
        self.t2 = wx.StaticText(self, label=self.well.getSampleNames(), pos = (1, 13))
        self.t2.SetFont(font8)
        self.t1.Bind(wx.EVT_LEFT_DOWN, self.OnLeftdown)
        self.t2.Bind(wx.EVT_LEFT_DOWN, self.OnLeftdown)
        self.t1.Bind(wx.EVT_LEFT_UP, self.OnLeftup)
        self.t2.Bind(wx.EVT_LEFT_UP, self.OnLeftup)
        self.t1.Bind(wx.EVT_MOTION, self.OnMotion)
        self.t2.Bind(wx.EVT_MOTION, self.OnMotion)
    
    def OnKeydown(self, e):
        keymap = {65 : (0, -1),
                  83 : (1, 0),
                  68 : (0, 1),
                  87 : (-1, 0)}
        print e.GetKeyCode()
        key = e.GetKeyCode()
        a = keymap.get(key)
        if a <> None and self.plate.over_well <> None:
            old_well = self.plate.over_well
            new_well = old_well.offset(a[0], a[1])
            if new_well <> None:
                old_well.ui.mouseover = False
                old_well.ui.update()
                new_well.ui.mouseover = True
                new_well.ui.update()
                self.plate.over_well = new_well
                if e.ControlDown():
                    new_rng = Range(self.plate.start_well, self.plate.over_well)
                    print new_rng.show()
                    if self.plate.over_well in self.plate.selected_rng.wells:
                        for well in self.plate.selected_rng.wells - new_rng.wells:
                            well.ui.active = False
                            well.ui.update()
                    else:
                        for well in new_rng.wells - self.plate.selected_rng.wells:
                            well.ui.active = True
                            well.ui.update()
                    self.plate.selected_rng = new_rng
        elif a == None:
            if key == 308:
                if self.plate.selected_rng == None:
                    self.plate.selected_rng = Range(self.plate.over_well, self.plate.over_well)
                    self.plate.start_well = self.plate.over_well
                    self.plate.over_well.ui.active = True
                    self.plate.over_well.ui.update()

    def OnKeyup(self, e):
        if e.GetKeyCode() == 308:
            self.OnLeftup(e)
                  
    
    def OnMotion(self, e):
        #print 'move'
        #if self.well <> self.plate.over_well:
        if self.plate.over_well <> None:
            self.plate.over_well.ui.mouseover = False
            self.plate.over_well.ui.update()
        self.plate.over_well = self.well
        self.SetFocus()
        self.mouseover = True
        self.update()
        if e.LeftIsDown():
            if self.plate.selected_rng == None:
                #self.plate.over_well = self.well
                #self.mouseover = True
                self.plate.selected_rng = Range(self.plate.over_well, self.plate.over_well)
                self.plate.start_well = self.well
                self.active = True
                self.update()
            else:
                new_rng = Range(self.plate.start_well, self.well)
                if self.well in self.plate.selected_rng.wells:
                    for well in self.plate.selected_rng.wells - new_rng.wells:
                        well.ui.active = False
                        well.ui.update()
                else:
                    for well in new_rng.wells - self.plate.selected_rng.wells:
                        well.ui.active = True
                        well.ui.update()
                self.plate.selected_rng = new_rng
   
    def update(self):
        if self.active:
            self.color = self.active_color
        elif self.mouseover:
            self.color = self.over_color
        else:
            self.color = self.inactive_color
        self.SetBackgroundColour(self.color)
        if self.Parent.item == 'sample':
            self.t2.SetLabel(self.well.getSampleNames())
        elif self.Parent.item == 'detector':
            self.t2.SetLabel(self.well.getDetectorNames())
        elif self.Parent.item == 'value':
            self.t2.SetLabel(self.well.getDetectorValues())
        self.Parent.Info_Address.SetLabel(self.well.address)
        self.Parent.Info_Samples.SetLabel(self.well.getSampleNames())
        self.Parent.Info_Detectors.SetLabel(self.well.getDetectorNames())
        self.Refresh()

    def OnLeftdown(self, e):
        self.plate.selected_rng = Range(self.plate.over_well, self.plate.over_well)
        self.plate.start_well = self.well
        self.active = True
        self.plate.over_well = self.well
        self.SetFocus()
        self.mouseover = True
        self.update()
    
    def OnLeftup(self, e):
        self.plate.selected_rng.autoFill(item = self.Parent.item,
                                         entry = self.Parent.entry,
                                         index = self.Parent.index[self.Parent.item],
                                         n_row = self.Parent.Settings_row.GetValue(),
                                         n_column = self.Parent.Settings_col.GetValue(),
                                         direction = self.Parent.direction)
        
        for well in self.plate.selected_rng.wells:
            well.ui.active = False
            well.ui.update()
        self.plate.selected_rng = None
    
class Plate_ui(wx.Frame):
    def __init__(self, parent, plate):
        super(Plate_ui, self).__init__(parent)
        self.plate = plate
        self.item = 'sample'
        self.index = {'sample' : 0, 'detector' : 0}
        self.direction = 1
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftdown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftup)
        self.entry = sample
        self.initui()
        self.bind_event()

    def initui(self):
        toppanel = wx.Panel(self)
        #panel.SetBackgroundColour('red')
        pos = 0
        hight = 85
        width = 120
        gap = 5
        pos += gap
        wx.StaticBox(toppanel, label='Raw data', pos=(pos, 0), size=(width, hight))
        wx.Button(toppanel, label='Load Raw Data', pos=(pos + gap, 30))
        pos += width
        
        width = 85
        pos += gap
        wx.StaticBox(toppanel, label='Operation', pos=(pos, 0), size=(width, hight))
        wx.RadioButton(toppanel, label='Fill', pos=(pos + gap, 20), style=wx.RB_GROUP)
        wx.RadioButton(toppanel, label='Clear', pos=(pos + gap, 40))
        pos += width
        
        width = 90
        pos += gap
        wx.StaticBox(toppanel, label='Items', pos=(pos, 0), size=(width, hight))
        self.Items_Samples = wx.RadioButton(toppanel, label='Samples', pos=(pos + gap, 20), style=wx.RB_GROUP)
        self.Items_Detectors = wx.RadioButton(toppanel, label='Detectors', pos=(pos + gap, 40))
        self.Items_Values = wx.RadioButton(toppanel, label='Values', pos=(pos + gap, 60))
        pos += width
        
        width = 300
        pos += gap
        wx.StaticBox(toppanel, label='Settings', pos=(pos, 1), size=(width, hight))
        wx.StaticText(toppanel, label='Start from:', pos=(pos + gap, 20))
        wx.StaticText(toppanel, label='Size (x*y):', pos=(pos + gap, 50))
        pos1 = pos + 80
        choice_list = []
        for i in self.entry:
            choice_list.append(i.name)
        self.Settings_entry = wx.ComboBox(toppanel, pos=(pos1, 20), size=(80, -1), choices=choice_list, style=wx.CB_READONLY)
        self.Settings_entry.SetValue(choice_list[0])
        self.Settings_col = wx.SpinCtrl(toppanel, value='2', pos=(pos1, 50), size=(40, -1))
        self.Settings_col.SetRange(1, self.plate.n_columns)
        pos1 += 42
        wx.StaticText(toppanel, label='x', pos=(pos1, 50))
        pos1 += 8
        self.Settings_row = wx.SpinCtrl(toppanel, value='2', pos=(pos1, 50), size=(40, -1))
        self.Settings_row.SetRange(1, self.plate.n_rows)
        pos1 += 55
        wx.StaticText(toppanel, label='Direction:', pos=(pos1, 20))
        pos1 += 5
        self.Settings_Direction1 = wx.RadioButton(toppanel, label='Top to botton', pos=(pos1, 40), style=wx.RB_GROUP)
        self.Settings_Direction2 = wx.RadioButton(toppanel, label='Left to right', pos=(pos1, 60))
        pos += width
        
        width = 200
        pos += gap
        wx.StaticBox(toppanel, label='Info', pos=(pos, 1), size=(width, hight))
        wx.StaticText(toppanel, label='Address:', pos=(pos + gap, 20))
        wx.StaticText(toppanel, label='Samples:', pos=(pos + gap, 40))
        wx.StaticText(toppanel, label='Detectors:', pos=(pos + gap, 60))
        pos1 = pos + 70
        self.Info_Address = wx.StaticText(toppanel, label='NA', pos=(pos1, 20))
        self.Info_Samples = wx.StaticText(toppanel, label='NA', pos=(pos1, 40))
        self.Info_Detectors = wx.StaticText(toppanel, label='NA', pos=(pos1, 60))
        pos += width

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(toppanel, 0, flag=wx.EXPAND|wx.LEFT|wx.TOP|wx.RIGHT, border = 0)
        
    def bind_event(self):
        self.Items_Samples.Bind(wx.EVT_RADIOBUTTON, self.OnItemchange)
        self.Items_Detectors.Bind(wx.EVT_RADIOBUTTON, self.OnItemchange)
        self.Items_Values.Bind(wx.EVT_RADIOBUTTON, self.OnItemchange)
        self.Settings_Direction1.Bind(wx.EVT_RADIOBUTTON, self.OnDirectionchange)
        self.Settings_Direction2.Bind(wx.EVT_RADIOBUTTON, self.OnDirectionchange)

    def OnItemchange(self, e):
        s = self.Items_Samples.GetValue()
        d = self.Items_Detectors.GetValue()
        v = self.Items_Values.GetValue()
        if s:
            self.item = 'sample'
            self.entry = sample
            for well in self.plate.wells.values():
                well.ui.t2.SetLabel(well.getSampleNames())
                well.ui.Refresh()
            self.Settings_entry.Clear()
            choice_list = []
            for i in self.entry:
                choice_list.append(i.name)
                self.Settings_entry.Append(i.name)
            self.Settings_entry.SetValue(choice_list[0])
        elif d:
            self.item = 'detector'
            self.entry = detector
            for well in self.plate.wells.values():
                well.ui.t2.SetLabel(well.getDetectorNames())
                well.ui.Refresh()
            self.Settings_entry.Clear()
            choice_list = []
            for i in self.entry:
                choice_list.append(i.name)
                self.Settings_entry.Append(i.name)
            self.Settings_entry.SetValue(choice_list[0])
        elif v:
            self.item = 'value'
            self.entry = []
            for well in self.plate.wells.values():
                well.ui.t2.SetLabel(well.getDetectorValues())
                well.ui.Refresh()
            self.Settings_entry.Clear()

    def OnDirectionchange(self, e):
        d1 = self.Settings_Direction1.GetValue()
        d2 = self.Settings_Direction2.GetValue()
        if d1:
            self.direction = 1
        elif d2:
            self.direction = 2


    def OnLeftdown(self, e):
        self.plate.selected_rng = None
        
    def OnLeftup(self, e):
        self.plate.selected_rng.autoFill(item = self.item,
                                         entry = self.entry,
                                         index = self.index[self.Parent.item],
                                         n_row = self.Settings_row.GetValue(),
                                         n_column = self.Settings_col.GetValue(),
                                         direction = self.direction)
        for well in self.plate.selected_rng.wells:
            well.ui.active = False
            well.ui.update()
        self.plate.selected_rng = None

def main():

    app = wx.App()
    a = Plate('myplate',8,12)
    
    a.initui()
    print 'Plate showed!'
    #b = Range(a.getWell('a1'),a.getWell('d5'))
    #b.autoFill(item, entry, direction = 1)
    app.MainLoop()

if __name__ == '__main__':
    s = SampleList('s',1,40)
    naive = Group('Naive').addSampleList(s.subset(1,10))
    null = Group('Null').addSampleList(s.subset(11,10))
    neg = Group('Neg').addSampleList(s.subset(21,10))
    shRNA = Group('shRNA').addSampleList(s.subset(31,10))
    sample = naive.samples + null.samples + neg.samples + shRNA.samples
    tbp = Detector('Tbp')
    slc13a5 = Detector('NaCT')
    gapdh = Detector('Gapdh')
    detector = [tbp, slc13a5, gapdh]
    main()

#a = Plate('myplate',16,24)
#a1 = Plate('myplate2', 8, 12)
#s = SampleList('s',1,40)
#naive = Group('Naive').addSampleList(s.subset(1,10))
#null = Group('Null').addSampleList(s.subset(11,10))
#neg = Group('Neg').addSampleList(s.subset(21,10))
#shRNA = Group('shRNA').addSampleList(s.subset(31,10))
#item = 'sample'
#entry = naive.samples + null.samples + neg.samples + shRNA.samples
#b = Range(a.getWell('a1'),a.getWell('d5'))
#b.autoFill(item, entry, direction = 1)

#tbp = Detector('Tbp')
#slc13a5 = Detector('NaCT')
#gapdh = Detector('Gapdh')
#item = 'detector'
#entry = [tbp, slc13a5]
#b.autoFill(item = item, entry = entry, index = 0, n_row = 4, n_column = 1, direction = 2)

#c = Range(a.getWell('b3'), a.getWell('h12'))
#d = Range(a.getWell('a1'),a.getWell('h24'))
#print b.show()
#print d.show('sample')
#print b.show('group')
#print d.show('detector')
#print b.show('value')

#c.clear('sample')
#d1 = Range(a1.getWell('a1'),a1.getWell('h12'))
#print d.show('sample')
#print d.show('detector')
#print d1.show('sample')
#print d1.show('detector')


