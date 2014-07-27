#import Gird
from lib import Grid_class

def offset(pos, nrow, ncol):
    return (pos[0] + nrow, pos[1] + ncol)

class Sample(object):
    def __init__(self, ID):
        self._id = str(ID)
        self._group = None
        self._wells = []
    def __str__(self):
        if self._group:
            return self._id + '(' + str(self._group.getId()) + ')'
        else:
            return self._id + '(' + 'NoGroup' + ')'
    def setGroup(self, group):
        self._group = group
        return self
    def setWell(self, well):
        self._wells.append(well)
        return self
    def unsetWell(self, well):
        self._wells.remove(well)
        return self
    def getId(self):
        return self._id
    def getGroup(self):
        return self._group
    def getWells(self):
        for well in self._wells:
            yield well
        
class Group(object):
    def __init__(self, ID):
        self._id = str(ID)
        self._samples = []
        self._iscontrol = False
    def __str__(self):
        sampleids = []
        for sample in self._samples:
            sampleids.append(sample.getId())
        return self._id + ': ' + ', '.join(sampleids)
    def addSamples(self, *samples):
        for sample in samples:
            if not sample in self._samples:
                self._samples.append(sample)
                old_group = sample.getGroup()
                if old_group:
                    old_group.rmSamples(sample)
                sample.setGroup(self)
        return self
    def rmSamples(self, *samples):
        if samples:
            for sample in samples:
                try:
                    self._samples.remove(sample)
                    sample.setGroup(None)
                except:
                    continue
        else:
            for sample in self._samples:
                sample.setGroup(None)
            self._samples = []
    def setControl(self, iscont):
        if type(iscont) == bool:
            self._iscontrol = iscont
        return self
    def getId(self):
        return self._id
    def getSamples(self):
        for sample in self._samples:
            yield sample
    def getSample(self, sample_id):
        for sample in self._samples:
            if sample.getId() == sample_id:
                return sample
        else:
            return None
    def isControl(self):
        return self._iscontrol

class Assay(object):
    def __init__(self, ID):
        self._id = ID
        self._value = None
        self._wells = []
    def __str__(self):
        pass
    def setValue(self, value):
        self._value = float(value)
        return self
    def setWell(self, well):
        self._wells.append(well)
        return self
    def unsetWell(self, well):
        self._wells.remove(well)
        return self
    def getId(self):
        return self._id
    def getValue(self):
        return self._value
    def getWells(self):
        for well in self._wells:
            yield well    

class Well(object):
    def __init__(self, address, plate):
        self._address = address
        self._plate = plate
        self._samples = []
        self._assays = []
        self._isomit = False
    def __str__(self):
        pass
    def add(self, *items):
        for item in items:
            if type(item) == Sample:
                if not item in self._samples:
                    self._samples.append(item)
                    item.setWell(self)
            elif type(item) == Assay:
                if not item in self._assays:
                    self._assays.append(item)
                    item.setWell(self)
    def rm(self, *items):
        if items:
            for item in items:
                if type(item) == Sample:
                    try:
                        self._samples.remove(item)
                        item.unsetWell(self)
                    except:
                        continue
                elif type(item) == Assay:
                    try:
                        self._assays.remove(item)
                        item.unsetWell(self)
                    except:
                        continue
        else:
            for item in self._samples + self._assays:
                item.unsetWell(self)
            self._samples = []
            self._assays = []
    def rp(self, *items):
        sample_cleared = False
        assay_cleared = False
        for item in items:
            if type(item) == Sample:
                if not sample_cleared:
                    self.rm(*self._samples)
                    sample_cleared = True
                    if not item in self._samples:
                        self._samples.append(item)
                        item.setWell(self)
            elif type(item) == Assay:
                if not assay_cleared:
                    self.rm(*self._assays)
                    assay_cleared = True
                    if not item in self._assays:
                        self._assays.append(item)
                        item.setWell(self)
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
    def __init__(self, ID, nrow, ncol):
        self._id = str(ID)
        self._nrow = nrow
        self._ncol = ncol
        self._samples = [[[] for dummy_col in range(self._ncol)]
                        for dummy_row in range(self._nrow)]
        self._assays = [[[] for dummy_col in range(self._ncol)]
                        for dummy_row in range(self._nrow)]
    def __str__(self):
        output = self._id + ':\n'
        output += 'Samples:\n'
        for row in range(self._nrow):
            for col in range(self._ncol):
                if len(self._samples[row][col]) == 0:
                    output += '-'
                else:
                    for item in self._samples[row][col]:
                        output += item.getId() + ';'
                output += '\t'
            output += '\n'
        output += '\n'
        output += 'Assays:\n'
        for row in range(self._nrow):
            for col in range(self._ncol):
                if len(self._assays[row][col]) == 0:
                    output += '-'
                else:
                    for item in self._assays[row][col]:
                        output += item.getId() + ';'
                output += '\t'
            output += '\n'
        output += '\n'
        return output
    def addSample(self, sample, pos, method):
        if method == 'replace':
            self._samples[pos[0]][pos[1]] = [sample]
        elif method == 'append':
            if not sample in self._samples[pos[0]][pos[1]]:
                self._samples[pos[0]][pos[1]].append(sample)
        return self
    def addAssay(self, assay, pos, method):
        if method == 'replace':
            self._assays[pos[0]][pos[1]] = [assay]
        elif method == 'append':
            if not assay in self._assays[pos[0]][pos[1]]:
                self._assays[pos[0]][pos[1]].append(assay)
        return self
    def clear(self, item_class, pos):
        if item_class == 'sample':
            self._samples[pos[0]][pos[1]] = []
        elif item_class == 'assay':
            self._assays[pos[0]][pos[1]] = []
        elif item_class == 'all':
            self._samples[pos[0]][pos[1]] = []
            self._assays[pos[0]][pos[1]] = []    
    def getSample(self, pos):
        return self._samples[pos[0]][pos[1]]
    def getAssay(self, pos):
        return self._assays[pos[0]][pos[1]]
    def clone(self):
        plate = Plate(self._id + '_clone', self._nrow, self._ncol)
        plate._samples = self._samples[:]
        plate._assays = self._assays[:]
        return plate
    def posInplate(self, pos):
        return pos[0] < self._nrow and pos[1] < self._ncol


