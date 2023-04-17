# 
# Writen by Dylan Bateman
# Undergraduate, Department of Physics, University of Missouri
# Adapted from Min-Su Shin's "Python code to convert FITS files to images", found here:
# https://astromsshin.github.io/science/code/Python_fits_image/index.html
# 
# You can freely use the code
# 

import numpy
import matplotlib as mpl
import astropy.io.fits as pyfits
import img_scale
import pylab
import os
from alive_progress import alive_bar
import time
import csv
import warnings

def get_restframe_dict(filename):
	"""Get rest filters from a csv file
	
	@type filename: string
	@param filename: name of file which contains desired data
	@rtype: dictionary
	@return: dictionary where the key is the ID of a particular sample, and the value is the rest frame filter
	
	"""
	rframe_dict = {}
	
	with open(filename, newline='') as rframe_csv:
		rframe_reader = csv.reader(rframe_csv)
		for row in rframe_reader:
			try:
				sample_id = int(row[0])
				rframe_dict[row[0]] = row[2]
			except:
				continue
	return rframe_dict

def make_path_collage(folder_fn, mode_list):
	"""Make folders which match my organization scheme if they don't exist
	
	@type folder_fn: string
	@param folder_fn: name of folder which contains filter folders with desired data
	@type mode_list: list
	@param mode_list: list of scaling modes
	@rtype: None
	
	"""
	fn = folder_fn + '_collage'
	for mode in mode_list:
		path = (fn, mode).join('/')
		if not os.path.exists(path):
			os.makedirs(path)

def path_to_info(path_name, folder_name):
	"""Take a full path and convert it into the 3 strings I use in the rest of this code.
	
	@type path_name: string
	@param path_name: full path from root directory to a file
	@type folder_name: string
	@param folder_name: name of folder which contains filter folders with desired data
	@rtype: tuple
	@return: (shortened path string, file name string, filter string)
	
	"""
	sps = path_name[-29 - len(folder_name):] #Shortened Path String
	fns = path_name[-22:-5]                  #File Name String
	fts = path_name[-16:-11]                 #Filter String
	
	return (sps, fns, fts)

def get_fits_data(fn, sig_fract, percent_fract):
	"""Get pixel data from .fits file and return numpy pixel arrays.
	
	@type fn: string
	@param fn: file location string
	@type sig_fract: float
	@param sig_fract: fraction of sigma clipping
	@type percent_fract: float
	@param percent_fract: convergence fraction
	@rtype: tuple
	@return: (raw pixel data minus sky value ,raw pixel data array)
	
	"""
	
	with pyfits.open(fn) as hdulist:
		img_header = hdulist[0].header
		img_data_raw = hdulist[0].data
	width=img_data_raw.shape[0]
	height=img_data_raw.shape[1]
	# print("#INFO : ", fn, width, height)
	img_data_raw = numpy.array(img_data_raw, dtype=float)
	# sky, num_iter = img_scale.sky_median_sig_clip(img_data, sig_fract, percent_fract, max_iter=100)
	sky, num_iter = img_scale.sky_mean_sig_clip(img_data_raw, sig_fract, percent_fract, max_iter=10)
	# print("sky = ", sky, '(', num_iter, ')')
	img_data = img_data_raw - sky
	# print("... min. and max. value : ", numpy.min(img_data), numpy.max(img_data))

	return (img_data, img_data_raw, width, height)

def img_scale_getfig(fn, sig_fract, percent_fract, mode, min_val=None):
	"""Get pixel data from .fits file, scale it, turn it into a pyplot image.
	
	@type fn: string
	@param fn: file location string
	@type sig_fract: float
	@param sig_fract: fraction of sigma clipping
	@type percent_fract: float
	@param percent_fract: convergence fraction
	@type mode: string
	@param mode: method of scaling
	@type min_val: float
	@param min_val: minimum data value
	@rtype: numpy array
	@return: image data array
	
	"""
	(img_data, img_data_raw, width, height) = get_fits_data(fn, sig_fract, percent_fract)
	
	if mode == 'sqrt':
		new_img = img_scale.sqrt(img_data, scale_min = min_val)
	elif mode == 'power':
		new_img = img_scale.power(img_data, power_index=3.0, scale_min = min_val)
	elif mode == 'log':
		new_img = img_scale.log(img_data_raw, scale_min = min_val, exponent = 1000)
	elif mode == 'asinh_beta_01':
		new_img = img_scale.asinh(img_data, scale_min = min_val, non_linear=0.01)
	elif mode == 'asinh_beta_05':
		new_img = img_scale.asinh(img_data, scale_min = min_val, non_linear=0.5)
	elif mode == 'asinh_beta_20':
		new_img = img_scale.asinh(img_data, scale_min = min_val, non_linear=2.0)
	elif mode == 'histeq':
		new_img = img_scale.histeq(img_data_raw, num_bins=256)
	elif mode == 'logistic':
		new_img = img_scale.logistic(img_data_raw, center = 0.03, slope = 0.3)
	else:
		new_img = img_scale.linear(img_data, scale_min = min_val)

	return new_img

