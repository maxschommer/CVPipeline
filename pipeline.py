from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QFileDialog)
import numpy as np
import cv2


class ProcessingFunc(object):
    """An Image Processing function wrapper which contains the function and 
    argument options. The argument options are things such as type, range, 
    display, default, etc. to describe how to make the GUI for the function.
    """
    def __init__(self, func, args, rets):
        super(ProcessingFunc, self).__init__()
        self.func = func
        self.args = args
        self.ret = rets # Changed from: FuncRets()

    def run_func(self):
        """Runs the processing function, storing the return value as an 
        array in the attribute 'ret'.
        """
        args_list = []
        for arg in self.args:
            args_list.append(arg.get_val())
        ret_arr = [self.func(*args_list)]
        for i, ret_val in enumerate(ret_arr):
            self.ret[i].value = ret_val

class FileDialogueLine(object):
    def __init__(self):
        super(FileDialogueLine, self).__init__()
        self.text_edit = QLineEdit() # contents.setText(data)
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.get_file) 
        
    
    def get_components(self):
        return [self.text_edit, self.browse_btn]

    def get_file(self):
        """Helper GUI function to retrieve a file.
        
        Returns:
            str: A string representing the file path. 
        """
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        print("Getting File!")
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.text_edit.setText(filenames[0])

    def __getitem__(self, key):
        return self.get_components()[key]

    # def __iter__(self):
    #     return self.get_components().__iter__()

    # def __del__(self):
    #     print('Deleting File Dialogue: ', id(self))

class IO(object):
    def __init__(self, **kwargs):
        """Summary
        
        Args:
            **kwargs: Description
        """
        super(IO, self).__init__()

        self.io_type = None
        self.gui_disp = None
        self.gui_type = None

        # Options for combo_box gui_type
        self.gui_array = None

        # Options for slider gui_type 
        self.gui_range = None

        # General options
        self.default = None
        self.value = None

        if 'io_type' in kwargs:
            self.io_type = kwargs['io_type']

        if 'gui_disp' in kwargs:
            self.gui_disp = kwargs['gui_disp']

        if 'gui_type' in kwargs:
            self.gui_type = kwargs['gui_type']

        # If gui_type is a combo_box
        if 'gui_array' in kwargs:
            self.gui_array = kwargs['gui_array']

        # If gui_type is a slider
        if 'gui_range' in kwargs:
            self.gui_range = kwargs['gui_range']

        if 'default' in kwargs:
            self.default = kwargs['default']

        if 'value' in kwargs:
            self.value = kwargs['value']

    def get_val(self):
        if self.value is None:
            if self.default is not None:
                self.value = self.default
            else: # If no value or default value
                if self.gui_range is not None:  # If the parameter Gui Range 
                                                # exists
                    self.value = np.mean(self.gui_range) # Set the value 
                                                         # to halfway down 
                                                         # the range.


        # This is to check if it is an argument which was the return value 
        # of a previous stage in the pipeline. If this is true, the value 
        # should be extracted.
        if isinstance(self.value, FuncRets):
            self.value = self.value.get_val()

        return self.value



    def get_gui_components(self, component_type="default"):
        """Retrieves the GUI components needed for the argument to be edited.
        
        Args:
            component_type (str, optional): The type of component to use, 
                    if there are multiple options availiable. For example, 
                    a list of options can be selected by a series of radio 
                    buttons or by a dropdown menu, so forcing one over the 
                    other is done with component_type. 
        
        Returns:
            arr[QTWidget]: An array of QT widgets to be added to an 
                    existing layout.
        
        Raises:
            ValueError: Description
        """
        res = None
        # Logic to figure out which GUI component to use. 
        if self.gui_type is not None:

            if self.gui_type == "combo_box":
                res = QComboBox()

                if self.gui_array is not None:
                    res.addItems(self.gui_array)
                    res.setCurrentIndex(self.gui_array.index(self.get_val()))
                    return [res]
                else:
                    raise ValueError("gui_array must be specified \
                        for combo_box.")
            if self.gui_type == "file":
                fDialog = FileDialogueLine()
                return fDialog

            if self.gui_type == "check_box":
                pass

        else:
            pass
            # raise ValueError('gui_type must be specified.')





class FuncArgs(IO):
    """An Argument object to describe the type of parameters, defaults, 
    and GUI options.

    Args:
        io_type (str): String describing the type of the argument
        gui_disp (bool): Determines if parameter should be shown in the GUI
        gui_type (str): The type of GUI input to use. Can be one of 
            -- combo_box
            -- check_box
            -- radio_button
            -- push_button
            -- table_widget
            -- line_edit
            -- slider
        gui_range (arr): A two-tuple describing the minimum and maximum 
                values for a numeric parameter. 
        default (any): The default value of the parameter. 
    """
    def __init__(self, **kwargs):
        """Summary
        
        Args:
            **kwargs: Description
        """
        super(FuncArgs, self).__init__(**kwargs)

    def __str__(self):
        return "FuncArgs Object: \n" + "Value: " +str(self.get_val())

    def __repr__(self):
        return self.__str__()

