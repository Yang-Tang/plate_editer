import string
from collections import OrderedDict

ROW_NAMES = list(string.ascii_uppercase)
COLUMN_NAMES = map(str, range(1, 100))

class Experiment(object):
    def __init__(self, ID):
        self._id = str(ID)
        self._samples = OrderedDict()
        self._assays = OrderedDict()
    def addSamples(self, group, samples = None, num = 8):
        if samples:
            for sample in samples:
                self._samples[sample] = str(group)
        else:
            for idx in range(num):
                self._samples[str(group) + '-' + str(idx + 1)] = str(group)
        return self
    def addAssays(self, assays, isRef = False):
        for assay in assays:
            self._assays[assay] = isRef
        return self
    def get(self, item_class):
        if item_class == 's':
            return self._samples.keys()
        elif item_class == 'g':
            return self._samples.values()
        elif item_class == 'a':
            return self._assays.keys()

class Plate(object):
    def __init__(self, ID, nrow, ncol, samples = None, assays = None, values = None):
        self._id = str(ID)
        self._nrow = nrow
        self._ncol = ncol
        self._samples = [['NA' for dummy_col in range(self._ncol)]
                        for dummy_row in range(self._nrow)]
        self._assays = [['NA' for dummy_col in range(self._ncol)]
                        for dummy_row in range(self._nrow)]
        self._values = [['NA' for dummy_col in range(self._ncol)]
                        for dummy_row in range(self._nrow)]
        if samples:
            for row in range(self._nrow):
                for col in range(self._ncol):
                    try:
                        self._samples[row][col] = samples[row][col]
                    except IndexError:
                        self._samples[row][col] = 'NA'
        if assays:
            for row in range(self._nrow):
                for col in range(self._ncol):
                    try:
                        self._assays[row][col] = assays[row][col]
                    except IndexError:
                        self._assays[row][col] = 'NA'
        if values:
            for row in range(self._nrow):
                for col in range(self._ncol):
                    try:
                        self._values[row][col] = values[row][col]
                    except IndexError:
                        self._values[row][col] = 'NA'
    def __str__(self):
        output = self._id + ':\n'
        output += 'Samples:\n'
        output += '\t'.join([''] + COLUMN_NAMES[:self._ncol]) + '\n'
        for row in range(self._nrow):
            output += '\t'.join(list(ROW_NAMES[row]) + self._samples[row]) + '\n'
        output += 'Assays:\n'
        output += '\t'.join([''] + COLUMN_NAMES[:self._ncol]) + '\n'
        for row in range(self._nrow):
            output += '\t'.join(list(ROW_NAMES[row]) + self._assays[row]) + '\n'
        return output
    def set(self, item_class, item, pos):
        if item_class == 's':
            self._samples[pos[0]][pos[1]] = item
        elif item_class == 'a':
            self._assays[pos[0]][pos[1]] = item
        elif item_class == 'v':
            self._values[pos[0]][pos[1]] = item
        elif item_class == None:
            self._samples[pos[0]][pos[1]] = item[0]
            self._assays[pos[0]][pos[1]] = item[1]
            self._values[pos[0]][pos[1]] = item[2]
        return self
    def clear(self, item_class, pos):
        if item_class == 's':
            self._samples[pos[0]][pos[1]] = 'NA'
        elif item_class == 'a':
            self._assays[pos[0]][pos[1]] = 'NA'
        elif item_class == 'v':
            self._values[pos[0]][pos[1]] = 'NA'
        elif item_class == None:
            self._samples[pos[0]][pos[1]] = 'NA'
            self._assays[pos[0]][pos[1]] = 'NA'
            self._values[pos[0]][pos[1]] = 'NA'
    def get(self, item_class, pos):
        if item_class == 's':
            return self._samples[pos[0]][pos[1]]
        elif item_class == 'a':
            return self._assays[pos[0]][pos[1]]
        elif item_class == 'v':
            return self._values[pos[0]][pos[1]]
        elif item_class == None:
            return (self._samples[pos[0]][pos[1]],
                    self._assays[pos[0]][pos[1]],
                    self._values[pos[0]][pos[1]])
    def clone(self):
        plate = Plate(self._id + '_clone', self._nrow, self._ncol)
        plate._samples = [rows[:] for rows in self._samples]
        plate._assays = [rows[:] for rows in self._assays]
        plate._values = [rows[:] for rows in self._values]
        return plate
    def posInplate(self, pos):
        try:
            self._samples[pos[0]][pos[1]]
        except IndexError:
            return False
        return True

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
    def positions(self):
        for row in range(self._startpos[0], self._startpos[0] + self._nrow):
            for col in range(self._startpos[1], self._startpos[1] + self._ncol):
                yield (row, col)
    def autoFill(self, item_class = 's', itmes = [], index = 0, nrow = 2, ncol = 2, direction = 'row-wise', iteration = True):
        nCOL = self._ncol / ncol
        nROW = self._nrow / nrow
        #pos_lst = {}
        if direction == 'row-wise':
            for C_idx in range(nCOL):
                for R_idx in range(nROW):
                    for c_idx in range(ncol):
                        for r_idx in range(nrow):
                            pos = (self._startpos[0] + R_idx*nrow + r_idx,
                                   self._startpos[1] + C_idx*ncol + c_idx)
                            itmes_idx = index % len(itmes)
                            #pos_lst[pos] = index % len(itmes)
                            self._plate.set(item_class, itmes[itmes_idx], pos)
                    if iteration:
                        index += 1
        elif direction == 'col-wise':
            for R_idx in range(nROW):
                for C_idx in range(nCOL):
                    for c_idx in range(ncol):
                        for r_idx in range(nrow):
                            pos = (self._startpos[0] + R_idx*nrow + r_idx,
                                   self._startpos[1] + C_idx*ncol + c_idx)
                            itmes_idx = index % len(itmes)
                            #pos_lst[pos] = index % len(itmes)
                            self._plate.set(item_class, itmes[itmes_idx], pos)
                    if iteration:
                        index += 1
        return index % len(itmes)
    def copy(self, new_pos, cut = False, item_class = None):
        tmp_plate = self._plate.clone()
        if cut:
            self.clearall(item_class)
        nrow = new_pos[0] - self._startpos[0]
        ncol = new_pos[1] - self._startpos[1]
        offset = (new_pos[0] - self._startpos[0],
                  new_pos[1] - self._startpos[1])
        for pos in self.positions():
            offset_pos = (pos[0] + offset[0], pos[1] + offset[1])
            if self._plate.posInplate(offset_pos):
                self._plate.set(item_class, tmp_plate.get(item_class, pos), offset_pos)
        return self
    def clearall(self, item_class = None):
