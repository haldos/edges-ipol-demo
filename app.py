"""
ipol demo
review of some edge detection algorithms
"""

from lib import base_app, build, http, image
from lib.misc import app_expose, ctime
from lib.base_app import init_app
import cherrypy
from cherrypy import TimeoutError
import os.path
import shutil

class app(base_app):
    """ template demo app """
    
    title = "Review of Edge Detection Algorithms"
    input_nb = 1 # number of input images
    input_max_pixels = 500000 # max size (in pixels) of an input image
    input_max_weight = 1 * 1024 * 1024 # max size (in bytes) of an input file
    input_dtype = '3x8i' # input image expected data type
    input_ext = '.png'   # input image expected extension (ie file format)
    is_test = True       # switch to False for deployment

    def __init__(self):
        """
        app setup
        """
        # setup the parent class
        base_dir = os.path.dirname(os.path.abspath(__file__))
        base_app.__init__(self, base_dir)

        # select the base_app steps to expose
        # index() is generic
        app_expose(base_app.index)
        app_expose(base_app.input_select)
        app_expose(base_app.input_upload)
        # params() is modified from the template
        app_expose(base_app.params)
        # run() and result() must be defined here

    def build(self):
        """
        program build/update
        """
        # store common file path in variables
        tgz_file = self.dl_dir + "edge_detectors_v0.1.tar.gz"
        prog_file1 = self.bin_dir + "test_fded"
        prog_file2 = self.bin_dir + "test_haralick"
        prog_file3 = self.bin_dir + "test_mh"
        prog_file4 = self.bin_dir + "test_mh_log"
        log_file = self.base_dir + "build.log"
        # get the latest source archive
    	build.download("http://iie.fing.edu.uy/~haldos/downloads/"
                   	+ "edge_detectors_v0.1.tar.gz", tgz_file)
        # test if the dest file is missing, or too old
        if (os.path.isfile(prog_file)
            and ctime(tgz_file) < ctime(prog_file1)
			and ctime(tgz_file) < ctime(prog_file2)
			and ctime(tgz_file) < ctime(prog_file3)
			and ctime(tgz_file) < ctime(prog_file4)):
            cherrypy.log("not rebuild needed",
                         context='BUILD', traceback=False)
        else:
            # extract the archive
            build.extract(tgz_file, self.src_dir)
            # build the program
            build.run("cd %s && cmake . && make" % (self.src_dir),
                      stdout=log_file)
            # save into bin dir
            if os.path.isdir(self.bin_dir):
                shutil.rmtree(self.bin_dir)
            os.mkdir(self.bin_dir)
            shutil.copy(self.src_dir + "bin/test_fded" , prog_file1)
            shutil.copy(self.src_dir + "bin/test_haralick" , prog_file4)
            shutil.copy(self.src_dir + "bin/test_mh" , prog_file3)
            shutil.copy(self.src_dir + "bin/test_mh_log" , prog_file4)
            # cleanup the source dir
            shutil.rmtree(self.src_dir)
        return

    @cherrypy.expose
    @init_app
    def wait(self, **kwargs):
        """
        params handling and run redirection
        """
        # save and validate the parameters
        try:
           self.cfg['param'] = {'th_fded' : float(th_fded)}
           self.cfg['param'] = {'rho' : float(rho)}
           self.cfg['param'] = {'sigma' : float(sigma)}
           self.cfg['param'] = {'n' : int(n)}
           self.cfg['param'] = {'tzc' : float(tzc)}
           self.cfg['param'] = {'sigma2' : float(sigma2)}
           self.cfg['param'] = {'n2' : int(n2)}
           self.cfg['param'] = {'tzc2' : float(tzc2)}
           #self.cfg.save()
        #print("ENTER wait")
		#print("kwargs = " + str(kwargs))
        # FDED
#        self.cfg['param']['th_fded'] = kwargs['th_fded']
        # HARALICK
#        self.cfg['param']['rho'] = kwargs['rho']
        # MARR-HILDRETH GAUSSIAN