# class RetVal(object):
#     """
#     """
#     def __init__(self, val=None):
#         self.val = val

#     def get_val(self):
#         print("Getting Retval")
#         return self.val
#     def __str__(self):
#         return "Retval Object: \n" + str(self.val)

#     def __repr__(self):
#         return self.__str__()

class FuncRets(IO):
    """
    """
    def __init__(self, **kwargs):
        super(FuncRets, self).__init__(**kwargs)
        if 'num_vals' in kwargs:
            self.num_vals = kwargs['num_vals']
        else:
            self.num_vals = 0

        self.ret_vals = []

    def __iter__(self):
        return self

    # def __getitem__(self, key):
    #     if key < len(self.ret_vals):
    #         return self.ret_vals[key]
    #     else:
    #         while key >= len(self.ret_vals):
    #             self.ret_vals.append(RetVal())  # Add a RetVal object with 
    #                                             # the attribute val 
    #                                             # initialized as None, to 
    #                                             # be written later
    #         return self.ret_vals[key]

    # def __setitem__(self, key, value):
    #     self.ret_vals[key].val = value

class ProcessingPipeline(object):
    """Contains an array of ProcessingFunc and an input image, as well 
    as arguments.
    """
    def __init__(self, proc_funcs):
        super(ProcessingPipeline, self).__init__()
        self.proc_funcs = proc_funcs

    def run_pipeline(self):
        self.update_funcs()

        app = QApplication([])
        window = QWidget()
        layout = QGridLayout()
        main_tabs_widget = QTabWidget() # These are the tabs for the Image 
                                        # display and GUI inputs. 


        layout.addWidget(main_tabs_widget)
        tab_contents = []
        tab_h_boxs = []

        stored_gui_comps = []   # This is to prevent iterable objects with 
                                # multiple gui components from getting deleted
        for func in self.proc_funcs:
            tab_contents.append(QWidget())

            tab_h_boxs.append(QGridLayout())
            tab_h_boxs[-1].setContentsMargins(5, 5, 5, 5)
            for i, arg in enumerate(func.args):
                gui_comps = arg.get_gui_components()
                stored_gui_comps.append(gui_comps)
                if gui_comps is not None:
                    for j, gui_comp in enumerate(gui_comps):
                        tab_h_boxs[-1].addWidget(gui_comp, i, j)

            tab_contents[-1].setLayout(tab_h_boxs[-1])
            main_tabs_widget.addTab(tab_contents[-1], func.func.__name__)
        
        window.setLayout(layout)
        window.show()
        app.exec_()

    def update_funcs(self):
        if len(self.proc_funcs) == 0:
            raise ValueError('There must be at least one'+ \
                'processing function.')

        for i, proc_func in enumerate(self.proc_funcs):
            proc_func.run_func()


def load_img(file_name, dummy):
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
    f1_args = [FuncArgs(io_type="str", gui_disp=True, default=file, gui_type="file"), 
                FuncArgs(io_type="int", gui_disp=True, gui_type="combo_box", gui_array=["One", "Two", "Three"], default="Two")]

    f1_rets = [FuncRets(io_type="img")] #  TODO: Make return values labeled in order to display them.
    f1 = ProcessingFunc(load_img, f1_args, f1_rets)


    f2_args = [FuncArgs(io_type="img", value=f1_rets[0])]
    f2_rets = [FuncRets(io_type="img")]
    f2 = ProcessingFunc(to_gray, f2_args, f2_rets) # How to link return value of one function to the input of another

    # f3_args = [  FuncArgs(io_type="img", value=f2.ret[0]),
    #                 FuncArgs(io_type="double", gui_type="slider", gui_disp=True, gui_range=[0,100]),
    #                 FuncArgs(io_type="double", gui_disp=True, gui_range=[0,100]),
    #                 FuncArgs(io_type="array", default=None),
    #                 FuncArgs(io_type="int", default=3, gui_range=[3,10]),
    #                 FuncArgs(io_type="bool", default=False, gui_disp=True)
    #                 ]

    # f3 = ProcessingFunc(canny_edges, f3_args)

    pp = ProcessingPipeline([f1, f2]) #, f2, f3])

    pp.run_pipeline()

if __name__ == '__main__':
    main()