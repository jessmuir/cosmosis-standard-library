#include "gsl/gsl_spline.h"
#include "cosmosis/datablock/c_datablock.h"
#include "interp2d.h"


gsl_spline * spline_from_arrays(int n, double * x, double *y);

DATABLOCK_STATUS save_spline(c_datablock * block, const char * section, 
	const char * n_name, const char * x_name, const char * y_name,
	gsl_spline * s);

gsl_spline * load_spline(c_datablock * block, const char * section, 
	const char * x_name, const char * y_name);



void reverse(double * x, int n);


Interpolator2D * 
load_interpolator(c_datablock * block, gsl_spline * chi_of_z_spline, 
	const char * section,
	const char * k_name, const char * z_name, const char * P_name);