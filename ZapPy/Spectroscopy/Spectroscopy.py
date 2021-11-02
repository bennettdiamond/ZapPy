''' ----------------------------------------------------------------
                    ZAPPY CLASSES
--------------------------------------------------------------------

Created by Bennett Diamond -- 2021.11.1

Associated classes, methods, and data structures for plasma analysis
on ZaP-HD.
'''

# GENERAL IMPORTS --------------------------
import numpy as np

''' ----------------------------------------------------------------
                    SPECTROSCOPY CLASS
--------------------------------------------------------------------

TASKS:
[] add any other interesting meta data from SPE v2.x files to Spec object

'''
class Spec():

    def __init__(self, m_i = 12/6.02e23):
        '''
        Initializes spectrocopy class.

        Inputs
        ------
        - (optional) m_i : float
            Ion mass (kg)

        Returns
        -------
        None
        '''

        self.q_i = 1.6e-19 # C - elementry charge
        self.c = 3e8 # m/s - speed of light
        self.m_i = m_i


    def readSPE(self, file_path, file_name):
        '''
        Pulls data from .SPE file. Stores data in class structure. For 
        reading SPE v2.x files, Matlab and the Matlab engine API for
        python must be installed.

        Inputs
        ------
        - file_path : String
            Path to the file to be read.
        - file_name : String
            Name of the file to be read. The file extension should not 
            be included.
        
        Returns
        -------
        Appends Spec class with the following:

        '''

        import spe_loader as spe
        import os

        self.full_file_path = os.path.join(file_path, file_name) + ".SPE"
        self.shot_num = file_name

        try: 

            spe_object = spe.SpeFile(self.full_file_path)
            self.image_data = np.asarray(spe_object.data[0][0])

            self.wavelength_vector = spe_object.wavelength
            self.gain = int(spe_object.footer.SpeFormat.DataHistories.DataHistory.Origin.Experiment.Devices.Cameras.Camera.Intensifier.Gain.cdata)
            self.gate_width = 1e-3*float(spe_object.footer.SpeFormat.DataHistories.DataHistory.Origin.Experiment.Devices.Cameras.Camera.Gating.RepetitiveGate.Pulse['width'])
            self.gate_delay = 1e-3*float(spe_object.footer.SpeFormat.DataHistories.DataHistory.Origin.Experiment.Devices.Cameras.Camera.Gating.RepetitiveGate.Pulse['delay'])
            self.yrange = spe_object.ycoord
            self.ydim = spe_object.ydim[0]

        except AssertionError:
            '''
            REQUIRES MATLAB AND THE MATLAB ENGINE INSTALLED!!!11!!!1!
            see: https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html
            '''

            import matlab.engine

            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            
            eng = matlab.engine.start_matlab()
            matlab_output = eng.loadSPE(self.full_file_path, nargout=3)
            eng.quit()
            
            self.image_data = np.transpose(np.asarray(matlab_output[0]))
            self.wavelength_vector = np.asarray(matlab_output[1][0])

            self.ydim = self.image_data.shape[0]
            self.yrange = range(self.ydim)
            
            # import matplotlib.pyplot as plt
            # plt.pcolormesh(self.wavelength_vector, self.yrange, self.image_data, cmap='jet', shading='auto')


    def binData(self, bin_edges):
        '''
        Averages data over a range of pixels to 1-D spectra for 
        easy analysis.

        Inputs
        ------
        bin_edges : array-like
            1-D array containing pixel numbers corresponding to 
            bin edges. Method will bin according to pairs of bin
            edges. 
        '''

        self.num_rows = len(bin_edges) // 2
        self.binned_data = np.zeros([self.num_rows, self.ydim])
        self.bin_centers = np.zeros(self.num_rows)
        for chord in range(self.num_rows):

            lower_edge = bin_edges[2*chord]
            upper_edge = bin_edges[2*chord + 1]
            
            self.bin_centers[chord] = (lower_edge + upper_edge) // 2
            self.binned_data[chord,:] = np.mean(self.image_data[lower_edge:upper_edge, :], axis=0)


    def sliceROI(self, ROI_edges):
        '''
        Reduces analysis wavelength range to area of interest.

        Inputs
        ------
        - ROI_edges : array-like
            A pair of indices in pixel-space demarking the 
            edges of the ROI.

        Returns
        -------
        - : array-like
            An array of the binned data with just the area of
            interest.
        '''

        return self.binned_data[:, ROI_edges[0]:ROI_edges[1]]


    def createROI(self, thresholds, rel_height=0.95):
        '''
        Generates regions of interest given threshold values.

        Inputs
        ------
        - thresholds : dict 
            Dictionary of rel_height and prominence values for 
            determining peaks.

        Returns
        -------
        - ROI_edges : array-like
            Array of ROI_edges corresponding to the edges of 
            each determined region of interest in pixel space.
        '''
        from scipy.signal import find_peaks, peak_widths

        self.thresholds = thresholds

        mean_data = np.mean(self.binned_data, axis=0)

        peaks = find_peaks(mean_data, rel_height=self.thresholds['rel_height'], prominence=self.thresholds['prominence'])
        edges = peak_widths(mean_data, peaks, rel_height=rel_height)

        ROI_edges = edges[:, 2:3]

        return ROI_edges

    
    def findDopplerTemp(self, line_spectra, line_vector):
        '''
        Determines the doppler temperature of a 1D spectra.
        '''
        
        A_max = np.argmax(line_vector)

        fit = self.fitGaussian(line_spectra, line_vector)
        FWHM = fit[2] * (line_vector[1] - line_vector[0])
        
        temp = (FWHM/line_vector[A_max])**2 * self.m_i * self.c**2 / (8 * np.log(2) * self.q_i)

        return temp, fit


    def fitGaussian(self, row_data, row_vect):
        '''
        Fits a Gaussian distribution to an array of 1-D data.

        Inputs
        ------
        - row_data : array-like
            Y values, usually of intensity, corresponding to X 
            values from row_vect.
        - row_vect : array-like
            X values, usually of wavelength, corresponding to Y 
            values from row_data.

        Returns
        -------
        - fit_parameters : array-like
            Array of parameters for the fitted Gaussian.
            fit_parameters[0] = A -- amplitude
            fit_parameters[1] = x0 -- distribution center
            fit_parameters[2] = width -- distribution width
            fit_parameters[3] = yoffest -- height above 0   
        '''
        from scipy.optimize import curve_fit

        n = len(row_vect)
        mean = sum(row_data * row_vect)
        width = sum(row_data* (row_vect-mean)**2)/n
        guess=[max(row_data), mean, width]

        def gauss(x, A, x_0, width, yoffset):
            return A*np.exp(-(x-x_0)**2/(2*width**2)) + yoffset

        try:
            fit_parameters, covariance = curve_fit(gauss, row_vect, row_data, guess)
        except:
            print('No dice with fit')
            fit_parameters = np.ones(4)

        return fit_parameters
    

    def findPeakWavelength(self, line_spectra, line_vector):
        '''
        Returns the precise wavelength of the peak of a Gaussian
        fitted to spectra.
        '''
        
        fit = Spec.fitGaussian(self, line_spectra, line_vector)

        return fit[2]

    
    def wavelength2pix(self, data_wavelength_space):
        '''
        Converts input values from wavelength space to pixel space.

        Parameters
        ----------
        data_wavelength_space : numerical or array-like
            Data in wavelength space to be converted.
        wavelength_vector : array-like
            List of wavelengths in wavelength space needed to create
            the conversion factor to pixel space.
        
        Returns
        -------
        data_pixel_space : numerical or array-like
            Data converted to pixel space.
        '''
        from scipy.interpolate import interp1d

        f = interp1d(self.wavelength_vector, self.yrange)
        data_pixel_space = f(data_wavelength_space)

        return data_pixel_space  


    def pix2wavelength(self, data_pixel_space):
        '''
        Converts input values from wavelength space to pixel space.

        Parameters
        ----------
        data_pixel_space : numerical or array-like
            Data in pixel space to be converted.
        wavelength_vector : array-like
            List of wavelengths in wavelength space needed to create
            the conversion factor to pixel space.
        
        Returns
        -------
        data_wavelength_space : numerical or array-like
            Data converted to wavelength space.
        '''
        from scipy.interpolate import interp1d

        f = interp1d(range(self.ydim), self.wavelength_vector)
        data_wavelength_space = f(data_pixel_space)

        return data_wavelength_space  


    def fit3D(self, X, Y, Z):
        '''
        Fits a 3D quadratic surface to data, taken from @reox on github.
        Will be improved once I know how it works.
        '''
        # https://gist.github.com/alexlib/05abf4e42a0341047b1da12e69c2f3a3
        from scipy.linalg import lstsq
        from itertools import combinations

        data = [[X], [Y], [Z]]

        A = np.c_[np.ones(data.shape[0]), data[:,:2], np.prod(data[:,:2], axis=1), data[:,:2]**2]
        C,_,_,_ = lstsq(A, data[:,2])

        # evaluate it on a grid
        domain_X, domain_Y = np.meshgrid(np.linspace(X.min(), X.max()), np.linspace(Y.min(), Y.max()))
        domain_XX = domain_X.flatten()
        domain_YY = domain_Y.flatten()

        surface = np.dot(np.c_[np.ones(domain_XX.shape), domain_XX, domain_YY, domain_XX*domain_YY, 
            domain_XX**2, domain_YY**2], C).reshape(domain_X.shape)

        return C, surface