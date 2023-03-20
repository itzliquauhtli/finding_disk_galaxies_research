# finding_disk_galaxies_research

Code for generating images from FITS data for use in a public galaxy categorization effort. Adapted by Dylan Bateman, Undergraduate studying Physics at the University of Missouri, from code made available by Min-Su Shin at https://astromsshin.github.io/science/code/Python_fits_image/index.html.

### small_sample

  - Folder containing raw FITS data, as well as information about the projects goals and methods by the project head, Vicky Kuhn.

### small_sample_collage

  - Folder contains collages of each sample, containing each filter as well as an RGB composition and an extra panel showing the rest frame of the sample a second time.

![The collage of sample 30258. It is a three by three grid of square images, eight of which display greyscale images of individual filters, and one containing an RGB composite of three filters.](/small_sample_collage/linear/ceers_30258_linear.png)

### small_sample_converted

  - Folder contains individual .png images of each filter in each scaling mode available via img_scale.py.

![A greyscale image of the f277w filter of sample 30273.](/small_sample_converted/linear/f277w/ceers_f277w_30273_linear.png)

### small_sample_RGBComp

  - Folder contains test images containing the R, G, and B channels of the RGB composition, and then 3 RGB comps with different scaling methods for the channels.

![The comparison of different channel scaling for sample 24433. It is a two by three grid of square images. The first row is 3 grayscale images of filters, labeled left to right as 'Red: f444w', 'Green: f356w', and 'Blue: f150w'. The bottom row is three RGB composites of the top row. They are labeled according to the scaling factor of each channel, with the format (Red Scale, Green Scale, Blue Scale). From left to right, they read (1,1,1), (1,1.5,3), and (1,3,5).](/small_sample_RGBComp/Scale Inside/ceers_24433_linear.png)
  
### Loose Files

  - fits_to_png_bulk.py
    - This is the code that I wrote which generated the images. It was adapted from the methods in the code base found at Min-Su Shin's URL above. When run, it finds all .fits files under itself in the file heirarchy. Then, it generates .png images from that information. There is no interface, so to changing the operation mode involves changing the function called in main().
  - img_scale.py
    - Min-Su Shin's code for scaling the numpy arrays of image data. 
  - restframe.csv
    - This spreadsheet contains the restframe for each galaxy.
  - Trilogy_rgb.py
    - Code written by James McMillen, another undergrad, which he used to generate the images in the 'Galaxy Images' folder. Those images, as well as this code, is not used in the current implimentation, but was used for comparison when implimenting RGB images into my own fits_to_png_bulk.py program.
