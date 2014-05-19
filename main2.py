#!/usr/bin/env python
import string
import wx
ROW_NAMES = list(string.ascii_uppercase)
COLUMN_NAMES = map(str, range(1, 100))

class Sample(object):
    def __init__(self, name):
        self.name = name
        self.group = None
        self.wells = []
        
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
        self.wells = []
        
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
        self.up = None
        self.down = None
        self.left = None
        self.right = None
        self.samples = []
        self.detectors = []
        self.ui = Well_ui(self.plate.ui, self.plate, self.address)
        
    def omit(self):
        self.omit = True
        return self
    
    def include(self):
        self.omit = False
        return self
    
    def setPlate(self, plate):
        self.plate = plate
        return self
    
    def setUp(self, up):
        self.up = up
        return self
    
    def setDown(self, down):
        self.down = down
        return self
    
    def setLeft(self, left):
        self.left = left
        return self
    
    def setRight(self, right):
        self.right = right
        return self
    
    def addSample(self, sample):
        if not sample in self.samples:
            self.samples.append(sample)
        if not self in sample.wells:
            sample.wells.append(self)
        return self
    
    def addDetector(self, detector):
        if not detector in self.detectors:
            self.detectors.append(detector)
        if not self in detector.wells:
            detector.wells.append(self)
        return self
    
    def removeSample(self, sample):
        if self.samples.count(sample) == 1:
            self.samples.remove(sample)
        if sample.wells.count(self) == 1:
            sample.wells.remove(self)
        return self
    
    def removeDetector(self, detector):
        if self.detectors.count(detector) == 1:
            self.detectors.remove(detector)
        if detector.wells.count(self) == 1:
            detector.wells.remove(self)
        return self
    
    def clearSamples(self):
        for sample in self.samples:
            if sample.wells.count(self) == 1:
                sample.wells.remove(self)
        self.samples = []
        return self
    
    def clearDetectors(self):
        for detector in self.detectors:
            if detector.wells.count(self) == 1:
                detector.wells.remove(self)
        self.detectors = []
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

    def getAddress(self):
        return self.address
    def getPlate(self):
        return self.plate
    def getUp(self):
        return self.up
    def getDown(self):
        return self.down
    def getLeft(self):
        return self.left    
    def getRight(self):
        return self.right
    def getSamples(self):
        return self.samples
    def getDetectors(self):
        return self.detectors
    def getSampleNames(self):
        tmp = ''
        for i in self.samples:
            tmp += i.getName() + ';'
        if tmp == '':
            tmp = 'N/A'
        return tmp
    def getGroupNames(self):
        tmp = ''
        for i in self.samples:
            tmp += i.getGroup().getName() + ';'
        if tmp == '':
            tmp += 'N/A'
        return tmp
    def getDetectorNames(self):
        tmp = ''
        for i in self.detectors:
            tmp += i.getName() + ';'
        if tmp == '':
            tmp += 'N/A'
        return tmp
    def getDetectorValues(self):
        tmp = ''
        for i in self.detectors:
            tmp += i.getName() + ':' + str(i.getValue()) + ';'
        if tmp == '':
            tmp = 'N/A'
        return tmp
    
    def offset(self, n_rows, n_columns):
        well = self
        if n_rows < 0:
            for i in range(abs(n_rows)):
                well = well.getUp()
                if well == None:
                    return None
        else:
            for i in range(abs(n_rows)):
                well = well.getDown()
                if well == None:
                    return None
        if n_columns < 0:
            for i in range(abs(n_columns)):
                well = well.getLeft()
                if well == None:
                    return None
        else:
            for i in range(abs(n_columns)):
                well = well.getRight()
                if well == None:
                    return None
        return well

class Plate(object):
    def __init__(self, name, n_rows, n_columns):
        self.name = name
        self.n_rows = n_rows
        self.n_columns = n_columns
        self.ui = Plate_ui(None, self, self.n_rows, self.n_columns, self.name)
        self.wells = {}
        row_names = ROW_NAMES[:n_rows]
        column_names = COLUMN_NAMES[:n_columns]
        self.row_names = row_names
        self.column_names = column_names
        vbox = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridSizer(self.n_rows, self.n_columns, 1, 1)
        for j in row_names:
            for i in column_names:
                address = j + i
                well = Well(address, self)
                #well.setPlate(self)
                self.wells[address] = well
                grid.Add(well.ui, 0, wx.EXPAND|wx.ALL, 0)
        vbox.Add(grid, proportion = 1, flag = wx.EXPAND|wx.ALL, border = 10)
        self.ui.SetSizer(vbox)
        self.ui.SetSize((self.n_columns * 60, self.n_rows * 48))
        self.ui.SetTitle(self.name)
        self.ui.Centre()
        self.ui.Show()
        for address in self.wells:
            i = column_names.index(address[1:])
            j = row_names.index(address[0])
            if i <> 0:
                self.wells[address].setLeft(self.wells[row_names[j] + column_names[i-1]])
            else:
                self.wells[address].setLeft(None)
            if i <> n_columns - 1:
                self.wells[address].setRight(self.wells[row_names[j] + column_names[i+1]])
            else:
                self.wells[address].setRight(None)            
            if j <> 0:
                self.wells[address].setUp(self.wells[row_names[j-1] + column_names[i]])
            else:
                self.wells[address].setUp(None)                
            if j <> n_rows - 1:
                self.wells[address].setDown(self.wells[row_names[j+1] + column_names[i]])
            else:
                self.wells[address].setDown(None)
        self.selected_rng = None
        

    def getName(self):
        return self.name
    def getNrows(self):
        return self.n_rows
    def getNcols(self):
        return self.n_columns
    def getRow_names(self):
        return self.row_names    
    def getColumn_names(self):
        return self.column_names    
    def getWell(self, address):
        return self.wells.get(address.upper(), None)    
    def wellInPlate(self, well):
        return well.getPlate() == self    
    def rangeInPlate(self, myRange):
        return myRange.getPlate() == self