#        self.cfg['param']['sigma'] = kwargs['sigma']
#        self.cfg['param']['n'] = kwargs['n']
#        self.cfg['param']['tzc'] = kwargs['tzc']
        # MARR-HILDRETH LOG
#        self.cfg['param']['sigma2'] = kwargs['sigma2']
#        self.cfg['param']['n2'] = kwargs['n2']
#        self.cfg['param']['tzc2'] = kwargs['tzc2']		
#        self.cfg.save()
        except ValueError:
            return self.error(errcode='badparams',
                              errmsg="The parameter must be numeric.")

        http.refresh(self.base_url + 'run?key=%s' % self.key)
        return self.tmpl_out("wait.html")

    @cherrypy.expose
    @init_app
    def run(self):
        """
        algo execution
        """
        # read the parameters
		# FDED
        th_fded = self.cfg['param']['th_fded']
		# HARALICK
        rho = self.cfg['param']['rho']
		# MARR-HILDRETH GAUSSIAN
        sigma = self.cfg['param']['sigma']
        n = self.cfg['param']['n']
        tzc = self.cfg['param']['tzc']
		# MARR-HILDRETH LOG
        sigma2 = self.cfg['param']['sigma2']
        n2 = self.cfg['param']['n2']
        tzc2 = self.cfg['param']['tzc2']
        # run the algorithm
        try:
            self.run_algo(th_fded,rho,sigma,n,tzc,sigma2,n2,tzc2)
        except TimeoutError:
            return self.error(errcode='timeout') 
        except RuntimeError:
            return self.error(errcode='runtime')
        http.redir_303(self.base_url + 'result?key=%s' % self.key)

        # archive
        ##if self.cfg['meta']['original']:
        ar = self.make_archive()
        ar.add_file("input_0.png", info="input image")
        ar.add_file("roberts.png", info="output image of Roberts algorithm")
        ar.add_file("prewitt.png", info="output image of Prewitt algorithm")
        ar.add_file("sobel.png", info="output image of Sobel algorithm")
        ar.add_file("marr-hildreth.png", info="output image of Marr-Hildreth algorithm (Gaussian kernel)")
        ar.add_file("marr-hildreth-log.png", info="output image of Marr-Hildreth algorithm (LoG kernel)")
        ar.add_file("haralick.png", info="output image of Haralick algorithm")
        ar.add_info({"th_fded": th_fded})
        ar.add_info({"rho": rho})
        ar.add_info({"sigma": sigma})
        ar.add_info({"n": n})
        ar.add_info({"tzc": tzc})
        ar.add_info({"sigma2": sigma2})
        ar.add_info({"n2": n2})
        ar.add_info({"tzc2": tzc2})
        ar.save()
        return self.tmpl_out("run.html")

    def run_algo(self, th_fded, rho, sigma, n, tzc, sigma2, n2, tzc2):
        """
        the core algo runner
        could also be called by a batch processor
        this one needs no parameter
        """
		# FDED
        p1 = self.run_proc(['test_fded', "input_0.png", str(th_fded)])
        self.wait_proc(p1, timeout=self.timeout)
		# HARALICK
        p2 = self.run_proc(['test_haralick', "input_0.png", str(rho), 'haralick.png'])
        self.wait_proc(p2, timeout=self.timeout)
		# MARR-HILDRETH GAUSSIAN
        p3 = self.run_proc(['test_mh', "input_0.png", str(sigma), str(n), str(tzc), 'marr-hildreth.png'])
        self.wait_proc(p3, timeout=self.timeout)
		# MARR-HILDRETH LOG
        p4 = self.run_proc(['test_mh_log', "input_0.png", str(sigma2), str(n2), str(tzc2), 'marr-hildreth-log.png'])
        self.wait_proc(p4, timeout=self.timeout)
        return

    @cherrypy.expose
    @init_app
    def result(self):
        """
        display the algo results
        """
        return self.tmpl_out("result.html",
                             height=image(self.work_dir
                                          + 'marr-hildreth.png').size[1])
