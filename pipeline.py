from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
import numpy as np
import cv2


class ProcessingFunc(object):
    """An Image Processing function wrapper which contains the function and argument options. The
    argument options are things such as type, range, display, default, etc. to describe how to make the
    GUI for the function."""
    def __init__(self, func, args):
        super(ProcessingFunc, self).__init__()
        self.func = func
        self.args = args
        self.ret = FuncRet()

    def run_func(self):
        """Runs the processing function, storing the return value as an array in the attribute 'ret'.
        """
        args_list = []
        for arg in self.args:
            args_list.append(arg.get_val())
        ret_arr = [self.func(*args_list)]
        for i, ret_val in enumerate(ret_arr):
            self.ret[i].val = ret_val

class FuncArgs(object):
    """An Argument object to describe the type of parameters, defaults, and GUI options.

    Args:
        arg_type (str): String describing the type of the argument
        gui_input (bool): Determines if parameter should be shown in the GUI
        gui_range (arr): A two-tuple describing the minimum and maximum values for
                a numeric parameter. 
        default (any): The default value of the parameter. 
    """
    def __init__(self, **kwargs):
        """Summary
        
        Args:
            **kwargs: Description
        """
        super(FuncArgs, self).__init__()

        self.arg_type = None
        self.gui_input = None
        self.gui_range = None
        self.default = None
        self.value = None

        if 'arg_type' in kwargs:
            self.arg_type = kwargs['arg_type']

        if 'gui_input' in kwargs:
            self.gui_input = kwargs['gui_input']

        if 'gui_range' in kwargs:
            self.gui_range = kwargs['gui_range']
        
        if 'default' in kwargs:
            self.default = kwargs['default']

        if 'value' in kwargs:
            self.value = kwargs['value']

    def get_val(self):
        if self.value == None:
            if self.default != None:
                self.value = self.default
            else: # If no value or default value
                if self.gui_range != None: # If the parameter Gui Range exists
                    self.value = np.mean(self.gui_range) # Set the value to halfway down the range.


        # This is to check if it is an argument which was the return value of a previous
        # stage in the pipeline. If this is true, the value should be extracted.
        if isinstance(self.value, RetVal):
            self.value = self.value.get_val()

        return self.value

    def __str__(self):
        return str(self.get_val())

    def __repr__(self):
        return self.__str__()

class RetVal(object):
    """
    """
    def __init__(self, val=None):
        self.val = val

    def get_val(self):
        return self.val
    def __str__(self):
        return "Retval Object: \n" + str(self.val)

    def __repr__(self):
        return self.__str__()

class FuncRet(object):
    """
    """
    def __init__(self, **kwargs):
        super(FuncRet, self).__init__()
        if 'num_vals' in kwargs:
            self.num_vals = kwargs['num_vals']
        else:
            self.num_vals = 0

        self.ret_vals = []

    def __iter__(self):
        return self

    def __getitem__(self, key):
        if key < len(self.ret_vals):
            return self.ret_vals[key]
        else:
            while key >= len(self.ret_vals):
                self.ret_vals.append(RetVal()) # Add a RetVal object with the attribute val initialized as None, to be written later
            return self.ret_vals[key]

    def __setitem__(self, key, value):
        self.ret_vals[key].val = value

class ProcessingPipeline(object):
    """Contains an array of ProcessingFunc and an input image, as well as arguments """
    def __init__(self, proc_funcs):
        super(ProcessingPipeline, self).__init__()
        self.proc_funcs = proc_funcs

    def run_pipeline(self):
        if len(self.proc_funcs) == 0:
            raise ValueError('There must be at least one processing function.')

        for i, proc_func in enumerate(self.proc_funcs):
            proc_func.run_func()
            # print(proc_func.ret)
            # print(proc_func.args[0])
        #     cv2.imshow("Image {}".format(i), proc_func.ret[0].val)
        # cv2.waitKey(0)

def load_img(file_name):
    """Loads an image given a file name

    Args:
        file_name (str): File name of the image to load
    
    Returns:
        Image: Image loaded from file
    """
    cap = cv2.VideoCapture(file_name)

    ret, src = cap.read()
    return src

def to_gray(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

def canny_edges(img, threshold1, threshold2, edges=None, apertureSize=3, L2gradient=False):
    res = cv2.Canny(img, threshold1, threshold2, edges=edges, apertureSize=apertureSize)


def main():
    # First function in the chain. Should take 
    file = '/home/max/Videos/VID_20190403_105950~2_no_audio(1).mp4'
    f1_args = [FuncArgs(arg_type="str", gui_input=True, default=file)]
    f1 = ProcessingFunc(load_img, f1_args)


    f2_args = [FuncArgs(arg_type="img", value=f1.ret[0])]
    f2 = ProcessingFunc(to_gray, f2_args) # How to link return value of one function to the input of another

    f3_args = [  FuncArgs(arg_type="img", value=f2.ret[0]),
                    FuncArgs(arg_type="double", gui_input=True, gui_range=[0,100]),
                    FuncArgs(arg_type="double", gui_input=True, gui_range=[0,100]),
                    FuncArgs(arg_type="array", default=None),
                    FuncArgs(arg_type="int", default=3, gui_range=[3,10]),
                    FuncArgs(arg_type="bool", default=False, gui_input=True)
                    ]

    f3 = ProcessingFunc(canny_edges, f3_args)

    pp = ProcessingPipeline([f1, f2])

    pp.run_pipeline()

if __name__ == '__main__':
    main()