class Range(object):
    def __init__(self, start_well, end_well):
        self.plate = start_well.getPlate()
        self.wells = {}
        column_names = self.plate.getColumn_names()
        row_names = self.plate.getRow_names()
        i1 = column_names.index(start_well.getAddress()[1:])
        i2 = column_names.index(end_well.getAddress()[1:])
        j1 = row_names.index(start_well.getAddress()[0])
        j2 = row_names.index(end_well.getAddress()[0])
        i0 = min(i1, i2)
        j0 = min(j1, j2)
        self.start_well = self.plate.getWell(row_names[min(j1, j2)] + column_names[min(i1, i2)])
        self.n_rows = abs(j1 - j2) + 1
        self.n_columns = abs(i1 - i2) + 1
        self.column_names = column_names[i0 : (i0 + self.n_columns)]
        self.row_names = row_names[j0 : (j0 + self.n_rows)]
        for i in range(self.n_columns):
            for j in range(self.n_rows):
                well = self.start_well.offset(j, i)
                self.wells[well.getAddress()] = well

    def getPlate(self):
        return self.plate
    def getRow_names(self):
        return self.row_names    
    def getColumn_names(self):
        return self.column_names    
    def getWell(self, address):
        return self.wells.get(address.upper(), None)    
    def getStartWell(self):
        return self.start_well
    
    def wellInRange(self, well):
        address = well.getAddress()
        return well.getPlate() == self.getPlate() and address in self.wells
    
    def rangeInRange(self, myRange):
        if myRange.getPlate() <> self.getPlate():
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
                    output += well.getAddress()
                elif item.lower() == 'sample':
                    output += well.getSampleNames() #if well.getSamples() <> [] else 'N/A'
                elif item.lower() == 'group':
                    output += well.getGroupNames() #if well.getSamples() <> [] else 'N/A'
                elif item.lower() == 'detector':
                    output +=  well.getDetectorNames() #if well.getDetectors() <> [] else 'N/A'
                elif item.lower() == 'value':
                    output +=  well.getDetectorValues() #if well.getDetectors() <> [] else 'N/A'
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
        tmp_plate = Plate('tmp', self.getPlate().n_rows, self.getPlate().n_columns)
        address0 = self.getStartWell().getAddress()
        address1 = new_range.getStartWell().getAddress()
        j = ROW_NAMES.index(address1[0]) - ROW_NAMES.index(address0[0])
        i = COLUMN_NAMES.index(address1[1:]) - COLUMN_NAMES.index(address0[1:])
        for address in self.wells:
            if item.lower() == 'all':
                self.wells[address].copyAllTo(tmp_plate.getWell(address))
            elif item.lower() == 'sample':
                self.wells[address].copySamplesTo(tmp_plate.getWell(address))
            elif item.lower() == 'detector':
                self.wells[address].copyDetectorsTo(tmp_plate.getWell(address))
        for address in self.wells:
            new_well = new_range.getPlate().getWell(address).offset(j, i)
            if new_well <> None:
                tmp_plate.getWell(address).copyAllTo(new_well)
                
    def moveTo(self, new_range, item = 'all'):
        tmp_plate = Plate('tmp', self.getPlate().n_rows, self.getPlate().n_columns)
        address0 = self.getStartWell().getAddress()
        address1 = new_range.getStartWell().getAddress()
        j = ROW_NAMES.index(address1[0]) - ROW_NAMES.index(address0[0])
        i = COLUMN_NAMES.index(address1[1:]) - COLUMN_NAMES.index(address0[1:])
        for address in self.wells:
            if item.lower() == 'all':
                self.wells[address].moveAllTo(tmp_plate.getWell(address))
            elif item.lower() == 'sample':
                self.wells[address].moveSamplesTo(tmp_plate.getWell(address))
            elif item.lower() == 'detector':
                self.wells[address].moveDetectorsTo(tmp_plate.getWell(address))
        for address in self.wells:
            new_well = new_range.getPlate().getWell(address).offset(j, i)
            if new_well <> None:
                tmp_plate.getWell(address).copyAllTo(new_well)
                
    def clear(self, item = 'all'):
        for well in self.wells.values():
            if item.lower() == 'all':
                well.clearAll()
            elif item.lower() == 'sample':
                well.clearSamples()
            elif item.lower() == 'detector':
                well.clearDetectors()