def img_scale_savefig(new_img, fn, filt, folder_fn, mode, color=pylab.cm.hot, size_inches=3.4, dpi=300):
	"""Save a .png image of the numpy pixel data from img_scale_getfig().
	
	@type new_img: numpy array
	@param new_img: pixel data array
	@type fn: string
	@param fn: file name string
	@type filt: string
	@param filt: filter name string
	@type folder_fn: string
	@param folder_fn: sample folder name string
	@type mode: string
	@param mode: method of scaling
	@type color: matplotlib colormap
	@param color: colormap to use for saved image
	@type size_inches: float
	@param size_inches: size of output image
	@type dpi: integer
	@param dpi: dots per inch of output image
	@rtype: None
	@return: saves a pyplot figure as .png
	
	"""
	fig = pylab.gcf()
	fig.set_size_inches(size_inches, size_inches)
	
	out_path = folder_fn + '_converted/' + mode + '/' + filt
	
	if not os.path.exists(out_path):
		os.makedirs(out_path)
	
	pylab.imshow(new_img, interpolation='nearest', origin='lower', cmap=color)
	pylab.axis('off')
	pylab.tight_layout()
	pylab.savefig(out_path + '/' + fn + '_' + mode + '.png', dpi=(dpi))
	pylab.clf()

def img_scale_collage(fn_list, sig_fract, percent_fract, min_val, filters, mode, folder_fn, color=pylab.cm.hot, size_inches=3.4, dpi=300, restframe=None):
	"""Save a collage .png image of the fits data for each filter..
	
	@type fn: list
	@param fn: list of file name strings
	@type sig_fract: float
	@param sig_fract: fraction of sigma clipping
	@type percent_fract: float
	@param percent_fract: convergence fraction
	@type min_val: float
	@param min_val: minimum data value
	@type filters: list
	@param filters: list of filter name strings
	@type mode: string
	@param mode: method of scaling
	@type folder_fn: string
	@param folder_fn: name of folder which contains filter folders with desired data
	@type color: matplotlib colormap
	@param color: colormap to use for saved image
	@type size_inches: float
	@param size_inches: size of output image
	@type dpi: integer
	@param dpi: dots per inch of output image
	@rtype: None
	@return: saves a pyplot figure as .png
	
	"""
	fig, ((ax1, ax2, ax3), (ax4, ax5, ax6), (ax7, ax8, ax9)) = pylab.subplots(3, 3)
	fig.set_size_inches(size_inches, size_inches)
	
	axes = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9]
	
	for i, fn in enumerate(fn_list):
		new_img = img_scale_getfig(fn, sig_fract, percent_fract, mode, min_val = min_val)
		
		axes[i].set_title(str(i + 1) + ') ' + filters[i])
		axes[i].axis('off')
		axes[i].imshow(new_img, interpolation='nearest', origin='lower', cmap=color)
		
		if restframe == filters[i]:
			axes[8].set_title('Rest Frame) ' + filters[i])
			axes[8].axis('off')
			axes[8].imshow(new_img, interpolation='nearest', origin='lower', cmap=color)
			
	r = fn_list[6]
	g = fn_list[4]
	b = fn_list[1]
	
	rgb_array = get_rgb((r,g,b), min_val=min_val)
	
	axes[7].set_title('RGB')
	axes[7].axis('off')
	axes[7].imshow(rgb_array, interpolation='nearest', origin='lower')
	
	out_path = folder_fn + '_collage/' + mode
	
	if not os.path.exists(out_path):
		os.makedirs(out_path)
	
	pylab.suptitle('ceers_' + fn_list[0][-10:-5])
	pylab.savefig(out_path + '/ceers_' + fn_list[0][-10:-5] + '_' + mode + '.png', dpi=(dpi))
	pylab.close('all')

