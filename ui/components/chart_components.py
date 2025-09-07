"""
Chart components using matplotlib for data visualization.
"""
from config.dependencies import MATPLOTLIB_AVAILABLE

if MATPLOTLIB_AVAILABLE:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    from mpl_toolkits.mplot3d import Axes3D
    
    class MatplotlibCanvas(FigureCanvas):
        """Basic matplotlib canvas for 2D charts"""
        def __init__(self, parent=None, width=5, height=4, dpi=100):
            fig = Figure(figsize=(width, height), dpi=dpi)
            self.axes = fig.add_subplot(111)
            super(MatplotlibCanvas, self).__init__(fig)
    
    class ThreeDChartCanvas(FigureCanvas):
        """3D matplotlib canvas for 3D visualizations"""
        def __init__(self, parent=None, width=5, height=4, dpi=100):
            fig = Figure(figsize=(width, height), dpi=dpi)
            self.axes = fig.add_subplot(111, projection='3d')
            super(ThreeDChartCanvas, self).__init__(fig)

else:
    # Fallback classes when matplotlib is not available
    from PyQt6.QtWidgets import QLabel
    
    class MatplotlibCanvas(QLabel):
        """Fallback when matplotlib is not available"""
        def __init__(self, parent=None, width=5, height=4, dpi=100):
            super().__init__("Matplotlib not available", parent)
            
    class ThreeDChartCanvas(QLabel):
        """Fallback when matplotlib is not available"""
        def __init__(self, parent=None, width=5, height=4, dpi=100):
            super().__init__("Matplotlib not available for 3D charts", parent)