#UI
class Well_ui(wx.Panel):
    def __init__(self, parent, plate, address = 'NA', samples = 'NA', detectors = 'NA', over_color = '#0099f7', off_color = '#b3b3b3', active_color = 'gold', inactive_color = 'white'):
        super(Well_ui, self).__init__(parent)
        self.plate = plate
        self.address = address
        self.samples = samples
        self.detectors = detectors
        self.active = False
        self.over_color = over_color
        self.off_color = off_color
        self.color = self.off_color
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.SetBackgroundColour(self.inactive_color)
        self.mouseover = False
        #self.Bind(wx.EVT_PAINT, self.OnPaint)
        #self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftdown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftup)
        font9 = wx.Font(9, wx.MODERN, wx.SLANT, wx.NORMAL, False, u'Consolas')
        font8 = wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        self.t1 = wx.StaticText(self, label=self.address, pos = (1, 0))
        self.t1.SetFont(font9)
        self.t2 = wx.StaticText(self, label='S:', pos = (1, 13))
        self.t2.SetFont(font8)
        self.t3 = wx.StaticText(self, label='D: ', pos = (1, 26))
        self.t3.SetFont(font8)
        self.t1.Bind(wx.EVT_LEFT_DOWN, self.OnLeftdown)
        self.t1.Bind(wx.EVT_LEFT_UP, self.OnLeftup)
        self.t1.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)
        self.t1.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)
        self.t1.Bind(wx.EVT_MOTION, self.OnMotion)
        self.t2.Bind(wx.EVT_MOTION, self.OnMotion)
        self.t3.Bind(wx.EVT_MOTION, self.OnMotion)
        
    def OnMotion(self, e):
        #print 'move'
        self.OnEnter(e)
        
   
    def update(self):
        if self.active:
            self.color = self.active_color
        elif self.mouseover:
            self.color = self.over_color
        else:
            self.color = self.inactive_color
        self.SetBackgroundColour(self.color)
        self.Refresh()


    def OnEnter(self, e):
        if e.LeftIsDown():
            self.Parent.range.append(self.address)
            new_rng = Range(self.plate.getWell(self.Parent.range[0]), self.plate.getWell(self.Parent.range[-1]))
            if self.plate.selected_rng <> None:
                for well in self.plate.selected_rng.wells.values():
                    if not new_rng.wellInRange(well):
                        well.ui.active = False
                        well.ui.update()
                for well in new_rng.wells.values():
                    if not self.plate.selected_rng.wellInRange(well):
                        well.ui.active = True
                        well.ui.update()
            else:
                for well in new_rng.wells.values():
                    well.ui.active = True
                    well.ui.update()
            self.plate.selected_rng = new_rng
            print self.Parent.range
        self.mouseover = True
        self.update()
    
    def OnLeave(self, e):
        self.mouseover = False
        self.update()
    
    def OnLeftdown(self, e):
        self.Parent.range = []
        print e.GetPosition()
        if self.mouseover:
            self.Parent.range.append(self.address)
            self.plate.selected_rng = Range(self.plate.getWell(self.Parent.range[0]), self.plate.getWell(self.Parent.range[-1]))
            for well in self.plate.selected_rng.wells.values():
                well.ui.active = True
                well.ui.update()
            print self.Parent.range
    
    def OnLeftup(self, e):
        self.Parent.range = []
        for well in self.plate.selected_rng.wells.values():
            well.ui.active = False
            well.ui.update()
        print self.plate.selected_rng.show()
    
class Plate_ui(wx.Frame):
    def __init__(self, parent, plate, nrow = 8, ncol = 12, title = 'Plate'):
        super(Plate_ui, self).__init__(parent)
        self.plate = plate
        self.range = []
        self.nrow = nrow
        self.ncol = ncol
        self.title = title
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftdown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftup)

    def OnLeftdown(self, e):
        self.range = []
        
    def OnLeftup(self, e):
        self.range = []
        for well in self.plate.selected_rng.wells.values():
            well.ui.active = False
            well.ui.update()
        print self.plate.selected_rng.show()

def main():
    app = wx.App()
    a = Plate('myplate',8,12)
    app.MainLoop()

if __name__ == '__main__':
    main()

#a = Plate('myplate',16,24)
#a1 = Plate('myplate2', 8, 12)
#s = SampleList('s',1,40)
#naive = Group('Naive').addSampleList(s.subset(1,10))
#null = Group('Null').addSampleList(s.subset(11,10))
#neg = Group('Neg').addSampleList(s.subset(21,10))
#shRNA = Group('shRNA').addSampleList(s.subset(31,10))
#item = 'sample'
#entry = naive.getSamples() + null.getSamples() + neg.getSamples() + shRNA.getSamples()
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