def get_rgb(channel_list, sig_fract=3.0, percent_fract=5.0-4, min_val=None, color_balance=(1,1,1)):
	"""Get RGB Image Data from 3 Channels
	
	@type channel_list: list
	@param channel_list: list of file name strings
	@type sig_fract: float
	@param sig_fract: fraction of sigma clipping
	@type percent_fract: float
	@param percent_fract: convergence fraction
	@type min_val: float
	@param min_val: minimum data value
	@type color_balance: tuple
	@param color_balance: scaling factor for each channel
	@rtype: numpy array
	@return: RGB array ready for insertion into a matplotlib figure
	
	"""
	img_data_r = get_fits_data(channel_list[0], sig_fract, percent_fract)
	img_data_g = get_fits_data(channel_list[1], sig_fract, percent_fract)
	img_data_b = get_fits_data(channel_list[2], sig_fract, percent_fract)
	
	rgb_array = numpy.empty((img_data_r[2],img_data_r[3],3), dtype=float)
	
	r = img_scale.asinh(img_data_r[0] * color_balance[0], scale_min = min_val, non_linear=0.005)
	g = img_scale.asinh(img_data_g[0] * color_balance[1], scale_min = min_val, non_linear=0.005)
	b = img_scale.asinh(img_data_b[0] * color_balance[2], scale_min = min_val, non_linear=0.005)
	"""
	r = img_scale.log(img_data_r[0] * color_balance[0], scale_min = min_val)
	g = img_scale.log(img_data_g[0] * color_balance[1], scale_min = min_val)
	b = img_scale.log(img_data_b[0] * color_balance[2], scale_min = min_val)
	"""
	rgb_array[:,:,0] = r
	rgb_array[:,:,1] = g
	rgb_array[:,:,2] = b
	
	return rgb_array

def save_collage_bulk(folder_fn, mode_list, filter_list, sig_fract, percent_fract, restframes, color=pylab.cm.hot, size_inches=3.4, dpi=300):
	"""Get all .fits files in a given folder
	
	@type folder_fn: 
	@param folder_fn: 
	@type mode_list: 
	@param mode_list: 
	@type filter_list: 
	@param filter_list: 
	@type sig_fract: float
	@param sig_fract: fraction of sigma clipping
	@type percent_fract: float
	@param percent_fract: convergence fraction
	@type restframes: dictionary
	@param restframes: dictionary where the key is the ID of a particular sample, and the value is the rest frame filter
	@type color: matplotlib colormap
	@param color: colormap to use for saved image
	@type size_inches: float
	@param size_inches: size of output image
	@type dpi: integer
	@param dpi: dots per inch of output image
	@rtype: None
	@return: saves a pyplot figure as .png
	
	"""
	
	# Getting the current work directory (cwd)
	thisdir = os.getcwd()
	fn_list = []

	# r=root, d=directories, f = files
	for r, d, f in os.walk(thisdir):
		for file in f:
			if file.endswith(".fits") and (folder_fn in r):
				if path_to_info(os.path.join(r, file), folder_fn) not in fn_list:
					fn_list.append(path_to_info(os.path.join(r, file), folder_fn))
	
	file_ids_unique = []
	for i in fn_list:
		if i[1][-5:] not in file_ids_unique:
			file_ids_unique.append(i[1][-5:])
	
	with alive_bar(len(file_ids_unique) * len(mode_list), title='Total Progress') as bar:
		for index, mode in enumerate(mode_list):
			print('Processing: ' + mode)
			for f_id in file_ids_unique:
				with warnings.catch_warnings(record=True) as caught_warnings:
					files = []
					for filt in filter_list:
						files.append(folder_fn + '/' + filt + '/ceers_' + filt + '_' + f_id + '.fits')
					img_scale_collage(files, sig_fract, percent_fract, 0.0, filter_list, mode, folder_fn, color=color, size_inches=size_inches, dpi=dpi, restframe=restframes[f_id])
					if caught_warnings:
						print('Something happened on sample ' + f_id)
						for warn in caught_warnings:
							print(f"{warn.message}")
				bar()

