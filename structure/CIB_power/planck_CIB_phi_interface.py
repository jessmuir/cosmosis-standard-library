from cosmosis.datablock import names, option_section
import numpy as np
import kappa_cmb_kern
import scipy.integrate
from scipy.interpolate import RectBivariateSpline, interp1d
import sys
# We have a collection of commonly used pre-defined block section names.
# If none of the names here is relevant for your calculation you can use any
# string you want instead.
cosmo = names.cosmological_parameters
distances = names.distances

# TODO



def cl_limber_x(z_chi, p_kz, l, k1, k2=None, xmin=0.0, xmax=13000.):
    """ calculate the cross-spectrum at multipole l between kernels k1 and k2 in the limber approximation.
    the distance integral is performed from conformal distance xmin to xmax (both in Mpc). """
    if k2 == None:
        k2 = k1

    def integrand(x):
        z = z_chi(x)
        return 1. / x ** 2 * k1.w_lxz(l, x, z) * k2.w_lxz(l, x, z) * rbs.ev((l + 0.5) / x, z)

    return scipy.integrate.quad(integrand, xmin, xmax, limit=100)[0]


def cl_limber_z(chi_z, hspline, rbs, l, k1, k2=None, zmin=0.0, zmax=1100.):
    """ calculate the cross-spectrum at multipole l between kernels k1 and k2 in the limber approximation.
    the distance integral is performed from redshifts zmin to zmax. """

    #  TODO check the H factor.

    if k2 == None:
        k2 = k1

    def integrand(z):

        x = chi_z(z)
        return 1. / x ** 2 / hspline(z) * k1.w_lxz(l, x, z) * k2.w_lxz(l, x, z) * rbs.ev((l + 0.5) / x, z)

    return scipy.integrate.quad(integrand, zmin, zmax, limit=100)[0]


def setup(options):

    llmin = options.get_double(option_section, "llmin", default=1.)
    llmax = options.get_double(option_section, "llmax", default=3.5)
    dlnl = options.get_double(option_section, "dlnl", default=.1)
    zmin = options.get_double(option_section, "zmin", default=1e-2)
    zmax = options.get_double(option_section, "zmax",
                              default=10.)

    # Frequency of the CIB
    # you can pass an array but they have to be separated by commas  " , "

    nu= options[option_section, "nu"]
    nu=np.fromstring(nu, dtype=float, sep=',')
    zc = options.get_double(option_section, "zc", default=2.)
    zs = options.get_double(option_section, "zs", default=2.)
    b = options.get_double(option_section, "b", default=1.)
    sys.exit()

    blockname = options.get_string(option_section, "matter_power", default="matter_power_nl")
    # blockname = options.get_string(option_section, "matter_power", default="matter_power_nl")
    # maybe the suffix for saving the spectra
    # zmax (or take it from CAMB)
    # maybe choose between kappa and others
    lbins = np.arange(llmin, llmax, dlnl)
    lbins = 10. ** lbins
    return (lbins, blockname, zmin, zmax, nu, zc, zs, b)


def execute(block, config):
    # Just a simple rename for clarity.
    lbins, blockname, zmin, zmax, nu, zc, zs, b = config


    # LOAD POWER
    # =======================

    zpower = block[blockname, "z"]
    kpower = block[blockname, "k_h"]
    powerarray = block[blockname, "p_k"].reshape([np.size(zpower), np.size(kpower)]).T
    rbs = RectBivariateSpline(kpower, zpower, powerarray)

    # Cosmological parameters
    # =======================

    omega_m = block[cosmo, "omega_m"]
    h0 = block[cosmo, "h0"]
    # Distances
    h = block[distances, "h"]
    tmp = h[::-1]
    h = tmp

    zdist = block[distances, "z"]
    tmp = zdist[::-1]  # reverse them so they are going in ascending order
    zdist = tmp
    # =======================

    # Distances
    # =======================
    # reverse them so they are going in ascending order

    d_m = block[distances, "d_m"]
    tmp = d_m[::-1]
    d_m = tmp

    xlss = block[distances, "chistar"]

    # These have dimensions of Mpc; change to h^{-1} Mpc
    d_m *= h0
    h /= h0
    xlss *= h0
    # now in units of h^{-1} Mpc or the inverse
    chispline = interp1d(zdist, d_m)
    hspline = interp1d(zdist, h)

    # =======================
    # DEFINE KERNEL
    chs   = [ ('857',     '350',    1.e-6/np.sqrt(4.99),   'orange', 1.),
          ('545',     '550',    1.e-6/np.sqrt(3391.5), 'blue', 10**3),
          ('353',     '850',    1.e-6/np.sqrt(83135.), 'magenta', 10**5),
          ('217',    '1380',    1.e-6/np.sqrt(231483), 'green') , 2*10**6]#

    lkern = kappa_cmb_kern.kern(zdist, omega_m, h0, xlss)

    cl = np.zeros(np.size(lbins))




    for i, l in enumerate(lbins):
        cl[i] = cl_limber_z(chispline, hspline, rbs, l, cib_hall.ssed_kern(h0, zdist, chispline, nu, jbar_kwargs={'zc': 2.0, 'sigmaz': zs}), lkern, zmin=zmin, zmax=zmax)
        print cl[i]
        print ""


    cl = [cl_limber_z(chispline, hspline, rbs, l, cib_hall.ssed_kern(h0, zdist, chispline, nu, jbar_kwargs={'zc': 2.0, 'sigmaz': zs}), lkern, zmin=zmin, zmax=zmax) for l in lbins]
    # =======================
    # SAVE INTO DATABLOCK

    section = "limber_spectra"
    block[section, "cl_kappa"] = cl
    block[section, "l_kappa"] = lbins

    return 0