class Range(object):
    def __init__(self, plate, pos1, pos2):
        self._plate = plate
        row1 = min(pos1[0], pos2[0])
        row2 = max(pos1[0], pos2[0])
        col1 = min(pos1[1], pos2[1])
        col2 = max(pos1[1], pos2[1])
        self._startpos = (row1, col1)
        self._nrow = row2 - row1 + 1
        self._ncol = col2 - col1 + 1
        self._samples = [[plate.getSample((row, col)) for col in range(col1, col2 + 1)]
                        for row in range(row1, row2 + 1)]
        self._assays = [[plate.getAssay((row, col)) for col in range(col1, col2 + 1)]
                        for row in range(row1, row2 + 1)]
    def positions(self):
        for row in range(self._startpos[0], self._startpos[0] + self._nrow + 1):
            for col in range(self._startpos[1], self._startpos[1] + self._ncol + 1):
                yield (row, col)
    def autoFill(self, item_class = 'sample', entry = [], index = 0, nrow = 2, ncol = 2, direction = 'row-wise', method = 'replace', iteration = True, s_shape = False):
        nCOL = self._ncol / ncol
        nROW = self._nrow / nrow
        pos_lst = {}
        if direction == 'row-wise':
            for C_idx in range(nCOL):
                for R_idx in range(nROW):
                    for c_idx in range(ncol):
                        for r_idx in range(nrow):
                            pos = (self._startpos[0] + R_idx*nrow + r_idx,
                                   self._startpos[1] + C_idx*ncol + c_idx)
                            pos_lst[pos] = index % len(entry)
                    if iteration:
                        index += 1
        elif direction == 'col-wise':
            for R_idx in range(nROW):
                for C_idx in range(nCOL):
                    for c_idx in range(ncol):
                        for r_idx in range(nrow):
                            pos = (self._startpos[0] + R_idx*nrow + r_idx,
                                   self._startpos[1] + C_idx*ncol + c_idx)
                            pos_lst[pos] = index % len(entry)
                    if iteration:
                        index += 1
        for pos, idx in pos_lst.items():
            if item_class == 'sample':
                self._plate.addSample(entry[idx], pos, method)
            elif item_class == 'assay':
                self._plate.addAssay(entry[idx], pos, method)
        return index % len(entry)
    def copy(self, item_class, new_pos, move = False):
        tmp_plate = self._plate.clone()
        print tmp_plate
        if move:
            self.clearall(item_class)
        nrow = new_pos[0] - self._startpos[0]
        ncol = new_pos[1] - self._startpos[1]
        if item_class == 'sample':
            for pos in self.positions():
                offset_pos = (pos[0] + nrow, pos[1] + ncol)
                if self._plate.posInplate(offset_pos):
                    for sample in tmp_plate.getSample(pos):
                        self._plate.addSample(sample, offset_pos, 'replace')
        elif item_class == 'assay':
            for pos in self.positions():
                self._assays[pos[0] + nrow][pos[1] + ncol] = tmp_plate.getAssay(pos)[:]
        print tmp_plate
        return self
    def clearall(self, item_class = 'sample'):
        for pos in self.positions():
            self._plate.clear(item_class, pos)
        return self
            


a = Sample('mya')
b = Sample('myb')
c = Sample('myc')
g = Group('jjj')
g1 = Group('111')
g.addSamples(a,b,c)
g.rmSamples(a)
g.rmSamples(a)
w1 = Well((1,1), 'p1')
w1.add(a,b,c)
w1.rm(*w1._samples)
p1 = Plate('myp1', 4, 6)
r1 = Range(p1,(0,0),(2,3))
r1.autoFill(entry=[a,b,c], nrow=2, ncol=2)
r1.copy('sample', (2,2), True)
print p1