def collage_rgb_comparison(fn_list, sig_fract, percent_fract, min_val, filters, mode, folder_name, color=pylab.cm.hot, size_inches=3.4, dpi=300, restframe=None):
	"""Save a collage .png image of the fits data for each filter..
	
	@type fn: list
	@param fn: list of file name strings
	@type sig_fract: float
	@param sig_fract: fraction of sigma clipping
	@type percent_fract: float
	@param percent_fract: convergence fraction
	@type min_val: float
	@param min_val: minimum data value
	@type filters: list
	@param filters: list of filter name strings
	@type mode: string
	@param mode: method of scaling
	@type folder_name: string
	@param folder_name: name of folder which contains filter folders with desired data
	@type color: matplotlib colormap
	@param color: colormap to use for saved image
	@type size_inches: float
	@param size_inches: size of output image
	@type dpi: integer
	@param dpi: dots per inch of output image
	@rtype: None
	@return: saves a pyplot figure as .png
	
	"""
	fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = pylab.subplots(2, 3)
	fig.set_size_inches(size_inches, size_inches)
	
	axes = [ax1, ax2, ax3, ax4, ax5, ax6]
			
	r = fn_list[6]
	g = fn_list[4]
	b = fn_list[1]
	
	cb1 = (1,1,1)
	cb2 = (1,1.5,3)
	cb3 = (1,3,5)
	
	rChannel = img_scale_getfig(r, sig_fract, percent_fract, mode, min_val = min_val)
	gChannel = img_scale_getfig(g, sig_fract, percent_fract, mode, min_val = min_val)
	bChannel = img_scale_getfig(b, sig_fract, percent_fract, mode, min_val = min_val)
	
	rgb_array1 = get_rgb((r,g,b), min_val=min_val, color_balance=cb1)
	rgb_array2 = get_rgb((r,g,b), min_val=min_val, color_balance=cb2)
	rgb_array3 = get_rgb((r,g,b), min_val=min_val, color_balance=cb3)
	
	fs = 7
	
	axes[0].set_title('Red: f444w', fontsize=fs)
	axes[0].axis('off')
	axes[0].imshow(rChannel, interpolation='nearest', origin='lower', cmap=color)
	
	axes[1].set_title('Green: f356w', fontsize=fs)
	axes[1].axis('off')
	axes[1].imshow(gChannel, interpolation='nearest', origin='lower', cmap=color)
	
	axes[2].set_title('Blue: f150w', fontsize=fs)
	axes[2].axis('off')
	axes[2].imshow(bChannel, interpolation='nearest', origin='lower', cmap=color)
	
	axes[3].set_title(str(cb1), fontsize=fs)
	axes[3].axis('off')
	axes[3].imshow(rgb_array1, interpolation='nearest', origin='lower')
	
	axes[4].set_title(str(cb2), fontsize=fs)
	axes[4].axis('off')
	axes[4].imshow(rgb_array2, interpolation='nearest', origin='lower')
	
	axes[5].set_title(str(cb3), fontsize=fs)
	axes[5].axis('off')
	axes[5].imshow(rgb_array3, interpolation='nearest', origin='lower')
	
	pylab.suptitle('ceers_' + fn_list[0][-10:-5])
	pylab.savefig(folder_name + '_RGBComp/' + mode + '/ceers_' + fn_list[0][-10:-5] + '_' + mode + '.png', dpi=(dpi))
	pylab.close('all')

def save_comparison_bulk(folder_fn, mode_list, filter_list, sig_fract, percent_fract, restframes, color=pylab.cm.hot, size_inches=3.4, dpi=300):
	"""Get all .fits files in a given folder
	
	@type folder_fn: 
	@param folder_fn: 
	@type mode_list: 
	@param mode_list: 
	@type filter_list: 
	@param filter_list: 
	@type sig_fract: float
	@param sig_fract: fraction of sigma clipping
	@type percent_fract: float
	@param percent_fract: convergence fraction
	@type restframes: dictionary
	@param restframes: dictionary where the key is the ID of a particular sample, and the value is the rest frame filter
	@type color: matplotlib colormap
	@param color: colormap to use for saved image
	@type size_inches: float
	@param size_inches: size of output image
	@type dpi: integer
	@param dpi: dots per inch of output image
	@rtype: None
	@return: saves a pyplot figure as .png
	
	"""
	
	# Getting the current work directory (cwd)
	thisdir = os.getcwd()
	fn_list = []

	# r=root, d=directories, f = files
	for r, d, f in os.walk(thisdir):
		for file in f:
			if file.endswith(".fits"):
				if path_to_info(os.path.join(r, file), folder_fn) not in fn_list:
					fn_list.append(path_to_info(os.path.join(r, file), folder_fn))
	
	file_ids_unique = []
	for i in fn_list:
		if i[1][-5:] not in file_ids_unique:
			file_ids_unique.append(i[1][-5:])
	
	with alive_bar(len(file_ids_unique) * len(mode_list), title='Total Progress') as bar:
		for index, mode in enumerate(mode_list):
			print('Processing: ' + mode)
			for f_id in file_ids_unique:
				files = []
				for filt in filter_list:
					files.append(folder_fn + '/' + filt + '/ceers_' + filt + '_' + f_id + '.fits')
				collage_rgb_comparison(files, sig_fract, percent_fract, 0.0, filter_list, mode, folder_fn, color=color, size_inches=size_inches, dpi=dpi, restframe=restframes[f_id])
				bar()

def main():
	sig_fract = 5.0
	percent_fract = 0.01
	i_scale = 6.8
	dpi = 300
	color = pylab.cm.Greys
	restframes = get_restframe_dict('sample_2/id_list.csv')

	data_folder = 'sample_2'

	scale_modes = ['sqrt',
			'power',
			'log',
			'linear',
			'asinh_beta_01',
			'asinh_beta_05',
			'asinh_beta_20',
			'histeq',
			'logistic']
	
	filter_list = ['f115w',
			'f150w',
			'f200w',
			'f277w',
			'f356w',
			'f410m',
			'f444w',]

	save_collage_bulk(data_folder, scale_modes[2:3], filter_list, sig_fract, percent_fract, restframes, color=color, size_inches=i_scale, dpi=dpi)
	
if __name__ == "__main__":
	main()
